import os
import shutil

from fastapi import APIRouter, UploadFile, File, Depends

from app.config import UPLOAD_DIR
from app.services.document_service import ingest_document
from app.auth.dependencies import require_user
from app.models.user import User


router=APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user: User = Depends(require_user)
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
