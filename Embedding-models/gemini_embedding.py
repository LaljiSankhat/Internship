from google import genai
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["What is the meaning of life?", "This is gemini embedding"]
)

vectors = [emb.values for emb in result.embeddings]

# Dimension of embedding
print("Embedding dimension:", len(vectors[0]))

# Cosine similarity
similarity = cosine_similarity(vectors)
print("Cosine similarity matrix:")
print(similarity)