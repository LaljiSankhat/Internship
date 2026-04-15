from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from services.embeddings import EmbeddingModel
from typing import List

client = QdrantClient(url="http://localhost:6333")

model = EmbeddingModel()

client.recreate_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=384, distance=Distance.DOT),
)

texts = [
    "Berlin is the capital of Germany and known for its rich history.",
    "London is a major financial hub with famous landmarks like Big Ben.",
    "Moscow is known for the Kremlin and its cold winters.",
    "New York is called the city that never sleeps and is a global business center.",
    "Mumbai is the financial capital of India and home to Bollywood."
]

city = [
    "Berlin", "London", "Moscow", "New York", "Beijing", "Mumbai"
]

def create_points(texts: List[str], city: List[str]):
    points = []
    n = len(texts)

    embeddings = model.embed_texts(texts)

    for i in range(n):
        points.append(PointStruct(id=i, vector=embeddings[i], payload={"city": city[i]}))
    
    return points

operation_info = client.upsert(
    collection_name = "test_collection",
    wait=True,
    points=create_points(texts, city)
)

print(operation_info)

query = "tell me about Berlin."


search_result = client.query_points(
    collection_name = "test_collection",
    query=model.embed_texts([query])[0],
    with_payload=False,
    limit=3
).points



# query with filtering 
search_with_filter = client.query_points(
    collection_name = "test_collection",
    query = model.embed_texts([query])[0],
    query_filter = Filter(
        must=[FieldCondition(key="city", match=MatchValue(value="Berlin"))]
    ),
    with_payload=True,
    limit=3,
).points

print(search_result)
print(search_with_filter)
