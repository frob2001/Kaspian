from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.calendar_widget import CalendarWidget
from ui.widgets.camera_widget import CameraWidget
from ui.widgets.clock_widget import ClockWidget
from ui.widgets.music_widget import MusicWidget
from ui.widgets.orb_widget import OrbWidget
from ui.widgets.person_card_widget import PersonCardWidget
from ui.widgets.status_widget import StatusWidget
from ui.widgets.transcript_widget import TranscriptWidget


class Dashboard(QWidget):
    manual_text_submitted = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardRoot")

        self.clock_widget = ClockWidget()
        self.calendar_widget = CalendarWidget()
        self.status_widget = StatusWidget()
        self.transcript_widget = TranscriptWidget()
        self.orb_widget = OrbWidget()
        self.camera_widget = CameraWidget()
        self.person_card_widget = PersonCardWidget()
        self.music_widget = MusicWidget()

        self.manual_input = QLineEdit()
        self.manual_input.setObjectName("ManualInput")
        self.manual_input.setPlaceholderText("Escribe: Kaspian, ¿qué hora es?")
        self.manual_input.returnPressed.connect(self._submit_manual_text)

        self.send_button = QPushButton("Enviar")
        self.send_button.setObjectName("PrimaryButton")
        self.send_button.clicked.connect(self._submit_manual_text)

        self.listen_button = QPushButton("Activar")
        self.listen_button.clicked.connect(lambda: self.manual_text_submitted.emit("Kaspian"))

        left_column = QVBoxLayout()
        left_column.setSpacing(16)
        left_column.addWidget(self.clock_widget)
        left_column.addWidget(self.status_widget)
        left_column.addWidget(self.calendar_widget, 1)

        center_column = QVBoxLayout()
        center_column.setSpacing(16)
        center_column.addWidget(self.orb_widget)
        center_column.addWidget(self.transcript_widget, 1)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.addWidget(self.manual_input, 1)
        input_row.addWidget(self.listen_button)
        input_row.addWidget(self.send_button)
        center_column.addLayout(input_row)

        right_column = QVBoxLayout()
        right_column.setSpacing(16)
        right_column.addWidget(self.camera_widget, 2)
        right_column.addWidget(self.person_card_widget)
        right_column.addWidget(self.music_widget)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(28, 24, 28, 24)
        root_layout.setSpacing(18)
        root_layout.addLayout(left_column, 3)
        root_layout.addLayout(center_column, 4)
        root_layout.addLayout(right_column, 4)

    def _submit_manual_text(self) -> None:
        text = self.manual_input.text().strip()
        if text:
            self.manual_text_submitted.emit(text)
            self.manual_input.clear()
