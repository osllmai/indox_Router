"""
Tests for the OpenAI provider.
"""

import os
import pytest
import json
from unittest.mock import patch, MagicMock

from app.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    """Tests for the OpenAI provider."""

    @pytest.fixture
    def api_key(self):
        """Get the API key from the environment."""
        return os.environ.get("OPENAI_API_KEY", "test_api_key")

    @pytest.fixture
    def provider(self, api_key):
        """Create an OpenAI provider instance."""
        return OpenAIProvider(api_key=api_key, model_name="gpt-3.5-turbo")

    @patch("openai.OpenAI")
    def test_chat(self, mock_openai, provider):
        """Test the chat method."""
        # Mock the response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    role="assistant", content="Hello, how can I help you?"
                ),
                index=0,
                finish_reason="stop",
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
        )

        mock_client.chat.completions.create.return_value = mock_response

        # Call the method
        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat(messages)

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

    @patch("openai.OpenAI")
    def test_complete(self, mock_openai, provider):
        """Test the complete method."""
        # Mock the response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                text="This is a completion",
                index=0,
                finish_reason="stop",
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=5,
            completion_tokens=5,
            total_tokens=10,
        )

        mock_client.completions.create.return_value = mock_response

        # Call the method
        response = provider.complete("Complete this")

        # Check the response
        assert "choices" in response
        assert len(response["choices"]) == 1
        assert response["choices"][0]["text"] == "This is a completion"
        assert "usage" in response
        assert response["usage"]["prompt_tokens"] == 5
        assert response["usage"]["completion_tokens"] == 5
        assert response["usage"]["total_tokens"] == 10

    @patch("openai.OpenAI")
    def test_embed(self, mock_openai, provider):
        """Test the embed method."""
        # Mock the response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_response.usage = MagicMock(
            prompt_tokens=5,
            total_tokens=5,
        )

        mock_client.embeddings.create.return_value = mock_response

        # Call the method
        response = provider.embed("Embed this")

        # Check the response
        assert "embeddings" in response
        assert len(response["embeddings"]) == 1
        assert response["embeddings"][0] == [0.1, 0.2, 0.3]
        assert "dimensions" in response
        assert response["dimensions"] == 3
        assert "usage" in response
        assert response["usage"]["prompt_tokens"] == 5
        assert response["usage"]["total_tokens"] == 5

    @patch("openai.OpenAI")
    def test_generate_image(self, mock_openai, provider):
        """Test the generate_image method."""
        # Mock the response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(url="https://example.com/image.png", revised_prompt=None)
        ]

        mock_client.images.generate.return_value = mock_response

        # Call the method
        response = provider.generate_image("Generate an image")

        # Check the response
        assert "images" in response
        assert len(response["images"]) == 1
        assert response["images"][0]["url"] == "https://example.com/image.png"

    def test_get_token_count(self, provider):
        """Test the get_token_count method."""
        # Call the method
        count = provider.get_token_count("Count tokens in this text")

        # Check the result
        assert isinstance(count, int)
        assert count > 0

    def test_get_model_info(self, provider):
        """Test the get_model_info method."""
        # Call the method
        info = provider.get_model_info()

        # Check the result
        assert "id" in info
        assert info["id"] == "gpt-3.5-turbo"
        assert "name" in info
        assert info["name"] == "gpt-3.5-turbo"
        assert "provider" in info
        assert info["provider"] == "openai"
        assert "capabilities" in info
        assert "chat" in info["capabilities"]
        assert "completion" in info["capabilities"]
