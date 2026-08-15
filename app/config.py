import os
from dotenv import load_dotenv


load_dotenv()


GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)

S3_BUCKET = os.getenv(
    "S3_BUCKET"
)

VECTORSTORE_DIR = "vectorstore"
UPLOAD_DIR = "uploads"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rag:rag@localhost:5432/rag_chatbot"
)

SESSION_SECRET = os.getenv(
    "SESSION_SECRET"
)

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)
GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)

GITHUB_CLIENT_ID = os.getenv(
    "GITHUB_CLIENT_ID"
)
GITHUB_CLIENT_SECRET = os.getenv(
    "GITHUB_CLIENT_SECRET"
)

YAHOO_CLIENT_ID = os.getenv(
    "YAHOO_CLIENT_ID"
)
YAHOO_CLIENT_SECRET = os.getenv(
    "YAHOO_CLIENT_SECRET"
)