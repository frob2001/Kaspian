from __future__ import annotations

from collections.abc import Sequence
import logging

import httpx

from config.settings import Settings


logger = logging.getLogger(__name__)


class OllamaClient:
    """Local Ollama HTTP client."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(base_url=self.settings.ollama_host, timeout=self.settings.ollama_timeout)

    def healthcheck(self) -> bool:
        try:
            response = self._client.get("/api/tags")
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            logger.warning("Ollama no disponible: %s", exc)
            return False

    def generate_response(self, messages: Sequence[dict[str, str]]) -> str:
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "messages": list(messages),
        }
        response = self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        content = str(message.get("content", "")).strip()
        return content or "No pude generar una respuesta en este momento."

    def close(self) -> None:
        self._client.close()
