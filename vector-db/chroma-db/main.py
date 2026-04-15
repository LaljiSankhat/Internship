from fastapi import FastAPI
from models import *
from services.chroma_db_config import *



# Initialize FastAPI
app = FastAPI(title="ChromaDB FastAPI Example")


@app.post("/upsert-chroma")
def upsert_documents(request: UpsertRequest):
    response = add_into_chromadb(request=request)
    return response


@app.post("/query-chroma")
def query_documents(request: QueryRequest):
    response = query_in_chromadb(request=request)
    return response
