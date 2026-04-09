from __future__ import annotations

from threading import Event, Thread
import logging
import time

import cv2

from config.settings import Settings


logger = logging.getLogger(__name__)


class CameraStream:
    """Continuously captures frames in a background thread."""

    def __init__(self, settings: Settings, on_frame=None, on_error=None) -> None:
        self.settings = settings
        self.on_frame = on_frame
        self.on_error = on_error
        self._capture = None
        self._thread: Thread | None = None
        self._stop_event = Event()

    def start(self) -> None:
        if not self.settings.camera_enabled:
            return
        self._capture = cv2.VideoCapture(self.settings.camera_index)
        if not self._capture.isOpened():
            message = "No pude abrir la cámara configurada."
            logger.error(message)
            if self.on_error is not None:
                self.on_error(message)
            return

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.camera_width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.camera_height)
        self._capture.set(cv2.CAP_PROP_FPS, self.settings.camera_fps)

        self._stop_event.clear()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _loop(self) -> None:  # pragma: no cover - hardware path
        delay = max(0.01, 1 / max(1, self.settings.camera_fps))
        while not self._stop_event.is_set():
            assert self._capture is not None
            success, frame = self._capture.read()
            if success and self.on_frame is not None:
                self.on_frame(frame)
            elif not success and self.on_error is not None:
                self.on_error("La cámara devolvió un frame vacío.")
            time.sleep(delay)
