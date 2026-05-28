from pymilvus import MilvusClient
from services.embedding_service import EmbeddingService
import pymupdf
import asyncio
from chonkie import RecursiveChunker
from dotenv import load_dotenv
import os
from groq import Groq
load_dotenv()  # Load environment variables from .env file

COLLECTION_NAME = "my_text_embeddings"


class MilvusService:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = MilvusClient(uri=f"http://{self.host}:{self.port}")
        self.collection_name = COLLECTION_NAME
        self.embedding_model = EmbeddingService()
        self.llm_client =  Groq(api_key=os.getenv("GROQ_API_KEY"))
    

    async def create_collection(self, collection_name: str, dimension: int):
        if self.client.has_collection(collection_name):
            self.client.drop_collection(collection_name)
        self.client.create_collection(
            collection_name=collection_name,
            dimension=dimension
        )
    
    async def _get_document_embedding(self, document: list[str]) -> list[float]:
        embeddings = []
        for text in document:
            embedding = await self.embedding_model.embed_text(text)
            embeddings.append(embedding)
        return embeddings

    async def _create_data(self, document: list[str]):
        data = []
        embeddings = await self._get_document_embedding(document)
        for idx, (text, embedding) in enumerate(zip(document, embeddings)):
            data.append({"id": idx + 1, "vector": embedding, "text": text})
        return data

    async def insert_data(self, collection_name: str, document: list[str]):
        data = await self._create_data(document)
        self.client.insert(collection_name=collection_name, data=data)
        print(f"Successfully inserted {len(data)} entities into collection '{collection_name}'.")

    async def search(self, query: str, collection_name: str = COLLECTION_NAME, limit: int = 10):
        query_vector = await self._get_document_embedding([query])
        search_results = self.client.search(
            collection_name=collection_name,
            data=query_vector,
            limit=limit,
            output_fields=["text"]
        )
        return search_results

    async def get_all_collections_data(self) -> dict:
        """
        Retrieves all documents, including text, scalars, and vector embeddings
        from every collection found in the Milvus instance.
        """
        # 1. Fetch names of all active collections
        # Since pymilvus is synchronous natively, we run it in an executor to avoid blocking the loop
        loop = asyncio.get_running_loop()
        collections = await loop.run_in_executor(None, self.client.list_collections)
        
        all_data = {}

        # 2. Iterate through each collection to pull all records
        for collection_name in collections:
            try:
                records = await loop.run_in_executor(
                    None, 
                    lambda col=collection_name: self.client.query(
                        collection_name=col,
                        filter="",              # Empty filter string grabs all rows
                        output_fields=["id", "text"],    # CRITICAL: Wildcard to include embeddings + text
                        limit=100             # Adjust limit based on how many records you expect
                    )
                )
                all_data[collection_name] = records
            except Exception as e:
                print(f"Error reading collection {collection_name}: {e}")
                all_data[collection_name] = []

        return all_data

    async def _parse_document_bytes(self, file_bytes: bytes):
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")

        text_parts: list[str] = []

        for page in doc:
            text = page.get_text()
            if text:
                text_parts.append(text) 
            else:
                text_parts.append(" ")
        return "\n".join(text_parts)

    async def _create_chunks(self, file_text: str):
        chunker = RecursiveChunker(chunk_size=512)
        chunks = chunker.chunk(file_text)
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedding_model.embed_text(chunk_texts)
        return [
            {"text": text, "embedding": embedding}
            for text, embedding in zip(chunk_texts, embeddings)
        ]

    
    async def upload_document_milvus(self, title: str, file_bytes: bytes):
        file_text = await self._parse_document_bytes(file_bytes)

        chunks = await self._create_chunks(file_text)

        text_list = [chunk["text"] for chunk in chunks]
        await self.insert_data(collection_name=self.collection_name, document=text_list)
        return {
            "num_chunks": len(chunks),
            "message": f"Successfully uploaded document '{title}' with {len(chunks)} chunks",
        }

    async def _get_relavent_context(self, query: str, top_k: int = 10):
        search_results = await self.search(query=query, limit=top_k)
        relevant_context = []
        for hits in search_results:
            for hit in hits:
                relevant_context.append(hit["entity"]["text"])
        context_text = "\n".join(relevant_context)
        return context_text

    async def _call_llm(self, query: str, context: str):
        response = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0,
            stream=False,
        )
        return response.choices[0].message.content

    async def chat(self, query: str):
        context = await self._get_relavent_context(query)
        response = await self._call_llm(query, context)
        return {
            "answer": response,
            "context": context
        }

    async def print_search_results(self, search_results):
        print("\n--- Search Results ---")
        for hits in search_results:
            for hit in hits:
                print(f"ID: {hit['id']}, Score (Distance): {hit['distance']:.4f}, Text: {hit['entity']['text']}")