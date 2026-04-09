from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class PersonNameDialog(QDialog):
    def __init__(self, image_path: str, suggested_name: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Registrar persona")
        self.setModal(True)
        self.setMinimumWidth(460)

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setMinimumSize(180, 180)
        if Path(image_path).exists():
            pixmap = QPixmap(image_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("Sin imagen")

        right_column = QVBoxLayout()
        prompt_label = QLabel("No reconozco a esta persona. ¿Cómo se llama?")
        prompt_label.setWordWrap(True)
        prompt_label.setObjectName("DialogPrompt")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Escribe el nombre")
        self.name_input.setText(suggested_name)

        buttons_row = QHBoxLayout()
        self.skip_button = QPushButton("Omitir")
        self.save_button = QPushButton("Guardar")
        self.skip_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)
        buttons_row.addWidget(self.skip_button)
        buttons_row.addWidget(self.save_button)

        right_column.addWidget(prompt_label)
        right_column.addWidget(self.name_input)
        right_column.addStretch(1)
        right_column.addLayout(buttons_row)

        root.addWidget(image_label)
        root.addLayout(right_column, 1)

    def entered_name(self) -> str:
        return self.name_input.text().strip()
