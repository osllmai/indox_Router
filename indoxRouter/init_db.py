#!/usr/bin/env python3
"""
Initialize the database for IndoxRouter.

This script creates the database tables and an admin user.
"""

import os
import sys
import logging
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
        logging.FileHandler(os.path.join("logs", "init_db.log"), mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    parser = argparse.ArgumentParser(description="Initialize the IndoxRouter database")
    parser.add_argument(
        "--force", action="store_true", help="Force initialization even if tables exist"
    )
    parser.add_argument("--admin-email", help="Admin user email")
    parser.add_argument("--admin-password", help="Admin user password")
    args = parser.parse_args()

    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Import here to avoid circular imports
        from indoxRouter.utils.migrations import create_tables, create_admin_user

        # Create the tables
        logger.info("Creating database tables...")
        create_tables(force=args.force)

        # Create the admin user
        admin_email = args.admin_email or os.environ.get(
            "ADMIN_EMAIL", "admin@example.com"
        )
        admin_password = args.admin_password or os.environ.get(
            "ADMIN_PASSWORD", "admin"
        )

        logger.info(f"Creating admin user with email: {admin_email}")
        create_admin_user(email=admin_email, password=admin_password)

        logger.info("Database initialization complete.")
        logger.info("You can now log in with the following credentials:")
        logger.info(f"Email: {admin_email}")
        logger.info(f"Password: {admin_password}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
