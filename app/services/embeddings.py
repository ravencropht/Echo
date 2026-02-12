"""Embedding service for text chunking and vector generation."""
from pathlib import Path
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import config


class EmbeddingService:
    """Service for generating embeddings from text."""

    def __init__(self, model_name: str | None = None):
        """Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model.
        """
        self.model_name = model_name or config.embedding.model
        self.model = SentenceTransformer(self.model_name)
        self.chunk_size = config.embedding.chunk_size
        self.chunk_overlap = config.embedding.chunk_overlap

    def chunk_text(self, text: str, metadata: dict | None = None) -> List[dict]:
        """Split text into overlapping chunks.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text, metadata, and chunk_id
        """
        if metadata is None:
            metadata = {}

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunk_metadata = {
                **metadata,
                "chunk_id": chunk_id,
                "start": start,
                "end": end,
            }

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata,
            })

            start = end - self.chunk_overlap
            chunk_id += 1

        return chunks

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        result = self.model.encode(texts)
        # Convert numpy array to list
        import numpy as np
        if isinstance(result, np.ndarray):
            return result.tolist()
        return result

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text string

        Returns:
            Embedding vector
        """
        import numpy as np
        result = self.model.encode(text)
        if isinstance(result, np.ndarray):
            return result.tolist()
        return result if isinstance(result, list) else list(result)
