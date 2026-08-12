from unittest.mock import MagicMock

import app.services.document_service as document_service


def test_process_document_loads_and_splits(monkeypatch):
    fake_documents = ["doc1", "doc2"]
    fake_chunks = ["chunk1", "chunk2", "chunk3"]

    monkeypatch.setattr(document_service, "load_pdf", lambda path: fake_documents)
    monkeypatch.setattr(document_service, "split_documents", lambda docs: fake_chunks)

    result = document_service.process_document("fake.pdf")

    assert result == fake_chunks


def test_ingest_document_creates_new_vectorstore_when_none_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(document_service, "VECTORSTORE_DIR", str(tmp_path / "vectorstore"))
    monkeypatch.setattr(document_service, "process_document", lambda path: ["chunk1", "chunk2"])
    monkeypatch.setattr(document_service, "download_vectorstore", lambda d: None)
    monkeypatch.setattr(document_service, "upload_vectorstore", lambda d: None)
    monkeypatch.setattr(document_service, "upload_source_document", lambda p, f: None)

    fake_vectorstore = MagicMock()
    monkeypatch.setattr(
        document_service.FAISS, "from_documents", MagicMock(return_value=fake_vectorstore)
    )

    count = document_service.ingest_document("fake.pdf")

    assert count == 2
    fake_vectorstore.save_local.assert_called_once()


def test_ingest_document_appends_to_existing_vectorstore(monkeypatch, tmp_path):
    vs_dir = tmp_path / "vectorstore"
    vs_dir.mkdir()
    (vs_dir / "index.faiss").write_text("fake")

    monkeypatch.setattr(document_service, "VECTORSTORE_DIR", str(vs_dir))
    monkeypatch.setattr(document_service, "process_document", lambda path: ["chunk1"])
    monkeypatch.setattr(document_service, "download_vectorstore", lambda d: None)
    monkeypatch.setattr(document_service, "upload_vectorstore", lambda d: None)
    monkeypatch.setattr(document_service, "upload_source_document", lambda p, f: None)

    fake_vectorstore = MagicMock()
    monkeypatch.setattr(
        document_service.FAISS, "load_local", MagicMock(return_value=fake_vectorstore)
    )

    count = document_service.ingest_document("fake.pdf")

    assert count == 1
    fake_vectorstore.add_documents.assert_called_once_with(["chunk1"])
    fake_vectorstore.save_local.assert_called_once()


def test_ingest_document_uploads_index_and_source_after_saving(monkeypatch, tmp_path):
    monkeypatch.setattr(document_service, "VECTORSTORE_DIR", str(tmp_path / "vectorstore"))
    monkeypatch.setattr(document_service, "process_document", lambda path: ["chunk1"])
    monkeypatch.setattr(document_service, "download_vectorstore", lambda d: None)

    upload_calls = []
    monkeypatch.setattr(
        document_service, "upload_vectorstore", lambda d: upload_calls.append(("vectorstore", d))
    )
    monkeypatch.setattr(
        document_service,
        "upload_source_document",
        lambda p, f: upload_calls.append(("source", p, f)),
    )

    fake_vectorstore = MagicMock()
    monkeypatch.setattr(
        document_service.FAISS, "from_documents", MagicMock(return_value=fake_vectorstore)
    )

    document_service.ingest_document("uploads/fake.pdf")

    assert ("source", "uploads/fake.pdf", "fake.pdf") in upload_calls
    assert any(call[0] == "vectorstore" for call in upload_calls)
