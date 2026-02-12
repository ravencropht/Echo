"""API request and response models."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID to continue conversation")


class SourceInfo(BaseModel):
    """Information about a source document."""

    file: str = Field(..., description="Source file name")
    relevance: float = Field(..., description="Similarity score (0-1)")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="AI character's response")
    session_id: str = Field(..., description="Session ID for continuing conversation")
    sources: List[SourceInfo] = Field(default_factory=list, description="Source documents used")
    timestamp: str = Field(..., description="Response timestamp")


class CharacterResponse(BaseModel):
    """Response model for character endpoint."""

    name: str
    personality: str
    background: str
    relationships: str
    example_dialogue: str


class SessionSummary(BaseModel):
    """Summary of a chat session."""

    session_id: str
    created_at: str
    message_count: int


class SessionsListResponse(BaseModel):
    """Response model for sessions list endpoint."""

    sessions: List[SessionSummary]


class SessionHistoryResponse(BaseModel):
    """Response model for session history endpoint."""

    session_id: str
    created_at: str
    messages: List[dict]


class KnowledgeRebuildResponse(BaseModel):
    """Response model for knowledge rebuild endpoint."""

    files_indexed: int
    total_chunks: int
    sources: List[str]
    message: str


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = "ok"
    vector_db_initialized: bool
    character_loaded: bool
