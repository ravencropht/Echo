# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Echo is a single-character chat application using RAG (Retrieval-Augmented Generation). The AI character responds based on a `profile.txt` and additional knowledge files, with personality and speaking style consistent with the character definition.

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: HTML + JavaScript + HTMX (no build step)
- **Vector Store**: ChromaDB (embedded, persistent)
- **Embeddings**: sentence-transformers `all-MiniLM-L6-v2` (local)
- **LLM**: Anthropic Claude API only

## Environment Variables

Required:
```bash
LLM_API_KEY=sk-ant-xxxxx              # Anthropic API key
LLM_API_URL=https://api.anthropic.com # Anthropic API URL
LLM_MODEL=claude-3-haiku-20240307     # Model to use
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Rebuild vector index after adding/modifying knowledge files
curl -X POST http://localhost:8000/api/knowledge/rebuild
```

## Architecture

```
Browser → FastAPI → Service Layer → (RAG + LLM) → Anthropic API
                    ↓
              ChromaDB (local)    +    profile.txt + *.txt (knowledge)
```

### Service Layer Components

- **Character Manager**: Parses `profile.txt` and builds character-specific system prompts
- **RAG Service**: Handles embedding generation, vector similarity search, and context retrieval
- **Conversation Manager**: Manages chat history stored in `sessions/*.json`
- **LLM Service**: Anthropic Claude client for generating responses

### Data Flow

1. User sends message via `/api/chat`
2. RAG retrieves relevant context from knowledge files using ChromaDB
3. Character profile + retrieved context builds system prompt
4. LLM generates character-style response
5. Message appended to session history

## File Structure

```
.
├── profile.txt          # Character definition (NAME, PERSONALITY, BACKGROUND, etc.)
├── knowledge*.txt       # Additional context files for RAG
├── sessions/            # Chat history (JSON)
└── config.yaml          # Server, embedding, and RAG settings
```

### Profile.txt Format

```
NAME: [Character Name]
PERSONALITY: [Traits, mannerisms, speaking style]
BACKGROUND: [History, world context]
RELATIONSHIPS: [Connections to others]
EXAMPLE_DIALOGUE: |
  [Sample quotes showing speech patterns]
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serve chat UI |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/character` | Get character profile |
| `POST` | `/api/chat` | Send message, get response |
| `GET` | `/api/sessions` | List chat sessions |
| `GET` | `/api/sessions/{id}` | Get session history |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `POST` | `/api/knowledge/rebuild` | Rebuild vector index |

## Design Document

Full system architecture details in `docs/design.md`.
