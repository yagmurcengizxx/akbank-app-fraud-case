from __future__ import annotations

import asyncio
import hmac
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .audio import InvalidPCMFrame, analyze_pcm16_le
from .config import Settings
from .models import CreateSessionRequest, CreateSessionResponse, SessionView
from .store import SessionState, SessionStore, utcnow

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()
    store = SessionStore(config.session_ttl_seconds, config.sample_rate)
    app = FastAPI(title="CallGuard GSM Audio Monitor", version="1.0.0", docs_url=None, redoc_url=None)
    app.state.settings = config
    app.state.store = store

    async def require_admin(x_admin_key: str = Header(default="")) -> None:
        if not hmac.compare_digest(x_admin_key, config.admin_key):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid admin credentials")

    async def authorized_session(session_id: str, authorization: str = Header(default="")) -> SessionState:
        session = store.get(session_id)
        token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        if not session or not hmac.compare_digest(token, session.token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid session credentials")
        if session.status == "EXPIRED":
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="session expired")
        return session

    def websocket_session(websocket: WebSocket, session_id: str) -> SessionState | None:
        origin = (websocket.headers.get("origin") or "").rstrip("/")
        if (not origin and not config.allow_missing_origin) or (origin and origin not in config.allowed_origins):
            return None
        session = store.get(session_id)
        token = websocket.query_params.get("token", "")
        if not session or session.status != "ACTIVE" or not hmac.compare_digest(token, session.token):
            return None
        return session

    @app.exception_handler(InvalidPCMFrame)
    async def invalid_pcm_handler(_: Request, exc: InvalidPCMFrame) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": {"code": "INVALID_AUDIO_FRAME", "message": str(exc)}})

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "service": "callguard-listener", "sampleRate": config.sample_rate,
                "rawAudioStored": False, "transcriptionEnabled": False}

    @app.post("/listener/api/sessions", response_model=CreateSessionResponse, status_code=201,
              dependencies=[Depends(require_admin)])
    async def create_session(body: CreateSessionRequest) -> CreateSessionResponse:
        try:
            session = await store.create(body)
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return CreateSessionResponse(**session.view().model_dump(), sessionToken=session.token)

    @app.get("/listener/api/sessions/{session_id}", response_model=SessionView)
    async def get_session(session: SessionState = Depends(authorized_session)) -> SessionView:
        return session.view()

    @app.post("/listener/api/sessions/{session_id}/stop", response_model=SessionView)
    async def stop_session(session: SessionState = Depends(authorized_session)) -> SessionView:
        await store.stop(session)
        return session.view()

    @app.websocket("/listener/ws/events/{session_id}")
    async def event_socket(websocket: WebSocket, session_id: str) -> None:
        session = websocket_session(websocket, session_id)
        if not session:
            await websocket.close(code=4401)
            return
        await websocket.accept()
        session.event_sockets.add(websocket)
        await websocket.send_json({
            "event": {"type": "SNAPSHOT", "timestamp": utcnow().isoformat(),
                      "data": {"events": [event.model_dump(mode="json") for event in session.events]}},
            "session": session.view().model_dump(mode="json"),
        })
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            session.event_sockets.discard(websocket)

    @app.websocket("/listener/ws/audio/{session_id}")
    async def audio_socket(websocket: WebSocket, session_id: str) -> None:
        session = websocket_session(websocket, session_id)
        if not session:
            await websocket.close(code=4401)
            return
        if session.audio_socket is not None:
            await websocket.close(code=4409)
            return
        await websocket.accept()
        session.audio_socket = websocket
        session.client_connected = True
        await store.emit(session, "WEBSOCKET_CONNECTED", {"mode": session.mode})
        interrupted = False
        try:
            while session.status == "ACTIVE":
                message = await asyncio.wait_for(websocket.receive(), timeout=10.0)
                if message.get("type") == "websocket.disconnect":
                    break
                frame = message.get("bytes")
                if frame is None:
                    await store.emit(session, "STREAM_INTERRUPTED", {"reason": "binary PCM16 required"})
                    await websocket.close(code=1003, reason="binary PCM16 required")
                    interrupted = True
                    break
                try:
                    metrics = analyze_pcm16_le(frame, config.max_frame_bytes)
                except InvalidPCMFrame as exc:
                    await store.emit(session, "STREAM_INTERRUPTED", {"reason": str(exc)})
                    await websocket.close(code=1009, reason="invalid audio frame")
                    interrupted = True
                    break
                now = utcnow()
                first = session.packets_received == 0
                if first:
                    session.stream_started_at = now
                    await store.emit(session, "STREAM_STARTED", {"sampleRate": config.sample_rate})
                session.last_packet_at = now
                session.packets_received += 1
                session.audio_bytes_received += len(frame)
                session.current_rms = metrics.rms
                session.peak_amplitude = max(session.peak_amplitude, metrics.peak)
                if first:
                    await store.emit(session, "FIRST_AUDIO", {"bytes": len(frame)})
                if metrics.rms >= config.activity_rms_threshold:
                    session.silence_samples = 0
                    session.silence_reported = False
                    if not session.active_audio:
                        session.active_audio = True
                        session.audio_activity_count += 1
                        await store.emit(session, "AUDIO_ACTIVITY", {"rms": round(metrics.rms, 6)})
                elif metrics.rms < config.silence_rms_threshold:
                    session.active_audio = False
                    session.silence_samples += metrics.sample_count
                    if (not session.silence_reported and
                            session.silence_samples >= config.sample_rate * config.silence_seconds):
                        session.silence_reported = True
                        await store.emit(session, "SILENCE_DETECTED", {
                            "silenceSeconds": round(session.silence_samples / config.sample_rate, 2)
                        })
        except asyncio.TimeoutError:
            interrupted = True
            await store.emit(session, "STREAM_INTERRUPTED", {"reason": "packet timeout"})
            try:
                await websocket.close(code=1001, reason="packet timeout")
            except Exception:
                pass
        except WebSocketDisconnect:
            pass
        finally:
            if session.audio_socket is websocket:
                session.audio_socket = None
            session.client_connected = False
            if session.status == "ACTIVE":
                await store.emit(session, "STREAM_DISCONNECTED", {"interrupted": interrupted})

    @app.get("/", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()

