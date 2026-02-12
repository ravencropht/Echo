"""Main entry point for the application."""
import uvicorn

from app.config import config


def main():
    """Run the application."""
    uvicorn.run(
        "app.api.app:app",
        host=config.server.host,
        port=config.server.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
