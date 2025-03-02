#!/usr/bin/env python3
"""
Dashboard demo script.

This script demonstrates how to use the IndoxRouter dashboard.
"""

import os
import sys
import argparse

# Add the parent directory to the path to import from indoxRouter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dashboard import Dashboard


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the IndoxRouter dashboard demo")
    parser.add_argument(
        "--port", type=int, default=7860, help="Port to run the dashboard on"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    return parser.parse_args()


def main():
    """Run the dashboard demo."""
    args = parse_args()

    # Print startup message
    print("=" * 80)
    print("IndoxRouter Dashboard Demo")
    print("=" * 80)
    print("\nThis demo shows how to use the IndoxRouter dashboard.")
    print("The dashboard allows you to:")
    print("- Generate and manage API keys")
    print("- Test completions with different providers and models")
    print("- Check the security of your configuration")
    print("\nDefault login credentials:")
    print("- Username: admin")
    print("- Password: admin")
    print("\nStarting the dashboard on http://localhost:%d" % args.port)
    print("=" * 80)

    # Create and run the dashboard
    dashboard = Dashboard()

    # Add some example API keys for demonstration
    dashboard.current_user = {
        "id": "admin",
        "name": "Administrator",
        "email": "admin@example.com",
    }
    dashboard.generate_key()
    dashboard.generate_key()

    # Reset the current user so the user has to login
    dashboard.current_user = None

    # Run the dashboard
    dashboard.run(port=args.port)


if __name__ == "__main__":
    main()
