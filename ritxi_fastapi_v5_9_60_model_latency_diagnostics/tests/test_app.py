from fastapi.testclient import TestClient

from app.main import app


def test_health_and_chat_mock():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        data = health.json()
        assert data["app"] == "Ritxi FastAPI v5"
        assert data["current_character"]["id"] == "ritxi_tutor_comunicacion_di"

        chat = client.post(
            "/api/chat",
            json={
                "text": "hola",
                "session_id": "test",
                "flags": {
                    "output_audio": False,
                    "robot_motion": False,
                    "speech_motion": False,
                    "streaming": True,
                    "synchronize_turn": True,
                    "debug": True,
                },
            },
        )
        assert chat.status_code == 200
        payload = chat.json()
        assert payload["provider"] == "mock"
        assert payload["character_id"] == "ritxi_tutor_comunicacion_di"
        assert payload["text"]
