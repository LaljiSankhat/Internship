import faiss
import os
import pickle
import numpy as np

VECTOR_DIM = 384
BASE_DIR = "vectorstore/faiss_index"
INDEX_PATH = f"{BASE_DIR}/index.faiss"
META_PATH = f"{BASE_DIR}/meta.pkl"

os.makedirs(BASE_DIR, exist_ok=True)

class FAISSStore:
    def __init__(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(VECTOR_DIM)
            self.metadata = []

    def add_vectors(self, vectors: np.ndarray, metadatas: list[dict]):
        vectors = vectors.astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadatas)
        self.save()

    def search(self, query_vector: np.ndarray, k=5):
        query_vector = query_vector.astype("float32").reshape(1, -1)
        D, I = self.index.search(query_vector, k)
        return [self.metadata[i] for i in I[0]]

    def save(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
