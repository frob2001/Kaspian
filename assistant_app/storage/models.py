from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SpeakerRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(slots=True)
class ConversationMessage:
    id: int | None
    role: str
    content: str
    source: str
    timestamp: str
    was_activation: bool = False
    speaker_name: str | None = None


@dataclass(slots=True)
class MemoryRecord:
    id: int | None
    category: str
    content: str
    priority: int
    source: str
    person_id: int | None
    created_at: str
    updated_at: str


@dataclass(slots=True)
class PersonRecord:
    id: int
    name: str
    created_at: str
    updated_at: str
    notes: str | None = None


@dataclass(slots=True)
class DetectedFace:
    bbox: tuple[int, int, int, int]
    confidence: float
    embedding: list[float] | None = None
    crop: Any = None
    person_id: int | None = None
    person_name: str | None = None
    match_score: float | None = None
    unknown_id: str | None = None


@dataclass(slots=True)
class CommandResult:
    handled: bool
    response_text: str
    command_name: str = "chat"
    success: bool = True
    details: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
