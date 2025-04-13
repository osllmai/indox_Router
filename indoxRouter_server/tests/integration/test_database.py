"""
Integration tests for database operations.
"""

import pytest
import asyncio
from datetime import datetime
from bson import ObjectId

from app.db.database import (
    save_conversation,
    get_user_conversations,
    get_conversation,
    delete_conversation,
    get_user_by_id,
    get_user_by_email,
    get_user_by_api_key,
    get_user_usage,
    get_user_cost,
    log_usage,
    get_all_models,
    get_model_by_name,
    get_all_providers,
    get_provider_by_name,
)


@pytest.mark.asyncio
async def test_get_user_by_id(mongo_db):
    """Test retrieving a user by ID"""
    user = await get_user_by_id("test-user-id")

    assert user is not None
    assert user["id"] == "test-user-id"
    assert user["email"] == "test@example.com"
    assert user["full_name"] == "Test User"
    assert len(user["api_keys"]) == 1
    assert user["api_keys"][0]["key"] == "test-api-key"


@pytest.mark.asyncio
async def test_get_user_by_email(mongo_db):
    """Test retrieving a user by email"""
    user = await get_user_by_email("test@example.com")

    assert user is not None
    assert user["id"] == "test-user-id"
    assert user["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_api_key(mongo_db):
    """Test retrieving a user by API key"""
    user = await get_user_by_api_key("test-api-key")

    assert user is not None
    assert user["id"] == "test-user-id"
    assert user["email"] == "test@example.com"
    assert len(user["api_keys"]) > 0
    assert any(key["key"] == "test-api-key" for key in user["api_keys"])


@pytest.mark.asyncio
async def test_save_and_get_conversation(mongo_db):
    """Test saving and retrieving a conversation"""
    conversation_id = "new-conversation-id"
    user_id = "test-user-id"

    # Define a new conversation
    conversation = {
        "id": conversation_id,
        "user_id": user_id,
        "title": "New Test Conversation",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?",
                "created_at": datetime.now().isoformat(),
            }
        ],
    }

    # Save the conversation
    saved = await save_conversation(conversation)
    assert saved is True

    # Retrieve the conversation
    retrieved = await get_conversation(conversation_id, user_id)

    assert retrieved is not None
    assert retrieved["id"] == conversation_id
    assert retrieved["user_id"] == user_id
    assert retrieved["title"] == "New Test Conversation"
    assert len(retrieved["messages"]) == 1
    assert retrieved["messages"][0]["role"] == "user"
    assert retrieved["messages"][0]["content"] == "What is the capital of France?"


@pytest.mark.asyncio
async def test_get_user_conversations(mongo_db):
    """Test retrieving all conversations for a user"""
    user_id = "test-user-id"

    # First add another conversation
    conversation_id = "another-conversation-id"
    conversation = {
        "id": conversation_id,
        "user_id": user_id,
        "title": "Another Test Conversation",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [],
    }
    await save_conversation(conversation)

    # Get all conversations for the user
    conversations = await get_user_conversations(user_id)

    assert conversations is not None
    assert (
        len(conversations) >= 2
    )  # At least the original test conversation and the new one

    # Check if both conversations are present
    conversation_ids = [conv["id"] for conv in conversations]
    assert "test-conversation-1" in conversation_ids
    assert conversation_id in conversation_ids


@pytest.mark.asyncio
async def test_delete_conversation(mongo_db):
    """Test deleting a conversation"""
    user_id = "test-user-id"
    conversation_id = "test-conversation-1"

    # Delete the conversation
    deleted = await delete_conversation(conversation_id, user_id)
    assert deleted is True

    # Try to retrieve the deleted conversation
    retrieved = await get_conversation(conversation_id, user_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_log_and_get_usage(mongo_db):
    """Test logging usage and retrieving usage data"""
    user_id = "test-user-id"

    # Log new usage
    await log_usage(
        user_id=user_id,
        request_id="test-request-3",
        provider="anthropic",
        model="claude-3-opus",
        endpoint="chat",
        input_tokens=150,
        output_tokens=300,
        total_tokens=450,
        input_cost=0.0225,
        output_cost=0.225,
        total_cost=0.2475,
        latency=2.5,
        created_at=datetime.now().isoformat(),
    )

    # Get user usage
    usage = await get_user_usage(user_id)

    assert usage is not None
    # Should have at least 3 usage entries (2 initial + 1 new)
    assert len(usage) >= 3

    # Get user cost
    cost = await get_user_cost(user_id)

    assert cost is not None
    # Should include costs from all usage entries
    assert cost >= 0.2545  # 0.002 + 0.005 + 0.2475


@pytest.mark.asyncio
async def test_get_all_models(mongo_db):
    """Test retrieving all models"""
    models = await get_all_models()

    assert models is not None
    assert len(models) == 3

    model_names = [model["name"] for model in models]
    assert "gpt-4o-mini" in model_names
    assert "mistral-large" in model_names
    assert "claude-3-opus" in model_names


@pytest.mark.asyncio
async def test_get_model_by_name(mongo_db):
    """Test retrieving a model by name"""
    model = await get_model_by_name("gpt-4o-mini")

    assert model is not None
    assert model["name"] == "gpt-4o-mini"
    assert model["provider"] == "openai"
    assert model["display_name"] == "GPT-4o Mini"
    assert "chat" in model["endpoints"]
    assert "completion" in model["endpoints"]
    assert model["context_window"] == 128000
    assert model["pricing"]["input"] == 0.00005
    assert model["pricing"]["output"] == 0.00015


@pytest.mark.asyncio
async def test_get_all_providers(mongo_db):
    """Test retrieving all providers"""
    providers = await get_all_providers()

    assert providers is not None
    assert len(providers) == 3

    provider_names = [provider["name"] for provider in providers]
    assert "openai" in provider_names
    assert "mistral" in provider_names
    assert "anthropic" in provider_names


@pytest.mark.asyncio
async def test_get_provider_by_name(mongo_db):
    """Test retrieving a provider by name"""
    provider = await get_provider_by_name("openai")

    assert provider is not None
    assert provider["name"] == "openai"
    assert provider["display_name"] == "OpenAI"
    assert "chat" in provider["endpoints"]
    assert "completion" in provider["endpoints"]
    assert "embedding" in provider["endpoints"]
    assert "image" in provider["endpoints"]
    assert "gpt-4o-mini" in provider["models"]
