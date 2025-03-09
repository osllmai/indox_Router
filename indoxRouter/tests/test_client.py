"""
Tests for the indoxRouter client.
"""

import os
import pytest
import json
from unittest.mock import patch, MagicMock

from indoxrouter import Client
from indoxrouter.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError,
)


class TestClient:
    """Tests for the indoxRouter client."""

    @pytest.fixture
    def api_key(self):
        """Get the API key from the environment."""
        return os.environ.get("INDOXROUTER_API_KEY", "test_api_key")

    @pytest.fixture
    def client(self, api_key):
        """Create a client instance."""
        return Client(api_key=api_key, base_url="http://localhost:8000")

    @patch("requests.Session.request")
    def test_chat(self, mock_request, client):
        """Test the chat method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello, how can I help you?",
                    },
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
            },
            "request_id": "test_request_id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 100,
            "provider": "openai",
            "model": "gpt-3.5-turbo",
        }
        mock_request.return_value = mock_response

        # Call the method
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat(messages)

        # Check the response
        assert "choices" in response
        assert len(response["choices"]) == 1
        assert response["choices"][0]["message"]["role"] == "assistant"
        assert (
            response["choices"][0]["message"]["content"] == "Hello, how can I help you?"
        )
        assert "usage" in response
        assert response["usage"]["prompt_tokens"] == 10
        assert response["usage"]["completion_tokens"] == 10
        assert response["usage"]["total_tokens"] == 20

    @patch("requests.Session.request")
    def test_completion(self, mock_request, client):
        """Test the completion method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "text": "This is a completion",
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 5,
                "total_tokens": 10,
            },
            "request_id": "test_request_id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 50,
            "provider": "openai",
            "model": "gpt-3.5-turbo-instruct",
        }
        mock_request.return_value = mock_response

        # Call the method
        response = client.completion("Complete this")

        # Check the response
        assert "choices" in response
        assert len(response["choices"]) == 1
        assert response["choices"][0]["text"] == "This is a completion"
        assert "usage" in response
        assert response["usage"]["prompt_tokens"] == 5
        assert response["usage"]["completion_tokens"] == 5
        assert response["usage"]["total_tokens"] == 10

    @patch("requests.Session.request")
    def test_embeddings(self, mock_request, client):
        """Test the embeddings method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2, 0.3]],
            "dimensions": 3,
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5,
            },
            "request_id": "test_request_id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 20,
            "provider": "openai",
            "model": "text-embedding-ada-002",
        }
        mock_request.return_value = mock_response

        # Call the method
        response = client.embeddings("Embed this")

        # Check the response
        assert "embeddings" in response
        assert len(response["embeddings"]) == 1
        assert response["embeddings"][0] == [0.1, 0.2, 0.3]
        assert "dimensions" in response
        assert response["dimensions"] == 3
        assert "usage" in response
        assert response["usage"]["prompt_tokens"] == 5
        assert response["usage"]["total_tokens"] == 5

    @patch("requests.Session.request")
    def test_images(self, mock_request, client):
        """Test the images method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "images": [
                {
                    "url": "https://example.com/image.png",
                    "revised_prompt": None,
                }
            ],
            "request_id": "test_request_id",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 1000,
            "provider": "openai",
            "model": "dall-e-3",
        }
        mock_request.return_value = mock_response

        # Call the method
        response = client.images("Generate an image")

        # Check the response
        assert "images" in response
        assert len(response["images"]) == 1
        assert response["images"][0]["url"] == "https://example.com/image.png"

    @patch("requests.Session.request")
    def test_models(self, mock_request, client):
        """Test the models method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "OpenAI models",
                "capabilities": ["chat", "completion", "embedding", "image"],
                "models": [
                    {
                        "id": "gpt-3.5-turbo",
                        "name": "GPT-3.5 Turbo",
                        "provider": "openai",
                        "capabilities": ["chat", "completion"],
                    }
                ],
            }
        ]
        mock_request.return_value = mock_response

        # Call the method
        response = client.models()

        # Check the response
        assert isinstance(response, list)
        assert len(response) == 1
        assert response[0]["id"] == "openai"
        assert "models" in response[0]
        assert len(response[0]["models"]) == 1
        assert response[0]["models"][0]["id"] == "gpt-3.5-turbo"

    @patch("requests.Session.request")
    def test_authentication_error(self, mock_request, client):
        """Test authentication error handling."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "detail": "Invalid authentication credentials",
        }
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        # Call the method and check the exception
        with pytest.raises(AuthenticationError):
            client.chat([{"role": "user", "content": "Hello"}])

    @patch("requests.Session.request")
    def test_rate_limit_error(self, mock_request, client):
        """Test rate limit error handling."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "detail": "Rate limit exceeded",
        }
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        # Call the method and check the exception
        with pytest.raises(RateLimitError):
            client.chat([{"role": "user", "content": "Hello"}])

    @patch("requests.Session.request")
    def test_provider_not_found_error(self, mock_request, client):
        """Test provider not found error handling."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "detail": "Provider 'nonexistent' not found",
        }
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        # Call the method and check the exception
        with pytest.raises(ProviderNotFoundError):
            client.chat(
                [{"role": "user", "content": "Hello"}],
                provider="nonexistent",
            )

    @patch("requests.Session.request")
    def test_model_not_found_error(self, mock_request, client):
        """Test model not found error handling."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "detail": "Model 'nonexistent' not found for provider 'openai'",
        }
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        # Call the method and check the exception
        with pytest.raises(ModelNotFoundError):
            client.chat(
                [{"role": "user", "content": "Hello"}],
                provider="openai",
                model="nonexistent",
            )

    @patch("requests.Session.request")
    def test_invalid_parameters_error(self, mock_request, client):
        """Test invalid parameters error handling."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "detail": "Invalid parameters: temperature must be between 0 and 1",
        }
        mock_request.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        # Call the method and check the exception
        with pytest.raises(InvalidParametersError):
            client.chat(
                [{"role": "user", "content": "Hello"}],
                temperature=2.0,
            )

    def test_context_manager(self, api_key):
        """Test the client as a context manager."""
        with Client(api_key=api_key, base_url="http://localhost:8000") as client:
            assert client is not None
            assert client.api_key == api_key
            assert client.base_url == "http://localhost:8000"
