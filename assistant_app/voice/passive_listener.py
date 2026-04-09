from __future__ import annotations

from threading import Event, Thread
import logging
import time

from services.event_bus import AppEventBus, AssistantMode


logger = logging.getLogger(__name__)


class PassiveListener:
    """Background passive listening loop prepared for voice activation."""

    def __init__(self, audio_capture, stt_service, assistant_service, event_bus: AppEventBus, enabled: bool = True) -> None:
        self.audio_capture = audio_capture
        self.stt_service = stt_service
        self.assistant_service = assistant_service
        self.event_bus = event_bus
        self.enabled = enabled
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if not self.enabled:
            return
        started = self.audio_capture.start()
        if not started:
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self.audio_capture.stop()

    def _loop(self) -> None:  # pragma: no cover - hardware path
        self.event_bus.emit_state(AssistantMode.PASSIVE_LISTENING, "Escucha continua activa")
        while not self._stop_event.is_set():
            chunk = self.audio_capture.read_latest()
            if chunk is None:
                time.sleep(0.15)
                continue
            text = self.stt_service.transcribe(chunk)
            if not text:
                continue
            logger.debug("Transcripción pasiva: %s", text)
            self.assistant_service.process_input(text, source="voice")
