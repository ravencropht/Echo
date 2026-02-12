"""Main FastAPI application."""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import config
from app.models.api import (
    ChatRequest,
    ChatResponse,
    CharacterResponse,
    HealthResponse,
    KnowledgeRebuildResponse,
    SessionHistoryResponse,
    SessionSummary,
    SessionsListResponse,
)
from app.models.character import Character
from app.models.session import ChatMessage
from app.services.llm import LLMService
from app.services.rag import RAGService
from app.services.sessions import SessionStore
from app.services.vector_store import VectorStore

# Global services
character: Character | None = None
vector_store: VectorStore | None = None
rag_service: RAGService | None = None
llm_service: LLMService | None = None
session_store: SessionStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global character, vector_store, rag_service, llm_service, session_store

    # Load character profile
    character = Character.from_profile_file()

    # Initialize services
    vector_store = VectorStore()
    rag_service = RAGService(character=character, vector_store=vector_store)
    llm_service = LLMService()
    session_store = SessionStore()

    # Index knowledge files on startup if vector store is empty
    if vector_store.count() == 0:
        rag_service.vector_store.index_knowledge_files()

    yield

    # Cleanup on shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Echo - Character Chat",
    description="RAG-based character chat application",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the chat UI."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "character_name": character.name if character else "Loading..."},
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        vector_db_initialized=vector_store is not None and vector_store.count() > 0,
        character_loaded=character is not None,
    )


@app.get("/api/character", response_model=CharacterResponse)
async def get_character():
    """Get character profile."""
    if character is None:
        raise HTTPException(status_code=503, detail="Character not loaded")
    return CharacterResponse(**character.to_dict())


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    if llm_service is None or rag_service is None or session_store is None:
        raise HTTPException(status_code=503, detail="Services not initialized")

    # Get or create session
    session = session_store.get_or_create(request.session_id)

    # Retrieve relevant context
    context_results = rag_service.retrieve_context(request.message)

    # Build system prompt
    system_prompt = rag_service.build_prompt(request.message, context_results)

    # Get conversation history
    history_messages = session.get_llm_messages(max_history=20)

    # Add user message to session
    session.add_message("user", request.message)

    # Generate response
    llm_messages = history_messages + [session.messages[-1].to_llm_message()]
    response_text = llm_service.chat(llm_messages, system_prompt=system_prompt)

    # Add assistant response to session
    session.add_message("assistant", response_text)

    # Trim session if needed
    session.trim_to_max_tokens()

    # Save session
    session_store.save(session)

    # Get sources
    sources = rag_service.get_sources(context_results)

    return ChatResponse(
        response=response_text,
        session_id=session.session_id,
        sources=sources,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@app.get("/api/sessions", response_model=SessionsListResponse)
async def list_sessions():
    """List all chat sessions."""
    if session_store is None:
        raise HTTPException(status_code=503, detail="Session store not initialized")

    sessions = session_store.list_all()
    return SessionsListResponse(
        sessions=[SessionSummary(**s) for s in sessions]
    )


@app.get("/api/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session(session_id: str):
    """Get session history."""
    if session_store is None:
        raise HTTPException(status_code=503, detail="Session store not initialized")

    session = session_store.load(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionHistoryResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        messages=[m.to_dict() for m in session.messages],
    )


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_store is None:
        raise HTTPException(status_code=503, detail="Session store not initialized")

    deleted = session_store.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "deleted", "session_id": session_id}


@app.post("/api/knowledge/rebuild", response_model=KnowledgeRebuildResponse)
async def rebuild_knowledge():
    """Rebuild the vector index from knowledge files."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    result = vector_store.index_knowledge_files()
    return KnowledgeRebuildResponse(
        **result,
        message=f"Indexed {result['files_indexed']} files with {result['total_chunks']} chunks",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
