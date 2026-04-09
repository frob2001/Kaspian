from __future__ import annotations

import logging
import sys

import cv2
from PySide6.QtWidgets import QApplication

from brain.assistant_service import AssistantService
from brain.command_router import CommandRouter
from brain.context_manager import ContextManager
from brain.importance_analyzer import ImportanceAnalyzer
from brain.memory_manager import MemoryManager
from brain.ollama_client import OllamaClient
from config.logging_config import configure_logging
from config.settings import get_settings
from control.spotify_controller import SpotifyController
from control.system_actions import SystemActions
from services.event_bus import AppEventBus, AssistantMode
from services.image_storage_service import ImageStorageService
from storage.sqlite_store import SQLiteStore
from ui.main_window import MainWindow
from vision.camera_stream import CameraStream
from vision.face_detector import FaceDetector
from vision.face_registry import FaceRegistry
from vision.person_manager import PersonManager
from voice.audio_capture import AudioCapture
from voice.passive_listener import PassiveListener
from voice.stt import SpeechToTextService
from voice.tts import TextToSpeechService
from voice.voice_controller import VoiceController


logger = logging.getLogger(__name__)


class KaspianRuntime:
    def __init__(self) -> None:
        self.settings = get_settings()
        configure_logging(self.settings)

        self.store = SQLiteStore(self.settings.db_path)
        self.event_bus = AppEventBus()
        self.image_storage = ImageStorageService(self.settings)
        self.face_registry = FaceRegistry(self.store)
        self.person_manager = PersonManager(
            store=self.store,
            face_registry=self.face_registry,
            image_storage=self.image_storage,
            save_unknown_faces=self.settings.save_unknown_faces,
        )
        self.context_manager = ContextManager(self.store, recent_limit=self.settings.max_recent_messages)
        self.memory_manager = MemoryManager(self.store, ImportanceAnalyzer())
        self.ollama_client = OllamaClient(self.settings)
        self.spotify_controller = SpotifyController()
        self.command_router = CommandRouter(self.store, self.spotify_controller, SystemActions())
        self.tts_service = TextToSpeechService(enabled=self.settings.tts_enabled)
        self.assistant_service = AssistantService(
            event_bus=self.event_bus,
            store=self.store,
            context_manager=self.context_manager,
            memory_manager=self.memory_manager,
            ollama_client=self.ollama_client,
            command_router=self.command_router,
            tts_engine=self.tts_service,
            activation_name=self.settings.activation_name,
        )
        self.face_detector = FaceDetector(face_recognition_enabled=self.settings.face_recognition_enabled)

        self.audio_capture = AudioCapture()
        self.stt_service = SpeechToTextService(model_name=self.settings.whisper_model, language=self.settings.language)
        self.passive_listener = PassiveListener(
            audio_capture=self.audio_capture,
            stt_service=self.stt_service,
            assistant_service=self.assistant_service,
            event_bus=self.event_bus,
            enabled=self.settings.voice_always_on,
        )
        self.voice_controller = VoiceController(self.passive_listener, self.tts_service)

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Kaspian")
        self._apply_theme()

        self.window = MainWindow(
            settings=self.settings,
            assistant_service=self.assistant_service,
            event_bus=self.event_bus,
            person_manager=self.person_manager,
            store=self.store,
        )

        self.camera_stream: CameraStream | None = None
        self._frame_index = 0
        self._last_detection = None
        self._last_visible_person_id: int | None = None

        if self.settings.camera_enabled and self.settings.show_camera:
            self.camera_stream = CameraStream(self.settings, on_frame=self._handle_camera_frame, on_error=self._handle_camera_error)

        self.app.aboutToQuit.connect(self.shutdown)

    def _apply_theme(self) -> None:
        if self.settings.theme_path.exists():
            self.app.setStyleSheet(self.settings.theme_path.read_text(encoding="utf-8"))

    def start(self) -> int:
        self.event_bus.emit_state(AssistantMode.IDLE, "En espera")
        if not self.ollama_client.healthcheck():
            self.event_bus.error_occurred.emit("Ollama no responde todavía. La UI seguirá disponible.")
        if self.camera_stream is not None:
            self.event_bus.emit_state(AssistantMode.WATCHING, "Cámara activa")
            self.camera_stream.start()
        if self.settings.voice_always_on:
            self.voice_controller.start()
        self.window.show()
        return self.app.exec()

    def shutdown(self) -> None:
        logger.info("Apagando Kaspian")
        if self.camera_stream is not None:
            self.camera_stream.stop()
        self.voice_controller.stop()
        self.ollama_client.close()
        self.store.close()

    def _handle_camera_error(self, message: str) -> None:
        self.event_bus.error_occurred.emit(message)

    def _handle_camera_frame(self, frame) -> None:  # pragma: no cover - hardware path
        self._frame_index += 1
        annotated = frame.copy()

        if self._frame_index % 8 == 0:
            detections = self.face_detector.detect_faces(frame)
            dominant = self._choose_dominant_detection(detections)
            if dominant is not None:
                dominant = self.person_manager.enrich_detection(dominant)
            self._last_detection = dominant
            self._update_person_context(dominant)
            self.event_bus.face_detection_updated.emit(dominant)

        if self._last_detection is not None:
            self._draw_detection(annotated, self._last_detection)

        self.event_bus.camera_frame_ready.emit(annotated)

    def _choose_dominant_detection(self, detections):
        if not detections:
            return None
        return max(detections, key=lambda item: (item.bbox[2] - item.bbox[0]) * (item.bbox[3] - item.bbox[1]))

    def _update_person_context(self, detection) -> None:
        if detection is None:
            self._last_visible_person_id = None
            self.assistant_service.set_visible_person(None)
            self.assistant_service.set_pending_unknown_detection(None)
            return

        if detection.person_id:
            person = self.store.get_person(detection.person_id)
            if person and self._last_visible_person_id != person.id:
                self._last_visible_person_id = person.id
                self.assistant_service.set_visible_person(person)
            return

        self._last_visible_person_id = None
        self.assistant_service.set_visible_person(None)
        prompt_payload = self.person_manager.create_prompt_payload(detection)
        self.assistant_service.set_pending_unknown_detection(prompt_payload)

    def _draw_detection(self, frame, detection) -> None:
        left, top, right, bottom = detection.bbox
        color = (44, 194, 255) if detection.person_name else (255, 179, 71)
        label = detection.person_name or "Desconocido"
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, max(18, top - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def main() -> int:
    runtime = KaspianRuntime()
    return runtime.start()


if __name__ == "__main__":
    raise SystemExit(main())
