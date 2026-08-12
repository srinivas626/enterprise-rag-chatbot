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