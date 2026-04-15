from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )
        return embeddings

# m = EmbeddingModel()

# print(m.embed_texts(["helo"]))