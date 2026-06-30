"""Microphone capture + speaker playback for the live voice mode.

Audio libraries are optional: text/auto demo modes never import this. If sounddevice
/ soundfile aren't installed, voice mode raises a clear, actionable error.
"""
from __future__ import annotations

import io
import wave


def _require_audio():
    try:
        import sounddevice  # noqa: F401
        import soundfile  # noqa: F401
    except Exception as e:  # pragma: no cover - depends on local audio stack
        raise RuntimeError(
            "Voice mode needs audio libs. Install:  pip install sounddevice soundfile numpy\n"
            "(On macOS you may also need:  brew install portaudio)\n"
            f"Original import error: {e}"
        )


def record_until_silence(max_seconds: float = 8.0, sample_rate: int = 16000) -> bytes:
    """Record from the default mic for up to max_seconds, return WAV bytes (16kHz mono).

    Simple fixed-window capture — robust across machines. 16kHz mono is Saaras' sweet spot.
    """
    _require_audio()
    import numpy as np
    import sounddevice as sd

    print(f"  🎙  (listening up to {int(max_seconds)}s — speak now)")
    frames = sd.rec(int(max_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(sample_rate)
        wf.writeframes(np.asarray(frames, dtype="int16").tobytes())
    return buf.getvalue()


def play_wav_bytes(audio: bytes) -> None:
    """Play WAV bytes returned by Sarvam TTS through the default speaker."""
    if not audio:
        return
    _require_audio()
    import soundfile as sf
    import sounddevice as sd

    data, sr = sf.read(io.BytesIO(audio), dtype="float32")
    sd.play(data, sr)
    sd.wait()
