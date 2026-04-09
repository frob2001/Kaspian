from __future__ import annotations

from collections import deque
from threading import Lock
import logging

import numpy as np

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - optional runtime dependency
    sd = None


logger = logging.getLogger(__name__)


class AudioCapture:
    """Ring-buffer based microphone capture helper."""

    def __init__(self, samplerate: int = 16000, channels: int = 1, blocksize: int = 4000) -> None:
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self._chunks: deque[np.ndarray] = deque(maxlen=64)
        self._lock = Lock()
        self._stream = None

    def start(self) -> bool:
        if sd is None:
            logger.warning("sounddevice no disponible; captura de audio desactivada.")
            return False
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            blocksize=self.blocksize,
            callback=self._audio_callback,
        )
        self._stream.start()
        return True

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def read_latest(self) -> np.ndarray | None:
        with self._lock:
            if not self._chunks:
                return None
            return self._chunks.pop()

    def _audio_callback(self, indata, frames, time, status) -> None:  # pragma: no cover - real device callback
        if status:
            logger.warning("Estado de audio: %s", status)
        with self._lock:
            self._chunks.append(np.copy(indata))
