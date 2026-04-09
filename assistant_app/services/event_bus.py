from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QObject, Signal


class AssistantMode(str, Enum):
    IDLE = "IDLE"
    PASSIVE_LISTENING = "PASSIVE_LISTENING"
    ACTIVATED_LISTENING = "ACTIVATED_LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    WATCHING = "WATCHING"
    LEARNING_PERSON = "LEARNING_PERSON"
    CONTROLLING_APP = "CONTROLLING_APP"
    ERROR = "ERROR"


class AppEventBus(QObject):
    """Central Qt signal hub shared across the app."""

    state_changed = Signal(str, str)
    user_transcript = Signal(str, str)
    assistant_transcript = Signal(str)
    camera_frame_ready = Signal(object)
    face_detection_updated = Signal(object)
    person_context_changed = Signal(object)
    music_status_changed = Signal(str, str)
    unknown_person_prompt = Signal(object)
    error_occurred = Signal(str)

    def emit_state(self, mode: AssistantMode, detail: str = "") -> None:
        self.state_changed.emit(mode.value, detail)
