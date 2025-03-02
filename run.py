#!/usr/bin/env python3
"""
Main entry point for running the IndoxRouter application.

This script can run both the API and dashboard, or either one individually.
"""

import os
import sys
import argparse
import logging
import subprocess
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "run.log"), mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def run_api():
    """Run the FastAPI application."""
    try:
        logger.info("Starting API server...")
        from indoxRouter.main import app
        import uvicorn

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Error starting API server: {e}", exc_info=True)
        sys.exit(1)


def run_dashboard():
    """Run the Gradio dashboard."""
    try:
        logger.info("Starting dashboard...")
        from indoxRouter.utils.dashboard import Dashboard

        dashboard = Dashboard()
        dashboard.run()
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Parse arguments and run the application."""
    parser = argparse.ArgumentParser(description="Run the IndoxRouter application")
    parser.add_argument(
        "--api-only", action="store_true", help="Run only the API server"
    )
    parser.add_argument(
        "--dashboard-only", action="store_true", help="Run only the dashboard"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode with more verbose logging",
    )
    args = parser.parse_args()

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Run API only
    if args.api_only:
        logger.info("Running API only")
        run_api()
        return

    # Run dashboard only
    if args.dashboard_only:
        logger.info("Running dashboard only")
        run_dashboard()
        return

    # Run both API and dashboard
    logger.info("Running both API and dashboard")

    # Start API in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Wait for API to start
    logger.info("Waiting for API to start...")
    time.sleep(2)

    # Run dashboard in the main thread
    run_dashboard()


if __name__ == "__main__":
    main()
