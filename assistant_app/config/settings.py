from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    app_env: str = "dev"
    fullscreen: bool = True
    allow_esc_exit: bool = True
    language: str = "es"
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:1b"
    ollama_timeout: int = 120
    db_path: Path = BASE_DIR / "data" / "app.db"
    whisper_model: str = "small"
    tts_enabled: bool = True
    voice_always_on: bool = True
    activation_name: str = "Kaspian"
    camera_enabled: bool = True
    face_recognition_enabled: bool = True
    spotify_control_enabled: bool = True
    save_unknown_faces: bool = True
    camera_index: int = 0
    camera_width: int = 960
    camera_height: int = 540
    camera_fps: int = 20
    log_level: str = "INFO"
    show_camera: bool = True
    manual_mode_enabled: bool = True
    allow_background_memory: bool = False
    max_recent_messages: int = 12

    @property
    def base_dir(self) -> Path:
        return BASE_DIR

    @property
    def data_dir(self) -> Path:
        return BASE_DIR / "data"

    @property
    def known_faces_dir(self) -> Path:
        return self.data_dir / "known_faces"

    @property
    def unknown_faces_dir(self) -> Path:
        return self.data_dir / "unknown_faces"

    @property
    def conversation_cache_dir(self) -> Path:
        return self.data_dir / "conversation_cache"

    @property
    def theme_path(self) -> Path:
        return BASE_DIR / "assets" / "styles" / "theme.qss"

    @property
    def is_dev(self) -> bool:
        return self.app_env.lower() == "dev"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.known_faces_dir.mkdir(parents=True, exist_ok=True)
        self.unknown_faces_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")
    settings = Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        fullscreen=_to_bool(os.getenv("FULLSCREEN"), True),
        allow_esc_exit=_to_bool(os.getenv("ALLOW_ESC_EXIT"), True),
        language=os.getenv("LANGUAGE", "es"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:1b"),
        ollama_timeout=int(os.getenv("OLLAMA_TIMEOUT", "120")),
        db_path=(BASE_DIR / os.getenv("DB_PATH", "data/app.db")).resolve(),
        whisper_model=os.getenv("WHISPER_MODEL", "small"),
        tts_enabled=_to_bool(os.getenv("TTS_ENABLED"), True),
        voice_always_on=_to_bool(os.getenv("VOICE_ALWAYS_ON"), True),
        activation_name=os.getenv("ACTIVATION_NAME", "Kaspian"),
        camera_enabled=_to_bool(os.getenv("CAMERA_ENABLED"), True),
        face_recognition_enabled=_to_bool(os.getenv("FACE_RECOGNITION_ENABLED"), True),
        spotify_control_enabled=_to_bool(os.getenv("SPOTIFY_CONTROL_ENABLED"), True),
        save_unknown_faces=_to_bool(os.getenv("SAVE_UNKNOWN_FACES"), True),
        camera_index=int(os.getenv("CAMERA_INDEX", "0")),
        camera_width=int(os.getenv("CAMERA_WIDTH", "960")),
        camera_height=int(os.getenv("CAMERA_HEIGHT", "540")),
        camera_fps=int(os.getenv("CAMERA_FPS", "20")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        show_camera=_to_bool(os.getenv("SHOW_CAMERA"), True),
        manual_mode_enabled=_to_bool(os.getenv("MANUAL_MODE_ENABLED"), True),
        allow_background_memory=_to_bool(os.getenv("ALLOW_BACKGROUND_MEMORY"), False),
        max_recent_messages=int(os.getenv("MAX_RECENT_MESSAGES", "12")),
    )
    settings.ensure_directories()
    return settings
