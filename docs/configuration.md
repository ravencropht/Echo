# Configuration Guide

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Required

```bash
LLM_API_KEY=sk-ant-xxxxx
```

Your Anthropic API key. Get one from https://console.anthropic.com/

### Optional

```bash
LLM_API_URL=https://api.anthropic.com
LLM_MODEL=claude-3-haiku-20240307
```

- `LLM_API_URL`: Custom API endpoint URL (for proxies or custom deployments)
- `LLM_MODEL`: Claude model to use. Options:
  - `claude-3-haiku-20240307` - Fastest, most cost-effective
  - `claude-3-5-sonnet-20241022` - Balanced
  - `claude-3-opus-20240229` - Highest quality

## config.yaml

The `config.yaml` file controls application settings:

### Server

```yaml
server:
  host: "127.0.0.1"
  port: 8000
```

- `host`: Address to bind to
- `port`: Port to listen on

### Embedding

```yaml
embedding:
  model: "all-MiniLM-L6-v2"
  chunk_size: 500
  chunk_overlap: 50
```

- `model`: sentence-transformers model for embeddings
- `chunk_size`: Maximum characters per text chunk
- `chunk_overlap`: Overlapping characters between chunks

### RAG

```yaml
rag:
  top_k: 3
  min_similarity: 0.6
```

- `top_k`: Number of documents to retrieve for context
- `min_similarity`: Minimum similarity threshold (0-1) for including documents

### Paths

```yaml
paths:
  profile: "profile.txt"
  knowledge_dir: "."
  sessions_dir: "sessions"
  chroma_db: ".chroma_db"
```

- `profile`: Path to character profile file
- `knowledge_dir`: Directory containing knowledge files
- `sessions_dir`: Directory for chat history
- `chroma_db`: Directory for ChromaDB storage

## Character Profile Format

Your `profile.txt` should follow this format:

```
NAME: Character Name

PERSONALITY: Detailed description of personality traits, mannerisms, and speaking style.

BACKGROUND: Character history, world context, and important events.

RELATIONSHIPS: |
  Connection 1: Description
  Connection 2: Description

EXAMPLE_DIALOGUE: |
  "Sample quote 1 showing speech patterns."
  "Sample quote 2 demonstrating how they speak."
```

## Knowledge Files

Place additional knowledge files as `*.txt` in the project root (or configured `knowledge_dir`). These files will be:

1. Automatically detected on startup
2. Chunked according to `embedding.chunk_size`
3. Embedded and stored in ChromaDB
4. Retrieved during conversations based on semantic similarity

After adding new knowledge files, rebuild the index:

```bash
curl -X POST http://localhost:8000/api/knowledge/rebuild
```

Or use the API from your application.

## Tips

### Better Character Responses

1. **Detailed PERSONALITY**: Include specific speaking patterns, catchphrases, and mannerisms
2. **Rich EXAMPLE_DIALOGUE**: Provide 3-5 examples showing different moods/situations
3. **Comprehensive BACKGROUND**: Include formative experiences and world knowledge

### Better Knowledge Retrieval

1. **Chunk Size**: Smaller chunks (300-500) are more precise but may miss context
2. **Top K**: Higher values (5-10) provide more context but may increase noise
3. **Similarity Threshold**: Lower values (0.5-0.6) include more diverse results

### Performance

- Use `claude-3-haiku-20240307` for fastest responses
- Reduce `top_k` to 2-3 for faster retrieval
- Set `chunk_overlap` to 0 for faster indexing
