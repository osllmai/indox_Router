"""
Tests for the database models.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from indoxRouter.models.database import User, ApiKey, RequestLog, ProviderConfig


class TestModels(unittest.TestCase):
    """Test the database models."""

    def setUp(self):
        """Set up the test case."""
        # Mock the session
        self.session_mock = MagicMock()

        # Apply the patches
        self.session_patcher = patch(
            "indoxRouter.models.database.get_session", return_value=self.session_mock
        )
        self.session_patcher.start()

    def tearDown(self):
        """Tear down the test case."""
        self.session_patcher.stop()

    def test_user_model(self):
        """Test the User model."""
        # Create a user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            is_admin=False,
        )

        # Check the user attributes
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.password_hash, "hashed_password")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.is_admin, False)
        self.assertEqual(user.is_active, True)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_api_key_model(self):
        """Test the ApiKey model."""
        # Create an API key
        api_key = ApiKey(
            user_id=1,
            key_name="Test API Key",
            key_prefix="ir-",
            key_hash="hashed_key",
            expires_at=datetime.utcnow() + timedelta(days=365),
        )

        # Check the API key attributes
        self.assertEqual(api_key.user_id, 1)
        self.assertEqual(api_key.key_name, "Test API Key")
        self.assertEqual(api_key.key_prefix, "ir-")
        self.assertEqual(api_key.key_hash, "hashed_key")
        self.assertEqual(api_key.is_active, True)
        self.assertIsNotNone(api_key.expires_at)
        self.assertIsNone(api_key.last_used_at)
        self.assertIsNotNone(api_key.created_at)
        self.assertIsNotNone(api_key.updated_at)

    def test_request_log_model(self):
        """Test the RequestLog model."""
        # Create a request log
        request_log = RequestLog(
            user_id=1,
            api_key_id=1,
            provider="openai",
            model="gpt-3.5-turbo",
            prompt="Hello, world!",
            response="This is a test response.",
            tokens_input=3,
            tokens_output=5,
            latency_ms=100,
            status_code=200,
            ip_address="127.0.0.1",
            user_agent="Test User Agent",
        )

        # Check the request log attributes
        self.assertEqual(request_log.user_id, 1)
        self.assertEqual(request_log.api_key_id, 1)
        self.assertEqual(request_log.provider, "openai")
        self.assertEqual(request_log.model, "gpt-3.5-turbo")
        self.assertEqual(request_log.prompt, "Hello, world!")
        self.assertEqual(request_log.response, "This is a test response.")
        self.assertEqual(request_log.tokens_input, 3)
        self.assertEqual(request_log.tokens_output, 5)
        self.assertEqual(request_log.latency_ms, 100)
        self.assertEqual(request_log.status_code, 200)
        self.assertEqual(request_log.ip_address, "127.0.0.1")
        self.assertEqual(request_log.user_agent, "Test User Agent")
        self.assertIsNone(request_log.error_message)
        self.assertIsNotNone(request_log.created_at)

    def test_provider_config_model(self):
        """Test the ProviderConfig model."""
        # Create a provider config
        provider_config = ProviderConfig(
            provider="openai",
            config_json='{"api_key": "test_api_key"}',
            is_active=True,
        )

        # Check the provider config attributes
        self.assertEqual(provider_config.provider, "openai")
        self.assertEqual(provider_config.config_json, '{"api_key": "test_api_key"}')
        self.assertEqual(provider_config.is_active, True)
        self.assertIsNotNone(provider_config.created_at)
        self.assertIsNotNone(provider_config.updated_at)


if __name__ == "__main__":
    unittest.main()
