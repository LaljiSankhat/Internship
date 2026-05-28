
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)

    async def embed_text(self, text):
        return self.embedding_model.encode(text)