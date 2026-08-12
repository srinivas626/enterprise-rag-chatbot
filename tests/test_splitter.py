from langchain_core.documents import Document

from app.rag.splitter import split_documents


def test_split_documents_breaks_long_text_into_multiple_chunks():
    long_text = "word " * 400
    documents = [Document(page_content=long_text, metadata={"source": "test.pdf"})]

    chunks = split_documents(documents)

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 500 for chunk in chunks)


def test_split_documents_keeps_short_text_as_single_chunk():
    documents = [Document(page_content="short text", metadata={"source": "test.pdf"})]

    chunks = split_documents(documents)

    assert len(chunks) == 1
    assert chunks[0].page_content == "short text"


def test_split_documents_preserves_metadata():
    documents = [Document(page_content="short text", metadata={"source": "test.pdf", "page": 1})]

    chunks = split_documents(documents)

    assert chunks[0].metadata["source"] == "test.pdf"
    assert chunks[0].metadata["page"] == 1


def test_split_documents_empty_input_returns_empty_list():
    assert split_documents([]) == []
