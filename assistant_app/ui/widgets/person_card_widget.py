from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from storage.models import DetectedFace, PersonRecord


class PersonCardWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PersonCard")

        self.title_label = QLabel("Persona detectada")
        self.title_label.setObjectName("SectionTitle")

        self.face_preview = QLabel("Sin detección")
        self.face_preview.setObjectName("FacePreview")
        self.face_preview.setAlignment(Qt.AlignCenter)
        self.face_preview.setMinimumHeight(160)

        self.name_label = QLabel("Nadie identificado")
        self.name_label.setObjectName("PersonName")

        self.meta_label = QLabel("Esperando cámara")
        self.meta_label.setObjectName("StatusDetail")
        self.meta_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(self.title_label)
        layout.addWidget(self.face_preview)
        layout.addWidget(self.name_label)
        layout.addWidget(self.meta_label)

    def set_detection(self, detection: DetectedFace | None) -> None:
        if detection is None:
            self.name_label.setText("Nadie identificado")
            self.meta_label.setText("No hay un rostro dominante visible.")
            self.face_preview.setText("Sin detección")
            self.face_preview.setPixmap(QPixmap())
            return

        if detection.person_name:
            score = detection.match_score if detection.match_score is not None else 0.0
            self.name_label.setText(detection.person_name)
            self.meta_label.setText(f"Coincidencia facial registrada. Distancia: {score:.3f}")
        else:
            self.name_label.setText("Persona desconocida")
            self.meta_label.setText("Rostro visible sin identidad confirmada.")

        if detection.crop is not None:
            rgb = cv2.cvtColor(detection.crop, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb.shape
            image = QImage(rgb.data, width, height, channel * width, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image).scaled(220, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.face_preview.setPixmap(pixmap)
            self.face_preview.setText("")

    def set_person(self, person: PersonRecord | None, image_path: str | None = None) -> None:
        if person is None:
            self.name_label.setText("Nadie identificado")
            self.meta_label.setText("Sin contexto personal activo.")
        else:
            self.name_label.setText(person.name)
            self.meta_label.setText(person.notes or "Persona conocida lista para conversación contextual.")

        if image_path and Path(image_path).exists():
            pixmap = QPixmap(image_path).scaled(220, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.face_preview.setPixmap(pixmap)
            self.face_preview.setText("")
