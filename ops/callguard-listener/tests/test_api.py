import json
import unittest
from datetime import UTC, datetime, timedelta

from app.config import Settings
from app.main import create_app


def settings(ttl=60):
    return Settings("test-admin-key", ("http://testserver",), ttl, 8192, 16000, .008, .04, .02, False)


async def request(app, method, path, body=None, headers=None):
    payload = json.dumps(body).encode() if body is not None else b""
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    if body is not None:
        raw_headers.append((b"content-type", b"application/json"))
    async def receive():
        return {"type": "http.request", "body": payload, "more_body": False}

    messages = []

    async def send(message):
        messages.append(message)

    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method,
             "scheme": "http", "path": path, "raw_path": path.encode(), "query_string": b"",
             "root_path": "", "headers": raw_headers, "client": ("127.0.0.1", 1234), "server": ("testserver", 80)}
    await app(scope, receive, send)
    status = next(message["status"] for message in messages if message["type"] == "http.response.start")
    data = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return status, json.loads(data) if data else None


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_health(self):
        status, body = await request(create_app(settings()), "GET", "/health")
        self.assertEqual(status, 200)
        self.assertFalse(body["rawAudioStored"])

    async def test_session_requires_admin_and_masks_phone(self):
        app = create_app(settings())
        status, _ = await request(app, "POST", "/listener/api/sessions", {"phoneNumber": "+905550001234"})
        self.assertEqual(status, 401)
        status, body = await request(app, "POST", "/listener/api/sessions",
                                     {"phoneNumber": "+905550001234", "riskLabel": "RISKY", "mode": "SYNTHETIC_TEST"},
                                     {"X-Admin-Key": "test-admin-key"})
        self.assertEqual(status, 201)
        self.assertNotEqual(body["maskedPhone"], "+905550001234")
        self.assertNotIn("5550001234", str(body))

    async def test_invalid_phone(self):
        status, _ = await request(create_app(settings()), "POST", "/listener/api/sessions",
                                  {"phoneNumber": "abc"}, {"X-Admin-Key": "test-admin-key"})
        self.assertEqual(status, 422)

    async def test_get_auth_stop_and_expiry(self):
        app = create_app(settings())
        _, body = await request(app, "POST", "/listener/api/sessions", {"phoneNumber": "+905550001234"},
                                {"X-Admin-Key": "test-admin-key"})
        path = f"/listener/api/sessions/{body['sessionId']}"
        status, _ = await request(app, "GET", path)
        self.assertEqual(status, 401)
        auth = {"Authorization": f"Bearer {body['sessionToken']}"}
        status, current = await request(app, "GET", path, headers=auth)
        self.assertEqual((status, current["status"]), (200, "ACTIVE"))
        status, stopped = await request(app, "POST", path + "/stop", headers=auth)
        self.assertEqual((status, stopped["status"]), (200, "ENDED"))

        app2 = create_app(settings(ttl=1))
        _, expired = await request(app2, "POST", "/listener/api/sessions", {"phoneNumber": "+905550001234"},
                                   {"X-Admin-Key": "test-admin-key"})
        app2.state.store.get(expired["sessionId"]).expires_at = datetime.now(UTC) - timedelta(seconds=1)
        status, _ = await request(app2, "GET", f"/listener/api/sessions/{expired['sessionId']}",
                                  headers={"Authorization": f"Bearer {expired['sessionToken']}"})
        self.assertEqual(status, 410)


if __name__ == "__main__":
    unittest.main()

