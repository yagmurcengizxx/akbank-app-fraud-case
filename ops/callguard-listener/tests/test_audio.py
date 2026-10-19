import math
import struct
import unittest

from app.audio import InvalidPCMFrame, analyze_pcm16_le, parse_pcm16_le


def pcm(*samples: int) -> bytes:
    return struct.pack(f"<{len(samples)}h", *samples)


class AudioTests(unittest.TestCase):
    def test_pcm16_little_endian_parsing(self):
        self.assertEqual(parse_pcm16_le(pcm(-32768, -1, 0, 1, 32767)), (-32768, -1, 0, 1, 32767))

    def test_rms_and_peak(self):
        result = analyze_pcm16_le(pcm(16384, -16384, 16384, -16384))
        self.assertAlmostEqual(result.rms, 0.5)
        self.assertAlmostEqual(result.peak, 0.5)

    def test_silence_has_zero_metrics(self):
        result = analyze_pcm16_le(pcm(*([0] * 320)))
        self.assertEqual(result.rms, 0)
        self.assertEqual(result.peak, 0)

    def test_broken_frames_rejected(self):
        for frame, limit in ((b"", 8192), (b"\x00", 8192), (b"\x00" * 10, 8)):
            with self.subTest(frame_length=len(frame)):
                with self.assertRaises(InvalidPCMFrame):
                    parse_pcm16_le(frame, max_frame_bytes=limit)

    def test_sine_rms_is_correct(self):
        samples = [round(math.sin(2 * math.pi * 440 * i / 16000) * 10000) for i in range(16000)]
        result = analyze_pcm16_le(pcm(*samples), max_frame_bytes=40000)
        self.assertAlmostEqual(result.rms, 10000 / 32768 / math.sqrt(2), places=4)


if __name__ == "__main__":
    unittest.main()

