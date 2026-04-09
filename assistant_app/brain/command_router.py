from __future__ import annotations

import re

from storage.models import CommandResult, PersonRecord


class CommandRouter:
    def __init__(self, store, spotify_controller, system_actions) -> None:
        self.store = store
        self.spotify_controller = spotify_controller
        self.system_actions = system_actions

    def route(self, text: str, visible_person: PersonRecord | None = None) -> CommandResult:
        normalized = text.lower().strip()

        if re.search(r"\b(qué hora es|hora actual|qué día es|fecha)\b", normalized):
            answer = self.system_actions.answer_datetime(normalized)
            self._log("datetime", text, True, answer)
            return CommandResult(True, answer, command_name="datetime")

        if "quién soy" in normalized or "quien soy" in normalized:
            if visible_person:
                answer = f"Creo que eres {visible_person.name}."
            else:
                answer = "Todavía no puedo confirmarlo con suficiente confianza."
            self._log("who_am_i", text, True, answer)
            return CommandResult(True, answer, command_name="who_am_i")

        spotify_result = self._route_spotify(normalized, text)
        if spotify_result is not None:
            return spotify_result

        return CommandResult(False, "", success=False)

    def _route_spotify(self, normalized: str, raw_text: str) -> CommandResult | None:
        if "spotify" in normalized or "música" in normalized or "musica" in normalized or "canción" in normalized or "cancion" in normalized:
            if "abre" in normalized:
                success, detail = self.spotify_controller.open_spotify()
                self._log("open_spotify", raw_text, success, detail)
                return CommandResult(True, detail, command_name="open_spotify", success=success, details=detail)
            if "pausa" in normalized or "detén" in normalized or "deten" in normalized:
                success, detail = self.spotify_controller.pause_music()
                self._log("pause_music", raw_text, success, detail)
                return CommandResult(True, detail, command_name="pause_music", success=success, details=detail)
            if "reanuda" in normalized or "continúa" in normalized or "continua" in normalized or "pon" in normalized or "reproduce" in normalized:
                success, detail = self.spotify_controller.play_music()
                self._log("play_music", raw_text, success, detail)
                return CommandResult(True, detail, command_name="play_music", success=success, details=detail)
            if "siguiente" in normalized:
                success, detail = self.spotify_controller.next_track()
                self._log("next_track", raw_text, success, detail)
                return CommandResult(True, detail, command_name="next_track", success=success, details=detail)
            if "anterior" in normalized:
                success, detail = self.spotify_controller.previous_track()
                self._log("previous_track", raw_text, success, detail)
                return CommandResult(True, detail, command_name="previous_track", success=success, details=detail)

            volume_match = re.search(r"volumen\s+(\d{1,3})", normalized)
            if volume_match:
                volume = max(0, min(100, int(volume_match.group(1))))
                success, detail = self.spotify_controller.set_volume(volume)
                self._log("set_volume", raw_text, success, detail)
                return CommandResult(True, detail, command_name="set_volume", success=success, details=detail)

        return None

    def _log(self, command_name: str, raw_text: str, success: bool, details: str) -> None:
        self.store.log_command(command_name=command_name, raw_text=raw_text, success=success, details=details)
