from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

import app.rag.storage as storage


def test_download_vectorstore_noop_when_no_bucket(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "_s3", None)

    storage.download_vectorstore(str(tmp_path))

    assert list(tmp_path.iterdir()) == []


def test_upload_vectorstore_noop_when_no_bucket(monkeypatch):
    monkeypatch.setattr(storage, "_s3", None)

    storage.upload_vectorstore("this_directory_does_not_exist")


def test_upload_source_document_noop_when_no_bucket(monkeypatch):
    monkeypatch.setattr(storage, "_s3", None)

    storage.upload_source_document("this_file_does_not_exist.pdf", "file.pdf")


def test_download_vectorstore_fetches_both_index_files(tmp_path, monkeypatch):
    mock_s3 = MagicMock()
    monkeypatch.setattr(storage, "_s3", mock_s3)
    monkeypatch.setattr(storage, "S3_BUCKET", "test-bucket")

    storage.download_vectorstore(str(tmp_path))

    assert mock_s3.download_file.call_count == 2
    called_keys = {call.args[1] for call in mock_s3.download_file.call_args_list}
    assert called_keys == {"vectorstore/index.faiss", "vectorstore/index.pkl"}


def test_download_vectorstore_ignores_missing_file_404(tmp_path, monkeypatch):
    mock_s3 = MagicMock()
    mock_s3.download_file.side_effect = ClientError({"Error": {"Code": "404"}}, "download_file")
    monkeypatch.setattr(storage, "_s3", mock_s3)
    monkeypatch.setattr(storage, "S3_BUCKET", "test-bucket")

    storage.download_vectorstore(str(tmp_path))


def test_download_vectorstore_reraises_non_404_errors(tmp_path, monkeypatch):
    mock_s3 = MagicMock()
    mock_s3.download_file.side_effect = ClientError({"Error": {"Code": "403"}}, "download_file")
    monkeypatch.setattr(storage, "_s3", mock_s3)
    monkeypatch.setattr(storage, "S3_BUCKET", "test-bucket")

    with pytest.raises(ClientError):
        storage.download_vectorstore(str(tmp_path))


def test_upload_vectorstore_uploads_only_files_that_exist(tmp_path, monkeypatch):
    mock_s3 = MagicMock()
    monkeypatch.setattr(storage, "_s3", mock_s3)
    monkeypatch.setattr(storage, "S3_BUCKET", "test-bucket")

    (tmp_path / "index.faiss").write_text("fake-index")

    storage.upload_vectorstore(str(tmp_path))

    assert mock_s3.upload_file.call_count == 1
    assert mock_s3.upload_file.call_args.args[1] == "test-bucket"
    assert mock_s3.upload_file.call_args.args[2] == "vectorstore/index.faiss"


def test_upload_source_document_uses_uploads_prefix(tmp_path, monkeypatch):
    mock_s3 = MagicMock()
    monkeypatch.setattr(storage, "_s3", mock_s3)
    monkeypatch.setattr(storage, "S3_BUCKET", "test-bucket")

    file_path = tmp_path / "doc.pdf"
    file_path.write_text("fake-pdf")

    storage.upload_source_document(str(file_path), "doc.pdf")

    mock_s3.upload_file.assert_called_once_with(str(file_path), "test-bucket", "uploads/doc.pdf")
