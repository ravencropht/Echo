# Echo - Character Chat Agent

A RAG-based (Retrieval-Augmented Generation) chat application where you can converse with AI characters. The character's personality, knowledge, and speaking style are defined through text files.

## Features

- **Character-Driven Conversations**: AI responds in character based on profile definition
- **Knowledge Base Integration**: RAG system retrieves relevant context from knowledge files
- **Chat History**: Persistent conversation sessions
- **Local Embeddings**: Uses sentence-transformers for free offline operation
- **Simple Setup**: Minimal configuration required

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your LLM_API_KEY

# Run the application
python main.py
```

Visit `http://127.0.0.1:8000` to start chatting.

**To stop the application**: Press `Ctrl+C` in the terminal.

**To exit the virtual environment**: Run `deactivate`

## Requirements

- Python 3.10+
- Anthropic API key (for Claude LLM)
- 2GB+ RAM (for embedding model)

## Configuration

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

### Environment Variables

```bash
LLM_API_KEY=sk-ant-xxxxx              # Required: Anthropic API key
LLM_API_URL=https://api.anthropic.com # Optional: Custom API URL
LLM_MODEL=claude-3-haiku-20240307     # Optional: Model to use
```

## Project Structure

```
.
├── profile.txt              # Character definition
├── knowledge_*.txt          # Additional knowledge files
├── config.yaml              # Application configuration
├── .env                     # Environment variables (not in repo)
├── sessions/                # Chat history (auto-created)
├── app/                     # Application code
├── templates/               # HTML templates
└── static/                  # Static assets
```

## Character Setup

Create a `profile.txt` in the project root:

```
NAME: [Character Name]
PERSONALITY: [Traits, mannerisms, speaking style]
BACKGROUND: [History, world context]
RELATIONSHIPS: [Connections to others]
EXAMPLE_DIALOGUE: |
  [Sample quotes showing speech patterns]
```

Add additional knowledge files as `*.txt` in the project root. These will be automatically indexed on startup.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Chat UI |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/character` | Get character profile |
| `POST` | `/api/chat` | Send message |
| `GET` | `/api/sessions` | List sessions |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `POST` | `/api/knowledge/rebuild` | Rebuild vector index |

## License

MIT
