#!/usr/bin/env python
"""
Test script for the IndoxRouter server database connections.
This script tests if the hybrid database approach with PostgreSQL and MongoDB is working properly.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from app.db.database import (
    init_db,
    get_pg_connection,
    release_pg_connection,
    get_mongo_db,
)
from app.core.config import settings


def test_postgres_connection():
    """Test PostgreSQL connection."""
    logger.info("Testing PostgreSQL connection...")
    try:
        conn = get_pg_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
            if result and result[0] == 1:
                logger.info("✅ PostgreSQL connection is working")
                return True
            else:
                logger.error("❌ PostgreSQL query failed")
                return False
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False
    finally:
        if "conn" in locals():
            release_pg_connection(conn)


def test_mongodb_connection():
    """Test MongoDB connection."""
    logger.info("Testing MongoDB connection...")
    try:
        db = get_mongo_db()
        result = db.command("ping")
        if result and result.get("ok") == 1:
            logger.info("✅ MongoDB connection is working")
            return True
        else:
            logger.error("❌ MongoDB ping failed")
            return False
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False


def test_creating_test_data():
    """Test creating test data in both databases."""
    logger.info("Testing data creation in PostgreSQL...")
    try:
        # Create a test user in PostgreSQL
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # Check if test user exists
                cur.execute("SELECT id FROM users WHERE username = 'testuser'")
                user = cur.fetchone()

                if not user:
                    # Create test user
                    cur.execute(
                        """
                        INSERT INTO users (username, email, password, credits, is_active)
                        VALUES ('testuser', 'test@example.com', 'password', 100.0, TRUE)
                        RETURNING id
                        """
                    )
                    user_id = cur.fetchone()[0]
                    conn.commit()
                    logger.info(f"✅ Created test user with ID: {user_id}")
                else:
                    user_id = user[0]
                    logger.info(f"✅ Test user already exists with ID: {user_id}")

                # Create a test API key
                cur.execute(
                    """
                    INSERT INTO api_keys (user_id, api_key, name)
                    VALUES (%s, 'test-api-key', 'Test Key')
                    ON CONFLICT (api_key) DO NOTHING
                    RETURNING id
                    """,
                    (user_id,),
                )
                conn.commit()
                logger.info("✅ Created test API key")

                return user_id
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"❌ PostgreSQL test data creation failed: {e}")
        return None


def test_mongodb_data_creation(user_id):
    """Test creating data in MongoDB."""
    if not user_id:
        logger.error("❌ Cannot create MongoDB data without a valid user ID")
        return False

    logger.info("Testing data creation in MongoDB...")
    try:
        db = get_mongo_db()

        # Create a test conversation
        result = db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": "Test Conversation",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"},
                    {
                        "role": "assistant",
                        "content": "I'm doing well, thank you for asking! How can I help you today?",
                    },
                ],
                "created_at": db.server_info()["localTime"],
                "updated_at": db.server_info()["localTime"],
            }
        )

        logger.info(f"✅ Created test conversation with ID: {result.inserted_id}")

        # Verify we can retrieve the conversation
        conv = db.conversations.find_one({"_id": result.inserted_id})
        if conv:
            logger.info("✅ Successfully retrieved test conversation")
            return True
        else:
            logger.error("❌ Failed to retrieve test conversation")
            return False
    except Exception as e:
        logger.error(f"❌ MongoDB test data creation failed: {e}")
        return False


def main():
    """Main function."""
    logger.info("Starting IndoxRouter database test")

    # Initialize the databases
    if not init_db():
        logger.error("❌ Database initialization failed")
        sys.exit(1)

    # Test PostgreSQL connection
    pg_success = test_postgres_connection()

    # Test MongoDB connection (if configured)
    mongo_success = True
    if settings.MONGODB_URI:
        mongo_success = test_mongodb_connection()
    else:
        logger.warning("⚠️ MongoDB URI not configured, skipping MongoDB tests")

    # Test creating test data
    if pg_success:
        user_id = test_creating_test_data()

        if user_id and settings.MONGODB_URI and mongo_success:
            test_mongodb_data_creation(user_id)

    # Overall result
    if pg_success and mongo_success:
        logger.info("✅ All database tests passed!")
    else:
        logger.error("❌ Some database tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
