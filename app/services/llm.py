"""LLM service for Anthropic Claude."""
from typing import List, Optional

import httpx

from app.config import config


class Message:
    """Chat message."""

    def __init__(self, role: str, content: str):
        """Initialize a message.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        self.role = role
        self.content = content

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {"role": self.role, "content": self.content}


class LLMService:
    """Service for interacting with Anthropic Claude API."""

    API_VERSION = "2023-06-01"
    MAX_TOKENS = 4096

    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = config.settings.llm_api_key
        self.api_url = config.settings.llm_api_url
        self.model = config.settings.llm_model

    def _get_headers(self) -> dict:
        """Get request headers."""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

    def _get_client(self) -> httpx.Client:
        """Get HTTP client."""
        return httpx.Client(
            base_url=self.api_url,
            headers=self._get_headers(),
            timeout=120.0,
        )

    def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a chat request to Claude.

        Args:
            messages: List of chat messages
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text

        Raises:
            httpx.HTTPError: If the API request fails
        """
        max_tokens = max_tokens or self.MAX_TOKENS

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [m.to_dict() for m in messages],
        }

        if system_prompt:
            payload["system"] = system_prompt

        with self._get_client() as client:
            response = client.post(
                "/v1/messages",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    def chat_single(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a single message chat request.

        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        return self.chat(
            messages=[Message(role="user", content=user_message)],
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
