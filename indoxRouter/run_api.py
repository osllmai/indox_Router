#!/usr/bin/env python3
"""
Run the IndoxRouter FastAPI application.
"""

import os
import sys
import logging
import uvicorn
import argparse
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "api.log"), mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI application."""
    parser = argparse.ArgumentParser(description="Run the IndoxRouter API")
    parser.add_argument("--host", help="Host to bind the server to")
    parser.add_argument("--port", type=int, help="Port to bind the server to")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument("--workers", type=int, help="Number of worker processes")
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level",
    )
    args = parser.parse_args()

    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Get the host and port from arguments, environment variables, or use defaults
        host = args.host or os.environ.get("INDOXROUTER_HOST", "0.0.0.0")
        port = args.port or int(os.environ.get("INDOXROUTER_PORT", "8000"))
        reload = (
            args.reload
            or os.environ.get("INDOXROUTER_RELOAD", "false").lower() == "true"
        )
        workers = args.workers or int(os.environ.get("INDOXROUTER_WORKERS", "1"))
        log_level = (
            args.log_level or os.environ.get("INDOXROUTER_LOG_LEVEL", "info").lower()
        )

        # Run the application
        logger.info(f"Starting IndoxRouter API on {host}:{port} with {workers} workers")
        uvicorn.run(
            "indoxRouter.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
        )
    except Exception as e:
        logger.error(f"Error running IndoxRouter API: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
