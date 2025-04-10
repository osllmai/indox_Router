"""
Unit tests for the API schemas in IndoxRouter.
These tests ensure that the Pydantic models are correctly defined.
"""

import unittest
import json
from pydantic import ValidationError
import pytest

from app.models.schemas import (
    ChatMessage,
    ChatRequest,
    CompletionRequest,
    EmbeddingRequest,
    ImageRequest,
    TokenRequest,
    Token,
    Usage,
    SuccessResponse,
    ChatResponse,
    CompletionResponse,
    EmbeddingResponse,
    ImageResponse,
    ModelInfo,
    ProviderInfo,
    ErrorResponse,
)


class TestSchemaValidation(unittest.TestCase):
    """Test the Pydantic schema validation."""

    def test_chat_message(self):
        """Test ChatMessage schema validation."""
        # Valid message
        valid_message = {"role": "user", "content": "Hello, world!"}
        message = ChatMessage(**valid_message)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello, world!")

        # Invalid message (missing required field)
        with pytest.raises(ValidationError):
            ChatMessage(content="Hello, world!")

        with pytest.raises(ValidationError):
            ChatMessage(role="user")

    def test_chat_request(self):
        """Test ChatRequest schema validation."""
        # Valid request
        valid_request = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"},
            ],
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
        }
        request = ChatRequest(**valid_request)
        self.assertEqual(len(request.messages), 2)
        self.assertEqual(request.provider, "openai")
        self.assertEqual(request.model, "gpt-3.5-turbo")
        self.assertEqual(request.temperature, 0.7)

        # Invalid request (missing required field)
        with pytest.raises(ValidationError):
            ChatRequest(provider="openai", model="gpt-3.5-turbo")

    def test_completion_request(self):
        """Test CompletionRequest schema validation."""
        # Valid request
        valid_request = {
            "prompt": "Tell me a joke",
            "provider": "openai",
            "model": "gpt-3.5-turbo-instruct",
            "max_tokens": 100,
        }
        request = CompletionRequest(**valid_request)
        self.assertEqual(request.prompt, "Tell me a joke")
        self.assertEqual(request.provider, "openai")
        self.assertEqual(request.model, "gpt-3.5-turbo-instruct")
        self.assertEqual(request.max_tokens, 100)

        # Invalid request (missing required field)
        with pytest.raises(ValidationError):
            CompletionRequest(provider="openai", model="gpt-3.5-turbo-instruct")

    def test_embedding_request(self):
        """Test EmbeddingRequest schema validation."""
        # Valid request with string
        valid_request_str = {
            "text": "Embed this text",
            "provider": "openai",
            "model": "text-embedding-ada-002",
        }
        request_str = EmbeddingRequest(**valid_request_str)
        self.assertEqual(request_str.text, "Embed this text")

        # Valid request with list
        valid_request_list = {
            "text": ["Embed this text", "And this one too"],
            "provider": "openai",
            "model": "text-embedding-ada-002",
        }
        request_list = EmbeddingRequest(**valid_request_list)
        self.assertEqual(len(request_list.text), 2)

        # Invalid request (missing required field)
        with pytest.raises(ValidationError):
            EmbeddingRequest(provider="openai", model="text-embedding-ada-002")

    def test_image_request(self):
        """Test ImageRequest schema validation."""
        # Valid request
        valid_request = {
            "prompt": "A beautiful sunset",
            "provider": "openai",
            "model": "dall-e-3",
            "size": "1024x1024",
            "n": 1,
        }
        request = ImageRequest(**valid_request)
        self.assertEqual(request.prompt, "A beautiful sunset")
        self.assertEqual(request.provider, "openai")
        self.assertEqual(request.model, "dall-e-3")
        self.assertEqual(request.size, "1024x1024")
        self.assertEqual(request.n, 1)

        # Invalid request (missing required field)
        with pytest.raises(ValidationError):
            ImageRequest(provider="openai", model="dall-e-3")

    def test_success_response(self):
        """Test SuccessResponse schema validation."""
        # Valid response
        valid_response = {
            "request_id": "123",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 500.0,
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "success": True,
            "message": "Success",
            "usage": {
                "tokens_prompt": 10,
                "tokens_completion": 20,
                "tokens_total": 30,
                "cost": 0.001,
                "latency": 0.5,
                "timestamp": "2023-01-01T00:00:00Z",
            },
        }
        response = SuccessResponse(**valid_response)
        self.assertEqual(response.request_id, "123")
        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.model, "gpt-3.5-turbo")
        self.assertEqual(response.usage.tokens_total, 30)
        self.assertEqual(response.usage.cost, 0.001)

        # Optional fields can be omitted
        minimal_response = {
            "request_id": "123",
            "created_at": "2023-01-01T00:00:00Z",
            "duration_ms": 500.0,
            "provider": "openai",
            "model": "gpt-3.5-turbo",
        }
        response = SuccessResponse(**minimal_response)
        self.assertEqual(response.request_id, "123")
        self.assertEqual(response.success, True)  # Default value
        self.assertEqual(response.message, "")  # Default value
        self.assertIsNone(response.usage)  # Default value

        # Invalid response (missing required field)
        with pytest.raises(ValidationError):
            SuccessResponse(request_id="123", created_at="2023-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
