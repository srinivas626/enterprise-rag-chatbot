import io

from fastapi.testclient import TestClient

import app.api.upload as upload_module
from app.main import app

client = TestClient(app)


def test_upload_endpoint_ingests_file(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_module, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(upload_module, "ingest_document", lambda path: 42)

    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 fake content"), "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "File uploaded and ingested",
        "filename": "test.pdf",
        "chunks_ingested": 42,
    }
    assert (tmp_path / "test.pdf").exists()


def test_upload_endpoint_sanitizes_path_traversal_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_module, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(upload_module, "ingest_document", lambda path: 1)

    response = client.post(
        "/upload",
        files={"file": ("../../evil.pdf", io.BytesIO(b"content"), "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "evil.pdf"
    assert (tmp_path / "evil.pdf").exists()
    assert not (tmp_path.parent.parent / "evil.pdf").exists()


def test_upload_endpoint_requires_a_file():
    response = client.post("/upload")

    assert response.status_code == 422
