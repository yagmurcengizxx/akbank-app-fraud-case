from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateSessionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    phone_number: str = Field(alias="phoneNumber", min_length=8, max_length=24)
    risk_label: Literal["UNMARKED", "RISKY"] = Field(default="UNMARKED", alias="riskLabel")
    mode: Literal["LIVE_MICROPHONE", "SYNTHETIC_TEST"] = "LIVE_MICROPHONE"

    @field_validator("phone_number")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        compact = "".join(ch for ch in value if ch not in " ()-")
        digits = compact[1:] if compact.startswith("+") else compact
        if not digits.isdigit() or not 8 <= len(digits) <= 15:
            raise ValueError("phoneNumber must contain 8-15 digits in local or E.164 form")
        return compact


class SessionView(BaseModel):
    sessionId: str
    createdAt: datetime
    expiresAt: datetime
    status: Literal["ACTIVE", "ENDED", "EXPIRED"]
    maskedPhone: str
    riskLabel: Literal["UNMARKED", "RISKY"]
    mode: Literal["LIVE_MICROPHONE", "SYNTHETIC_TEST"]
    clientConnected: bool
    streamStartedAt: datetime | None
    lastPacketAt: datetime | None
    packetsReceived: int
    audioBytesReceived: int
    currentRms: float
    peakAmplitude: float
    audioActivityCount: int
    durationSeconds: float
    sampleRate: int


class CreateSessionResponse(SessionView):
    sessionToken: str


class EventView(BaseModel):
    type: str
    timestamp: datetime
    data: dict[str, object] = Field(default_factory=dict)

