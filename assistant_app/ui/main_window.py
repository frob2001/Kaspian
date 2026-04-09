from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow

from ui.dashboard import Dashboard
from ui.dialogs.person_name_dialog import PersonNameDialog


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings, assistant_service, event_bus, person_manager, store) -> None:
        super().__init__()
        self.settings = settings
        self.assistant_service = assistant_service
        self.event_bus = event_bus
        self.person_manager = person_manager
        self.store = store

        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)
        self.setWindowTitle("Kaspian")
        self.resize(1500, 900)

        self.dashboard.manual_text_submitted.connect(self.assistant_service.handle_manual_input)
        self.dashboard.music_widget.action_requested.connect(self.assistant_service.handle_manual_input)

        self.event_bus.state_changed.connect(self._on_state_changed)
        self.event_bus.user_transcript.connect(self._on_user_transcript)
        self.event_bus.assistant_transcript.connect(self._on_assistant_transcript)
        self.event_bus.camera_frame_ready.connect(self.dashboard.camera_widget.update_frame)
        self.event_bus.face_detection_updated.connect(self.dashboard.person_card_widget.set_detection)
        self.event_bus.person_context_changed.connect(self._on_person_context_changed)
        self.event_bus.music_status_changed.connect(self.dashboard.music_widget.set_status)
        self.event_bus.unknown_person_prompt.connect(self._on_unknown_person_prompt)
        self.event_bus.error_occurred.connect(self._on_error)

        self.space_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.space_shortcut.activated.connect(self.dashboard.manual_input.setFocus)

        if self.settings.allow_esc_exit and self.settings.is_dev:
            self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
            self.escape_shortcut.activated.connect(self.close)

        if self.settings.fullscreen:
            self.showFullScreen()

    def _on_state_changed(self, mode: str, detail: str) -> None:
        self.dashboard.status_widget.set_status(mode, detail)
        self.dashboard.orb_widget.set_mode(mode)

    def _on_user_transcript(self, source: str, text: str) -> None:
        self.dashboard.transcript_widget.append_entry("Tú", text)

    def _on_assistant_transcript(self, text: str) -> None:
        self.dashboard.transcript_widget.append_entry("Kaspian", text)

    def _on_person_context_changed(self, person) -> None:
        if person is None:
            self.dashboard.person_card_widget.set_person(None)
            return
        images = self.store.get_person_images(person.id)
        image_path = images[0] if images else None
        self.dashboard.person_card_widget.set_person(person, image_path=image_path)

    def _on_unknown_person_prompt(self, payload) -> None:
        dialog = PersonNameDialog(payload.image_path, payload.suggested_name, self)
        if dialog.exec():
            entered_name = dialog.entered_name()
            if entered_name:
                person = self.person_manager.register_person(entered_name, proposed_unknown_id=payload.unknown_id)
                self.assistant_service.set_visible_person(person)
                self.dashboard.transcript_widget.append_entry("Sistema", f"Identidad guardada para {entered_name}.")

    def _on_error(self, message: str) -> None:
        logger.error(message)
        self.dashboard.status_widget.set_status("ERROR", message)
