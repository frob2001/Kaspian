from __future__ import annotations

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class CameraWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CameraCard")
        self._current_pixmap: QPixmap | None = None

        self.title_label = QLabel("Camara")
        self.title_label.setObjectName("SectionTitle")

        self.video_label = QLabel("Esperando camara...")
        self.video_label.setObjectName("CameraFeed")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(False)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(320, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(self.title_label)
        layout.addWidget(self.video_label)

    def update_frame(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb.shape
        image = QImage(rgb.data, width, height, channel * width, QImage.Format_RGB888)
        self._current_pixmap = QPixmap.fromImage(image)
        self._render_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render_pixmap()

    def _render_pixmap(self) -> None:
        if self._current_pixmap is None:
            return
        target_size = self.video_label.contentsRect().size()
        if not target_size.isValid() or target_size.width() <= 0 or target_size.height() <= 0:
            return
        scaled = self._current_pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(scaled)
