"""
Code will not run because zvec is only compatible with systems like 
Linux (x86_64, ARM64)
macOS (ARM64)

"""



import zvec

# Define collection schema
schema = zvec.CollectionSchema(
    name="example",
    vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, 4),
)
print("Creating collection...")

# Create collection
collection = zvec.create_and_open(path = "/app/zvec_data/example", schema=schema)
print("Collection created...")
# Insert documents
collection.insert([
    zvec.Doc(id="doc_1", vectors={"embedding": [0.1, 0.2, 0.3, 0.4]}),
    zvec.Doc(id="doc_2", vectors={"embedding": [0.2, 0.3, 0.4, 0.1]}),
])
print("Documents inserted...")
# Search by vector similarity
results = collection.query(
    zvec.VectorQuery("embedding", vector=[0.4, 0.3, 0.3, 0.1]),
    topk=10
)
print("Search completed...")
# Results: list of {'id': str, 'score': float, ...}, sorted by relevance
print(results)