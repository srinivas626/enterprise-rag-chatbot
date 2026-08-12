from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import ask_question


router=APIRouter()


class Question(BaseModel):

    question:str
    session_id:str="default"


@router.post("/chat")
def chat(
    request:Question
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
