from google import genai
from google.genai import types
import numpy as np
import os
from dotenv import load_dotenv

from sklearn.metrics.pairwise import (
    cosine_similarity,
    euclidean_distances,
    manhattan_distances
)

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Read images
with open("data/m2.mp3", "rb") as f:
    image_bytes = f.read()

with open("data/Lalji3.mp3", "rb") as f:
    image_bytes2 = f.read()

# Generate embeddings
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type="audio/mpeg",
        ),
        types.Part.from_bytes(
            data=image_bytes2,
            mime_type="audio/mpeg",
        ),
    ],
    # config={
    #     "output_dimensionality": 768
    # },
)

# Extract embeddings
embedding1 = np.array(result.embeddings[0].values)
embedding2 = np.array(result.embeddings[1].values)

print("Embedding1 length:", len(embedding1))
print("Embedding2 length:", len(embedding2))

# Reshape for sklearn (expects 2D arrays)
embedding1 = embedding1.reshape(1, -1)
embedding2 = embedding2.reshape(1, -1)

# -------- Similarity / Distance Metrics -------- #

cos_sim = cosine_similarity(embedding1, embedding2)[0][0]
euclid_dist = euclidean_distances(embedding1, embedding2)[0][0]
manhattan_dist = manhattan_distances(embedding1, embedding2)[0][0]



# -------- Print Results -------- #

print("\nSimilarity Metrics")
print("----------------------")
print("Cosine Similarity:", cos_sim)
print("Euclidean Distance:", euclid_dist)
print("Manhattan Distance:", manhattan_dist)
