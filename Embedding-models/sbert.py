from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "I love deep learning",
    "I enjoy studying neural networks",
    "The cat sits on the mat"
]

embeddings = model.encode(sentences)

print(embeddings)

# cosine similarity
print(cosine_similarity(embeddings))
