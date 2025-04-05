#!/usr/bin/env python
"""
Migration script to move model data from PostgreSQL to MongoDB.

This script:
1. Connects to both PostgreSQL and MongoDB databases
2. Reads model data from PostgreSQL
3. Writes model data to MongoDB
4. Optionally migrates usage statistics and other relevant data

Usage:
    python migrate_to_mongodb.py [--dry-run]
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.db.database import (
        init_db,
        get_pg_connection,
        release_pg_connection,
        get_mongo_db,
        save_model_info,
        log_model_usage,
    )
    from app.core.config import settings
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the indoxRouter_server directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("migration")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Migrate model data from PostgreSQL to MongoDB"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes to MongoDB",
    )
    return parser.parse_args()


def migrate_models(dry_run=False):
    """Migrate models from PostgreSQL to MongoDB."""
    logger.info("Starting model migration from PostgreSQL to MongoDB")

    try:
        conn = get_pg_connection()
        mongo_db = get_mongo_db()

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if models table exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'models'
                    )
                    """
                )
                if not cur.fetchone()["exists"]:
                    logger.warning(
                        "Models table does not exist in PostgreSQL. Nothing to migrate."
                    )
                    return False

                # Get all models from PostgreSQL
                cur.execute(
                    """
                    SELECT m.model_id, m.display_name, p.provider_id, 
                           m.capabilities, m.cost_per_1k_input_tokens, 
                           m.cost_per_1k_output_tokens, m.context_length, 
                           m.token_limit, m.created_at, m.updated_at
                    FROM models m
                    JOIN providers p ON m.provider_id = p.provider_id
                    WHERE m.is_enabled = TRUE
                    """
                )

                models = cur.fetchall()
                logger.info(f"Found {len(models)} models to migrate")

                for model in models:
                    # Convert capabilities from JSONB to list
                    capabilities = model["capabilities"]
                    if isinstance(capabilities, str):
                        # Try to convert string representation to list
                        if capabilities.startswith("[") and capabilities.endswith("]"):
                            capabilities = (
                                capabilities.strip("[]").replace('"', "").split(",")
                            )
                            capabilities = [c.strip() for c in capabilities]
                        else:
                            capabilities = [capabilities]

                    # Prepare pricing information
                    pricing = {
                        "input_tokens_per_1k": (
                            float(model["cost_per_1k_input_tokens"])
                            if model["cost_per_1k_input_tokens"]
                            else 0.0
                        ),
                        "output_tokens_per_1k": (
                            float(model["cost_per_1k_output_tokens"])
                            if model["cost_per_1k_output_tokens"]
                            else 0.0
                        ),
                    }

                    # Prepare metadata
                    metadata = {
                        "context_length": model["context_length"],
                        "migrated_from_postgres": True,
                        "migration_date": datetime.now().isoformat(),
                    }

                    # Log the migration
                    logger.info(
                        f"Migrating model: {model['provider_id']}/{model['model_id']}"
                    )

                    if not dry_run:
                        # Save to MongoDB
                        result = save_model_info(
                            provider=model["provider_id"],
                            name=model["model_id"],
                            capabilities=capabilities,
                            description=f"{model['display_name']} model by {model['provider_id']}",
                            max_tokens=model["token_limit"],
                            pricing=pricing,
                            metadata=metadata,
                        )

                        if result:
                            logger.info(
                                f"Successfully migrated model {model['model_id']} to MongoDB with ID: {result}"
                            )
                        else:
                            logger.error(
                                f"Failed to migrate model {model['model_id']} to MongoDB"
                            )

                logger.info("Model migration completed")
                return True
        finally:
            release_pg_connection(conn)

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False


def migrate_usage_data(dry_run=False):
    """Migrate usage statistics from PostgreSQL to MongoDB."""
    logger.info("Starting usage data migration from PostgreSQL to MongoDB")

    try:
        conn = get_pg_connection()

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if api_requests table exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'api_requests'
                    )
                    """
                )
                if not cur.fetchone()["exists"]:
                    logger.warning(
                        "API requests table does not exist in PostgreSQL. Skipping usage migration."
                    )
                    return False

                # Get usage data with a reasonable limit to avoid memory issues
                cur.execute(
                    """
                    SELECT 
                        user_id,
                        provider,
                        model,
                        tokens_input,
                        tokens_output,
                        cost,
                        duration_ms,
                        request_id,
                        created_at
                    FROM api_requests
                    WHERE created_at > NOW() - INTERVAL '30 days'
                    ORDER BY created_at DESC
                    LIMIT 10000
                    """
                )

                requests = cur.fetchall()
                logger.info(f"Found {len(requests)} recent API requests to migrate")

                migrated_count = 0
                for req in requests:
                    if not dry_run:
                        success = log_model_usage(
                            user_id=req["user_id"],
                            provider=req["provider"],
                            model=req["model"],
                            tokens_prompt=req["tokens_input"] or 0,
                            tokens_completion=req["tokens_output"] or 0,
                            cost=float(req["cost"]) if req["cost"] else 0.0,
                            latency=(
                                float(req["duration_ms"]) if req["duration_ms"] else 0.0
                            ),
                            request_id=req["request_id"],
                        )
                        if success:
                            migrated_count += 1

                if not dry_run:
                    logger.info(f"Successfully migrated {migrated_count} usage records")

                return True
        finally:
            release_pg_connection(conn)

    except Exception as e:
        logger.error(f"Error during usage data migration: {e}")
        return False


def main():
    """Main migration function."""
    args = parse_args()

    if args.dry_run:
        logger.info("Running in dry-run mode - no changes will be made")

    # Initialize database connections
    if not init_db():
        logger.error("Failed to initialize database connections. Exiting.")
        return 1

    # Migrate models
    models_migrated = migrate_models(dry_run=args.dry_run)
    if not models_migrated and not args.dry_run:
        logger.warning("Model migration failed or no models to migrate")

    # Migrate usage data
    usage_migrated = migrate_usage_data(dry_run=args.dry_run)
    if not usage_migrated and not args.dry_run:
        logger.warning("Usage data migration failed or no usage data to migrate")

    logger.info("Migration script completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
