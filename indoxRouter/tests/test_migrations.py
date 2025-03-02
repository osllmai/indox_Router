"""
Tests for the migrations.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.migrations import (
    create_tables,
    drop_tables,
    create_admin_user,
)


class TestMigrations(unittest.TestCase):
    """Test the migrations."""

    def setUp(self):
        """Set up the test case."""
        # Mock the Base, get_engine, and get_session
        self.base_mock = MagicMock()
        self.engine_mock = MagicMock()
        self.session_mock = MagicMock()

        # Mock the AuthManager
        self.auth_manager_mock = MagicMock()

        # Apply the patches
        self.base_patcher = patch("indoxRouter.utils.migrations.Base", self.base_mock)
        self.engine_patcher = patch(
            "indoxRouter.utils.migrations.get_engine", return_value=self.engine_mock
        )
        self.session_patcher = patch(
            "indoxRouter.utils.migrations.get_session", return_value=self.session_mock
        )
        self.auth_manager_patcher = patch(
            "indoxRouter.utils.migrations.AuthManager",
            return_value=self.auth_manager_mock,
        )

        self.base_patcher.start()
        self.engine_patcher.start()
        self.session_patcher.start()
        self.auth_manager_patcher.start()

    def tearDown(self):
        """Tear down the test case."""
        self.base_patcher.stop()
        self.engine_patcher.stop()
        self.session_patcher.stop()
        self.auth_manager_patcher.stop()

    def test_create_tables(self):
        """Test creating tables."""
        # Create tables
        create_tables()

        # Check that the tables were created
        self.base_mock.metadata.create_all.assert_called_once_with(self.engine_mock)

    def test_drop_tables(self):
        """Test dropping tables."""
        # Drop tables
        drop_tables()

        # Check that the tables were dropped
        self.base_mock.metadata.drop_all.assert_called_once_with(self.engine_mock)

    def test_create_admin_user(self):
        """Test creating an admin user."""
        # Mock the query
        query_mock = MagicMock()
        self.session_mock.query.return_value = query_mock

        # Mock the filter
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock

        # Mock the first method to return None (no admin user exists)
        filter_mock.first.return_value = None

        # Mock the create_user method
        self.auth_manager_mock.create_user.return_value = 1

        # Mock the generate_api_key method
        self.auth_manager_mock.generate_api_key.return_value = ("ir-test", 1)

        # Create an admin user
        create_admin_user()

        # Check that the query was made
        self.session_mock.query.assert_called_once()

        # Check that the create_user method was called
        self.auth_manager_mock.create_user.assert_called_once_with(
            email="admin@example.com",
            password="admin",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )

        # Check that the generate_api_key method was called
        self.auth_manager_mock.generate_api_key.assert_called_once_with(
            user_id=1,
            key_name="Admin API Key",
        )

        # Check that the session was closed
        self.session_mock.close.assert_called_once()

    def test_create_admin_user_exists(self):
        """Test creating an admin user when one already exists."""
        # Mock the query
        query_mock = MagicMock()
        self.session_mock.query.return_value = query_mock

        # Mock the filter
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock

        # Mock the first method to return an admin user
        admin_mock = MagicMock()
        filter_mock.first.return_value = admin_mock

        # Create an admin user
        create_admin_user()

        # Check that the query was made
        self.session_mock.query.assert_called_once()

        # Check that the create_user method was not called
        self.auth_manager_mock.create_user.assert_not_called()

        # Check that the generate_api_key method was not called
        self.auth_manager_mock.generate_api_key.assert_not_called()

        # Check that the session was closed
        self.session_mock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
