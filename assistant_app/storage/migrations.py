from __future__ import annotations


SCHEMA_STATEMENTS: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        source TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        was_activation INTEGER NOT NULL DEFAULT 0,
        speaker_name TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        priority INTEGER NOT NULL DEFAULT 1,
        source TEXT NOT NULL,
        person_id INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(category, content, person_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS person_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_primary INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS face_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        embedding_blob TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS assistant_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_mode TEXT NOT NULL,
        last_user_input TEXT,
        last_assistant_output TEXT,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS commands_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_name TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        success INTEGER NOT NULL,
        details TEXT,
        created_at TEXT NOT NULL
    )
    """,
]


def run_migrations(connection) -> None:
    cursor = connection.cursor()
    for statement in SCHEMA_STATEMENTS:
        cursor.execute(statement)
    connection.commit()
