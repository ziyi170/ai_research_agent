"""
Vector Store - manages FAISS index for fast semantic similarity search.

FAISS (Facebook AI Similarity Search) allows sub-millisecond nearest
neighbour search over millions of vectors. Used here for document retrieval.
"""

import numpy as np
import faiss
import pickle
import os
from typing import Optional


class VectorStore:
    """
    In-memory FAISS vector store with optional disk persistence.
    
    Stores:
      - FAISS index (for fast similarity search)
      - metadata list (maps vector index -> chunk text + source)
    """

    def __init__(self, dim: int = 1536, index_path: str = "faiss.index"):
        """
        Args:
            dim: embedding dimension (1536 for text-embedding-3-small)
            index_path: path to save/load FAISS index
        """
        self.dim = dim
        self.index_path = index_path
        self.meta_path = index_path + ".meta"
        self.metadata: list[dict] = []

        # Try loading existing index, otherwise create new one
        if os.path.exists(index_path):
            self._load()
        else:
            # IndexFlatIP = inner product (cosine similarity with normalised vectors)
            self.index = faiss.IndexFlatIP(dim)

    def add(self, embeddings: list[list[float]], chunks: list[dict]):
        """
        Adds embeddings and their corresponding chunk metadata to the store.
        Vectors are L2-normalised for cosine similarity via inner product.
        """
        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)  # Normalise for cosine similarity
        self.index.add(vectors)
        self.metadata.extend(chunks)

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """
        Returns top_k most similar chunks to the query embedding.
        Each result includes the chunk text, source, and similarity score.
        """
        query_vec = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vec)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            result = dict(self.metadata[idx])
            result["score"] = float(score)
            results.append(result)

        return results

    def save(self):
        """Persists index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def _load(self):
        """Loads index and metadata from disk."""
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)

    @property
    def size(self) -> int:
        return self.index.ntotal
