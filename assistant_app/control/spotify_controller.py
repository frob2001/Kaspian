from __future__ import annotations

import platform
import shutil
import subprocess

from control.app_controller import AppController


class SpotifyController:
    """Desktop-oriented Spotify control using local OS tools."""

    def __init__(self) -> None:
        self.app_controller = AppController()

    def open_spotify(self) -> tuple[bool, str]:
        system = platform.system().lower()
        if system == "linux":
            success, message = self.app_controller.open_application(["spotify", "spotify-launcher"])
            if success:
                return True, "Spotify abierto."
            return False, message
        if system == "windows":
            try:
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", "Start-Process spotify:"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True, "Intenté abrir Spotify en Windows."
            except Exception:
                success, message = self.app_controller.open_application(["Spotify"])
                if success:
                    return True, "Spotify abierto."
                return False, "No pude abrir Spotify automáticamente en Windows."
        return False, "La apertura automática de Spotify está preparada para Linux de escritorio."

    def play_music(self) -> tuple[bool, str]:
        return self._playerctl(["play"], "Reproducción reanudada.")

    def pause_music(self) -> tuple[bool, str]:
        return self._playerctl(["pause"], "Música en pausa.")

    def next_track(self) -> tuple[bool, str]:
        return self._playerctl(["next"], "Pasé a la siguiente pista.")

    def previous_track(self) -> tuple[bool, str]:
        return self._playerctl(["previous"], "Volví a la pista anterior.")

    def set_volume(self, percent: int) -> tuple[bool, str]:
        normalized = max(0, min(100, percent)) / 100
        return self._playerctl(["volume", str(normalized)], f"Volumen ajustado al {percent} por ciento.")

    def _playerctl(self, args: list[str], success_message: str) -> tuple[bool, str]:
        playerctl = shutil.which("playerctl")
        if playerctl is None:
            return False, "playerctl no está instalado en el sistema."
        process = subprocess.run([playerctl, *args], capture_output=True, text=True, check=False)
        if process.returncode == 0:
            return True, success_message
        stderr = (process.stderr or "").strip()
        return False, stderr or "No pude controlar Spotify con playerctl."
