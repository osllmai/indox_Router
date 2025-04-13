"""
Integration tests for database operations.
"""

import pytest
import datetime
from uuid import uuid4

from app.db.database import (
    save_model_usage,
    get_user_model_usage,
    get_user_usage_stats,
    save_model_info,
    get_models,
    get_model,
    save_conversation,
    get_user_conversations,
    get_conversation,
)


@pytest.mark.integration
class TestDatabaseOperations:
    """Integration tests for database operations."""

    def test_save_and_get_model_usage(self, mongo_db, test_user):
        """Test saving and retrieving model usage."""

        # Create a unique request ID
        request_id = str(uuid4())

        # Save model usage
        usage_data = {
            "user_id": test_user["id"],
            "provider": "openai",
            "model": "gpt-4o-mini",
            "tokens_prompt": 25,
            "tokens_completion": 75,
            "tokens_total": 100,
            "cost": 0.005,
            "latency": 0.85,
            "request_id": request_id,
            "request": {
                "endpoint": "chat",
                "messages": [{"role": "user", "content": "Hello"}],
            },
            "response": {"data": "Hi there! How can I help you today?"},
        }

        save_model_usage(**usage_data)

        # Retrieve model usage
        usage = get_user_model_usage(test_user["id"])

        # Find the usage entry we just created
        saved_usage = next(u for u in usage if u["request_id"] == request_id)

        # Verify the data was saved correctly
        assert saved_usage["provider"] == "openai"
        assert saved_usage["model"] == "gpt-4o-mini"
        assert saved_usage["tokens_prompt"] == 25
        assert saved_usage["tokens_completion"] == 75
        assert saved_usage["tokens_total"] == 100
        assert saved_usage["cost"] == 0.005
        assert saved_usage["latency"] == 0.85
        assert saved_usage["request_id"] == request_id
        assert "request" in saved_usage
        assert "response" in saved_usage

    def test_get_user_usage_stats(self, mongo_db, test_user):
        """Test getting user usage statistics."""

        # Create unique request IDs
        request_id1 = str(uuid4())
        request_id2 = str(uuid4())

        # Save model usage entries
        save_model_usage(
            user_id=test_user["id"],
            provider="openai",
            model="gpt-4o-mini",
            tokens_prompt=10,
            tokens_completion=20,
            tokens_total=30,
            cost=0.001,
            latency=0.5,
            request_id=request_id1,
            request={"endpoint": "chat"},
            response={"data": "Response 1"},
        )

        save_model_usage(
            user_id=test_user["id"],
            provider="mistral",
            model="mistral-large-latest",
            tokens_prompt=15,
            tokens_completion=25,
            tokens_total=40,
            cost=0.002,
            latency=0.6,
            request_id=request_id2,
            request={"endpoint": "completion"},
            response={"data": "Response 2"},
        )

        # Get user usage stats
        stats = get_user_usage_stats(test_user["id"])

        # Verify the stats
        assert stats["total_requests"] >= 2  # Could be more if other tests ran
        assert stats["total_cost"] >= 0.003  # Could be more if other tests ran

        # Check providers
        assert "openai" in stats["providers"]
        assert "mistral" in stats["providers"]

        # Check endpoints
        assert "chat" in stats["endpoints"]
        assert "completion" in stats["endpoints"]

        # Check models
        assert "openai/gpt-4o-mini" in stats["models"]
        assert "mistral/mistral-large-latest" in stats["models"]

    def test_save_and_get_model_info(self, mongo_db):
        """Test saving and retrieving model information."""

        # Save model info
        model_data = {
            "provider": "test-provider",
            "name": "test-model",
            "capabilities": ["chat", "completion"],
            "description": "Test model for integration testing",
            "max_tokens": 32000,
            "pricing": {"input": 0.0001, "output": 0.0002},
        }

        save_model_info(**model_data)

        # Get all models
        models = get_models(provider="test-provider")

        # Find our test model
        test_model = next(m for m in models if m["name"] == "test-model")

        # Verify the data
        assert test_model["provider"] == "test-provider"
        assert test_model["name"] == "test-model"
        assert "chat" in test_model["capabilities"]
        assert "completion" in test_model["capabilities"]
        assert test_model["description"] == "Test model for integration testing"
        assert test_model["max_tokens"] == 32000
        assert test_model["pricing"]["input"] == 0.0001
        assert test_model["pricing"]["output"] == 0.0002

        # Get the specific model
        model = get_model(provider="test-provider", name="test-model")
        assert model["name"] == "test-model"

    def test_conversation_operations(self, mongo_db, test_user):
        """Test conversation operations."""

        # Create a conversation
        conversation_id = save_conversation(
            user_id=test_user["id"],
            title="Test Conversation",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
        )

        # Get user conversations
        conversations = get_user_conversations(test_user["id"])

        # Find our test conversation
        test_conversation = next(
            c for c in conversations if c["_id"] == conversation_id
        )

        # Verify the data
        assert test_conversation["title"] == "Test Conversation"
        assert len(test_conversation["messages"]) == 3

        # Get the specific conversation
        conversation = get_conversation(conversation_id)
        assert conversation["title"] == "Test Conversation"
        assert len(conversation["messages"]) == 3
        assert conversation["messages"][0]["role"] == "system"
        assert conversation["messages"][1]["role"] == "user"
        assert conversation["messages"][2]["role"] == "assistant"
