from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.main import app

client = TestClient(app)


def test_chat_endpoint_returns_answer(monkeypatch):
    monkeypatch.setattr(chat_module, "ask_question", lambda question, session_id: "mocked answer")

    response = client.post("/chat", json={"question": "what is ec2?", "session_id": "s1"})

    assert response.status_code == 200
    assert response.json() == {
        "question": "what is ec2?",
        "answer": "mocked answer",
        "session_id": "s1",
    }


def test_chat_endpoint_defaults_session_id_when_omitted(monkeypatch):
    captured = {}

    def fake_ask_question(question, session_id):
        captured["session_id"] = session_id
        return "answer"

    monkeypatch.setattr(chat_module, "ask_question", fake_ask_question)

    response = client.post("/chat", json={"question": "hi"})

    assert response.status_code == 200
    assert captured["session_id"] == "default"
    assert response.json()["session_id"] == "default"


def test_chat_endpoint_rejects_missing_question():
    response = client.post("/chat", json={})

    assert response.status_code == 422


def test_chat_endpoint_passes_question_through_unmodified(monkeypatch):
    captured = {}

    def fake_ask_question(question, session_id):
        captured["question"] = question
        return "answer"

    monkeypatch.setattr(chat_module, "ask_question", fake_ask_question)

    client.post("/chat", json={"question": "  What is EC2?  "})

    assert captured["question"] == "  What is EC2?  "
