"""
Tests for the client.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from indoxRouter.client import Client


class TestClient(unittest.TestCase):
    """Test the client."""

    def setUp(self):
        """Set up the test case."""
        # Mock the AuthManager
        self.auth_manager_mock = MagicMock()
        self.auth_manager_mock.verify_api_key.return_value = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_admin": False,
            "api_key_id": 1,
        }

        # Create a client
        with patch(
            "indoxRouter.client.AuthManager", return_value=self.auth_manager_mock
        ):
            self.client = Client(api_key="test_api_key")

    def test_generate(self):
        """Test generating a response."""
        # Mock the requests module
        with patch("indoxRouter.client.requests") as requests_mock:
            # Mock the response
            response_mock = MagicMock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "choices": [
                    {
                        "text": "This is a test response.",
                    }
                ]
            }
            requests_mock.post.return_value = response_mock

            # Generate a response
            response = self.client.generate(
                provider="openai",
                model="gpt-3.5-turbo",
                prompt="Hello, world!",
                temperature=0.7,
                max_tokens=1000,
            )

            # Check that the response was generated
            self.assertEqual(response, "This is a test response.")

            # Check that the request was made
            requests_mock.post.assert_called_once_with(
                "http://localhost:8000/v1/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test_api_key",
                },
                json={
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "prompt": "Hello, world!",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )

    def test_list_models(self):
        """Test listing models."""
        # Mock the requests module
        with patch("indoxRouter.client.requests") as requests_mock:
            # Mock the response
            response_mock = MagicMock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "data": [
                    {
                        "id": "gpt-3.5-turbo",
                        "provider": "openai",
                        "name": "GPT-3.5 Turbo",
                    }
                ]
            }
            requests_mock.get.return_value = response_mock

            # List models
            models = self.client.list_models(provider="openai")

            # Check that the models were listed
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0]["id"], "gpt-3.5-turbo")
            self.assertEqual(models[0]["provider"], "openai")
            self.assertEqual(models[0]["name"], "GPT-3.5 Turbo")

            # Check that the request was made
            requests_mock.get.assert_called_once_with(
                "http://localhost:8000/v1/models?provider=openai",
                headers={
                    "Authorization": "Bearer test_api_key",
                },
            )

    def test_list_providers(self):
        """Test listing providers."""
        # Mock the requests module
        with patch("indoxRouter.client.requests") as requests_mock:
            # Mock the response
            response_mock = MagicMock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "data": [
                    "openai",
                    "anthropic",
                    "mistral",
                ]
            }
            requests_mock.get.return_value = response_mock

            # List providers
            providers = self.client.list_providers()

            # Check that the providers were listed
            self.assertEqual(len(providers), 3)
            self.assertEqual(providers[0], "openai")
            self.assertEqual(providers[1], "anthropic")
            self.assertEqual(providers[2], "mistral")

            # Check that the request was made
            requests_mock.get.assert_called_once_with(
                "http://localhost:8000/v1/providers",
                headers={
                    "Authorization": "Bearer test_api_key",
                },
            )


if __name__ == "__main__":
    unittest.main()
