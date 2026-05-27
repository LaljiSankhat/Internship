
import uvicorn
import os 
from dotenv import load_dotenv
from core.db import init_db
from services.pg_vector_service import PGVectorService
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Body, File, UploadFile, Depends, FastAPI
from config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        raise
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_document(
    title: Annotated[str, Body()],
    file: Annotated[UploadFile, File()],
    service: Annotated[PGVectorService, Depends()]
):
    file_bytes = await file.read()
    document = await service.upload_document(
        title=title,
        file_bytes=file_bytes
    )
    return {
        "id": str(document.id),
        "title": document.title,
    }


@app.post("/query_document")
async def query_document(
    query: Annotated[str, Body()],
    service: Annotated[PGVectorService, Depends()],
    top_k: Annotated[int, Body()] = 10,
):
    documents = await service.query_document(
        query=query,
        top_k=top_k
    )
    return {
        "documents": documents
    }

@app.post("/chat")
async def chat(
    query: Annotated[str, Body()],
    service: Annotated[PGVectorService, Depends()]
):
    response = await service.chat(query);
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True
    )