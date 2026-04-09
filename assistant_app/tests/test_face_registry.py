from pathlib import Path

from storage.sqlite_store import SQLiteStore
from vision.face_registry import FaceRegistry


def test_face_registry_matches_known_embedding(tmp_path: Path):
    store = SQLiteStore(tmp_path / "faces.db")
    person_id = store.save_person("Ana")
    store.attach_face_embedding(person_id, [0.1, 0.2, 0.3])

    registry = FaceRegistry(store, match_threshold=0.2)
    match_id, match_name, score = registry.match([0.1, 0.21, 0.29])

    assert match_id == person_id
    assert match_name == "Ana"
    assert score is not None
