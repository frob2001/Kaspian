from __future__ import annotations

import math

from storage.sqlite_store import SQLiteStore


class FaceRegistry:
    """Simple in-memory index of known face embeddings."""

    def __init__(self, store: SQLiteStore, match_threshold: float = 0.48) -> None:
        self.store = store
        self.match_threshold = match_threshold
        self._entries: list[tuple[int, str, list[float]]] = []
        self.reload()

    def reload(self) -> None:
        self._entries.clear()
        persons = {person.id: person.name for person in self.store.list_persons()}
        for person_id, embedding in self.store.load_face_embeddings():
            person_name = persons.get(person_id)
            if person_name:
                self._entries.append((person_id, person_name, embedding))

    def match(self, embedding: list[float] | None) -> tuple[int | None, str | None, float | None]:
        if embedding is None or not self._entries:
            return None, None, None

        best_match: tuple[int | None, str | None, float | None] = (None, None, None)
        best_distance = 999.0
        for person_id, person_name, known_embedding in self._entries:
            distance = self._euclidean_distance(embedding, known_embedding)
            if distance < best_distance:
                best_distance = distance
                best_match = (person_id, person_name, distance)

        if best_distance <= self.match_threshold:
            return best_match
        return None, None, best_distance

    @staticmethod
    def _euclidean_distance(a: list[float], b: list[float]) -> float:
        size = min(len(a), len(b))
        return math.sqrt(sum((a[index] - b[index]) ** 2 for index in range(size)))
