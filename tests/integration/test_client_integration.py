"""
Integration tests for the Client class.

These tests require valid API keys and will make actual API calls.
They should be skipped by default and only run when explicitly enabled.
"""

import os
import pytest
from unittest.mock import patch

from indoxRouter import Client
from indoxRouter.models import ChatMessage
from indoxRouter.exceptions import AuthenticationError


# Skip all tests in this module by default
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable."
)


@pytest.fixture
def client():
    """Create a client instance with the API key from environment variable."""
    api_key = os.environ.get("INDOX_ROUTER_API_KEY")
    if not api_key:
        pytest.skip("INDOX_ROUTER_API_KEY environment variable not set")
    
    return Client(api_key=api_key)


class TestClientIntegration:
    """Integration tests for the Client class."""

    def test_authentication(self, client):
        """Test authentication with a valid API key."""
        assert client._auth_token is not None
        assert client.user_info is not None

    def test_authentication_failure(self):
        """Test authentication with an invalid API key."""
        with pytest.raises(AuthenticationError):
            Client(api_key="invalid-api-key")

    def test_providers(self, client):
        """Test getting available providers."""
        providers = client.providers()
        assert isinstance(providers, list)
        assert len(providers) > 0

    def test_models(self, client):
        """Test getting available models."""
        models = client.models()
        assert isinstance(models, dict)
        assert len(models) > 0

    def test_model_info(self, client):
        """Test getting model information."""
        # Get the first provider and model
        providers = client.providers()
        provider = providers[0]['id']
        
        provider_models = client.models(provider=provider)
        model = provider_models[provider][0]['id']
        
        model_info = client.model_info(provider=provider, model=model)
        assert model_info is not None


@pytest.mark.skipif(
    os.environ.get("RUN_EXPENSIVE_TESTS") != "1",
    reason="Expensive tests are disabled. Set RUN_EXPENSIVE_TESTS=1 to enable."
)
class TestClientAPIIntegration:
    """Integration tests for the Client API methods that make actual API calls."""

    def test_chat(self, client):
        """Test the chat method."""
        messages = [
            ChatMessage(role="user", content="Hello, who are you?")
        ]
        
        response = client.chat(
            messages=messages,
            model="openai/gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=50
        )
        
        assert response.data is not None
        assert response.model == "gpt-3.5-turbo"
        assert response.provider == "openai"
        assert response.success is True

    def test_completion(self, client):
        """Test the completion method."""
        response = client.completion(
            prompt="Write a short sentence about AI.",
            model="anthropic/claude-instant-1",
            temperature=0.7,
            max_tokens=50
        )
        
        assert response.data is not None
        assert response.model == "claude-instant-1"
        assert response.provider == "anthropic"
        assert response.success is True

    def test_embeddings(self, client):
        """Test the embeddings method."""
        response = client.embeddings(
            text="This is a test.",
            model="openai/text-embedding-ada-002"
        )
        
        assert response.data is not None
        assert len(response.data) > 0
        assert response.model == "text-embedding-ada-002"
        assert response.provider == "openai"
        assert response.success is True

    def test_image(self, client):
        """Test the image method."""
        response = client.image(
            prompt="A simple blue circle on a white background.",
            model="openai/dall-e-2",
            size="256x256"
        )
        
        assert response.data is not None
        assert len(response.data) > 0
        assert response.model == "dall-e-2"
        assert response.provider == "openai"
        assert response.success is True

    def test_streaming(self, client):
        """Test streaming responses."""
        messages = [
            ChatMessage(role="user", content="Count from 1 to 5.")
        ]
        
        generator = client.chat(
            messages=messages,
            model="openai/gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=50,
            stream=True,
            return_generator=True
        )
        
        chunks = []
        for chunk in generator:
            if isinstance(chunk, dict) and chunk.get("is_usage_info"):
                # This is the final usage info
                assert "usage" in chunk
            else:
                # This is a content chunk
                chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0 