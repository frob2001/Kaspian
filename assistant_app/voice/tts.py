from __future__ import annotations

import logging
import shutil
import subprocess


logger = logging.getLogger(__name__)


class TextToSpeechService:
    """Minimal espeak-ng based TTS."""

    def __init__(self, enabled: bool = True, voice: str = "es") -> None:
        self.enabled = enabled
        self.voice = voice

    def speak(self, text: str) -> None:
        if not self.enabled or not text.strip():
            return
        executable = shutil.which("espeak-ng")
        if executable is None:
            logger.warning("espeak-ng no está instalado; omito TTS.")
            return
        subprocess.Popen([executable, "-v", self.voice, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
