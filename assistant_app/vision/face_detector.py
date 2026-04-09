from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from storage.models import DetectedFace

try:
    import face_recognition
except Exception:  # pragma: no cover - optional runtime dependency
    face_recognition = None


logger = logging.getLogger(__name__)


class FaceDetector:
    """Detects faces and optionally extracts embeddings."""

    def __init__(self, face_recognition_enabled: bool = True) -> None:
        self.face_recognition_enabled = face_recognition_enabled and face_recognition is not None
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(str(cascade_path))

    def detect_faces(self, frame: np.ndarray) -> list[DetectedFace]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections: list[DetectedFace] = []

        if self.face_recognition_enabled:
            locations = face_recognition.face_locations(rgb_frame, model="hog")
            encodings = face_recognition.face_encodings(rgb_frame, known_face_locations=locations)
            for location, encoding in zip(locations, encodings):
                top, right, bottom, left = location
                crop = frame[top:bottom, left:right].copy()
                detections.append(
                    DetectedFace(
                        bbox=(left, top, right, bottom),
                        confidence=1.0,
                        embedding=list(map(float, encoding.tolist())),
                        crop=crop,
                    )
                )
            return detections

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))
        for (x, y, w, h) in faces:
            crop = frame[y : y + h, x : x + w].copy()
            detections.append(
                DetectedFace(
                    bbox=(int(x), int(y), int(x + w), int(y + h)),
                    confidence=0.55,
                    embedding=None,
                    crop=crop,
                )
            )
        return detections
