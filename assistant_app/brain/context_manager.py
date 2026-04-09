from __future__ import annotations

from storage.sqlite_store import SQLiteStore


class ContextManager:
    def __init__(self, store: SQLiteStore, recent_limit: int = 12) -> None:
        self.store = store
        self.recent_limit = recent_limit

    def get_recent_context(self) -> list[dict[str, str]]:
        messages = self.store.get_recent_messages(limit=self.recent_limit)
        return [{"role": message.role, "content": message.content} for message in messages]

    def get_relevant_memories(self, text: str) -> list[dict[str, str]]:
        memories = self.store.search_memories(text)
        return [
            {
                "category": memory.category,
                "content": memory.content,
            }
            for memory in memories[:8]
        ]
