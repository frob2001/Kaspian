from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from services.datetime_service import DateTimeService


class ClockWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ClockCard")

        self.time_label = QLabel()
        self.time_label.setObjectName("ClockTime")
        self.time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.date_label = QLabel()
        self.date_label.setObjectName("ClockDate")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(6)
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    def refresh(self) -> None:
        self.time_label.setText(DateTimeService.formatted_time())
        self.date_label.setText(DateTimeService.formatted_date())
