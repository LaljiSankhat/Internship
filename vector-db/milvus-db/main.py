# from services.milvus_service import MilvusService


# async def main():
#     milvus_service = MilvusService(host="localhost", port=19530)
    
#     # Create collection
#     await milvus_service.create_collection(collection_name="my_text_embeddings", dimension=5)

#     # Insert data
#     documents = [
#         "This is the first document.",
#         "This is the second document.",
#         "This is the third document."
#     ]
#     await milvus_service.insert_data(collection_name="my_text_embeddings", document=documents)

#     # Search for similar documents
#     query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]  # Example query vector (5-dimensional)
#     search_results = await milvus_service.search(query_vector=query_vector, collection_name="my_text_embeddings", limit=2)

#     # Print search results
#     await milvus_service.print_search_results(search_results)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


from fastapi import FastAPI, Body, Depends
import uvicorn
from services.milvus_service import MilvusService
from typing import Annotated
from fastapi import File, UploadFile

app = FastAPI()


service = MilvusService(host="localhost", port=19530)

@app.on_event("startup")
async def startup_event():
    await service.create_collection(collection_name="my_text_embeddings", dimension=384)

@app.get("/")
async def root():
    return {"message": "Welcome to the Milvus API!"}


@app.post("/upload-pdf")
async def upload_document(
    title: Annotated[str, Body()],
    file: Annotated[UploadFile, File()],
):
    file_bytes = await file.read()
    document = await service.upload_document_milvus(
        title=title,
        file_bytes=file_bytes
    )
    return {
        "result": document,
    }

@app.post("/query")
async def query_document(
    query: Annotated[str, Body()],
    top_k: Annotated[int, Body()] = 10,
):
    documents = await service.search(
        query=query,
        limit=top_k
    )
    return {
        "documents": documents
    }

@app.get("/collections")
async def get_collections():
    collections = await service.get_all_collections_data()
    return {
        "collections": collections
    }

@app.post("/chat")
async def chat(
    query: Annotated[str, Body()]
):
    response = await service.chat(query=query)
    return {
        "response": response
    }
    


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )