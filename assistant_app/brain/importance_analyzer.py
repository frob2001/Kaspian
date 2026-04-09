from __future__ import annotations

import re


class ImportanceAnalyzer:
    """Simple heuristic memory selector for early local-first versions."""

    PREFERENCE_PATTERNS = [
        re.compile(r"\bme gusta\b", re.IGNORECASE),
        re.compile(r"\bprefiero\b", re.IGNORECASE),
        re.compile(r"\bmi color favorito es\b", re.IGNORECASE),
        re.compile(r"\bmi artista favorito es\b", re.IGNORECASE),
        re.compile(r"\bno me gusta\b", re.IGNORECASE),
    ]

    RELATION_PATTERNS = [
        re.compile(r"\bes mi (hermana|hermano|amigo|amiga|mamá|madre|papá|padre)\b", re.IGNORECASE),
        re.compile(r"\bella es\b", re.IGNORECASE),
        re.compile(r"\bese es\b", re.IGNORECASE),
    ]

    REMINDER_PATTERNS = [
        re.compile(r"\brecuerda que\b", re.IGNORECASE),
        re.compile(r"\bimportante\b", re.IGNORECASE),
    ]

    def analyze(self, text: str) -> tuple[bool, str, int]:
        cleaned = text.strip()
        if len(cleaned) < 10:
            return False, "smalltalk", 0

        if any(pattern.search(cleaned) for pattern in self.PREFERENCE_PATTERNS):
            return True, "preference", 3
        if any(pattern.search(cleaned) for pattern in self.RELATION_PATTERNS):
            return True, "person_relation", 3
        if any(pattern.search(cleaned) for pattern in self.REMINDER_PATTERNS):
            return True, "reminder", 2
        if cleaned.lower().startswith("mi ") and len(cleaned.split()) > 4:
            return True, "personal_fact", 2
        return False, "smalltalk", 0
