from __future__ import annotations

from storage.models import MemoryRecord, PersonRecord


BASE_SYSTEM_PROMPT = """
Eres Kaspian, un asistente de hogar visual premium.

Tu personalidad:
- Hablas siempre en español.
- Eres cálido, elegante, sereno y tecnológico.
- Respondes breve por defecto.
- Si el usuario pide más detalle, amplías con claridad.
- No inventas información sobre personas que no conoces.
- No actúas si no te han invocado por tu nombre.
- Si reconoces a una persona conocida, puedes mencionarla naturalmente.
- Si una persona es desconocida, dilo con honestidad y con cortesía.
- Puedes recordar preferencias del usuario si existen.

Estilo:
- Frases claras y naturales.
- Sin tono robótico.
- Evita listas largas salvo que el usuario las pida.
""".strip()


def build_system_prompt(
    visible_person: PersonRecord | None,
    memories: list[MemoryRecord],
    preferences: dict[str, str],
) -> str:
    memory_lines = [f"- [{memory.category}] {memory.content}" for memory in memories[:8]]
    preference_lines = [f"- {key}: {value}" for key, value in preferences.items()]
    visible_person_text = (
        f"Persona visible actualmente: {visible_person.name}."
        if visible_person
        else "No hay una persona visible reconocida con suficiente confianza."
    )

    prompt_parts = [
        BASE_SYSTEM_PROMPT,
        visible_person_text,
        "Preferencias conocidas:",
        "\n".join(preference_lines) if preference_lines else "- No hay preferencias guardadas.",
        "Memorias relevantes:",
        "\n".join(memory_lines) if memory_lines else "- No hay memorias relevantes.",
    ]
    return "\n\n".join(prompt_parts)
