from unittest.mock import MagicMock

import app.services.rag_service as rag_service


def test_extract_text_from_plain_string():
    assert rag_service._extract_text("hello") == "hello"


def test_extract_text_from_content_blocks():
    content = [
        {"type": "text", "text": "Hello "},
        {"type": "text", "text": "world"},
        {"type": "thinking", "text": "should be ignored"},
    ]

    assert rag_service._extract_text(content) == "Hello world"


def test_extract_text_ignores_non_dict_blocks():
    content = ["not a dict", {"type": "text", "text": "kept"}]

    assert rag_service._extract_text(content) == "kept"


def test_ask_question_invokes_graph_with_given_thread_id(monkeypatch):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {"messages": [MagicMock(content="the answer")]}
    monkeypatch.setattr(rag_service, "graph", fake_graph)

    answer = rag_service.ask_question("what is ec2?", session_id="abc123")

    assert answer == "the answer"
    assert fake_graph.invoke.call_args.kwargs["config"] == {"configurable": {"thread_id": "abc123"}}


def test_ask_question_defaults_thread_id_to_default(monkeypatch):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {"messages": [MagicMock(content="hi there")]}
    monkeypatch.setattr(rag_service, "graph", fake_graph)

    rag_service.ask_question("hello")

    assert fake_graph.invoke.call_args.kwargs["config"] == {"configurable": {"thread_id": "default"}}
