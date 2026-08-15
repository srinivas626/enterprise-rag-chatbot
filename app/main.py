from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.upload import router
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.config import SESSION_SECRET
from app.db import Base, engine
from app.models.user import User


app=FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)


@app.on_event("startup")
def create_tables():

    Base.metadata.create_all(bind=engine)


app.include_router(router)

app.include_router(chat_router)

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home():

    return FileResponse("app/static/index.html")


@app.get("/health")
def health():

    return {
        "message":
        "RAG API Running"
    }