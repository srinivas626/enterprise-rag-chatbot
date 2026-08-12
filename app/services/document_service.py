import os

from langchain_community.vectorstores import FAISS

from app.config import VECTORSTORE_DIR
from app.rag.embeddings import embeddings
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.storage import (
    download_vectorstore,
    upload_vectorstore,
    upload_source_document
)


def process_document(file_path):


    documents = load_pdf(
        file_path
    )


    chunks = split_documents(
        documents
    )


    return chunks


def ingest_document(file_path):

    chunks = process_document(file_path)

    download_vectorstore(VECTORSTORE_DIR)

    index_file = os.path.join(VECTORSTORE_DIR, "index.faiss")

    if os.path.exists(index_file):

        vectorstore = FAISS.load_local(
            VECTORSTORE_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

        vectorstore.add_documents(chunks)

    else:

        vectorstore = FAISS.from_documents(
            chunks,
            embeddings
        )

    vectorstore.save_local(VECTORSTORE_DIR)

    upload_vectorstore(VECTORSTORE_DIR)
    upload_source_document(file_path, os.path.basename(file_path))

    return len(chunks)