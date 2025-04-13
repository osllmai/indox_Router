"""
PostgreSQL test fixtures for IndoxRouter tests.
This module provides common mock classes and functions for PostgreSQL testing.
"""

from unittest.mock import MagicMock, patch
import pytest


class MockCursor:
    """
    Mock cursor for PostgreSQL testing.
    Provides a controllable cursor that can return predetermined values.
    """

    def __init__(self, return_values=None):
        """
        Initialize the mock cursor.

        Args:
            return_values: The values to return from fetchone/fetchall calls.
                           Can be a single value, a list, or None.
        """
        self.return_values = return_values or []
        self.execute_calls = []
        self.rowcount = 1  # Default rowcount is 1 to indicate success

    def execute(self, query, params=None):
        """
        Mock execute method. Records the query and parameters.

        Args:
            query: The SQL query string
            params: The query parameters
        """
        self.execute_calls.append((query, params))

    def fetchone(self):
        """
        Mock fetchone method.

        Returns:
            The first item from return_values if it's a list,
            or return_values itself if it's a single value,
            or None if return_values is empty or None.
        """
        if not self.return_values:
            return None
        if isinstance(self.return_values, list):
            return self.return_values[0] if self.return_values else None
        return self.return_values

    def fetchall(self):
        """
        Mock fetchall method.

        Returns:
            return_values as a list if it's already a list,
            or [return_values] if it's a single value,
            or [] if return_values is empty or None.
        """
        if isinstance(self.return_values, list):
            return self.return_values
        return [self.return_values] if self.return_values else []


class MockConnection:
    """
    Mock connection for PostgreSQL testing.
    Provides a controllable connection that supports the context manager protocol.
    """

    def __init__(self, cursor=None):
        """
        Initialize the mock connection.

        Args:
            cursor: A MockCursor instance or None to create a default one
        """
        self.cursor_obj = cursor or MockCursor()
        self.commit_called = False
        self.rollback_called = False

    def cursor(self):
        """
        Mock cursor method that returns a context manager.

        Returns:
            self as a context manager for with statements
        """
        return self

    def __enter__(self):
        """
        Enter context manager, returning the cursor.

        Returns:
            The cursor object
        """
        return self.cursor_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass

    def commit(self):
        """Mock commit method that tracks if commit was called."""
        self.commit_called = True

    def rollback(self):
        """Mock rollback method that tracks if rollback was called."""
        self.rollback_called = True


@pytest.fixture
def mock_pg_connection():
    """
    Fixture to provide a mock PostgreSQL connection.

    Returns:
        A tuple of (mock_connection, mock_cursor)
    """
    mock_cursor = MockCursor()
    mock_conn = MockConnection(mock_cursor)
    return mock_conn, mock_cursor


@pytest.fixture
def patched_pg_pool():
    """
    Fixture that patches the pg_pool and returns mock connection objects.

    Yields:
        A tuple of (mock_pg_pool, mock_connection, mock_cursor)
    """
    mock_cursor = MockCursor()
    mock_conn = MockConnection(mock_cursor)

    with patch("app.db.database.pg_pool") as mock_pg_pool:
        mock_pg_pool.getconn.return_value = mock_conn
        yield mock_pg_pool, mock_conn, mock_cursor


def setup_mock_user_response(
    mock_cursor, user_id=123, username="testuser", email="test@example.com"
):
    """
    Helper to set up a mock user response.

    Args:
        mock_cursor: The mock cursor to configure
        user_id: The user ID
        username: The username
        email: The user's email

    Returns:
        The user data dictionary
    """
    user_data = {
        "id": user_id,
        "username": username,
        "email": email,
        "credits": 100.0,
        "is_active": True,
        "account_tier": "basic",
        "created_at": "2023-01-01T00:00:00Z",
        "last_login_at": "2023-01-02T00:00:00Z",
    }
    mock_cursor.return_values = user_data
    return user_data


def setup_mock_api_key_response(mock_cursor, api_key_id=456, api_key="test-api-key"):
    """
    Helper to set up a mock API key response.

    Args:
        mock_cursor: The mock cursor to configure
        api_key_id: The API key ID
        api_key: The API key string

    Returns:
        The API key data dictionary
    """
    api_key_data = {
        "id": api_key_id,
        "api_key": api_key,
        "name": "Test API Key",
        "created_at": "2023-01-01T00:00:00Z",
    }
    mock_cursor.return_values = api_key_data
    return api_key_data
