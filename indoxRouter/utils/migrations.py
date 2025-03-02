#!/usr/bin/env python3
"""
Database migration utility for IndoxRouter.

This script provides commands for initializing and running database migrations.
"""

import os
import sys
import argparse
from pathlib import Path
import logging
import alembic.config
from alembic import command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent


def get_alembic_config():
    """Get the Alembic configuration."""
    alembic_cfg = alembic.config.Config(str(ROOT_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(ROOT_DIR / "migrations"))
    return alembic_cfg


def init():
    """Initialize the migrations directory."""
    alembic_cfg = get_alembic_config()
    command.init(alembic_cfg, str(ROOT_DIR / "migrations"))
    logger.info("Migrations directory initialized")


def create(message):
    """Create a new migration."""
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=True)
    logger.info(f"Migration created: {message}")


def upgrade(revision="head"):
    """Upgrade the database to the specified revision."""
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)
    logger.info(f"Database upgraded to: {revision}")


def downgrade(revision="-1"):
    """Downgrade the database to the specified revision."""
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    logger.info(f"Database downgraded to: {revision}")


def create_tables():
    """Create all tables directly without using migrations."""
    from indoxRouter.utils.database import Base, get_engine
    from indoxRouter.models.database import User, ApiKey, RequestLog, ProviderConfig

    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("All tables created")


def drop_tables():
    """Drop all tables directly without using migrations."""
    from indoxRouter.utils.database import Base, get_engine

    engine = get_engine()
    Base.metadata.drop_all(engine)
    logger.info("All tables dropped")


def create_admin_user():
    """Create an admin user if one doesn't exist."""
    from indoxRouter.utils.auth import AuthManager
    from indoxRouter.models.database import User
    from indoxRouter.utils.database import get_session

    auth_manager = AuthManager()
    session = get_session()

    try:
        # Check if admin user exists
        admin = session.query(User).filter(User.email == "admin@example.com").first()

        if not admin:
            # Create admin user
            user_id = auth_manager.create_user(
                email="admin@example.com",
                password="admin",
                first_name="Admin",
                last_name="User",
                is_admin=True,
            )

            if user_id:
                # Generate an API key for the admin user
                api_key, key_id = auth_manager.generate_api_key(
                    user_id=user_id, key_name="Admin API Key"
                )

                logger.info(f"Admin user created with API key: {api_key}")
            else:
                logger.error("Failed to create admin user")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
    finally:
        session.close()


def main():
    """Run the migration utility."""
    parser = argparse.ArgumentParser(
        description="IndoxRouter database migration utility"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init command
    subparsers.add_parser("init", help="Initialize the migrations directory")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade the database")
    upgrade_parser.add_argument(
        "--revision", default="head", help="Revision to upgrade to"
    )

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade the database")
    downgrade_parser.add_argument(
        "--revision", default="-1", help="Revision to downgrade to"
    )

    # Create tables command
    subparsers.add_parser("create_tables", help="Create all tables directly")

    # Drop tables command
    subparsers.add_parser("drop_tables", help="Drop all tables directly")

    # Create admin user command
    subparsers.add_parser("create_admin", help="Create an admin user")

    args = parser.parse_args()

    if args.command == "init":
        init()
    elif args.command == "create":
        create(args.message)
    elif args.command == "upgrade":
        upgrade(args.revision)
    elif args.command == "downgrade":
        downgrade(args.revision)
    elif args.command == "create_tables":
        create_tables()
    elif args.command == "drop_tables":
        drop_tables()
    elif args.command == "create_admin":
        create_admin_user()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
