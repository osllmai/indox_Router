#!/usr/bin/env python
"""
Helper script to start both the IndoxRouter server and dashboard.

This script:
1. Starts the server with docker-compose
2. Starts the dashboard with streamlit
"""

import os
import sys
import subprocess
import time
import signal
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("indoxrouter-starter")


def start_server():
    """Start the IndoxRouter server with docker-compose."""
    try:
        logger.info("Starting IndoxRouter server with docker-compose...")

        # Change to the server directory
        server_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "indoxRouter_server"
        )

        # Run docker-compose
        cmd = ["docker-compose", "up", "-d"]

        # Start the process
        server_process = subprocess.Popen(
            cmd,
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Wait for the process to complete
        stdout, stderr = server_process.communicate()

        # Log the output
        logger.info(stdout)
        if stderr:
            logger.error(stderr)

        # Check exit code
        if server_process.returncode != 0:
            logger.error(
                f"Failed to start server: Exit code {server_process.returncode}"
            )
            return False

        logger.info("Server started successfully")
        return True
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False


def start_dashboard():
    """Start the IndoxRouter dashboard with streamlit."""
    try:
        logger.info("Starting IndoxRouter dashboard with streamlit...")

        # Change to the dashboard directory
        dashboard_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "indoxRouter_dashboard"
        )

        # Run streamlit
        cmd = [
            "streamlit",
            "run",
            "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
        ]

        # Start the process
        dashboard_process = subprocess.Popen(
            cmd,
            cwd=dashboard_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Set up signal handlers to shut down the dashboard
        def signal_handler(sig, frame):
            logger.info("Stopping dashboard...")
            dashboard_process.terminate()

            # Stop the server
            stop_server()

            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Print the startup message
        logger.info("Dashboard started at http://localhost:8501")

        # Wait for the process to complete
        while dashboard_process.poll() is None:
            # Read and print output
            stdout_line = dashboard_process.stdout.readline()
            if stdout_line:
                print(stdout_line.strip())

            stderr_line = dashboard_process.stderr.readline()
            if stderr_line:
                print(f"ERROR: {stderr_line.strip()}", file=sys.stderr)

            # Sleep a bit to avoid high CPU usage
            time.sleep(0.1)

        # Check exit code
        exit_code = dashboard_process.returncode
        if exit_code != 0:
            logger.error(f"Dashboard exited with code {exit_code}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        return False


def stop_server():
    """Stop the IndoxRouter server with docker-compose."""
    try:
        logger.info("Stopping IndoxRouter server...")

        # Change to the server directory
        server_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "indoxRouter_server"
        )

        # Run docker-compose down
        cmd = ["docker-compose", "down"]

        # Start the process
        process = subprocess.Popen(
            cmd,
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Wait for the process to complete
        stdout, stderr = process.communicate()

        # Log the output
        logger.info(stdout)
        if stderr:
            logger.error(stderr)

        # Check exit code
        if process.returncode != 0:
            logger.error(f"Failed to stop server: Exit code {process.returncode}")
            return False

        logger.info("Server stopped successfully")
        return True
    except Exception as e:
        logger.error(f"Error stopping server: {e}")
        return False


def main():
    """Main function."""
    logger.info("Starting IndoxRouter components")

    # Start the server
    server_started = start_server()
    if not server_started:
        logger.error("Failed to start server. Exiting.")
        return 1

    # Wait for the server to be fully up
    logger.info("Waiting for server to start...")
    time.sleep(10)  # Wait 10 seconds for the server to initialize

    # Start the dashboard
    dashboard_started = start_dashboard()
    if not dashboard_started:
        logger.error("Failed to start dashboard. Stopping server and exiting.")
        stop_server()
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_server()
        sys.exit(0)
