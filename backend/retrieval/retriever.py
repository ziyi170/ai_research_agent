"""
Retriever - generates query embeddings and searches vector store.

This is the core of the RAG pipeline:
  query -> embedding -> FAISS search -> top-k chunks -> LLM context
"""

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()
from retrieval.vector_store import VectorStore

client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
store = VectorStore()

EMBEDDING_MODEL = "openai/text-embedding-3-small"  # 1536-dim, cheap and fast


async def embed_text(text: str) -> list[float]:
    """
    Converts text into a vector embedding using OpenAI's embedding API.
    These vectors capture semantic meaning for similarity search.
    """
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


async def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    """
    Embeds a list of chunks in parallel using asyncio.gather.
    Much faster than embedding sequentially.
    """
    tasks = [embed_text(chunk["text"]) for chunk in chunks]
    return await asyncio.gather(*tasks)


async def index_documents(documents: list[dict]):
    """
    Full ingestion pipeline:
    1. Chunk each document
    2. Embed all chunks in parallel
    3. Store in FAISS vector index
    """
    from retrieval.chunking import chunk_documents
    chunks = chunk_documents(documents)
    embeddings = await embed_chunks(chunks)
    store.add(embeddings, chunks)
    store.save()
    return len(chunks)


async def retrieve_docs(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieves the most relevant document chunks for a query.
    
    Steps:
    1. Embed the user query
    2. Search FAISS for nearest neighbours
    3. Return top_k chunks with text + source metadata
    """
    if store.size == 0:
        return []  # No documents indexed yet

    query_embedding = await embed_text(query)
    results = store.search(query_embedding, top_k=top_k)
    return results
