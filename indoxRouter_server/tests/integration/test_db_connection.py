#!/usr/bin/env python
"""
Integration test for database connections.
This script tests connectivity to PostgreSQL and MongoDB.
"""

import os
import sys
import logging
import unittest

# Add the parent directory to the path to find app module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from app.db.database import (
    init_db,
    get_pg_connection,
    release_pg_connection,
    get_mongo_db,
)
from app.core.config import settings


class TestDatabaseConnections(unittest.TestCase):
    """Test connection to PostgreSQL and MongoDB databases."""

    @classmethod
    def setUpClass(cls):
        """Initialize database connections before tests."""
        logger.info("Initializing database connections for tests")
        if not init_db():
            logger.error("Failed to initialize database connections")
            sys.exit(1)

    def test_postgres_connection(self):
        """Test PostgreSQL connection."""
        logger.info("Testing PostgreSQL connection...")
        try:
            conn = get_pg_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test")
                result = cur.fetchone()
                self.assertIsNotNone(result, "Query should return a result")
                self.assertEqual(result[0], 1, "Query should return 1")
                logger.info("✅ PostgreSQL connection is working")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            self.fail(f"PostgreSQL connection failed: {e}")
        finally:
            if "conn" in locals():
                release_pg_connection(conn)

    def test_mongodb_connection(self):
        """Test MongoDB connection."""
        if not settings.MONGODB_URI:
            logger.warning("MongoDB URI not configured, skipping test")
            self.skipTest("MongoDB URI not configured")

        logger.info("Testing MongoDB connection...")
        try:
            db = get_mongo_db()
            result = db.command("ping")
            self.assertIsNotNone(result, "Ping should return a result")
            self.assertEqual(result.get("ok"), 1, "Ping should return ok=1")
            logger.info("✅ MongoDB connection is working")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.fail(f"MongoDB connection failed: {e}")

    def test_create_retrieve_data(self):
        """Test creating and retrieving test data."""
        if not settings.MONGODB_URI:
            logger.warning("MongoDB URI not configured, skipping test")
            self.skipTest("MongoDB URI not configured")

        logger.info("Testing data creation and retrieval...")

        # Create test user
        try:
            conn = get_pg_connection()
            try:
                with conn.cursor() as cur:
                    # Check if test user exists or create one
                    cur.execute(
                        "SELECT id FROM users WHERE username = 'test_integration'"
                    )
                    user = cur.fetchone()

                    if not user:
                        cur.execute(
                            """
                            INSERT INTO users (username, email, password, credits, is_active)
                            VALUES ('test_integration', 'test_int@example.com', 'password', 100.0, TRUE)
                            RETURNING id
                            """
                        )
                        user_id = cur.fetchone()[0]
                        conn.commit()
                        logger.info(f"Created test user with ID: {user_id}")
                    else:
                        user_id = user[0]
                        logger.info(f"Using existing test user with ID: {user_id}")

                    self.assertIsNotNone(user_id, "Should have a valid user ID")

                    # Test MongoDB
                    db = get_mongo_db()
                    collection = "test_collection"

                    # Insert test document
                    result = db[collection].insert_one(
                        {
                            "user_id": user_id,
                            "test": True,
                            "message": "This is a test document",
                        }
                    )

                    self.assertIsNotNone(
                        result.inserted_id, "Should have inserted a document"
                    )
                    logger.info(f"Inserted test document with ID: {result.inserted_id}")

                    # Retrieve document
                    doc = db[collection].find_one({"user_id": user_id})
                    self.assertIsNotNone(doc, "Should retrieve the test document")
                    self.assertTrue(doc["test"], "Document should have test=True")

                    # Clean up
                    db[collection].delete_one({"_id": result.inserted_id})
                    logger.info("Deleted test document")

            finally:
                release_pg_connection(conn)
        except Exception as e:
            logger.error(f"Test data creation failed: {e}")
            self.fail(f"Test data creation failed: {e}")


if __name__ == "__main__":
    unittest.main()
