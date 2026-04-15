from services.faiss_store import FAISSStore
from services.embeddings import EmbeddingModel
from models import UpsertRequest, QueryRequest

model = EmbeddingModel()
store = FAISSStore()

def add_into_faiss(request: UpsertRequest):
    texts = request.documents

    embeddings = model.embed_texts(texts)

    metadatas = [{"text": text} for text in texts]

    store.add_vectors(embeddings, metadatas)

    return {"status": "success", "count": len(texts)}

def query_in_faiss(request: QueryRequest):
    query_embedding = model.embed_texts([request.query_text])[0]

    results = store.search(
        query_embedding,
        k=request.n_results
    )

    return results
