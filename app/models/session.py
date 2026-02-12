"""Session models for chat history."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.services.llm import Message


@dataclass
class ChatMessage:
    """A single chat message."""

    role: str
    content: str
    timestamp: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
        )

    def to_llm_message(self) -> Message:
        """Convert to LLM message format."""
        return Message(role=self.role, content=self.content)

    @classmethod
    def create(cls, role: str, content: str) -> "ChatMessage":
        """Create a new message with current timestamp."""
        return cls(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )


@dataclass
class Session:
    """A chat session with history."""

    session_id: str
    created_at: str
    messages: List[ChatMessage] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "messages": [m.to_dict() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            messages=[ChatMessage.from_dict(m) for m in data.get("messages", [])],
        )

    @classmethod
    def create(cls, session_id: Optional[str] = None) -> "Session":
        """Create a new session."""
        return cls(
            session_id=session_id or str(uuid4()),
            created_at=datetime.utcnow().isoformat() + "Z",
        )

    def add_message(self, role: str, content: str) -> ChatMessage:
        """Add a message to the session.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content

        Returns:
            The created message
        """
        message = ChatMessage.create(role, content)
        self.messages.append(message)
        return message

    def get_llm_messages(self, max_history: Optional[int] = None) -> List[Message]:
        """Get messages in LLM format.

        Args:
            max_history: Maximum number of recent messages to include

        Returns:
            List of LLM messages
        """
        messages = self.messages
        if max_history:
            messages = messages[-max_history:]

        return [m.to_llm_message() for m in messages]

    def trim_to_max_tokens(self, max_tokens: int = 8000) -> None:
        """Trim message history to fit within token limit.

        Args:
            max_tokens: Approximate token limit (rough estimate)
        """
        # Rough estimate: 1 token ~ 4 characters
        total_chars = sum(len(m.content) for m in self.messages)
        max_chars = max_tokens * 4

        if total_chars <= max_chars:
            return

        # Remove oldest messages until under limit
        while self.messages and total_chars > max_chars:
            removed = self.messages.pop(0)
            total_chars -= len(removed.content)
