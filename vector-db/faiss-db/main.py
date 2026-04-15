from fastapi import FastAPI
from models import UpsertRequest, QueryRequest
from services.faiss_config import add_into_faiss, query_in_faiss


app = FastAPI(title="FAISS Vector DB FastAPI Example")


@app.post("/upsert-faiss")
def upsert_documents(request: UpsertRequest):
    return add_into_faiss(request)


@app.post("/query-faiss")
def query_documents(request: QueryRequest):
    return query_in_faiss(request)
