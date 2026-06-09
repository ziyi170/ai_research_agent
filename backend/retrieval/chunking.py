"""
Chunking - splits long documents into smaller overlapping chunks
before embedding. Chunk quality directly affects retrieval quality.

Strategy: fixed-size sliding window with overlap to avoid
cutting sentences at boundaries.
"""

from typing import Optional


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64
) -> list[dict]:
    """
    Splits text into overlapping chunks.
    
    Args:
        text: raw document text
        chunk_size: target token/char size per chunk
        overlap: number of chars shared between consecutive chunks
                 (prevents losing context at boundaries)
    
    Returns:
        list of dicts with 'text' and 'chunk_index'
    """
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary to improve coherence
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.6:  # Only if break point is reasonable
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append({
            "text": chunk.strip(),
            "chunk_index": chunk_index,
            "char_start": start,
            "char_end": end,
        })

        start = end - overlap  # Slide with overlap
        chunk_index += 1

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunks a list of documents, preserving source metadata.
    Each output chunk includes the original document's source field.
    """
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for chunk in chunks:
            chunk["source"] = doc.get("source", "unknown")
            chunk["doc_id"] = doc.get("id", "")
        all_chunks.extend(chunks)
    return all_chunks
