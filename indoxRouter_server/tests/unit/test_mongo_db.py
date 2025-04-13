#!/usr/bin/env python
"""
Unit tests for MongoDB operations using mongomock_motor.
This file demonstrates using the mongomock_motor fixture for testing.
"""

import pytest
import asyncio
from datetime import datetime
import sys
import os
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import MongoDB functions from the database module
from app.db.database import (
    save_conversation,
    get_conversation,
    get_user_conversations,
    update_conversation_title,
    delete_conversation,
)
from app.models.schemas import ChatMessage, ChatRequest, UsageResponse


class TestMongoDBOperations:
    """Test MongoDB operations using mongomock_motor."""

    @pytest.mark.asyncio
    async def test_save_and_get_conversation(self, mongo_db):
        """Test saving and retrieving a conversation."""
        # Create test data
        user_id = "test-user-id"
        title = "Test Conversation Title"
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        ]

        # Save the conversation
        conversation_id = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": title,
                "messages": messages,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )

        # Retrieve the conversation
        conversation = await mongo_db.conversations.find_one(
            {"_id": conversation_id.inserted_id}
        )

        # Assertions
        assert conversation is not None
        assert conversation["user_id"] == user_id
        assert conversation["title"] == title
        assert len(conversation["messages"]) == 3
        assert conversation["messages"][0]["role"] == "system"
        assert conversation["messages"][1]["role"] == "user"
        assert conversation["messages"][2]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_get_user_conversations(self, mongo_db):
        """Test retrieving all conversations for a user."""
        # Create test user
        user_id = "test-user-id-2"

        # Create multiple conversations for the user
        conversation_data = [
            {
                "user_id": user_id,
                "title": f"Conversation {i}",
                "messages": [
                    {"role": "user", "content": f"Message {i}"},
                    {"role": "assistant", "content": f"Response {i}"},
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            for i in range(1, 4)  # Create 3 conversations
        ]

        # Insert conversations
        await mongo_db.conversations.insert_many(conversation_data)

        # Retrieve all conversations for the user
        cursor = mongo_db.conversations.find({"user_id": user_id})
        conversations = [doc async for doc in cursor]

        # Assertions
        assert len(conversations) == 3
        assert all(conv["user_id"] == user_id for conv in conversations)

    @pytest.mark.asyncio
    async def test_update_conversation(self, mongo_db):
        """Test updating a conversation title."""
        # Create a test conversation
        user_id = "test-user-id-3"
        original_title = "Original Title"
        new_title = "Updated Title"

        # Insert the conversation
        result = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": original_title,
                "messages": [{"role": "user", "content": "Test message"}],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        conversation_id = result.inserted_id

        # Update the conversation title
        await mongo_db.conversations.update_one(
            {"_id": conversation_id},
            {"$set": {"title": new_title, "updated_at": datetime.now().isoformat()}},
        )

        # Retrieve the updated conversation
        updated_conversation = await mongo_db.conversations.find_one(
            {"_id": conversation_id}
        )

        # Assertions
        assert updated_conversation is not None
        assert updated_conversation["title"] == new_title
        assert updated_conversation["title"] != original_title

    @pytest.mark.asyncio
    async def test_delete_conversation(self, mongo_db):
        """Test deleting a conversation."""
        # Create a test conversation
        user_id = "test-user-id-4"
        title = "Conversation to Delete"

        # Insert the conversation
        result = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": title,
                "messages": [{"role": "user", "content": "Delete me"}],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        conversation_id = result.inserted_id

        # Verify the conversation exists
        conversation = await mongo_db.conversations.find_one({"_id": conversation_id})
        assert conversation is not None

        # Delete the conversation
        await mongo_db.conversations.delete_one({"_id": conversation_id})

        # Verify the conversation was deleted
        deleted_conversation = await mongo_db.conversations.find_one(
            {"_id": conversation_id}
        )
        assert deleted_conversation is None

    @pytest.mark.asyncio
    async def test_usage_data_aggregation(self, mongo_db):
        """Test aggregating usage data from MongoDB."""
        # Create test usage data
        user_id = "test-user-id-5"
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Insert usage data
        usage_entries = [
            {
                "user_id": user_id,
                "request_id": f"req-{i}",
                "provider": "openai" if i % 2 == 0 else "mistral",
                "model": "gpt-4o" if i % 2 == 0 else "mistral-large",
                "endpoint": "chat",
                "tokens": 100 * i,
                "input_tokens": 50 * i,
                "output_tokens": 50 * i,
                "cost": 0.001 * i,
                "latency": 1.0 + (0.1 * i),
                "created_at": current_date,
            }
            for i in range(1, 6)  # Create 5 usage entries
        ]

        await mongo_db.usage.insert_many(usage_entries)

        # Perform aggregation to get total usage by provider
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$provider",
                    "total_tokens": {"$sum": "$tokens"},
                    "total_cost": {"$sum": "$cost"},
                    "request_count": {"$sum": 1},
                }
            },
        ]

        results = [doc async for doc in mongo_db.usage.aggregate(pipeline)]

        # Assertions
        assert len(results) == 2  # Should have data for both providers

        # Verify we have results for both providers
        provider_results = {result["_id"]: result for result in results}
        assert "openai" in provider_results
        assert "mistral" in provider_results

        # Verify the totals
        assert provider_results["openai"]["request_count"] == 3  # 0, 2, 4
        assert provider_results["mistral"]["request_count"] == 2  # 1, 3
