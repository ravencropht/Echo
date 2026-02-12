"""Vector store service using ChromaDB."""
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings

from app.config import config
from app.services.embeddings import EmbeddingService


class VectorStore:
    """Vector store manager using ChromaDB."""

    COLLECTION_NAME = "knowledge_base"

    def __init__(self, embedding_service: EmbeddingService | None = None):
        """Initialize the vector store.

        Args:
            embedding_service: Optional embedding service instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.db_path = config.get_chroma_db_path()

        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        chunks: List[dict],
    ) -> None:
        """Add document chunks to the vector store.

        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed(texts)

        # Prepare IDs and metadatas
        ids = []
        metadatas = []

        for chunk in chunks:
            metadata = chunk["metadata"]
            source = metadata.get("source", "unknown")
            chunk_id = metadata.get("chunk_id", 0)

            ids.append(f"{source}_chunk_{chunk_id}")
            metadatas.append({
                "source": source,
                "chunk_id": chunk_id,
                **{k: v for k, v in metadata.items() if k not in ["source", "chunk_id"]},
            })

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def search(
        self,
        query: str,
        top_k: int | None = None,
        min_similarity: float | None = None,
    ) -> List[dict]:
        """Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of search results with text, metadata, and similarity score
        """
        top_k = top_k or config.rag.top_k
        min_similarity = min_similarity or config.rag.min_similarity

        # Generate query embedding
        query_embedding = self.embedding_service.embed_single(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Format results
        formatted_results = []

        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                # ChromaDB returns distances, convert to similarity
                # For cosine distance: similarity = 1 - distance
                distance = results["distances"][0][i]
                similarity = 1 - distance

                if similarity >= min_similarity:
                    formatted_results.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                    })

        return formatted_results

    def delete_all(self) -> None:
        """Delete all documents from the collection."""
        self.client.delete_collection(self.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()

    def index_knowledge_files(self) -> dict:
        """Index all knowledge files from the knowledge directory.

        Returns:
            Dictionary with indexing statistics
        """
        knowledge_dir = config.get_knowledge_dir()
        profile_path = config.get_profile_path()

        # Find all .txt files except profile.txt
        txt_files = [
            f for f in knowledge_dir.glob("*.txt")
            if f != profile_path
        ]

        all_chunks = []

        for txt_file in txt_files:
            text = txt_file.read_text()
            chunks = self.embedding_service.chunk_text(
                text,
                metadata={"source": txt_file.name},
            )
            all_chunks.extend(chunks)

        # Clear existing data and add new chunks
        self.delete_all()
        self.add_documents(all_chunks)

        return {
            "files_indexed": len(txt_files),
            "total_chunks": len(all_chunks),
            "sources": [f.name for f in txt_files],
        }
