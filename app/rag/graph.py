from typing import Annotated

from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.rag.retriever import get_retriever
from app.rag.llm import get_llm


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    context: str
    route: str


CLASSIFY_PROMPT = SystemMessage(content="""You are a routing classifier for a document Q&A assistant.

Decide whether the user's latest message requires searching uploaded
documents to answer, or whether it's general conversation (greetings,
thanks, small talk, or questions about the assistant itself) that
doesn't need a document lookup.

Respond with exactly one word, nothing else: "retrieve" or "chat".""")


def classify_node(state: ChatState):

    llm = get_llm()

    response = llm.invoke([CLASSIFY_PROMPT] + state["messages"])

    decision = str(response.content).strip().lower()

    route = "chat" if "chat" in decision else "retrieve"

    return {"route": route}


def route_after_classify(state: ChatState):

    return state["route"]


def retrieve_node(state: ChatState):

    question = state["messages"][-1].content

    try:
        retriever = get_retriever()
        documents = retriever.invoke(question)
    except Exception:
        documents = []

    context = "\n\n".join(doc.page_content for doc in documents)

    return {"context": context}


def route_after_retrieve(state: ChatState):

    if state.get("context", "").strip():
        return "generate"

    return "chat"


def _respond(state: ChatState, system_content: str):

    system_prompt = SystemMessage(content=system_content)

    llm = get_llm()

    response = llm.invoke([system_prompt] + state["messages"])

    return {"messages": [response]}


def generate_node(state: ChatState):

    return _respond(state, f"""You are an AWS expert assistant.

Answer only using the given context. If the context doesn't contain
the answer, say you don't know.

Context:

{state['context']}""")


def chat_node(state: ChatState):

    return _respond(state, """You are a friendly assistant for an enterprise
document Q&A tool. Respond naturally and conversationally. If the
user asks something that would require looking up their uploaded
documents and none have been indexed yet, let them know they can
upload a PDF to ask questions about it.""")


graph_builder = StateGraph(ChatState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("generate", generate_node)
graph_builder.add_node("chat", chat_node)

graph_builder.set_entry_point("classify")

graph_builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {"retrieve": "retrieve", "chat": "chat"}
)

graph_builder.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {"generate": "generate", "chat": "chat"}
)

graph_builder.add_edge("generate", END)
graph_builder.add_edge("chat", END)

graph = graph_builder.compile(checkpointer=MemorySaver())
