from langchain_community.vectorstores import FAISS

from app.config import VECTORSTORE_DIR
from app.rag.embeddings import embeddings
from app.rag.storage import download_vectorstore


def get_retriever():


    download_vectorstore(VECTORSTORE_DIR)


    vectorstore = FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )


    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k":3
        }
    )


    return retriever