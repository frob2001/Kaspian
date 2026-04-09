from __future__ import annotations

from pathlib import Path
import json
import logging
import sqlite3

from storage.migrations import run_migrations
from storage.models import ConversationMessage, MemoryRecord, PersonRecord, utc_now


logger = logging.getLogger(__name__)


class SQLiteStore:
    """Thin repository layer on top of sqlite3."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        run_migrations(self.connection)
        self._ensure_assistant_state()

    def close(self) -> None:
        self.connection.close()

    def _ensure_assistant_state(self) -> None:
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT id FROM assistant_state ORDER BY id LIMIT 1").fetchone()
        if row is None:
            cursor.execute(
                """
                INSERT INTO assistant_state (current_mode, last_user_input, last_assistant_output, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                ("IDLE", "", "", utc_now()),
            )
            self.connection.commit()

    def save_message(
        self,
        role: str,
        content: str,
        source: str = "voice",
        was_activation: bool = False,
        speaker_name: str | None = None,
    ) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (role, content, source, timestamp, was_activation, speaker_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (role, content, source, utc_now(), int(was_activation), speaker_name),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_recent_messages(self, limit: int = 10) -> list[ConversationMessage]:
        rows = self.connection.cursor().execute(
            """
            SELECT * FROM conversations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            ConversationMessage(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                source=row["source"],
                timestamp=row["timestamp"],
                was_activation=bool(row["was_activation"]),
                speaker_name=row["speaker_name"],
            )
            for row in reversed(rows)
        ]

    def save_memory(
        self,
        category: str,
        content: str,
        priority: int = 1,
        source: str = "conversation",
        person_id: int | None = None,
    ) -> int:
        now = utc_now()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO memories (category, content, priority, source, person_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(category, content, person_id)
            DO UPDATE SET priority=excluded.priority, source=excluded.source, updated_at=excluded.updated_at
            """,
            (category, content, priority, source, person_id, now, now),
        )
        self.connection.commit()
        return int(cursor.lastrowid or 0)

    def search_memories(self, query: str) -> list[MemoryRecord]:
        like_query = f"%{query.lower()}%"
        rows = self.connection.cursor().execute(
            """
            SELECT * FROM memories
            WHERE lower(content) LIKE ? OR lower(category) LIKE ?
            ORDER BY priority DESC, updated_at DESC
            LIMIT 20
            """,
            (like_query, like_query),
        ).fetchall()
        return [
            MemoryRecord(
                id=row["id"],
                category=row["category"],
                content=row["content"],
                priority=row["priority"],
                source=row["source"],
                person_id=row["person_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def list_top_memories(self, limit: int = 10) -> list[MemoryRecord]:
        rows = self.connection.cursor().execute(
            """
            SELECT * FROM memories
            ORDER BY priority DESC, updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            MemoryRecord(
                id=row["id"],
                category=row["category"],
                content=row["content"],
                priority=row["priority"],
                source=row["source"],
                person_id=row["person_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def set_preference(self, key: str, value: str) -> None:
        now = utc_now()
        self.connection.cursor().execute(
            """
            INSERT INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (key, value, now),
        )
        self.connection.commit()

    def get_preference(self, key: str) -> str | None:
        row = self.connection.cursor().execute(
            "SELECT value FROM preferences WHERE key = ?",
            (key,),
        ).fetchone()
        return None if row is None else str(row["value"])

    def list_preferences(self) -> dict[str, str]:
        rows = self.connection.cursor().execute("SELECT key, value FROM preferences").fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def save_person(self, name: str, notes: str | None = None) -> int:
        now = utc_now()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO persons (name, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET updated_at=excluded.updated_at, notes=COALESCE(excluded.notes, persons.notes)
            """,
            (name.strip(), now, now, notes),
        )
        self.connection.commit()
        person = self.find_person_by_name(name)
        return 0 if person is None else person.id

    def update_person_notes(self, person_id: int, notes: str) -> None:
        self.connection.cursor().execute(
            "UPDATE persons SET notes = ?, updated_at = ? WHERE id = ?",
            (notes, utc_now(), person_id),
        )
        self.connection.commit()

    def find_person_by_name(self, name: str) -> PersonRecord | None:
        row = self.connection.cursor().execute(
            "SELECT * FROM persons WHERE lower(name) = ?",
            (name.strip().lower(),),
        ).fetchone()
        if row is None:
            return None
        return PersonRecord(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            notes=row["notes"],
        )

    def get_person(self, person_id: int) -> PersonRecord | None:
        row = self.connection.cursor().execute(
            "SELECT * FROM persons WHERE id = ?",
            (person_id,),
        ).fetchone()
        if row is None:
            return None
        return PersonRecord(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            notes=row["notes"],
        )

    def list_persons(self) -> list[PersonRecord]:
        rows = self.connection.cursor().execute("SELECT * FROM persons ORDER BY name").fetchall()
        return [
            PersonRecord(
                id=row["id"],
                name=row["name"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def add_person_image(self, person_id: int, image_path: str, is_primary: bool = False) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO person_images (person_id, image_path, created_at, is_primary)
            VALUES (?, ?, ?, ?)
            """,
            (person_id, image_path, utc_now(), int(is_primary)),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_person_images(self, person_id: int) -> list[str]:
        rows = self.connection.cursor().execute(
            "SELECT image_path FROM person_images WHERE person_id = ? ORDER BY is_primary DESC, created_at DESC",
            (person_id,),
        ).fetchall()
        return [str(row["image_path"]) for row in rows]

    def attach_face_embedding(self, person_id: int, embedding: list[float]) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO face_embeddings (person_id, embedding_blob, created_at)
            VALUES (?, ?, ?)
            """,
            (person_id, json.dumps(embedding), utc_now()),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def load_face_embeddings(self) -> list[tuple[int, list[float]]]:
        rows = self.connection.cursor().execute(
            "SELECT person_id, embedding_blob FROM face_embeddings ORDER BY created_at"
        ).fetchall()
        embeddings: list[tuple[int, list[float]]] = []
        for row in rows:
            try:
                embeddings.append((int(row["person_id"]), json.loads(row["embedding_blob"])))
            except json.JSONDecodeError:
                logger.warning("Embedding corrupto para person_id=%s", row["person_id"])
        return embeddings

    def update_assistant_state(
        self,
        current_mode: str,
        last_user_input: str | None = None,
        last_assistant_output: str | None = None,
    ) -> None:
        self.connection.cursor().execute(
            """
            UPDATE assistant_state
            SET current_mode = ?, last_user_input = COALESCE(?, last_user_input),
                last_assistant_output = COALESCE(?, last_assistant_output), updated_at = ?
            WHERE id = (SELECT id FROM assistant_state ORDER BY id LIMIT 1)
            """,
            (current_mode, last_user_input, last_assistant_output, utc_now()),
        )
        self.connection.commit()

    def get_assistant_state(self) -> dict[str, str]:
        row = self.connection.cursor().execute(
            "SELECT * FROM assistant_state ORDER BY id LIMIT 1"
        ).fetchone()
        return {
            "current_mode": str(row["current_mode"]),
            "last_user_input": str(row["last_user_input"] or ""),
            "last_assistant_output": str(row["last_assistant_output"] or ""),
            "updated_at": str(row["updated_at"]),
        }

    def log_command(self, command_name: str, raw_text: str, success: bool, details: str = "") -> None:
        self.connection.cursor().execute(
            """
            INSERT INTO commands_log (command_name, raw_text, success, details, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (command_name, raw_text, int(success), details, utc_now()),
        )
        self.connection.commit()
