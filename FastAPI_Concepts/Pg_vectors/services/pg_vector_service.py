import pymupdf
from services.embeddings import EmbeddingModel
from models.document import Document, DocumentChunks
from core.db import db_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import text, select
from chonkie import RecursiveChunker
from groq import Groq
from config import settings

class PGVectorService:
    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        self.session = session
        self.embedding_model = EmbeddingModel()
        self.llm_client =  Groq(api_key=settings.GROQ_API_KEY)

    async def create_table(self):
        async with self.session.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
            await conn.run_sync(Document.metadata.create_all)
    
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

    
    async def upload_document(self, title: str, file_bytes: bytes):
        file_text = await self._parse_document_bytes(file_bytes)

        chunks = await self._create_chunks(file_text)

        docs_chunks = [
            DocumentChunks(
                chunk_text=chunk["text"],
                chunk_vector=chunk["embedding"]
            )
            for chunk in chunks
        ]

        document = Document(
            title=title,
            chunks=docs_chunks
        )

        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)

        return document
    
    async def query_document(self, query: str, top_k: int = 10):
        query_vector = await self.embedding_model.embed_text(query)
        selected_document_chunks = await self.session.scalars(
            select(DocumentChunks)
            .order_by(DocumentChunks.chunk_vector.cosine_distance(query_vector))
            .limit(top_k)
        )
        document_chunks = selected_document_chunks.all()
        return [
            {
                "document_id": str(document.document_id),
                "chunk_text": str(document.chunk_text),
                # "chunk_vector": str(document.chunk_vector),
            }
            for document in document_chunks
        ]
    
    async def _get_context(self, query: str):
        top_context = await self.query_document(query, 5)
        context_text = ""
        for context in top_context:
            context_text += f"{context["chunk_text"]} \n"
        
        print(context_text)
        return context_text
    
    async def _call_llm(self, query: str, context_text: str):
        response = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": context_text
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0,
            stream=False,
        )
        return response.choices[0].message
    
    async def chat(self, query: str):
        context_text = await self._get_context(query)
        result_answer = await self._call_llm(query, context_text)

        return {
            "answer": result_answer,
            "relavant_information": context_text
        }
        