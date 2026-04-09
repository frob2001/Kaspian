from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class TranscriptWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("TranscriptCard")

        self.title_label = QLabel("Conversación")
        self.title_label.setObjectName("SectionTitle")

        self.transcript_box = QTextEdit()
        self.transcript_box.setObjectName("TranscriptBox")
        self.transcript_box.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(self.title_label)
        layout.addWidget(self.transcript_box)

    def append_entry(self, speaker: str, text: str) -> None:
        existing = self.transcript_box.toPlainText().strip()
        line = f"{speaker}: {text}"
        self.transcript_box.setPlainText(f"{existing}\n{line}".strip())
        cursor = self.transcript_box.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.transcript_box.setTextCursor(cursor)
