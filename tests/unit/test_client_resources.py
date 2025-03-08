"""
Unit tests for client resources (chat, completion, embeddings, images).
"""

import pytest
from unittest.mock import patch, MagicMock

from indoxRouter.models import ChatMessage
from indoxRouter.exceptions import InvalidParametersError, ProviderNotFoundError


class TestChatResource:
    """Tests for the Chat resource."""

    def test_chat_call(self, mock_client, chat_messages, mock_chat_response):
        """Test the chat method."""
        # Mock the _make_request method
        mock_client._make_request = MagicMock(return_value=mock_chat_response)
        
        # Call the chat method
        response = mock_client.chat(
            messages=chat_messages,
            model="openai/gpt-4o-mini",
            temperature=0.7,
            max_tokens=500
        )
        
        # Verify the response
        assert response.data == mock_chat_response['data']
        assert response.model == mock_chat_response['model']
        assert response.provider == mock_chat_response['provider']
        assert response.success == mock_chat_response['success']
        assert response.message == mock_chat_response['message']
        assert response.usage.tokens_prompt == mock_chat_response['usage']['tokens_prompt']
        assert response.usage.tokens_completion == mock_chat_response['usage']['tokens_completion']
        assert response.usage.tokens_total == mock_chat_response['usage']['tokens_total']
        assert response.usage.cost == mock_chat_response['usage']['cost']
        assert response.finish_reason == mock_chat_response['finish_reason']
        assert response.raw_response == mock_chat_response['raw_response']
        
        # Verify the _make_request call
        mock_client._chat._make_request.assert_called_once()

    def test_chat_with_invalid_messages(self, mock_client):
        """Test the chat method with invalid messages."""
        with pytest.raises(InvalidParametersError):
            mock_client.chat(
                messages=[{"invalid_key": "value"}],
                model="openai/gpt-4o-mini"
            )

    def test_chat_with_invalid_model(self, mock_client, chat_messages):
        """Test the chat method with invalid model format."""
        with pytest.raises(InvalidParametersError):
            mock_client.chat(
                messages=chat_messages,
                model="invalid-model-format"
            )

    def test_chat_with_streaming(self, mock_client, chat_messages):
        """Test the chat method with streaming."""
        # Mock the _stream_request method
        mock_client._chat._stream_request = MagicMock(return_value=iter(["chunk1", "chunk2"]))
        
        # Call the chat method with streaming
        generator = mock_client.chat(
            messages=chat_messages,
            model="openai/gpt-4o-mini",
            stream=True,
            return_generator=True
        )
        
        # Verify the generator
        chunks = list(generator)
        assert chunks == ["chunk1", "chunk2"]
        
        # Verify the _stream_request call
        mock_client._chat._stream_request.assert_called_once()


class TestCompletionResource:
    """Tests for the Completion resource."""

    def test_completion_call(self, mock_client, mock_completion_response):
        """Test the completion method."""
        # Mock the _make_request method
        mock_client._make_request = MagicMock(return_value=mock_completion_response)
        
        # Call the completion method
        response = mock_client.completion(
            prompt="Write a short story.",
            model="anthropic/claude-3-haiku",
            temperature=0.7,
            max_tokens=500
        )
        
        # Verify the response
        assert response.data == mock_completion_response['data']
        assert response.model == mock_completion_response['model']
        assert response.provider == mock_completion_response['provider']
        assert response.success == mock_completion_response['success']
        assert response.message == mock_completion_response['message']
        assert response.usage.tokens_prompt == mock_completion_response['usage']['tokens_prompt']
        assert response.usage.tokens_completion == mock_completion_response['usage']['tokens_completion']
        assert response.usage.tokens_total == mock_completion_response['usage']['tokens_total']
        assert response.usage.cost == mock_completion_response['usage']['cost']
        assert response.finish_reason == mock_completion_response['finish_reason']
        assert response.raw_response == mock_completion_response['raw_response']
        
        # Verify the _make_request call
        mock_client._completions._make_request.assert_called_once()

    def test_completion_with_invalid_prompt(self, mock_client):
        """Test the completion method with invalid prompt."""
        with pytest.raises(InvalidParametersError):
            mock_client.completion(
                prompt=123,  # Not a string
                model="anthropic/claude-3-haiku"
            )

    def test_completion_with_invalid_model(self, mock_client):
        """Test the completion method with invalid model format."""
        with pytest.raises(InvalidParametersError):
            mock_client.completion(
                prompt="Write a short story.",
                model="invalid-model-format"
            )

    def test_completion_with_streaming(self, mock_client):
        """Test the completion method with streaming."""
        # Mock the _stream_request method
        mock_client._completions._stream_request = MagicMock(return_value=iter(["chunk1", "chunk2"]))
        
        # Call the completion method with streaming
        generator = mock_client.completion(
            prompt="Write a short story.",
            model="anthropic/claude-3-haiku",
            stream=True,
            return_generator=True
        )
        
        # Verify the generator
        chunks = list(generator)
        assert chunks == ["chunk1", "chunk2"]
        
        # Verify the _stream_request call
        mock_client._completions._stream_request.assert_called_once()


class TestEmbeddingResource:
    """Tests for the Embedding resource."""

    def test_embeddings_call_with_string(self, mock_client, mock_embedding_response):
        """Test the embeddings method with a string."""
        # Mock the _make_request method
        mock_client._make_request = MagicMock(return_value=mock_embedding_response)
        
        # Call the embeddings method
        response = mock_client.embeddings(
            text="This is a test.",
            model="openai/text-embedding-3-small"
        )
        
        # Verify the response
        assert response.data == mock_embedding_response['data']
        assert response.model == mock_embedding_response['model']
        assert response.provider == mock_embedding_response['provider']
        assert response.success == mock_embedding_response['success']
        assert response.message == mock_embedding_response['message']
        assert response.usage.tokens_prompt == mock_embedding_response['usage']['tokens_prompt']
        assert response.usage.tokens_total == mock_embedding_response['usage']['tokens_total']
        assert response.usage.cost == mock_embedding_response['usage']['cost']
        assert response.dimensions == mock_embedding_response['dimensions']
        assert response.raw_response == mock_embedding_response['raw_response']
        
        # Verify the _make_request call
        mock_client._embeddings._make_request.assert_called_once()

    def test_embeddings_call_with_list(self, mock_client, mock_embedding_response):
        """Test the embeddings method with a list of strings."""
        # Mock the _make_request method
        mock_client._make_request = MagicMock(return_value=mock_embedding_response)
        
        # Call the embeddings method
        response = mock_client.embeddings(
            text=["This is a test.", "This is another test."],
            model="openai/text-embedding-3-small"
        )
        
        # Verify the response
        assert response.data == mock_embedding_response['data']
        
        # Verify the _make_request call
        mock_client._embeddings._make_request.assert_called_once()

    def test_embeddings_with_invalid_text(self, mock_client):
        """Test the embeddings method with invalid text."""
        with pytest.raises(InvalidParametersError):
            mock_client.embeddings(
                text=123,  # Not a string or list of strings
                model="openai/text-embedding-3-small"
            )

    def test_embeddings_with_invalid_model(self, mock_client):
        """Test the embeddings method with invalid model format."""
        with pytest.raises(InvalidParametersError):
            mock_client.embeddings(
                text="This is a test.",
                model="invalid-model-format"
            )


class TestImageResource:
    """Tests for the Image resource."""

    def test_image_call(self, mock_client, mock_image_response):
        """Test the image method."""
        # Mock the _make_request method
        mock_client._make_request = MagicMock(return_value=mock_image_response)
        
        # Call the image method
        response = mock_client.image(
            prompt="A futuristic city with flying cars.",
            model="openai/dall-e-3",
            size="1024x1024"
        )
        
        # Verify the response
        assert response.data == mock_image_response['data']
        assert response.model == mock_image_response['model']
        assert response.provider == mock_image_response['provider']
        assert response.success == mock_image_response['success']
        assert response.message == mock_image_response['message']
        assert response.usage.tokens_prompt == mock_image_response['usage']['tokens_prompt']
        assert response.usage.tokens_total == mock_image_response['usage']['tokens_total']
        assert response.usage.cost == mock_image_response['usage']['cost']
        assert response.raw_response == mock_image_response['raw_response']
        
        # Verify the _make_request call
        mock_client._images._make_request.assert_called_once()

    def test_image_with_invalid_prompt(self, mock_client):
        """Test the image method with invalid prompt."""
        with pytest.raises(InvalidParametersError):
            mock_client.image(
                prompt=123,  # Not a string
                model="openai/dall-e-3"
            )

    def test_image_with_invalid_model(self, mock_client):
        """Test the image method with invalid model format."""
        with pytest.raises(InvalidParametersError):
            mock_client.image(
                prompt="A futuristic city with flying cars.",
                model="invalid-model-format"
            )

    def test_image_with_invalid_size(self, mock_client):
        """Test the image method with invalid size."""
        with pytest.raises(InvalidParametersError):
            mock_client.image(
                prompt="A futuristic city with flying cars.",
                model="openai/dall-e-3",
                size="invalid-size"
            ) 