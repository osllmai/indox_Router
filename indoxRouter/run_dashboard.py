#!/usr/bin/env python3
"""
Run the IndoxRouter dashboard.

This script launches a Gradio dashboard for testing the IndoxRouter application.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import the Dashboard class from indoxRouter package
from indoxRouter.utils.dashboard import Dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "dashboard.log"), mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Run the dashboard."""
    parser = argparse.ArgumentParser(description="Run the IndoxRouter Dashboard")
    parser.add_argument("--host", help="Host to bind the server to")
    parser.add_argument("--port", type=int, help="Port to bind the server to")
    parser.add_argument("--share", action="store_true", help="Create a public URL")
    args = parser.parse_args()

    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Get the host and port from arguments, environment variables, or use defaults
        host = args.host or os.environ.get("DASHBOARD_HOST", "0.0.0.0")
        port = args.port or int(os.environ.get("DASHBOARD_PORT", "7860"))
        share = (
            args.share or os.environ.get("DASHBOARD_SHARE", "false").lower() == "true"
        )

        # Create and run the dashboard
        logger.info(f"Starting IndoxRouter Dashboard on {host}:{port} (share={share})")
        dashboard = Dashboard()
        dashboard.run(host=host, port=port, share=share)
    except Exception as e:
        logger.error(f"Error running IndoxRouter Dashboard: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
