from __future__ import annotations

import logging

from brain.importance_analyzer import ImportanceAnalyzer
from storage.sqlite_store import SQLiteStore


logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self, store: SQLiteStore, importance_analyzer: ImportanceAnalyzer) -> None:
        self.store = store
        self.importance_analyzer = importance_analyzer

    def process_text_for_memory(self, text: str, source: str = "conversation", person_id: int | None = None) -> None:
        should_save, category, priority = self.importance_analyzer.analyze(text)
        if not should_save:
            return
        self.store.save_memory(category=category, content=text.strip(), priority=priority, source=source, person_id=person_id)
        logger.info("Memoria guardada [%s]: %s", category, text.strip())
        if category == "preference":
            normalized_key = self._extract_preference_key(text)
            if normalized_key:
                self.store.set_preference(normalized_key, text.strip())

    def _extract_preference_key(self, text: str) -> str | None:
        lower = text.lower()
        if "artista favorito" in lower:
            return "artista_favorito"
        if "color favorito" in lower:
            return "color_favorito"
        if "prefiero" in lower:
            return "preferencia_general"
        if "me gusta" in lower:
            return "gusto_general"
        if "no me gusta" in lower:
            return "disgusto_general"
        return None
