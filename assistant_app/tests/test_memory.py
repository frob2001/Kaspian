from pathlib import Path

from brain.importance_analyzer import ImportanceAnalyzer
from brain.memory_manager import MemoryManager
from storage.sqlite_store import SQLiteStore


def test_memory_manager_saves_relevant_preference(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    manager = MemoryManager(store, ImportanceAnalyzer())

    manager.process_text_for_memory("Mi color favorito es azul", source="manual")

    memories = store.search_memories("azul")
    assert len(memories) == 1
    assert memories[0].category == "preference"
    assert store.get_preference("color_favorito") == "Mi color favorito es azul"
