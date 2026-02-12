"""Application configuration."""
import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PathsConfig(BaseModel):
    """Paths configuration."""

    profile: str = "profile.txt"
    knowledge_dir: str = "."
    sessions_dir: str = "sessions"
    chroma_db: str = ".chroma_db"


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = "127.0.0.1"
    port: int = 8000


class EmbeddingConfig(BaseModel):
    """Embedding configuration."""

    model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50


class RAGConfig(BaseModel):
    """RAG configuration."""

    top_k: int = 3
    min_similarity: float = 0.6


class Settings(BaseSettings):
    """Application settings from environment variables."""

    llm_api_key: str
    llm_api_url: str = "https://api.anthropic.com"
    llm_model: str = "claude-3-haiku-20240307"

    model_config = {"env_file": ".env"}


class Config:
    """Main application configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file and environment."""
        self.project_root = Path(__file__).parent.parent

        # Load YAML config
        if config_path is None:
            config_path = self.project_root / "config.yaml"

        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)

        self.server = ServerConfig(**yaml_config.get("server", {}))
        self.embedding = EmbeddingConfig(**yaml_config.get("embedding", {}))
        self.rag = RAGConfig(**yaml_config.get("rag", {}))
        self.paths = PathsConfig(**yaml_config.get("paths", {}))

        # Load environment settings
        self.settings = Settings()

    def get_profile_path(self) -> Path:
        """Get the full path to the profile file."""
        return self.project_root / self.paths.profile

    def get_knowledge_dir(self) -> Path:
        """Get the full path to the knowledge directory."""
        return self.project_root / self.paths.knowledge_dir

    def get_sessions_dir(self) -> Path:
        """Get the full path to the sessions directory."""
        path = self.project_root / self.paths.sessions_dir
        path.mkdir(exist_ok=True)
        return path

    def get_chroma_db_path(self) -> Path:
        """Get the full path to the ChromaDB storage."""
        return self.project_root / self.paths.chroma_db


# Global config instance
config = Config()
