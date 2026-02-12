# Use Debian slim base image (better for PyTorch/ChromaDB compatibility)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY static ./static
COPY templates ./templates
COPY character ./character
COPY config.yaml .
COPY main.py .

# Create directories for persistent data
RUN mkdir -p sessions .chroma_db

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
