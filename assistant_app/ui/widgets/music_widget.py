from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class MusicWidget(QWidget):
    action_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MusicCard")

        self.title_label = QLabel("Control musical")
        self.title_label.setObjectName("SectionTitle")

        self.status_label = QLabel("Sin acciones recientes")
        self.status_label.setObjectName("StatusDetail")
        self.status_label.setWordWrap(True)

        grid = QGridLayout()
        actions = [
            ("Abrir", "Kaspian, abre Spotify"),
            ("Play", "Kaspian, reanuda Spotify"),
            ("Pausa", "Kaspian, pausa la música"),
            ("Anterior", "Kaspian, canción anterior"),
            ("Siguiente", "Kaspian, siguiente canción"),
        ]
        for index, (label, command) in enumerate(actions):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, value=command: self.action_requested.emit(value))
            grid.addWidget(button, index // 2, index % 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addLayout(grid)

    def set_status(self, title: str, detail: str) -> None:
        self.status_label.setText(f"{title}: {detail}")
