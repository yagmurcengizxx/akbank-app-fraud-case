from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip().rstrip("/") for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    admin_key: str
    allowed_origins: tuple[str, ...]
    session_ttl_seconds: int
    max_frame_bytes: int
    sample_rate: int
    silence_rms_threshold: float
    silence_seconds: float
    activity_rms_threshold: float
    allow_missing_origin: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            admin_key=os.getenv("CALLGUARD_ADMIN_KEY", "change-me-local-only"),
            allowed_origins=_csv(os.getenv(
                "CALLGUARD_ALLOWED_ORIGINS",
                "http://localhost:8091,http://127.0.0.1:8091",
            )),
            session_ttl_seconds=int(os.getenv("CALLGUARD_SESSION_TTL_SECONDS", "900")),
            max_frame_bytes=int(os.getenv("CALLGUARD_MAX_FRAME_BYTES", "8192")),
            sample_rate=int(os.getenv("CALLGUARD_SAMPLE_RATE", "16000")),
            silence_rms_threshold=float(os.getenv("CALLGUARD_SILENCE_RMS", "0.008")),
            silence_seconds=float(os.getenv("CALLGUARD_SILENCE_SECONDS", "1.0")),
            activity_rms_threshold=float(os.getenv("CALLGUARD_ACTIVITY_RMS", "0.02")),
            allow_missing_origin=os.getenv("CALLGUARD_ALLOW_MISSING_ORIGIN", "false").lower() == "true",
        )

