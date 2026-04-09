from types import SimpleNamespace

from brain.ollama_client import OllamaClient
from config.settings import Settings


class DummyHttpClient:
    def __init__(self) -> None:
        self.last_payload = None

    def get(self, path: str):
        assert path == "/api/tags"
        return SimpleNamespace(raise_for_status=lambda: None)

    def post(self, path: str, json: dict):
        self.last_payload = json
        assert path == "/api/chat"
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"message": {"content": "Respuesta local"}},
        )

    def close(self):
        return None


def test_ollama_client_builds_chat_request():
    settings = Settings()
    client = OllamaClient(settings)
    dummy = DummyHttpClient()
    client._client = dummy

    text = client.generate_response([{"role": "user", "content": "Hola"}])

    assert text == "Respuesta local"
    assert dummy.last_payload["model"] == settings.ollama_model
    assert dummy.last_payload["stream"] is False
