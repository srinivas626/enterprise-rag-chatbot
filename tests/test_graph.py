from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage

import app.rag.graph as graph_module


def test_route_after_classify_returns_chat():
    assert graph_module.route_after_classify({"route": "chat"}) == "chat"


def test_route_after_classify_returns_retrieve():
    assert graph_module.route_after_classify({"route": "retrieve"}) == "retrieve"


def test_route_after_retrieve_goes_to_generate_when_context_found():
    assert graph_module.route_after_retrieve({"context": "some relevant text"}) == "generate"


def test_route_after_retrieve_goes_to_chat_when_context_empty():
    assert graph_module.route_after_retrieve({"context": ""}) == "chat"


def test_route_after_retrieve_goes_to_chat_when_context_whitespace_only():
    assert graph_module.route_after_retrieve({"context": "   \n  "}) == "chat"


def test_route_after_retrieve_goes_to_chat_when_context_key_missing():
    assert graph_module.route_after_retrieve({}) == "chat"


def test_classify_node_routes_small_talk_to_chat(monkeypatch):
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="chat")
    monkeypatch.setattr(graph_module, "get_llm", lambda: fake_llm)

    state = {"messages": [HumanMessage(content="hi")], "context": "", "route": ""}

    assert graph_module.classify_node(state) == {"route": "chat"}


def test_classify_node_routes_document_question_to_retrieve(monkeypatch):
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="retrieve")
    monkeypatch.setattr(graph_module, "get_llm", lambda: fake_llm)

    state = {"messages": [HumanMessage(content="what is ec2?")], "context": "", "route": ""}

    assert graph_module.classify_node(state) == {"route": "retrieve"}


def test_classify_node_defaults_to_retrieve_on_ambiguous_output(monkeypatch):
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="unsure / not clear")
    monkeypatch.setattr(graph_module, "get_llm", lambda: fake_llm)

    state = {"messages": [HumanMessage(content="what is ec2?")], "context": "", "route": ""}

    assert graph_module.classify_node(state) == {"route": "retrieve"}


def test_retrieve_node_joins_retrieved_documents_into_context(monkeypatch):
    fake_doc1 = MagicMock(page_content="chunk one")
    fake_doc2 = MagicMock(page_content="chunk two")
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc1, fake_doc2]
    monkeypatch.setattr(graph_module, "get_retriever", lambda: fake_retriever)

    state = {"messages": [HumanMessage(content="what is ec2?")], "context": "", "route": "retrieve"}

    assert graph_module.retrieve_node(state) == {"context": "chunk one\n\nchunk two"}


def test_retrieve_node_returns_empty_context_when_no_vectorstore(monkeypatch):
    def raise_missing_index():
        raise FileNotFoundError("no vectorstore on disk")

    monkeypatch.setattr(graph_module, "get_retriever", raise_missing_index)

    state = {"messages": [HumanMessage(content="what is ec2?")], "context": "", "route": "retrieve"}

    assert graph_module.retrieve_node(state) == {"context": ""}


def test_generate_node_includes_context_in_system_prompt(monkeypatch):
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="EC2 is a compute service.")
    monkeypatch.setattr(graph_module, "get_llm", lambda: fake_llm)

    state = {
        "messages": [HumanMessage(content="what is ec2?")],
        "context": "EC2 stands for Elastic Compute Cloud",
        "route": "retrieve",
    }

    result = graph_module.generate_node(state)

    sent_messages = fake_llm.invoke.call_args.args[0]
    assert "EC2 stands for Elastic Compute Cloud" in sent_messages[0].content
    assert result["messages"][0].content == "EC2 is a compute service."


def test_chat_node_does_not_reference_context(monkeypatch):
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="Hi there!")
    monkeypatch.setattr(graph_module, "get_llm", lambda: fake_llm)

    state = {"messages": [HumanMessage(content="hi")], "context": "", "route": "chat"}

    result = graph_module.chat_node(state)

    sent_messages = fake_llm.invoke.call_args.args[0]
    assert "friendly assistant" in sent_messages[0].content
    assert result["messages"][0].content == "Hi there!"
