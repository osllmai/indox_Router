"""
Tests for the Client class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from indoxRouter import Client, ChatMessage
from indoxRouter.exceptions import AuthenticationError


class TestClient(unittest.TestCase):
    """Test cases for the Client class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database for testing
        self.db_path = "test_indoxRouter.db"

        # Mock the database authentication
        self.patcher = patch("indoxRouter.database.Database.authenticate_user")
        self.mock_auth = self.patcher.start()
        self.mock_auth.return_value = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
        }

        # Create a client instance
        self.client = Client(api_key="test_key", db_path=self.db_path)

    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()

        # Remove the test database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, "test_key")
        self.mock_auth.assert_called_once_with("test_key")

    @patch("indoxRouter.client.get_provider")
    def test_chat(self, mock_get_provider):
        """Test the chat method."""
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.chat.return_value = {
            "content": "Hello, I am an AI assistant.",
            "usage": {"total_tokens": 20},
            "cost": 0.0004,
        }
        mock_get_provider.return_value = mock_provider

        # Mock the record_usage method
        with patch.object(self.client.db, "record_usage") as mock_record_usage:
            # Call the chat method
            messages = [ChatMessage(role="user", content="Hello, who are you?")]
            response = self.client.chat(
                messages=messages, provider="openai", model="gpt-3.5-turbo"
            )

            # Check the response
            self.assertEqual(response.content, "Hello, I am an AI assistant.")
            self.assertEqual(response.provider, "openai")
            self.assertEqual(response.model, "gpt-3.5-turbo")
            self.assertEqual(response.usage, {"total_tokens": 20})
            self.assertEqual(response.cost, 0.0004)

            # Check that the provider was called correctly
            mock_provider.chat.assert_called_once()

            # Check that usage was recorded
            mock_record_usage.assert_called_once_with(
                1, "openai", "gpt-3.5-turbo", 20, 0.0004
            )

    @patch("indoxRouter.client.list_available_providers")
    def test_list_providers(self, mock_list_providers):
        """Test the list_providers method."""
        mock_list_providers.return_value = ["openai", "claude", "mistral"]

        providers = self.client.list_providers()

        self.assertEqual(providers, ["openai", "claude", "mistral"])
        mock_list_providers.assert_called_once()

    @patch("indoxRouter.client.list_available_models")
    def test_list_models(self, mock_list_models):
        """Test the list_models method."""
        mock_list_models.return_value = {
            "openai": [{"modelName": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}]
        }

        models = self.client.list_models("openai")

        self.assertEqual(
            models,
            {"openai": [{"modelName": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}]},
        )
        mock_list_models.assert_called_once_with("openai")

    @patch("indoxRouter.client.get_model_info")
    def test_get_model_info(self, mock_get_model_info):
        """Test the get_model_info method."""
        mock_get_model_info.return_value = {
            "modelName": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "type": "Text Generation",
            "inputPricePer1KTokens": 0.003,
            "outputPricePer1KTokens": 0.006,
        }

        model_info = self.client.get_model_info("openai", "gpt-3.5-turbo")

        self.assertEqual(model_info.name, "gpt-3.5-turbo")
        self.assertEqual(model_info.provider, "openai")
        self.assertEqual(model_info.type, "Text Generation")
        self.assertEqual(model_info.input_price_per_1k_tokens, 0.003)
        self.assertEqual(model_info.output_price_per_1k_tokens, 0.006)

        mock_get_model_info.assert_called_once_with("openai", "gpt-3.5-turbo")

    def test_authentication_error(self):
        """Test authentication error handling."""
        self.mock_auth.side_effect = AuthenticationError("Invalid API key.")

        with self.assertRaises(AuthenticationError):
            Client(api_key="invalid_key", db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
