import os
import shutil

from fastapi import APIRouter, UploadFile, File

from app.config import UPLOAD_DIR
from app.services.document_service import ingest_document


router=APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    filename = os.path.basename(file.filename)

    path = os.path.join(UPLOAD_DIR, filename)


    with open(path,"wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    chunks_ingested = ingest_document(path)


    return {

        "message":"File uploaded and ingested",
        "filename":filename,
        "chunks_ingested":chunks_ingested

    }
