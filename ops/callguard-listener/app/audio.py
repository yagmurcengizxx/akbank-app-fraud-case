from __future__ import annotations

import math
from dataclasses import dataclass


class InvalidPCMFrame(ValueError):
    pass


@dataclass(frozen=True)
class AudioMetrics:
    rms: float
    peak: float
    sample_count: int


def parse_pcm16_le(frame: bytes, max_frame_bytes: int = 8192) -> tuple[int, ...]:
    if not frame:
        raise InvalidPCMFrame("empty audio frame")
    if len(frame) > max_frame_bytes:
        raise InvalidPCMFrame("audio frame exceeds size limit")
    if len(frame) % 2:
        raise InvalidPCMFrame("PCM16 frame must contain complete 16-bit samples")
    return tuple(int.from_bytes(frame[i:i + 2], "little", signed=True) for i in range(0, len(frame), 2))


def calculate_metrics(samples: tuple[int, ...]) -> AudioMetrics:
    if not samples:
        raise InvalidPCMFrame("PCM16 frame contains no samples")
    scale = 32768.0
    sum_squares = sum((sample / scale) ** 2 for sample in samples)
    peak = max(abs(sample) for sample in samples) / scale
    return AudioMetrics(rms=math.sqrt(sum_squares / len(samples)), peak=peak, sample_count=len(samples))


def analyze_pcm16_le(frame: bytes, max_frame_bytes: int = 8192) -> AudioMetrics:
    return calculate_metrics(parse_pcm16_le(frame, max_frame_bytes=max_frame_bytes))

