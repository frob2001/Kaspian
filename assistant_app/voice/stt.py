from __future__ import annotations

import logging

import numpy as np

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover - optional runtime dependency
    WhisperModel = None


logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Lazy-loaded Faster Whisper wrapper."""

    def __init__(self, model_name: str = "small", language: str = "es") -> None:
        self.model_name = model_name
        self.language = language
        self._model = None

    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        if WhisperModel is None:
            logger.warning("faster-whisper no disponible; STT desactivado.")
            return False
        self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return True

    def transcribe(self, audio: np.ndarray) -> str:
        if not self._ensure_model():
            return ""
        segments, _ = self._model.transcribe(audio.flatten(), language=self.language, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
