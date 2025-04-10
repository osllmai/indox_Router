#!/usr/bin/env python
"""
Unit tests for the IndoxRouter database functionality.
"""

import unittest
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to find app module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from app.db.database import (
    init_db,
    get_pg_connection,
    release_pg_connection,
    get_mongo_db,
    get_user_by_api_key,
    get_user_by_id,
    save_conversation,
    get_user_conversations,
)
from app.core.config import settings


class TestDatabaseConnections(unittest.TestCase):
    """Test the database connection functionality."""

    def test_postgres_connection(self):
        """Test the PostgreSQL connection function."""
        # This test requires an actual database connection
        # Consider skipping it if running in CI environment
        if os.environ.get("CI") == "true":
            self.skipTest("Skipping in CI environment")

        # Initialize the database
        self.assertTrue(init_db(), "Database initialization should succeed")

        # Test connection
        conn = get_pg_connection()
        self.assertIsNotNone(conn, "Should get a valid connection")

        # Test query
        with conn.cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
            self.assertEqual(result[0], 1, "Query should return 1")

        # Release connection
        release_pg_connection(conn)

    @patch("app.db.database.pg_pool")
    def test_get_user_by_id_success(self, mock_pool):
        """Test getting a user by ID when successful."""
        # Create mock connection and cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        # Mock the query result
        mock_cur.fetchone.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "credits": 100.0,
            "account_tier": "basic",
            "created_at": "2023-01-01T00:00:00Z",
            "last_login_at": "2023-01-01T00:00:00Z",
        }

        # Call the function
        user = get_user_by_id(1)

        # Verify the result
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["username"], "testuser")

        # Verify the mock was called correctly
        mock_pool.getconn.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)

    @patch("app.db.database.pg_pool")
    def test_get_user_by_api_key_success(self, mock_pool):
        """Test getting a user by API key when successful."""
        # Create mock connection and cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        # Mock the query result
        mock_cur.fetchone.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "credits": 100.0,
            "account_tier": "basic",
            "api_key_id": 123,
        }

        # Call the function
        user = get_user_by_api_key("test-api-key")

        # Verify the result
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["username"], "testuser")

        # Verify the mock was called correctly
        mock_pool.getconn.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)


class TestMongoDBFunctions(unittest.TestCase):
    """Test the MongoDB specific functions."""

    @patch("app.db.database.mongo_db")
    def test_save_conversation(self, mock_db):
        """Test saving a conversation."""
        # Mock the MongoDB insert_one result
        mock_result = MagicMock()
        mock_result.inserted_id = "test_conversation_id"
        mock_db.conversations.insert_one.return_value = mock_result

        # Call the function
        conversation_id = save_conversation(
            1,
            "Test Conversation",
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        )

        # Verify the result
        self.assertEqual(conversation_id, "test_conversation_id")

        # Verify the mock was called correctly
        mock_db.conversations.insert_one.assert_called_once()

    @patch("app.db.database.mongo_db")
    def test_get_user_conversations(self, mock_db):
        """Test getting user conversations."""
        # Mock the MongoDB find result
        mock_conversations = [
            {
                "_id": "conv1",
                "title": "Conversation 1",
                "messages": [{"role": "user", "content": "Hello"}],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            {
                "_id": "conv2",
                "title": "Conversation 2",
                "messages": [{"role": "user", "content": "Hi"}],
                "created_at": "2023-01-02T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
            },
        ]

        # Setup the mock cursor
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_conversations)
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor

        mock_db.conversations.find.return_value = mock_cursor

        # Call the function
        conversations = get_user_conversations(1, limit=10, skip=0)

        # Verify the result
        self.assertEqual(len(conversations), 2)
        self.assertEqual(conversations[0]["_id"], "conv1")
        self.assertEqual(conversations[1]["_id"], "conv2")

        # Verify the mock was called correctly
        mock_db.conversations.find.assert_called_once()


if __name__ == "__main__":
    unittest.main()
