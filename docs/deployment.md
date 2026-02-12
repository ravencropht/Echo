# Deployment Guide

## Local Development

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API key

# Run development server
python main.py
```

### With Environment Variables in Command

```bash
# Activate venv first
source venv/bin/activate

# Run with environment variables
LLM_API_KEY="your-key" LLM_API_URL="your-url" LLM_MODEL="your-model" python main.py
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.api.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --access-logfile - \
  --error-logfile -
```

### Using systemd

Create `/etc/systemd/system/easy-rag.service`:

```ini
[Unit]
Description=Echo Character Chat
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/easy-rag
Environment="LLM_API_KEY=your_api_key"
Environment="LLM_MODEL=claude-3-haiku-20240307"
ExecStart=/path/to/venv/bin/gunicorn app.api.app:app --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable easy-rag
sudo systemctl start easy-rag
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `.dockerignore`:

```
sessions/
.chroma_db/
__pycache__/
*.pyc
.env
.venv/
```

Build and run:

```bash
docker build -t easy-rag .
docker run -d -p 8000:8000 \
  -e LLM_API_KEY=your_api_key \
  -v $(pwd)/sessions:/app/sessions \
  -v $(pwd)/.chroma_db:/app/.chroma_db \
  easy-rag
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_API_URL=${LLM_API_URL:-https://api.anthropic.com}
      - LLM_MODEL=${LLM_MODEL:-claude-3-haiku-20240307}
    volumes:
      - ./sessions:/app/sessions
      - ./.chroma_db:/app/.chroma_db
      - ./profile.txt:/app/profile.txt
      - ./knowledge:/app/knowledge
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

### Nginx Reverse Proxy

Configure Nginx:

```nginx
server {
    listen 80;
    server_name chat.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **API Keys**: Never commit `.env` to version control
2. **CORS**: In production, set specific allowed origins in `app/api/app.py`
3. **Rate Limiting**: Consider adding rate limiting for public deployments
4. **HTTPS**: Use HTTPS in production with a valid certificate

## Environment-Specific Configs

### Development
```bash
LLM_MODEL=claude-3-haiku-20240307  # Faster, cheaper
```

### Production
```bash
LLM_MODEL=claude-3-5-sonnet-20241022  # Better quality
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok",
  "vector_db_initialized": true,
  "character_loaded": true
}
```

### Logs

For Docker:
```bash
docker-compose logs -f app
```

For systemd:
```bash
journalctl -u easy-rag -f
```

## Troubleshooting

### Vector store issues

Rebuild the index:
```bash
curl -X POST http://localhost:8000/api/knowledge/rebuild
```

### Memory issues

Reduce workers in gunicorn or use a smaller model:
```bash
gunicorn app.api.app:app --workers 2
```

### Character not loading

Check that `profile.txt` exists and is properly formatted.
