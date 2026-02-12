"""Session storage service."""
import json
from pathlib import Path
from typing import List, Optional

from app.config import config
from app.models.session import Session


class SessionStore:
    """Service for storing and retrieving chat sessions."""

    def __init__(self):
        """Initialize the session store."""
        self.sessions_dir = config.get_sessions_dir()

    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a session.

        Args:
            session_id: Session ID

        Returns:
            Path to session file
        """
        return self.sessions_dir / f"{session_id}.json"

    def save(self, session: Session) -> None:
        """Save a session to disk.

        Args:
            session: Session to save
        """
        path = self._get_session_path(session.session_id)
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load(self, session_id: str) -> Optional[Session]:
        """Load a session from disk.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        path = self._get_session_path(session_id)
        if not path.exists():
            return None

        with open(path) as f:
            data = json.load(f)
        return Session.from_dict(data)

    def delete(self, session_id: str) -> bool:
        """Delete a session from disk.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        path = self._get_session_path(session_id)
        if not path.exists():
            return False

        path.unlink()
        return True

    def list_all(self) -> List[dict]:
        """List all sessions.

        Returns:
            List of session summaries (id, created_at, message_count)
        """
        sessions = []

        for path in self.sessions_dir.glob("*.json"):
            with open(path) as f:
                data = json.load(f)
            sessions.append({
                "session_id": data["session_id"],
                "created_at": data["created_at"],
                "message_count": len(data.get("messages", [])),
            })

        # Sort by creation time, newest first
        sessions.sort(key=lambda s: s["created_at"], reverse=True)
        return sessions

    def get_or_create(self, session_id: Optional[str]) -> Session:
        """Get an existing session or create a new one.

        Args:
            session_id: Optional session ID

        Returns:
            Session instance
        """
        if session_id:
            session = self.load(session_id)
            if session:
                return session

        return Session.create()
