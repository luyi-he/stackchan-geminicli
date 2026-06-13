from __future__ import annotations

import logging
from typing import Any
import os

from .audio_utils import (
    DEVICE_SAMPLE_RATE,
    resample_pcm16_linear,
)
from .base import TTSEngine

logger = logging.getLogger(__name__)

# Default Chinese voice for edge-tts
DEFAULT_EDGE_VOICE = "zh-CN-XiaoxiaoNeural"

def _decode_mp3_to_pcm16_mono(mp3_bytes: bytes) -> tuple[int, bytes]:
    import miniaudio
    decoded = miniaudio.decode(
        mp3_bytes,
        output_format=miniaudio.SampleFormat.SIGNED16,
        nchannels=1,
    )
    return decoded.sample_rate, decoded.samples.tobytes()

class EdgeEngine(TTSEngine):
    name = "edge"

    async def synthesize(self, text: str, **opts: Any) -> bytes:
        import edge_tts

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Edge synthesize: 'text' must be a non-empty string")

        voice = opts.get("voice") or os.getenv("STACKCHAN_EDGE_VOICE") or DEFAULT_EDGE_VOICE
        
        communicate = edge_tts.Communicate(text, voice)
        mp3_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_bytes += chunk["data"]

        if not mp3_bytes:
            raise RuntimeError("Edge TTS returned no audio data.")

        sample_rate, pcm = _decode_mp3_to_pcm16_mono(mp3_bytes)
        if sample_rate != DEVICE_SAMPLE_RATE:
            pcm = resample_pcm16_linear(pcm, sample_rate, DEVICE_SAMPLE_RATE)

        return pcm
