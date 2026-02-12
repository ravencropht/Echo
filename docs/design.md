# System Architecture: Echo - Character Chat Agent

## Requirements

### Functional Requirements
- **Chat Interface**: Web-based chat UI for conversing with an AI character
- **Character Profile**: Load character information from `profile.txt` containing personality, background, and style
- **Knowledge Base**: RAG system using additional text files in a folder as character knowledge
- **Character-Style Responses**: AI responds in the character's distinctive voice and personality
- **Chat History**: Persist conversation history for context continuity

### Non-Functional Requirements
- **Performance**: Sub-3 second response time for RAG retrieval + generation
- **Simplicity**: Minimal setup, suitable for personal project deployment
- **Offline Capable**: Local embedding models option for full offline operation

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              User Browser                                │
│                      ┌──────────────────────┐                           │
│                      │   Chat UI (HTML/JS)   │                           │
│                      └──────────┬───────────┘                           │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │ HTTP
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Backend Server                                 │
│                        (Python FastAPI)                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     API Layer                                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │   │
│  │  │  Health  │  │  Chat    │  │ Knowledge│                      │   │
│  │  │  Check   │  │  Endpoint│  │  Rebuild │                      │   │
│  │  └──────────┘  └──────────┘  └──────────┘                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Service Layer                                │   │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐        │   │
│  │  │   Character Manager     │  │    RAG Service          │        │   │
│  │  │ - Load profile.txt      │  │ - Embedding generation  │        │   │
│  │  │ - Parse character data  │  │ - Vector similarity      │        │   │
│  │  │ - Build system prompt   │  │ - Context retrieval     │        │   │
│  │  └─────────────────────────┘  └─────────────────────────┘        │   │
│  │                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │              Conversation Manager                        │    │   │
│  │  │ - Message history                                       │    │   │
│  │  │ - Context window management                             │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         LLM Service                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │              Anthropic Claude Client                     │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Anthropic    │         │  Vector Store │         │ File System   │
│  Claude API   │         │   (ChromaDB)  │         │ - profile.txt  │
│               │         │               │         │ - *.txt (KB)   │
│  (LLM_API_URL)│         │  (Local file) │         │ - sessions/    │
└───────────────┘         └───────────────┘         └───────────────┘
```

---

## Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Backend Framework** | Python + FastAPI | Minimal boilerplate, async support, great for AI/ML integrations, built-in OpenAPI docs |
| **Frontend** | HTML + JavaScript + HTMX | No build step required, simple for personal projects, lightweight |
| **Vector Store** | ChromaDB | Pure Python, embedded, persistent storage, no separate database server needed |
| **Embedding Model** | sentence-transformers (local) | Local `all-MiniLM-L6-v2` for free offline operation |
| **LLM Provider** | Anthropic Claude | Configured via `LLM_API_KEY` and `LLM_API_URL` env vars |
| **Chat History** | JSON files on disk | Simple persistence, no database overhead |
| **Configuration** | YAML / TOML | Human-readable, easy to modify |
| **Styling** | Tailwind CSS (CDN) | Rapid UI development without build tools |

---

## Data Model

### File Structure
```
.
├── profile.txt          # Main character definition
├── knowledge1.txt       # Additional context
├── knowledge2.txt
├── ...
└── sessions/            # Chat history (JSON files)
    └── {session_id}.json
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

### Chat History Structure
```json
{
  "session_id": "uuid",
  "character": "character_name",
  "created_at": "2025-01-10T12:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Hello!",
      "timestamp": "2025-01-10T12:00:01Z"
    },
    {
      "role": "assistant",
      "content": "Well, greetings there, friend!",
      "timestamp": "2025-01-10T12:00:03Z"
    }
  ]
}
```

### Configuration Structure
```yaml
server:
  host: "127.0.0.1"
  port: 8000

embedding:
  model: "all-MiniLM-L6-v2"
  chunk_size: 500
  chunk_overlap: 50

rag:
  top_k: 3
  min_similarity: 0.6
```

**Environment Variables:**
```bash
LLM_API_KEY=sk-ant-xxxxx
LLM_API_URL=https://api.anthropic.com
LLM_MODEL=claude-3-haiku-20240307
```

---

## API Design

### Endpoints

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

### Chat Request/Response

**Request:**
```json
POST /api/chat
{
  "message": "Tell me about yourself",
  "session_id": "optional-uuid-or-null"
}
```

**Response:**
```json
{
  "response": "I am the character...",
  "session_id": "uuid",
  "sources": [
    {"file": "profile.txt", "relevance": 0.95},
    {"file": "knowledge1.txt", "relevance": 0.82}
  ],
  "timestamp": "2025-01-10T12:00:05Z"
}
```

---

## Implementation Tasks

```json
{
  "project": "Echo - Character Chat Agent",
  "tasks": [
    {
      "id": "T001",
      "title": "Project scaffolding and configuration",
      "description": "Set up project structure, virtual environment, dependencies, and configuration files",
      "priority": "high",
      "estimatedComplexity": "simple",
      "dependencies": [],
      "category": "backend",
      "deliverables": ["project structure", "requirements.txt", "config.yaml", ".env.example"],
      "acceptanceCriteria": ["Virtual environment created", "All dependencies installable", "Config file loads correctly"]
    },
    {
      "id": "T002",
      "title": "Character profile parser",
      "description": "Implement parser for profile.txt",
      "priority": "high",
      "estimatedComplexity": "simple",
      "dependencies": ["T001"],
      "category": "backend",
      "deliverables": ["Character model", "Profile parser"],
      "acceptanceCriteria": ["Can parse profile.txt", "Returns character data structure"]
    },
    {
      "id": "T003",
      "title": "Embedding service and vector store",
      "description": "Create document chunking, embedding generation, and vector storage using ChromaDB",
      "priority": "high",
      "estimatedComplexity": "moderate",
      "dependencies": ["T001"],
      "category": "backend",
      "deliverables": ["Embedding service", "Document chunker", "ChromaDB manager"],
      "acceptanceCriteria": ["Can chunk text files", "Generates embeddings locally", "Stores and retrieves vectors", "Similarity search works"]
    },
    {
      "id": "T004",
      "title": "RAG pipeline implementation",
      "description": "Combine character profile + retrieved context into system prompt for LLM",
      "priority": "high",
      "estimatedComplexity": "moderate",
      "dependencies": ["T002", "T003"],
      "category": "backend",
      "deliverables": ["RAG service", "Prompt builder", "Context manager"],
      "acceptanceCriteria": ["Retrieves relevant docs", "Builds character-specific prompts", "Includes sources in response"]
    },
    {
      "id": "T005",
      "title": "LLM service implementation",
      "description": "Implement Anthropic Claude client using LLM_API_KEY and LLM_API_URL env vars",
      "priority": "high",
      "estimatedComplexity": "simple",
      "dependencies": ["T001"],
      "category": "backend",
      "deliverables": ["Anthropic Claude client", "Message formatting"],
      "acceptanceCriteria": ["Connects to Claude API", "Handles streaming and non-streaming responses", "Error handling works"]
    },
    {
      "id": "T006",
      "title": "Chat history management",
      "description": "Implement session-based chat history with JSON file persistence",
      "priority": "medium",
      "estimatedComplexity": "simple",
      "dependencies": ["T001"],
      "category": "backend",
      "deliverables": ["Session model", "History storage service", "Session manager"],
      "acceptanceCriteria": ["Creates new sessions", "Appends messages to history", "Loads existing sessions", "Handles context window limits"]
    },
    {
      "id": "T007",
      "title": "FastAPI application and endpoints",
      "description": "Build REST API with all chat endpoints",
      "priority": "high",
      "estimatedComplexity": "moderate",
      "dependencies": ["T004", "T005", "T006"],
      "category": "backend",
      "deliverables": ["FastAPI app", "All API endpoints", "Request/response models", "CORS middleware"],
      "acceptanceCriteria": ["All endpoints defined", "OpenAPI docs generated", "CORS configured", "Request validation works"]
    },
    {
      "id": "T008",
      "title": "Chat UI frontend",
      "description": "Create responsive chat interface with HTML, HTMX, and Tailwind CSS",
      "priority": "high",
      "estimatedComplexity": "moderate",
      "dependencies": ["T007"],
      "category": "frontend",
      "deliverables": ["HTML template", "Chat UI styles", "Message display", "Input form"],
      "acceptanceCriteria": ["Can send messages", "Displays responses", "Responsive design", "Shows character info"]
    },
    {
      "id": "T009",
      "title": "Knowledge base rebuild endpoint",
      "description": "Admin endpoint to rebuild vector index when adding new documents",
      "priority": "medium",
      "estimatedComplexity": "simple",
      "dependencies": ["T003", "T007"],
      "category": "backend",
      "deliverables": ["Rebuild endpoint", "Index invalidation", "Progress feedback"],
      "acceptanceCriteria": ["Can rebuild index", "Clears old data", "Re-indexes all files", "Returns completion status"]
    },
    {
      "id": "T010",
      "title": "Sample character creation",
      "description": "Create example character with complete profile.txt and knowledge files",
      "priority": "low",
      "estimatedComplexity": "simple",
      "dependencies": ["T002"],
      "category": "testing",
      "deliverables": ["Sample profile.txt", "Test knowledge files", "Documentation"],
      "acceptanceCriteria": ["Has complete profile.txt", "Has additional knowledge files", "Shows distinctive speaking style"]
    },
    {
      "id": "T011",
      "title": "Testing and validation",
      "description": "Unit tests for core services, integration tests for chat flow",
      "priority": "medium",
      "estimatedComplexity": "moderate",
      "dependencies": ["T007", "T008"],
      "category": "testing",
      "deliverables": ["Unit tests", "Integration tests", "Test fixtures"],
      "acceptanceCriteria": ["Core services tested", "Chat flow tested", "Coverage report available"]
    },
    {
      "id": "T012",
      "title": "Documentation and deployment guide",
      "description": "README with setup instructions, usage guide, and deployment options",
      "priority": "low",
      "estimatedComplexity": "simple",
      "dependencies": ["T011"],
      "category": "devops",
      "deliverables": ["README.md", "CONFIGURATION.md", "DEPLOYMENT.md"],
      "acceptanceCriteria": ["Clear setup instructions", "Configuration documented", "Deployment options explained"]
    }
  ],
  "phases": [
    {
      "name": "Phase 1: Foundation",
      "tasks": ["T001", "T002", "T003"],
      "description": "Set up project structure, character parsing, and vector storage"
    },
    {
      "name": "Phase 2: Core AI Pipeline",
      "tasks": ["T004", "T005", "T006"],
      "description": "Build RAG pipeline, LLM integration, and session management"
    },
    {
      "name": "Phase 3: API and UI",
      "tasks": ["T007", "T008"],
      "description": "Create REST API and chat interface"
    },
    {
      "name": "Phase 4: Polish",
      "tasks": ["T009", "T010", "T011", "T012"],
      "description": "Add admin features, create examples, test, and document"
    }
  ]
}
```

---

## Considerations

### Security
- **API Key Management**: Store keys in environment variables, never commit to repo
- **Input Sanitization**: Validate all file paths to prevent directory traversal
- **Rate Limiting**: Optional rate limiting to prevent abuse if exposed publicly
- **CORS**: Configure appropriately for deployment context

### Scalability
- **Current Design**: Optimized for personal use (single user, low concurrency)
- **Future Scaling Paths**:
  - Add Redis for session storage
  - Migrate to PostgreSQL for chat history
  - Use dedicated vector database (Qdrant, Milvus)
  - Add caching layer for frequent queries
  - Deploy behind Gunicorn with multiple workers

### Trade-offs
| Decision | Trade-off | Rationale |
|----------|-----------|-----------|
| JSON file storage vs Database | Less scalable but simpler | Personal project scale, easier to inspect/debug |
| Local embeddings vs API | Free but lower quality vs paid but better | Cost-effective for personal use, still adequate |
| HTMX vs React framework | Less features but faster development | Single developer, personal project |
| Single character vs Multiple | Less flexible but simpler | Focused use case, easier setup |
| Anthropic-only vs Multi-provider | Less flexible but simpler | Single LLM provider reduces complexity |

### Future Enhancements
- **Streaming Responses**: Add SSE endpoint for real-time typing effect
- **Multi-turn Context**: Improved conversation history management
- **Character Memory**: Long-term memory of facts shared during conversation
- **Voice Interface**: Add speech-to-text and text-to-speech
- **Character Training**: Fine-tune models on specific character dialogue
