from __future__ import annotations

from pathlib import Path
import logging
import shutil
import uuid

import cv2
import numpy as np

from config.settings import Settings


logger = logging.getLogger(__name__)


class ImageStorageService:
    """Stores face captures for known and unknown people."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save_unknown_face(self, frame: np.ndarray) -> tuple[str, Path]:
        unknown_id = uuid.uuid4().hex[:12]
        path = self.settings.unknown_faces_dir / f"{unknown_id}.jpg"
        cv2.imwrite(str(path), frame)
        logger.info("Rostro desconocido guardado en %s", path)
        return unknown_id, path

    def save_known_face(self, person_name: str, frame: np.ndarray | None = None, unknown_path: Path | None = None) -> Path:
        safe_name = person_name.strip().replace(" ", "_").lower()
        folder = self.settings.known_faces_dir / safe_name
        folder.mkdir(parents=True, exist_ok=True)
        destination = folder / f"{uuid.uuid4().hex[:12]}.jpg"
        if unknown_path and unknown_path.exists():
            shutil.copy2(unknown_path, destination)
        elif frame is not None:
            cv2.imwrite(str(destination), frame)
        else:
            raise ValueError("Se requiere frame o unknown_path para guardar un rostro conocido.")
        logger.info("Rostro conocido guardado en %s", destination)
        return destination
