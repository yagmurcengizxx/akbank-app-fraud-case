from __future__ import annotations

import asyncio
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from fastapi import WebSocket

from .models import CreateSessionRequest, EventView, SessionView


def utcnow() -> datetime:
    return datetime.now(UTC)


def mask_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    prefix = "+" if phone.startswith("+") else ""
    if len(digits) <= 4:
        return prefix + "*" * len(digits)
    return prefix + digits[:2] + "*" * (len(digits) - 4) + digits[-2:]


@dataclass
class SessionState:
    session_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    masked_phone: str
    risk_label: str
    mode: str
    sample_rate: int
    status: str = "ACTIVE"
    ended_at: datetime | None = None
    client_connected: bool = False
    stream_started_at: datetime | None = None
    last_packet_at: datetime | None = None
    packets_received: int = 0
    audio_bytes_received: int = 0
    current_rms: float = 0.0
    peak_amplitude: float = 0.0
    audio_activity_count: int = 0
    silence_samples: int = 0
    silence_reported: bool = False
    active_audio: bool = False
    events: list[EventView] = field(default_factory=list)
    event_sockets: set[WebSocket] = field(default_factory=set)
    audio_socket: WebSocket | None = None

    def refresh_expiry(self) -> None:
        if self.status == "ACTIVE" and utcnow() >= self.expires_at:
            self.status = "EXPIRED"
            self.ended_at = self.expires_at
            self.client_connected = False

    def view(self) -> SessionView:
        self.refresh_expiry()
        end = self.ended_at or min(utcnow(), self.expires_at)
        return SessionView(
            sessionId=self.session_id,
            createdAt=self.created_at,
            expiresAt=self.expires_at,
            status=self.status,
            maskedPhone=self.masked_phone,
            riskLabel=self.risk_label,
            mode=self.mode,
            clientConnected=self.client_connected,
            streamStartedAt=self.stream_started_at,
            lastPacketAt=self.last_packet_at,
            packetsReceived=self.packets_received,
            audioBytesReceived=self.audio_bytes_received,
            currentRms=round(self.current_rms, 6),
            peakAmplitude=round(self.peak_amplitude, 6),
            audioActivityCount=self.audio_activity_count,
            durationSeconds=round(max(0.0, (end - self.created_at).total_seconds()), 3),
            sampleRate=self.sample_rate,
        )


class SessionStore:
    def __init__(self, ttl_seconds: int, sample_rate: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.sample_rate = sample_rate
        self.sessions: dict[str, SessionState] = {}
        self._lock = asyncio.Lock()

    async def create(self, request: CreateSessionRequest) -> SessionState:
        async with self._lock:
            for existing in self.sessions.values():
                existing.refresh_expiry()
                if existing.status == "ACTIVE":
                    raise RuntimeError("an active test session already exists")
            now = utcnow()
            session = SessionState(
                session_id=str(uuid.uuid4()),
                token=secrets.token_urlsafe(32),
                created_at=now,
                expires_at=now + timedelta(seconds=self.ttl_seconds),
                masked_phone=mask_phone(request.phone_number),
                risk_label=request.risk_label,
                mode=request.mode,
                sample_rate=self.sample_rate,
            )
            self.sessions[session.session_id] = session
        await self.emit(session, "SESSION_CREATED", {"mode": session.mode})
        if session.risk_label == "RISKY":
            await self.emit(session, "NUMBER_FLAGGED", {"source": "MANUAL_TEST_LABEL"})
        return session

    def get(self, session_id: str) -> SessionState | None:
        session = self.sessions.get(session_id)
        if session:
            session.refresh_expiry()
        return session

    async def emit(self, session: SessionState, event_type: str, data: dict[str, object] | None = None) -> None:
        event = EventView(type=event_type, timestamp=utcnow(), data=data or {})
        session.events.append(event)
        if len(session.events) > 500:
            del session.events[:-500]
        message = {"event": event.model_dump(mode="json"), "session": session.view().model_dump(mode="json")}
        stale: list[WebSocket] = []
        for socket in tuple(session.event_sockets):
            try:
                await socket.send_json(message)
            except Exception:
                stale.append(socket)
        for socket in stale:
            session.event_sockets.discard(socket)

    async def stop(self, session: SessionState) -> None:
        if session.status != "ACTIVE":
            return
        session.status = "ENDED"
        session.ended_at = utcnow()
        session.client_connected = False
        await self.emit(session, "SESSION_ENDED")
        if session.audio_socket:
            try:
                await session.audio_socket.close(code=1000, reason="session ended")
            except Exception:
                pass
            session.audio_socket = None

