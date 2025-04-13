#!/usr/bin/env python
"""
Unit tests for PostgreSQL database operations using mock.
This file demonstrates how to mock PostgreSQL for testing.
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

# Import database functions to test
from app.db.database import (
    get_user_by_id,
    get_user_by_api_key,
    create_user,
    update_user_credits,
    get_pg_connection,
    release_pg_connection,
)

# Import our custom PostgreSQL fixtures
from tests.fixtures.pg_test_fixture import (
    MockCursor,
    MockConnection,
    setup_mock_user_response,
    setup_mock_api_key_response,
)


class TestPostgreSQLOperations:
    """Test PostgreSQL operations using mocks."""

    def test_get_user_by_id_with_fixture(self, patched_pg_pool):
        """Test retrieving a user by ID using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Arrange
        user_id = 123
        expected_user = setup_mock_user_response(mock_cursor, user_id)

        # Act
        user = get_user_by_id(user_id)

        # Assert
        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"

        # Verify SQL execution
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "user" in sql.lower()
        assert user_id in params or user_id == params

    @patch("app.db.database.pg_pool")
    def test_get_user_by_id(self, mock_pg_pool):
        """Test retrieving a user by ID."""
        # Arrange
        user_id = 123
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock the database response
        expected_user = {
            "id": user_id,
            "username": "testuser",
            "email": "test@example.com",
            "credits": 100.0,
            "is_active": True,
            "account_tier": "basic",
            "created_at": "2023-01-01T00:00:00Z",
        }
        mock_cursor.fetchone.return_value = expected_user

        # Act
        user = get_user_by_id(user_id)

        # Assert
        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        # Verify connection was returned to the pool
        mock_pg_pool.putconn.assert_called_once_with(mock_conn)

    def test_get_user_by_api_key_with_fixture(self, patched_pg_pool):
        """Test retrieving a user by API key using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Arrange
        api_key = "test-api-key-123"
        user_id = 123

        # Setup the user data but include an api_key_id
        user_data = setup_mock_user_response(mock_cursor, user_id)
        user_data["api_key_id"] = 456

        # Act
        user = get_user_by_api_key(api_key)

        # Assert
        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == "testuser"
        assert user["api_key_id"] == 456

        # Verify SQL execution
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "api_key" in sql.lower()
        assert api_key in params or api_key == params

    @patch("app.db.database.pg_pool")
    def test_get_user_by_api_key(self, mock_pg_pool):
        """Test retrieving a user by API key."""
        # Arrange
        api_key = "test-api-key"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock the database response
        expected_user = {
            "id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "credits": 100.0,
            "is_active": True,
            "api_key_id": 456,
        }
        mock_cursor.fetchone.return_value = expected_user

        # Act
        user = get_user_by_api_key(api_key)

        # Assert
        assert user is not None
        assert user["id"] == 123
        assert user["username"] == "testuser"
        assert user["api_key_id"] == 456

        # Verify correct SQL was executed with the API key
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        assert "api_key" in call_args[0].lower()  # SQL contains "api_key"
        assert api_key in call_args[1]  # parameters contain the API key

    def test_create_user_with_fixture(self, patched_pg_pool):
        """Test creating a new user using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Arrange
        username = "newuser"
        email = "new@example.com"
        password = "password123"
        user_id = 123

        # Set the mock return value to a tuple with the user ID
        mock_cursor.return_values = (user_id,)

        # Act
        result_user_id = create_user(username, email, password)

        # Assert
        assert result_user_id == user_id
        assert mock_conn.commit_called is True

        # Verify SQL execution
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "insert into" in sql.lower()
        assert "user" in sql.lower()
        assert username in params
        assert email in params
        assert password not in params  # Password should be hashed

    @patch("app.db.database.pg_pool")
    def test_create_user(self, mock_pg_pool):
        """Test creating a new user."""
        # Arrange
        username = "newuser"
        email = "new@example.com"
        password = "password123"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock the database response
        mock_cursor.fetchone.return_value = (123,)  # Returned user ID

        # Act
        user_id = create_user(username, email, password)

        # Assert
        assert user_id == 123

        # Verify the SQL execution
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # Check that the parameters were passed correctly
        call_args = mock_cursor.execute.call_args[0]
        assert username in call_args[1]
        assert email in call_args[1]
        assert password not in call_args[1]  # Should be hashed

        # Verify connection was returned to the pool
        mock_pg_pool.putconn.assert_called_once_with(mock_conn)

    def test_update_user_credits_with_fixture(self, patched_pg_pool):
        """Test updating a user's credits using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Arrange
        user_id = 123
        credits_to_add = 50.0

        # The mock cursor already has rowcount=1 by default

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is True
        assert mock_conn.commit_called is True

        # Verify SQL execution
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "update" in sql.lower()
        assert "user" in sql.lower()
        assert "credit" in sql.lower()
        assert user_id in params
        assert credits_to_add in params

    @patch("app.db.database.pg_pool")
    def test_update_user_credits(self, mock_pg_pool):
        """Test updating a user's credits."""
        # Arrange
        user_id = 123
        credits_to_add = 50.0

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock the database response
        mock_cursor.rowcount = 1  # Indicate one row was updated

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is True

        # Verify SQL execution and transaction
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # Check that parameters were passed correctly
        call_args = mock_cursor.execute.call_args[0]
        assert user_id in call_args[1]
        assert credits_to_add in call_args[1]

    def test_update_user_credits_failure_with_fixture(self, patched_pg_pool):
        """Test updating credits for a non-existent user using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Arrange
        user_id = 999  # Non-existent user
        credits_to_add = 50.0

        # Set rowcount to 0 to indicate no rows were updated
        mock_cursor.rowcount = 0

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is False
        assert mock_conn.commit_called is True  # Transaction still committed

    @patch("app.db.database.pg_pool")
    def test_update_user_credits_failure(self, mock_pg_pool):
        """Test updating credits for a non-existent user."""
        # Arrange
        user_id = 999  # Non-existent user
        credits_to_add = 50.0

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock the database response - no rows updated
        mock_cursor.rowcount = 0

        # Act
        success = update_user_credits(user_id, credits_to_add)

        # Assert
        assert success is False

        # Verify the transaction was still committed (even though no rows were updated)
        mock_conn.commit.assert_called_once()

    def test_connection_management(self):
        """Test connection acquisition and release."""
        # Arrange
        mock_conn = MagicMock()

        # Act & Assert
        with patch("app.db.database.pg_pool") as mock_pg_pool:
            mock_pg_pool.getconn.return_value = mock_conn

            # Get a connection
            conn = get_pg_connection()
            assert conn is mock_conn
            mock_pg_pool.getconn.assert_called_once()

            # Release the connection
            release_pg_connection(conn)
            mock_pg_pool.putconn.assert_called_once_with(mock_conn)

    @patch("app.db.database.pg_pool")
    def test_connection_error_handling(self, mock_pg_pool):
        """Test error handling during database operations."""
        # Arrange
        user_id = 123
        mock_pg_pool.getconn.side_effect = Exception("Connection error")

        # Act & Assert
        with pytest.raises(Exception):
            user = get_user_by_id(user_id)

        # Verify no connection was returned to the pool
        mock_pg_pool.putconn.assert_not_called()


class TestTransactionManagement:
    """Test transaction management in PostgreSQL operations."""

    def test_transaction_commit_with_fixture(self, patched_pg_pool):
        """Test successful transaction commit using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Act
        conn = get_pg_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO test_table VALUES (1, 'test')")
        conn.commit()
        release_pg_connection(conn)

        # Assert
        assert mock_conn.commit_called is True

        # Verify SQL execution
        assert len(mock_cursor.execute_calls) == 1
        sql, params = mock_cursor.execute_calls[0]
        assert "insert into" in sql.lower()
        assert "test_table" in sql.lower()

    @patch("app.db.database.pg_pool")
    def test_transaction_commit(self, mock_pg_pool):
        """Test successful transaction commit."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Act
        try:
            # Simulate a function that gets a connection and performs a transaction
            conn = get_pg_connection()
            with conn.cursor() as cur:
                cur.execute("INSERT INTO test_table VALUES (1, 'test')")
            conn.commit()
            release_pg_connection(conn)
        except Exception as e:
            # This shouldn't happen in the happy path
            pytest.fail(f"Transaction failed: {e}")

        # Assert
        mock_conn.commit.assert_called_once()
        mock_pg_pool.putconn.assert_called_once_with(mock_conn)

    def test_transaction_rollback_with_fixture(self, patched_pg_pool):
        """Test transaction rollback on error using our fixture."""
        # Unpack the fixture
        mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

        # Configure the mock cursor to raise an exception on execute
        def raise_exception(*args, **kwargs):
            raise Exception("Database error")

        mock_cursor.execute = raise_exception

        # Act
        try:
            conn = get_pg_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_table VALUES (1, 'test')"
                )  # This will fail
            conn.commit()  # This shouldn't be reached
        except Exception:
            conn.rollback()
        finally:
            release_pg_connection(conn)

        # Assert
        assert mock_conn.commit_called is False
        assert mock_conn.rollback_called is True

    @patch("app.db.database.pg_pool")
    def test_transaction_rollback(self, mock_pg_pool):
        """Test transaction rollback on error."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Make the execute method raise an exception
        mock_cursor.execute.side_effect = Exception("Database error")

        # Act
        try:
            # Simulate a function that gets a connection and performs a transaction
            conn = get_pg_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_table VALUES (1, 'test')"
                )  # This will fail
            # This part shouldn't be reached
            conn.commit()
        except Exception:
            # Expected path
            conn.rollback()
        finally:
            release_pg_connection(conn)

        # Assert
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_pg_pool.putconn.assert_called_once_with(mock_conn)
