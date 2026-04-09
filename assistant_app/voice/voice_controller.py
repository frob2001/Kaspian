from __future__ import annotations


class VoiceController:
    """Facade that groups passive listening, STT and TTS services."""

    def __init__(self, passive_listener, tts_service) -> None:
        self.passive_listener = passive_listener
        self.tts_service = tts_service

    def start(self) -> None:
        if self.passive_listener is not None:
            self.passive_listener.start()

    def stop(self) -> None:
        if self.passive_listener is not None:
            self.passive_listener.stop()

    def speak(self, text: str) -> None:
        if self.tts_service is not None:
            self.tts_service.speak(text)
