from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.image_storage_service import ImageStorageService
from storage.models import DetectedFace, PersonRecord
from storage.sqlite_store import SQLiteStore
from vision.face_registry import FaceRegistry


@dataclass(slots=True)
class UnknownPersonPrompt:
    unknown_id: str
    image_path: str
    suggested_name: str = ""


class PersonManager:
    """Coordinates unknown-person capture and later registration."""

    def __init__(
        self,
        store: SQLiteStore,
        face_registry: FaceRegistry,
        image_storage: ImageStorageService,
        save_unknown_faces: bool = True,
    ) -> None:
        self.store = store
        self.face_registry = face_registry
        self.image_storage = image_storage
        self.save_unknown_faces = save_unknown_faces
        self.pending_unknowns: dict[str, Path] = {}
        self._active_unknown_id: str | None = None

    def enrich_detection(self, detection: DetectedFace) -> DetectedFace:
        person_id, person_name, score = self.face_registry.match(detection.embedding)
        detection.person_id = person_id
        detection.person_name = person_name
        detection.match_score = score
        if person_id is None and self.save_unknown_faces and detection.crop is not None and detection.unknown_id is None:
            if self._active_unknown_id and self._active_unknown_id in self.pending_unknowns:
                detection.unknown_id = self._active_unknown_id
            else:
                unknown_id, path = self.image_storage.save_unknown_face(detection.crop)
                detection.unknown_id = unknown_id
                self.pending_unknowns[unknown_id] = path
                self._active_unknown_id = unknown_id
        elif person_id is not None:
            self._active_unknown_id = None
        return detection

    def register_person(self, name: str, detection: DetectedFace | None = None, proposed_unknown_id: str | None = None) -> PersonRecord:
        person_id = self.store.save_person(name)
        unknown_path = self.pending_unknowns.get(proposed_unknown_id or "")

        if detection is not None and detection.crop is not None:
            stored_path = self.image_storage.save_known_face(name, detection.crop, unknown_path=unknown_path)
            self.store.add_person_image(person_id, str(stored_path), is_primary=True)
            if detection.embedding is not None:
                self.store.attach_face_embedding(person_id, detection.embedding)
        elif unknown_path is not None:
            stored_path = self.image_storage.save_known_face(name, unknown_path=unknown_path)
            self.store.add_person_image(person_id, str(stored_path), is_primary=True)

        if proposed_unknown_id:
            self.pending_unknowns.pop(proposed_unknown_id, None)
            if self._active_unknown_id == proposed_unknown_id:
                self._active_unknown_id = None

        self.face_registry.reload()
        person = self.store.get_person(person_id)
        assert person is not None
        return person

    def create_prompt_payload(self, detection: DetectedFace) -> UnknownPersonPrompt | None:
        if detection.unknown_id is None:
            return None
        path = self.pending_unknowns.get(detection.unknown_id)
        if path is None:
            return None
        return UnknownPersonPrompt(unknown_id=detection.unknown_id, image_path=str(path))
