import os

import boto3
from botocore.exceptions import ClientError

from app.config import S3_BUCKET, VECTORSTORE_DIR, UPLOAD_DIR


VECTORSTORE_PREFIX = VECTORSTORE_DIR + "/"
UPLOADS_PREFIX = UPLOAD_DIR + "/"

_s3 = boto3.client("s3") if S3_BUCKET else None


def download_vectorstore(local_dir):
    """Pull the latest FAISS index from S3 so this instance sees documents
    ingested by other instances. No-ops when S3_BUCKET isn't configured
    (local dev keeps using whatever is already on disk)."""

    if not _s3:
        return

    os.makedirs(local_dir, exist_ok=True)

    for filename in ("index.faiss", "index.pkl"):

        try:
            _s3.download_file(
                S3_BUCKET,
                VECTORSTORE_PREFIX + filename,
                os.path.join(local_dir, filename)
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise


def upload_vectorstore(local_dir):

    if not _s3:
        return

    for filename in ("index.faiss", "index.pkl"):

        local_path = os.path.join(local_dir, filename)

        if os.path.exists(local_path):
            _s3.upload_file(
                local_path,
                S3_BUCKET,
                VECTORSTORE_PREFIX + filename
            )


def upload_source_document(local_path, filename):

    if not _s3:
        return

    _s3.upload_file(
        local_path,
        S3_BUCKET,
        UPLOADS_PREFIX + filename
    )
