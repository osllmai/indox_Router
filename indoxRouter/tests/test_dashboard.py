"""
Tests for the dashboard.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.dashboard import Dashboard


class TestDashboard(unittest.TestCase):
    """Test the dashboard."""

    def setUp(self):
        """Set up the test case."""
        # Mock the AuthManager
        self.auth_manager_mock = MagicMock()

        # Mock the user data
        self.user_data = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_admin": False,
        }

        # Mock the API keys
        self.api_keys = [
            {
                "id": 1,
                "key_name": "Test API Key",
                "key_prefix": "ir-",
                "is_active": True,
                "expires_at": None,
                "last_used_at": None,
                "created_at": "2021-01-01T00:00:00",
            }
        ]

        # Mock the authenticate_user method
        self.auth_manager_mock.authenticate_user.return_value = self.user_data

        # Mock the get_user_api_keys method
        self.auth_manager_mock.get_user_api_keys.return_value = self.api_keys

        # Create a dashboard
        with patch(
            "indoxRouter.utils.dashboard.AuthManager",
            return_value=self.auth_manager_mock,
        ):
            self.dashboard = Dashboard()

    def test_login(self):
        """Test logging in."""
        # Mock the gradio Tabs
        with patch("indoxRouter.utils.dashboard.gr.Tabs") as tabs_mock:
            tabs_mock.return_value = "tabs"

            # Login
            message, main_tabs, login_tabs = self.dashboard.login(
                email="test@example.com",
                password="password",
            )

            # Check that the login was successful
            self.assertEqual(message, "Login successful!")
            self.assertEqual(main_tabs, "tabs")
            self.assertEqual(login_tabs, "tabs")

            # Check that the user data was set
            self.assertEqual(self.dashboard.current_user, self.user_data)

            # Check that the API keys were loaded
            self.assertEqual(self.dashboard.api_keys, self.api_keys)

            # Check that the authenticate_user method was called
            self.auth_manager_mock.authenticate_user.assert_called_once_with(
                "test@example.com",
                "password",
            )

            # Check that the get_user_api_keys method was called
            self.auth_manager_mock.get_user_api_keys.assert_called_once_with(1)

    def test_login_invalid(self):
        """Test logging in with invalid credentials."""
        # Mock the authenticate_user method to return None
        self.auth_manager_mock.authenticate_user.return_value = None

        # Mock the gradio Tabs
        with patch("indoxRouter.utils.dashboard.gr.Tabs") as tabs_mock:
            tabs_mock.return_value = "tabs"

            # Login
            message, main_tabs, login_tabs = self.dashboard.login(
                email="test@example.com",
                password="invalid",
            )

            # Check that the login failed
            self.assertEqual(message, "Invalid email or password")
            self.assertEqual(main_tabs, "tabs")
            self.assertEqual(login_tabs, "tabs")

            # Check that the user data was not set
            self.assertEqual(self.dashboard.current_user, None)

            # Check that the API keys were not loaded
            self.assertEqual(self.dashboard.api_keys, [])

            # Check that the authenticate_user method was called
            self.auth_manager_mock.authenticate_user.assert_called_once_with(
                "test@example.com",
                "invalid",
            )

            # Check that the get_user_api_keys method was not called
            self.auth_manager_mock.get_user_api_keys.assert_not_called()

    def test_register(self):
        """Test registering."""
        # Mock the create_user method
        self.auth_manager_mock.create_user.return_value = 1

        # Mock the generate_api_key method
        self.auth_manager_mock.generate_api_key.return_value = ("ir-test", 1)

        # Register
        message = self.dashboard.register(
            email="test@example.com",
            password="password",
            confirm_password="password",
            first_name="Test",
            last_name="User",
        )

        # Check that the registration was successful
        self.assertEqual(message, "Registration successful! Your API key: ir-test")

        # Check that the create_user method was called
        self.auth_manager_mock.create_user.assert_called_once_with(
            email="test@example.com",
            password="password",
            first_name="Test",
            last_name="User",
        )

        # Check that the generate_api_key method was called
        self.auth_manager_mock.generate_api_key.assert_called_once_with(
            user_id=1,
            key_name="Default API Key",
        )

    def test_register_invalid(self):
        """Test registering with invalid data."""
        # Register with mismatched passwords
        message = self.dashboard.register(
            email="test@example.com",
            password="password",
            confirm_password="invalid",
            first_name="Test",
            last_name="User",
        )

        # Check that the registration failed
        self.assertEqual(message, "Passwords do not match")

        # Check that the create_user method was not called
        self.auth_manager_mock.create_user.assert_not_called()

        # Check that the generate_api_key method was not called
        self.auth_manager_mock.generate_api_key.assert_not_called()

    def test_generate_key(self):
        """Test generating an API key."""
        # Set the current user
        self.dashboard.current_user = self.user_data

        # Mock the generate_api_key method
        self.auth_manager_mock.generate_api_key.return_value = ("ir-test", 1)

        # Generate an API key
        message, table = self.dashboard.generate_key()

        # Check that the API key was generated
        self.assertEqual(message, "API key generated: ir-test")

        # Check that the generate_api_key method was called
        self.auth_manager_mock.generate_api_key.assert_called_once_with(
            user_id=1,
            key_name="Key 1",
        )

        # Check that the get_user_api_keys method was called
        self.auth_manager_mock.get_user_api_keys.assert_called_once_with(1)

    def test_generate_key_not_logged_in(self):
        """Test generating an API key when not logged in."""
        # Generate an API key
        message, table = self.dashboard.generate_key()

        # Check that the API key was not generated
        self.assertEqual(message, "You must be logged in to generate an API key")

        # Check that the generate_api_key method was not called
        self.auth_manager_mock.generate_api_key.assert_not_called()

        # Check that the get_user_api_keys method was not called
        self.auth_manager_mock.get_user_api_keys.assert_not_called()

    def test_deactivate_key(self):
        """Test deactivating an API key."""
        # Set the current user
        self.dashboard.current_user = self.user_data

        # Mock the revoke_api_key method
        self.auth_manager_mock.revoke_api_key.return_value = True

        # Deactivate an API key
        message, table = self.dashboard.deactivate_key(1)

        # Check that the API key was deactivated
        self.assertEqual(message, "API key 1 deactivated")

        # Check that the revoke_api_key method was called
        self.auth_manager_mock.revoke_api_key.assert_called_once_with(
            api_key_id=1,
            user_id=1,
        )

        # Check that the get_user_api_keys method was called
        self.auth_manager_mock.get_user_api_keys.assert_called_once_with(1)

    def test_deactivate_key_not_logged_in(self):
        """Test deactivating an API key when not logged in."""
        # Deactivate an API key
        message, table = self.dashboard.deactivate_key(1)

        # Check that the API key was not deactivated
        self.assertEqual(message, "Please login first")

        # Check that the revoke_api_key method was not called
        self.auth_manager_mock.revoke_api_key.assert_not_called()

        # Check that the get_user_api_keys method was not called
        self.auth_manager_mock.get_user_api_keys.assert_not_called()

    def test_test_model(self):
        """Test testing a model."""
        # Mock the Client
        with patch("indoxRouter.utils.dashboard.Client") as client_mock:
            # Mock the generate method
            client_instance = MagicMock()
            client_instance.generate.return_value = "This is a test response."
            client_mock.return_value = client_instance

            # Test a model
            response = self.dashboard.test_model(
                api_key="test_api_key",
                provider="openai",
                model="gpt-3.5-turbo",
                prompt="Hello, world!",
                temperature=0.7,
                max_tokens=1000,
            )

            # Check that the response was generated
            self.assertEqual(response, "This is a test response.")

            # Check that the Client was created
            client_mock.assert_called_once_with(api_key="test_api_key")

            # Check that the generate method was called
            client_instance.generate.assert_called_once_with(
                provider="openai",
                model="gpt-3.5-turbo",
                prompt="Hello, world!",
                temperature=0.7,
                max_tokens=1000,
            )

    def test_test_model_invalid(self):
        """Test testing a model with invalid data."""
        # Test a model without an API key
        response = self.dashboard.test_model(
            api_key="",
            provider="openai",
            model="gpt-3.5-turbo",
            prompt="Hello, world!",
            temperature=0.7,
            max_tokens=1000,
        )

        # Check that the response was not generated
        self.assertEqual(response, "API key is required")

        # Test a model without a provider
        response = self.dashboard.test_model(
            api_key="test_api_key",
            provider="",
            model="gpt-3.5-turbo",
            prompt="Hello, world!",
            temperature=0.7,
            max_tokens=1000,
        )

        # Check that the response was not generated
        self.assertEqual(response, "Provider is required")

        # Test a model without a model
        response = self.dashboard.test_model(
            api_key="test_api_key",
            provider="openai",
            model="",
            prompt="Hello, world!",
            temperature=0.7,
            max_tokens=1000,
        )

        # Check that the response was not generated
        self.assertEqual(response, "Model is required")

        # Test a model without a prompt
        response = self.dashboard.test_model(
            api_key="test_api_key",
            provider="openai",
            model="gpt-3.5-turbo",
            prompt="",
            temperature=0.7,
            max_tokens=1000,
        )

        # Check that the response was not generated
        self.assertEqual(response, "Prompt is required")

    def test_update_models_dropdown(self):
        """Test updating the models dropdown."""
        # Mock the gradio Dropdown
        with patch("indoxRouter.utils.dashboard.gr.Dropdown") as dropdown_mock:
            dropdown_mock.return_value = "dropdown"

            # Set the models
            self.dashboard.models = {
                "openai": ["gpt-3.5-turbo", "gpt-4"],
            }

            # Update the models dropdown
            dropdown = self.dashboard.update_models_dropdown("openai")

            # Check that the dropdown was updated
            self.assertEqual(dropdown, "dropdown")

            # Check that the Dropdown was created
            dropdown_mock.assert_called_once_with(choices=["gpt-3.5-turbo", "gpt-4"])

    def test_update_models_dropdown_invalid(self):
        """Test updating the models dropdown with an invalid provider."""
        # Mock the gradio Dropdown
        with patch("indoxRouter.utils.dashboard.gr.Dropdown") as dropdown_mock:
            dropdown_mock.return_value = "dropdown"

            # Set the models
            self.dashboard.models = {
                "openai": ["gpt-3.5-turbo", "gpt-4"],
            }

            # Update the models dropdown
            dropdown = self.dashboard.update_models_dropdown("invalid")

            # Check that the dropdown was updated
            self.assertEqual(dropdown, "dropdown")

            # Check that the Dropdown was created
            dropdown_mock.assert_called_once_with(choices=[])

    def test_security_check(self):
        """Test running a security check."""
        # Set the current user
        self.dashboard.current_user = self.user_data

        # Set the API keys
        self.dashboard.api_keys = self.api_keys

        # Run a security check
        results = self.dashboard.security_check()

        # Check that the results were generated
        self.assertIn("### API Key Security", results)
        self.assertIn("✅ 1 API keys found.", results)


if __name__ == "__main__":
    unittest.main()
