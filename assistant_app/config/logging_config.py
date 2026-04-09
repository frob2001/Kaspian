from __future__ import annotations

from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging

from config.settings import Settings


def configure_logging(settings: Settings) -> None:
    log_dir = settings.base_dir / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "kaspian.log"

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.setLevel(settings.log_level.upper())
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
