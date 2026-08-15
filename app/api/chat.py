from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.rag_service import ask_question
from app.auth.dependencies import require_user
from app.models.user import User


router=APIRouter()


class Question(BaseModel):

    question:str
    session_id:str="default"


@router.post("/chat")
def chat(
    request:Question,
    user: User = Depends(require_user)
):

    answer=ask_question(
        request.question,
        request.session_id
    )


    return {

        "question":
        request.question,

        "answer":
        answer,

        "session_id":
        request.session_id
    }
