from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class ActivationResult:
    activated: bool
    cleaned_text: str
    confidence: float
    matched_phrase: str = ""


class ActivationDetector:
    """Name-based direct activation detector."""

    def __init__(self, activation_name: str = "Kaspian") -> None:
        self.activation_name = activation_name.strip()
        escaped = re.escape(self.activation_name)
        self.patterns = [
            re.compile(rf"^\s*(oye\s+)?{escaped}\b[:,]?\s*(.*)$", re.IGNORECASE),
            re.compile(rf"\b{escaped}\b[:,]?\s*(.*)$", re.IGNORECASE),
        ]

    def detect(self, text: str) -> ActivationResult:
        raw = text.strip()
        if not raw:
            return ActivationResult(False, "", 0.0)

        for pattern in self.patterns:
            match = pattern.search(raw)
            if not match:
                continue
            cleaned_text = self._normalize_content(match.group(match.lastindex or 0) or "")
            confidence = 1.0 if raw.lower().startswith(self.activation_name.lower()) or raw.lower().startswith(f"oye {self.activation_name.lower()}") else 0.8
            return ActivationResult(True, cleaned_text, confidence, matched_phrase=match.group(0).strip())

        return ActivationResult(False, raw, 0.0)

    def _normalize_content(self, content: str) -> str:
        cleaned = content.strip(" ,.:;!?¿¡")
        return re.sub(r"\s+", " ", cleaned).strip()
