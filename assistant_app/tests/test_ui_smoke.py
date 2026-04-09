import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Slot

from config.settings import Settings
from services.event_bus import AppEventBus
from storage.sqlite_store import SQLiteStore
from ui.main_window import MainWindow
from vision.face_registry import FaceRegistry
from vision.person_manager import PersonManager
from services.image_storage_service import ImageStorageService


class DummyAssistant(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.last_text = None

    @Slot(str)
    def handle_manual_input(self, text: str) -> None:
        self.last_text = text

    def set_visible_person(self, person) -> None:
        return None


def test_main_window_smoke(qtbot, tmp_path: Path):
    settings = Settings(
        fullscreen=False,
        allow_esc_exit=False,
        camera_enabled=False,
        db_path=tmp_path / "ui.db",
    )
    settings.ensure_directories()
    store = SQLiteStore(settings.db_path)
    event_bus = AppEventBus()
    person_manager = PersonManager(store, FaceRegistry(store), ImageStorageService(settings), save_unknown_faces=False)
    assistant = DummyAssistant()

    window = MainWindow(settings, assistant, event_bus, person_manager, store)
    qtbot.addWidget(window)
    window.show()

    assert window.windowTitle() == "Kaspian"
    assert window.dashboard.manual_input.placeholderText().startswith("Escribe")
