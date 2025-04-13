"""
Integration tests for API endpoints using mocked providers.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import (
    ChatResponse,
    CompletionResponse,
    EmbeddingResponse,
    ImageResponse,
)
from app.auth.auth_handler import create_access_token


@pytest.fixture
def api_client():
    """Test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def access_token(test_user):
    """Generate a valid access token for test user."""
    return create_access_token(test_user["id"])


@pytest.fixture
def auth_headers(access_token):
    """Authentication headers with bearer token."""
    return {"Authorization": f"Bearer {access_token}"}


class MockProviderResponse:
    """Mock response from provider."""

    @staticmethod
    def chat():
        """Mock chat response."""
        return {
            "id": "mock-chat-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "test-model",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock chat response.",
                    },
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }

    @staticmethod
    def completion():
        """Mock completion response."""
        return {
            "id": "mock-completion-123",
            "object": "text_completion",
            "created": 1677858242,
            "model": "test-model",
            "choices": [
                {
                    "text": "This is a mock completion response.",
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
        }

    @staticmethod
    def embedding():
        """Mock embedding response."""
        return {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0,
                }
            ],
            "model": "test-model",
            "usage": {"prompt_tokens": 5, "total_tokens": 5},
        }

    @staticmethod
    def image():
        """Mock image response."""
        return {
            "created": 1677858242,
            "data": [{"url": "https://example.com/mock-image.png"}],
        }


# Create a mock provider that returns the mock responses
class MockProvider:
    """Mock provider for testing API endpoints."""

    def __init__(self, api_key=None, model=None):
        """Initialize mock provider."""
        self.api_key = api_key
        self.model = model

    async def chat(self, messages, model=None, **kwargs):
        """Mock chat method."""
        return ChatResponse.model_validate(MockProviderResponse.chat())

    async def completion(self, prompt, model=None, **kwargs):
        """Mock completion method."""
        return CompletionResponse.model_validate(MockProviderResponse.completion())

    async def embedding(self, input, model=None, **kwargs):
        """Mock embedding method."""
        return EmbeddingResponse.model_validate(MockProviderResponse.embedding())

    async def image(self, prompt, model=None, **kwargs):
        """Mock image method."""
        return ImageResponse.model_validate(MockProviderResponse.image())


@pytest.mark.integration
class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    @patch("app.api.api.get_provider")
    def test_chat_endpoint(self, mock_get_provider, api_client, auth_headers, mongo_db):
        """Test chat endpoint."""
        # Setup mock
        mock_provider = MockProvider()
        mock_get_provider.return_value = mock_provider

        # Test request
        chat_request = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
        }

        # Send request
        response = api_client.post("/v1/chat", json=chat_request, headers=auth_headers)

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "choices" in data
        assert (
            data["choices"][0]["message"]["content"] == "This is a mock chat response."
        )
        assert "usage" in data
        assert data["usage"]["prompt_tokens"] == 10
        assert data["usage"]["completion_tokens"] == 20
        assert data["usage"]["total_tokens"] == 30

    @patch("app.api.api.get_provider")
    def test_completion_endpoint(
        self, mock_get_provider, api_client, auth_headers, mongo_db
    ):
        """Test completion endpoint."""
        # Setup mock
        mock_provider = MockProvider()
        mock_get_provider.return_value = mock_provider

        # Test request
        completion_request = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "prompt": "Complete this sentence:",
        }

        # Send request
        response = api_client.post(
            "/v1/completion", json=completion_request, headers=auth_headers
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "choices" in data
        assert data["choices"][0]["text"] == "This is a mock completion response."
        assert "usage" in data
        assert data["usage"]["prompt_tokens"] == 15
        assert data["usage"]["completion_tokens"] == 25
        assert data["usage"]["total_tokens"] == 40

    @patch("app.api.api.get_provider")
    def test_embedding_endpoint(
        self, mock_get_provider, api_client, auth_headers, mongo_db
    ):
        """Test embedding endpoint."""
        # Setup mock
        mock_provider = MockProvider()
        mock_get_provider.return_value = mock_provider

        # Test request
        embedding_request = {
            "provider": "openai",
            "model": "text-embedding-ada-002",
            "input": "Test text for embedding",
        }

        # Send request
        response = api_client.post(
            "/v1/embedding", json=embedding_request, headers=auth_headers
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "data" in data
        assert len(data["data"]) == 1
        assert "embedding" in data["data"][0]
        assert len(data["data"][0]["embedding"]) == 5
        assert "usage" in data
        assert data["usage"]["prompt_tokens"] == 5
        assert data["usage"]["total_tokens"] == 5

    @patch("app.api.api.get_provider")
    def test_image_endpoint(
        self, mock_get_provider, api_client, auth_headers, mongo_db
    ):
        """Test image endpoint."""
        # Setup mock
        mock_provider = MockProvider()
        mock_get_provider.return_value = mock_provider

        # Test request
        image_request = {
            "provider": "openai",
            "model": "dall-e-3",
            "prompt": "A test image",
        }

        # Send request
        response = api_client.post(
            "/v1/image", json=image_request, headers=auth_headers
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "data" in data
        assert len(data["data"]) == 1
        assert "url" in data["data"][0]
        assert data["data"][0]["url"] == "https://example.com/mock-image.png"

    def test_user_usage_endpoint(self, api_client, auth_headers, mongo_db, test_user):
        """Test user usage endpoint."""
        # Send request to get user usage
        response = api_client.get("/v1/user/usage", headers=auth_headers)

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_requests" in data
        assert "total_cost" in data
        assert "providers" in data
        assert "models" in data
        assert "endpoints" in data

    def test_models_endpoint(self, api_client, auth_headers, mongo_db):
        """Test models endpoint."""
        # Send request to get models
        response = api_client.get("/v1/models", headers=auth_headers)

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify it's a list
        assert isinstance(data, list)

    def test_providers_endpoint(self, api_client, auth_headers):
        """Test providers endpoint."""
        # Send request to get providers
        response = api_client.get("/v1/providers", headers=auth_headers)

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify it's a list
        assert isinstance(data, list)

        # Verify structure of first provider
        if data:
            provider = data[0]
            assert "name" in provider
            assert "description" in provider
            assert "endpoints" in provider
