import asyncio
import json
import math
import struct
import unittest
from urllib.parse import urlencode

from app.config import Settings
from app.main import create_app
from tests.test_api import request


SETTINGS = Settings("admin", ("http://testserver",), 60, 8192, 16000, .008, .04, .02, False)


class ASGIWebSocket:
    def __init__(self, app, path, query, origin="http://testserver"):
        self.app, self.path, self.query, self.origin = app, path, query, origin
        self.to_app, self.from_app = asyncio.Queue(), asyncio.Queue()
        self.task = None

    async def connect(self):
        scope = {"type": "websocket", "asgi": {"version": "3.0"}, "http_version": "1.1",
                 "scheme": "ws", "path": self.path, "raw_path": self.path.encode(),
                 "query_string": urlencode(self.query).encode(), "root_path": "",
                 "headers": [(b"origin", self.origin.encode())], "client": ("127.0.0.1", 1234),
                 "server": ("testserver", 80), "subprotocols": [], "state": {}}
        self.task = asyncio.create_task(self.app(scope, self.to_app.get, self.from_app.put))
        await self.to_app.put({"type": "websocket.connect"})
        return await asyncio.wait_for(self.from_app.get(), 1)

    async def send_bytes(self, data):
        await self.to_app.put({"type": "websocket.receive", "bytes": data})

    async def receive(self):
        return await asyncio.wait_for(self.from_app.get(), 1)

    async def receive_json(self):
        return json.loads((await self.receive())["text"])

    async def disconnect(self):
        if self.task and not self.task.done():
            await self.to_app.put({"type": "websocket.disconnect", "code": 1000, "reason": "test complete"})
            await asyncio.wait_for(self.task, 1)


async def new_session(app):
    _, body = await request(app, "POST", "/listener/api/sessions",
                            {"phoneNumber": "+905550001234", "mode": "SYNTHETIC_TEST"},
                            {"X-Admin-Key": "admin"})
    return body


def tone_frame(amplitude=.5):
    values = [round(math.sin(2 * math.pi * 440 * i / 16000) * amplitude * 32767) for i in range(320)]
    return struct.pack("<320h", *values)


class WebSocketTests(unittest.IsolatedAsyncioTestCase):
    async def test_binary_updates_metrics_and_dashboard_events(self):
        app = create_app(SETTINGS); session = await new_session(app); query = {"token": session["sessionToken"]}
        events = ASGIWebSocket(app, f"/listener/ws/events/{session['sessionId']}", query)
        self.assertEqual((await events.connect())["type"], "websocket.accept")
        self.assertEqual((await events.receive_json())["event"]["type"], "SNAPSHOT")
        audio = ASGIWebSocket(app, f"/listener/ws/audio/{session['sessionId']}", query)
        self.assertEqual((await audio.connect())["type"], "websocket.accept")
        self.assertEqual((await events.receive_json())["event"]["type"], "WEBSOCKET_CONNECTED")
        await audio.send_bytes(tone_frame())
        names = [(await events.receive_json())["event"]["type"] for _ in range(3)]
        self.assertEqual(names, ["STREAM_STARTED", "FIRST_AUDIO", "AUDIO_ACTIVITY"])
        current = app.state.store.get(session["sessionId"])
        self.assertEqual((current.packets_received, current.audio_bytes_received), (1, 640))
        self.assertTrue(.34 < current.current_rms < .36)
        self.assertTrue(.49 < current.peak_amplitude < .51)
        await audio.disconnect(); await events.disconnect()

    async def test_silence_disconnect_and_invalid_frame(self):
        app = create_app(SETTINGS); session = await new_session(app); query = {"token": session["sessionToken"]}
        audio = ASGIWebSocket(app, f"/listener/ws/audio/{session['sessionId']}", query)
        await audio.connect(); await audio.send_bytes(b"\0\0" * 320); await audio.send_bytes(b"\0\0" * 320)
        await asyncio.sleep(0); await audio.disconnect()
        current = app.state.store.get(session["sessionId"])
        self.assertEqual(current.packets_received, 2)
        self.assertIn("SILENCE_DETECTED", [event.type for event in current.events])
        self.assertIn("STREAM_DISCONNECTED", [event.type for event in current.events])

        await request(app, "POST", f"/listener/api/sessions/{session['sessionId']}/stop",
                      headers={"Authorization": f"Bearer {session['sessionToken']}"})
        session2 = await new_session(app)
        bad = ASGIWebSocket(app, f"/listener/ws/audio/{session2['sessionId']}", {"token": session2["sessionToken"]})
        await bad.connect(); await bad.send_bytes(b"x")
        close = await bad.receive(); self.assertEqual(close["type"], "websocket.close")
        await bad.task
        self.assertIn("STREAM_INTERRUPTED", [event.type for event in app.state.store.get(session2["sessionId"]).events])

    async def test_untrusted_origin_is_rejected(self):
        app = create_app(SETTINGS); session = await new_session(app)
        socket = ASGIWebSocket(app, f"/listener/ws/audio/{session['sessionId']}",
                               {"token": session["sessionToken"]}, "https://evil.example")
        response = await socket.connect()
        self.assertEqual((response["type"], response["code"]), ("websocket.close", 4401))
        await socket.task


if __name__ == "__main__":
    unittest.main()

