from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Slot

from brain.prompts import build_system_prompt
from services.event_bus import AppEventBus, AssistantMode
from storage.models import PersonRecord
from voice.activation_detector import ActivationDetector


logger = logging.getLogger(__name__)


class AssistantService(QObject):
    """Coordinates activation, memory, command routing and response generation."""

    def __init__(
        self,
        event_bus: AppEventBus,
        store,
        context_manager,
        memory_manager,
        ollama_client,
        command_router,
        tts_engine=None,
        activation_name: str = "Kaspian",
    ) -> None:
        super().__init__()
        self.event_bus = event_bus
        self.store = store
        self.context_manager = context_manager
        self.memory_manager = memory_manager
        self.ollama_client = ollama_client
        self.command_router = command_router
        self.tts_engine = tts_engine
        self.activation_detector = ActivationDetector(activation_name=activation_name)
        self.visible_person: PersonRecord | None = None
        self.pending_unknown_detection = None

    def set_visible_person(self, person: PersonRecord | None) -> None:
        self.visible_person = person
        self.event_bus.person_context_changed.emit(person)

    def set_pending_unknown_detection(self, detection) -> None:
        self.pending_unknown_detection = detection

    @Slot(str)
    def handle_manual_input(self, text: str) -> None:
        self.process_input(text, source="manual")

    def process_input(self, raw_text: str, source: str = "voice", speaker_name: str | None = None) -> str | None:
        text = raw_text.strip()
        if not text:
            return None

        activation_result = self.activation_detector.detect(text)
        self.store.save_message(
            role="user",
            content=text,
            source=source,
            was_activation=activation_result.activated,
            speaker_name=speaker_name,
        )
        self.event_bus.user_transcript.emit(source, text)

        if not activation_result.activated:
            self.event_bus.emit_state(AssistantMode.PASSIVE_LISTENING, "Escuchando sin intervenir")
            self.store.update_assistant_state(AssistantMode.PASSIVE_LISTENING.value, last_user_input=text)
            return None

        prompt_text = activation_result.cleaned_text or "Hola"
        self.event_bus.emit_state(AssistantMode.ACTIVATED_LISTENING, "Kaspian escuchando")
        self.store.update_assistant_state(AssistantMode.ACTIVATED_LISTENING.value, last_user_input=prompt_text)

        if self.pending_unknown_detection is not None:
            self.event_bus.unknown_person_prompt.emit(self.pending_unknown_detection)

        self.event_bus.emit_state(AssistantMode.THINKING, "Procesando")
        self.store.update_assistant_state(AssistantMode.THINKING.value, last_user_input=prompt_text)

        command_result = self.command_router.route(prompt_text, self.visible_person)
        if command_result.handled:
            response_text = command_result.response_text
            if command_result.command_name in {"open_spotify", "play_music", "pause_music", "next_track", "previous_track", "set_volume"}:
                self.event_bus.music_status_changed.emit(command_result.command_name, response_text)
        else:
            response_text = self._generate_llm_response(prompt_text)

        self.store.save_message(role="assistant", content=response_text, source="assistant", was_activation=True)
        self.memory_manager.process_text_for_memory(prompt_text, source=source, person_id=self.visible_person.id if self.visible_person else None)
        self.store.update_assistant_state(AssistantMode.SPEAKING.value, last_assistant_output=response_text)
        self.event_bus.assistant_transcript.emit(response_text)
        self.event_bus.emit_state(AssistantMode.SPEAKING, "Respondiendo")

        if self.tts_engine is not None:
            try:
                self.tts_engine.speak(response_text)
            except Exception as exc:  # pragma: no cover - defensive audio path
                logger.exception("Error al reproducir TTS: %s", exc)
                self.event_bus.error_occurred.emit(str(exc))

        self.event_bus.emit_state(AssistantMode.IDLE, "En espera")
        self.store.update_assistant_state(AssistantMode.IDLE.value, last_assistant_output=response_text)
        return response_text

    def _generate_llm_response(self, prompt_text: str) -> str:
        memories = self.store.search_memories(prompt_text)
        preferences = self.store.list_preferences()
        recent_context = self.context_manager.get_recent_context()
        system_prompt = build_system_prompt(self.visible_person, memories, preferences)
        messages = [{"role": "system", "content": system_prompt}, *recent_context, {"role": "user", "content": prompt_text}]
        try:
            return self.ollama_client.generate_response(messages)
        except Exception as exc:
            logger.exception("Fallo generando respuesta de Ollama: %s", exc)
            return "Ahora mismo no puedo consultar mi motor local, pero sigo atento."
