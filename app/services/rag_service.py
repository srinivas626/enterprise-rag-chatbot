from langchain_core.messages import HumanMessage

from app.rag.graph import graph


def _extract_text(content):

    if isinstance(content, str):
        return content

    return "".join(
        block["text"]
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def ask_question(question, session_id="default"):

    config = {"configurable": {"thread_id": session_id}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config
    )

    return _extract_text(result["messages"][-1].content)
