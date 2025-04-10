#!/usr/bin/env python3
"""
Script to reset the IndoxRouter databases.
This will clear all user data, API keys, transactions, and other data from both PostgreSQL and MongoDB.
"""

import os
import sys
import logging
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("db-reset")

# Load environment variables
load_dotenv()

# Database settings from config if possible
try:
    from app.core.config import settings

    POSTGRES_URI = settings.DATABASE_URL or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgrespassword@localhost:5433/indoxrouter",
    )
    MONGODB_URI = settings.MONGODB_URI or os.getenv(
        "MONGODB_URI", "mongodb://localhost:27018/indoxrouter"
    )
    MONGODB_DATABASE = settings.MONGODB_DATABASE or os.getenv(
        "MONGODB_DATABASE", "indoxrouter"
    )
except ImportError:
    # Fallback if app config is not available
    POSTGRES_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgrespassword@localhost:5433/indoxrouter",
    )
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27018/indoxrouter")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "indoxrouter")


def reset_postgres():
    """Reset PostgreSQL database by truncating all tables."""
    try:
        logger.info(f"Connecting to PostgreSQL: {POSTGRES_URI}")
        conn = psycopg2.connect(POSTGRES_URI)

        tables_to_truncate = [
            "api_requests",
            "api_keys",
            "billing_transactions",
            "usage_daily_summary",
            "user_subscriptions",
            "users",
        ]

        with conn.cursor() as cur:
            # Disable foreign key constraints temporarily
            cur.execute("SET session_replication_role = 'replica';")

            # Truncate all tables
            for table in tables_to_truncate:
                logger.info(f"Truncating table: {table}")
                cur.execute(f"TRUNCATE TABLE {table} CASCADE;")

            # Re-enable foreign key constraints
            cur.execute("SET session_replication_role = 'origin';")

            conn.commit()
            logger.info("PostgreSQL database reset successfully")
            return True
    except Exception as e:
        logger.error(f"Error resetting PostgreSQL database: {e}")
        return False
    finally:
        if "conn" in locals() and conn:
            conn.close()


def reset_mongodb():
    """Reset MongoDB database by dropping all collections."""
    try:
        logger.info(f"Connecting to MongoDB: {MONGODB_URI}")
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]

        # Drop all collections
        for collection in db.list_collection_names():
            logger.info(f"Dropping collection: {collection}")
            db.drop_collection(collection)

        logger.info("MongoDB database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting MongoDB database: {e}")
        return False
    finally:
        if "client" in locals() and client:
            client.close()


def main():
    """Main function to reset all databases."""
    logger.info("Starting database reset")

    pg_success = reset_postgres()
    mongo_success = reset_mongodb()

    if pg_success and mongo_success:
        logger.info("All databases reset successfully")
        return 0
    elif pg_success:
        logger.warning("PostgreSQL reset successful, but MongoDB reset failed")
        return 1
    elif mongo_success:
        logger.warning("MongoDB reset successful, but PostgreSQL reset failed")
        return 1
    else:
        logger.error("Failed to reset both databases")
        return 2


if __name__ == "__main__":
    sys.exit(main())
