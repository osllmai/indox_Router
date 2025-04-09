"""
Unit tests for the indoxRouter client.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import the client module
from indoxrouter.client import Client
from indoxrouter.exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderNotFoundError,
    ModelNotFoundError,
    InvalidParametersError,
    RateLimitError,
    ProviderError,
    InsufficientCreditsError,
)


class TestClient(unittest.TestCase):
    """Test the client class."""

    def setUp(self):
        """Set up the test case."""
        self.api_key = "test-api-key"
        self.client = Client(api_key=self.api_key)

        # Mock the session
        self.session_patcher = patch("indoxrouter.client.requests.Session")
        self.mock_session = self.session_patcher.start()
        self.mock_session_instance = self.mock_session.return_value
        self.client.session = self.mock_session_instance

        # Set up common response data
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {"status": "success"}
        self.mock_session_instance.request.return_value = self.mock_response

    def tearDown(self):
        """Tear down the test case."""
        self.session_patcher.stop()

    def test_initialization(self):
        """Test client initialization."""
        # Test with API key
        client = Client(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")

        # Test with environment variable
        with patch.dict(os.environ, {"INDOX_ROUTER_API_KEY": "env-key"}):
            client = Client()
            self.assertEqual(client.api_key, "env-key")

        # Test with missing API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                Client()

    def test_chat(self):
        """Test the chat method."""
        # Mock the response
        chat_response = {
            "request_id": "test-request-id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 100,
            "provider": "openai",
            "model": "gpt-4o-mini",
            "success": True,
            "message": "Success",
            "data": "This is a response",
            "finish_reason": "stop",
            "usage": {
                "tokens_prompt": 10,
                "tokens_completion": 5,
                "tokens_total": 15,
                "cost": 0.0001,
            },
        }
        self.mock_response.json.return_value = chat_response

        # Call the chat method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ]
        response = self.client.chat(messages)

        # Verify the request
        self.mock_session_instance.request.assert_called_once()
        call_args = self.mock_session_instance.request.call_args[0]
        call_kwargs = self.mock_session_instance.request.call_args[1]

        self.assertEqual(call_args[0], "POST")
        self.assertIn("chat/completions", call_args[1])
        self.assertEqual(call_kwargs["json"]["messages"], messages)

        # Verify the response
        self.assertEqual(response, chat_response)

    def test_completion(self):
        """Test the completion method."""
        # Mock the response
        completion_response = {
            "request_id": "test-request-id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 100,
            "provider": "openai",
            "model": "gpt-4o-mini",
            "success": True,
            "message": "Success",
            "data": "This is a response",
            "finish_reason": "stop",
            "usage": {
                "tokens_prompt": 10,
                "tokens_completion": 5,
                "tokens_total": 15,
                "cost": 0.0001,
            },
        }
        self.mock_response.json.return_value = completion_response

        # Call the completion method
        response = self.client.complete("Hello, world!")

        # Verify the request
        self.mock_session_instance.request.assert_called_once()
        call_args = self.mock_session_instance.request.call_args[0]
        call_kwargs = self.mock_session_instance.request.call_args[1]

        self.assertEqual(call_args[0], "POST")
        self.assertIn("completions", call_args[1])
        self.assertEqual(call_kwargs["json"]["prompt"], "Hello, world!")

        # Verify the response
        self.assertEqual(response, completion_response)

    def test_embeddings(self):
        """Test the embeddings method."""
        # Mock the response
        embeddings_response = {
            "request_id": "test-request-id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 100,
            "provider": "openai",
            "model": "text-embedding-3-large",
            "success": True,
            "message": "Success",
            "data": [[0.1, 0.2, 0.3, 0.4, 0.5]],
            "usage": {
                "tokens_prompt": 5,
                "tokens_completion": 0,
                "tokens_total": 5,
                "cost": 0.00005,
            },
        }
        self.mock_response.json.return_value = embeddings_response

        # Call the embeddings method
        response = self.client.embeddings("Hello, world!")

        # Verify the request
        self.mock_session_instance.request.assert_called_once()
        call_args = self.mock_session_instance.request.call_args[0]
        call_kwargs = self.mock_session_instance.request.call_args[1]

        self.assertEqual(call_args[0], "POST")
        self.assertIn("embeddings", call_args[1])
        self.assertEqual(call_kwargs["json"]["input"], "Hello, world!")

        # Verify the response
        self.assertEqual(response, embeddings_response)

    def test_models(self):
        """Test the models method."""
        # Mock the response
        models_response = {
            "models": [
                {
                    "id": "gpt-4o-mini",
                    "provider": "openai",
                    "name": "GPT-4o Mini",
                    "type": "chat",
                    "pricing": {"input_per_token": 0.00015, "output_per_token": 0.0006},
                }
            ]
        }
        self.mock_response.json.return_value = models_response

        # Call the models method
        response = self.client.models()

        # Verify the request
        self.mock_session_instance.request.assert_called_once()
        call_args = self.mock_session_instance.request.call_args[0]

        self.assertEqual(call_args[0], "GET")
        self.assertIn("models", call_args[1])

        # Verify the response
        self.assertEqual(response, models_response)

    def test_handle_errors(self):
        """Test error handling."""
        # Set up error response
        error_response = MagicMock()
        error_response.raise_for_status.side_effect = Exception("Error")
        error_response.status_code = 401
        error_response.json.return_value = {"detail": "Authentication failed"}
        self.mock_session_instance.request.return_value = error_response

        # Test authentication error
        with self.assertRaises(AuthenticationError):
            self.client.chat([{"role": "user", "content": "Hello"}])

        # Test other error types
        error_types = [
            (404, "Provider not found", ProviderNotFoundError),
            (404, "Model not found", ModelNotFoundError),
            (400, "Invalid parameters", InvalidParametersError),
            (429, "Rate limit exceeded", RateLimitError),
            (500, "Provider error", ProviderError),
            (402, "Insufficient credits", InsufficientCreditsError),
            (500, "Unknown error", NetworkError),
        ]

        for status_code, message, error_class in error_types:
            error_response.status_code = status_code
            error_response.json.return_value = {"detail": message}

            with self.assertRaises(error_class):
                self.client.chat([{"role": "user", "content": "Hello"}])

    def test_context_manager(self):
        """Test using the client as a context manager."""
        with Client(api_key=self.api_key) as client:
            self.assertIsInstance(client, Client)
            # Mock the close method to check if it's called
            client.close = MagicMock()

        client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
