#!/usr/bin/env python
"""
Unit tests for user-related PostgreSQL database functions.
Tests the actual database functions using mocked PostgreSQL connections.
"""

import pytest
import sys
import os
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import the database functions to test
from app.db.database import (
    get_user_by_id,
    get_user_by_api_key,
    update_user_credits,
    create_api_key,
    get_user_api_keys,
    delete_api_key,
)


class MockCursor:
    """Mock cursor for PostgreSQL testing."""

    def __init__(self, return_values=None):
        """Initialize the mock cursor."""
        self.return_values = return_values or []
        self.execute_calls = []
        self.rowcount = 1  # Default rowcount is 1 to indicate success

    def execute(self, query, params=None):
        """Mock execute method."""
        self.execute_calls.append((query, params))

    def fetchone(self):
        """Mock fetchone method."""
        if not self.return_values:
            return None
        if isinstance(self.return_values, list):
            return self.return_values[0] if self.return_values else None
        return self.return_values

    def fetchall(self):
        """Mock fetchall method."""
        if isinstance(self.return_values, list):
            return self.return_values
        return [self.return_values] if self.return_values else []


class MockConnection:
    """Mock connection for PostgreSQL testing."""

    def __init__(self, cursor=None):
        """Initialize the mock connection."""
        self.cursor_obj = cursor or MockCursor()
        self.commit_called = False
        self.rollback_called = False

    def cursor(self):
        """Mock cursor context manager."""
        return self

    def __enter__(self):
        """Enter context manager."""
        return self.cursor_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass

    def commit(self):
        """Mock commit method."""
        self.commit_called = True

    def rollback(self):
        """Mock rollback method."""
        self.rollback_called = True


class TestUserDatabaseFunctions:
    """Test user database functions with PostgreSQL mocks."""

    @patch("app.db.database.pg_pool")
    def test_get_user_by_id_success(self, mock_pg_pool):
        """Test retrieving a user by ID when successful."""
        # Arrange
        user_id = 123
        expected_user = {
            "id": user_id,
            "username": "testuser",
            "email": "test@example.com",
            "credits": 100.0,
            "is_active": True,
            "account_tier": "basic",
            "created_at": "2023-01-01T00:00:00Z",
            "last_login_at": "2023-01-02T00:00:00Z",
        }

        # Create mock cursor with expected return value
        mock_cursor = MockCursor(expected_user)
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        user = get_user_by_id(user_id)

        # Assert
        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"

        # Verify SQL contained user ID
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "user" in sql.lower()
        assert "id" in sql.lower()
        assert user_id in params or user_id == params

    @patch("app.db.database.pg_pool")
    def test_get_user_by_id_not_found(self, mock_pg_pool):
        """Test retrieving a non-existent user by ID."""
        # Arrange
        user_id = 999  # Non-existent user

        # Create mock cursor that returns None
        mock_cursor = MockCursor(None)
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        user = get_user_by_id(user_id)

        # Assert
        assert user is None

    @patch("app.db.database.pg_pool")
    def test_get_user_by_api_key_success(self, mock_pg_pool):
        """Test retrieving a user by API key when successful."""
        # Arrange
        api_key = "test-api-key-123"
        expected_user = {
            "id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "credits": 100.0,
            "is_active": True,
            "api_key_id": 456,
        }

        # Create mock cursor with expected return value
        mock_cursor = MockCursor(expected_user)
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        user = get_user_by_api_key(api_key)

        # Assert
        assert user is not None
        assert user["id"] == 123
        assert user["username"] == "testuser"
        assert user["api_key_id"] == 456

        # Verify SQL contained API key
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "api_key" in sql.lower()
        assert api_key in params or api_key == params

    @patch("app.db.database.pg_pool")
    def test_update_user_credits_success(self, mock_pg_pool):
        """Test successfully updating a user's credits."""
        # Arrange
        user_id = 123
        credits_to_add = 50.0

        # Create mock cursor that indicates success
        mock_cursor = MockCursor()
        mock_cursor.rowcount = 1
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is True
        assert mock_conn.commit_called is True

        # Verify SQL and parameters
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "update" in sql.lower()
        assert "user" in sql.lower()
        assert "credit" in sql.lower()
        assert user_id in params
        assert credits_to_add in params

    @patch("app.db.database.pg_pool")
    def test_update_user_credits_failure(self, mock_pg_pool):
        """Test updating credits for a non-existent user."""
        # Arrange
        user_id = 999  # Non-existent user
        credits_to_add = 50.0

        # Create mock cursor that indicates no rows were updated
        mock_cursor = MockCursor()
        mock_cursor.rowcount = 0
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is False
        assert mock_conn.commit_called is True

    @patch("app.db.database.pg_pool")
    def test_create_api_key(self, mock_pg_pool):
        """Test creating a new API key for a user."""
        # Arrange
        user_id = 123
        key_name = "Test API Key"

        # Mock return value for API key creation
        api_key_result = {"id": 456, "api_key": "new-api-key-123"}

        # Create mock cursor with expected return value
        mock_cursor = MockCursor(api_key_result)
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        result = create_api_key(user_id, key_name)

        # Assert
        assert result is not None
        assert result["id"] == 456
        assert result["api_key"] == "new-api-key-123"
        assert mock_conn.commit_called is True

        # Verify SQL and parameters
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "insert into" in sql.lower()
        assert "api_key" in sql.lower()
        assert user_id in params
        assert key_name in params

    @patch("app.db.database.pg_pool")
    def test_get_user_api_keys(self, mock_pg_pool):
        """Test retrieving all API keys for a user."""
        # Arrange
        user_id = 123

        # Mock return value for API keys retrieval
        api_keys = [
            {
                "id": 456,
                "api_key": "api-key-1",
                "name": "Key 1",
                "created_at": "2023-01-01T00:00:00Z",
            },
            {
                "id": 457,
                "api_key": "api-key-2",
                "name": "Key 2",
                "created_at": "2023-01-02T00:00:00Z",
            },
        ]

        # Create mock cursor with expected return value
        mock_cursor = MockCursor(api_keys)
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        keys = get_user_api_keys(user_id)

        # Assert
        assert keys is not None
        assert len(keys) == 2
        assert keys[0]["api_key"] == "api-key-1"
        assert keys[1]["api_key"] == "api-key-2"

        # Verify SQL and parameters
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "select" in sql.lower()
        assert "api_key" in sql.lower()
        assert user_id in params or user_id == params

    @patch("app.db.database.pg_pool")
    def test_delete_api_key(self, mock_pg_pool):
        """Test deleting an API key."""
        # Arrange
        api_key_id = 456
        user_id = 123

        # Create mock cursor that indicates success
        mock_cursor = MockCursor()
        mock_cursor.rowcount = 1
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        success = delete_api_key(api_key_id, user_id)

        # Assert
        assert success is True
        assert mock_conn.commit_called is True

        # Verify SQL and parameters
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "delete" in sql.lower()
        assert "api_key" in sql.lower()
        assert api_key_id in params
        assert user_id in params

    @patch("app.db.database.pg_pool")
    def test_delete_api_key_failure(self, mock_pg_pool):
        """Test failing to delete an API key (wrong user or non-existent key)."""
        # Arrange
        api_key_id = 999  # Non-existent key
        user_id = 123

        # Create mock cursor that indicates no rows were affected
        mock_cursor = MockCursor()
        mock_cursor.rowcount = 0
        mock_conn = MockConnection(mock_cursor)

        # Setup pg_pool mock to return our mock connection
        mock_pg_pool.getconn.return_value = mock_conn

        # Act
        success = delete_api_key(api_key_id, user_id)

        # Assert
        assert success is False
        assert mock_conn.commit_called is True
