import chromadb
from models import *
from dotenv import load_dotenv
import os

load_dotenv


# chroma_client = chromadb.Client()

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8001"))
chroma_client = chromadb.HttpClient(
    host=HOST,
    port=PORT
)
collection = chroma_client.get_or_create_collection(name="my_collection")



def add_into_chromadb(request: UpsertRequest):
    collection.upsert(
        documents=request.documents,
        ids=request.ids,
    )
    return {"status": "success", "count": len(request.documents)}

def query_in_chromadb(request: QueryRequest):
    results = collection.query(
        query_texts=request.query_texts,
        n_results=request.n_results,
    )
    return results



