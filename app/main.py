from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.upload import router
from app.api.chat import router as chat_router


app=FastAPI()


app.include_router(router)

app.include_router(chat_router)

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