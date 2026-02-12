"""RAG service for retrieval-augmented generation."""
from typing import List, Optional

from app.config import config
from app.models.character import Character
from app.services.vector_store import VectorStore


class RAGService:
    """RAG service for combining character profile with retrieved context."""

    def __init__(
        self,
        character: Character,
        vector_store: Optional[VectorStore] = None,
    ):
        """Initialize the RAG service.

        Args:
            character: Character profile
            vector_store: Optional vector store instance
        """
        self.character = character
        self.vector_store = vector_store or VectorStore()

    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> List[dict]:
        """Retrieve relevant context from the knowledge base.

        Args:
            query: User query
            top_k: Number of results to retrieve

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        return self.vector_store.search(query, top_k=top_k)

    def build_prompt(self, user_message: str, context_results: List[dict]) -> str:
        """Build the complete prompt for the LLM.

        Args:
            user_message: User's message
            context_results: Retrieved context from vector search

        Returns:
            Complete prompt string
        """
        # Start with character system prompt
        system_prompt = self.character.build_system_prompt()

        # Add language instruction
        system_prompt += """

IMPORTANT: Always respond in the same language as the user's message. If the user writes in English, respond in English. If they write in Russian, respond in Russian. If they write in any other language, respond in that same language."""

        # Add retrieved context if available
        if context_results:
            context_text = "\n\n".join([
                f"[From {r['metadata']['source']}]: {r['text']}"
                for r in context_results
            ])
            system_prompt += f"""

RELEVANT CONTEXT FROM YOUR KNOWLEDGE:
{context_text}

Use this information to inform your response, but always stay in character as {self.character.name}."""
        else:
            system_prompt += f"""

Respond to the user as {self.character.name}, staying in character."""

        return system_prompt

    def get_sources(self, context_results: List[dict]) -> List[dict]:
        """Extract source information from context results.

        Args:
            context_results: Retrieved context from vector search

        Returns:
            List of source dictionaries with file and relevance
        """
        return [
            {
                "file": r["metadata"]["source"],
                "relevance": round(r["similarity"], 3),
            }
            for r in context_results
        ]
