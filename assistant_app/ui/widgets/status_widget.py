from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatusWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusCard")

        self.title_label = QLabel("Estado del asistente")
        self.title_label.setObjectName("SectionTitle")

        self.mode_label = QLabel("IDLE")
        self.mode_label.setObjectName("StatusMode")
        self.mode_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.detail_label = QLabel("En espera")
        self.detail_label.setObjectName("StatusDetail")
        self.detail_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.detail_label)

    def set_status(self, mode: str, detail: str) -> None:
        self.mode_label.setText(mode)
        self.detail_label.setText(detail or "Sin detalles")
