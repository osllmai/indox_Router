#!/usr/bin/env python
"""
Unit tests for conversation-related database functions using mongomock_motor.
Tests the actual database functions against the mocked MongoDB.
"""

import pytest
import asyncio
from datetime import datetime
import sys
import os
import logging
from unittest.mock import patch, MagicMock

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import the database functions to test
from app.db.database import (
    save_conversation,
    get_conversation,
    get_user_conversations,
    update_conversation_title,
    delete_conversation,
)


class TestConversationDatabaseFunctions:
    """Test conversation database functions with mongomock_motor."""

    @pytest.mark.asyncio
    async def test_save_conversation(self, mongo_db):
        """Test saving a new conversation to the database."""
        # Arrange
        user_id = "test-user-id"
        title = "Test Conversation"
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, how can I help you?"},
        ]

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            conversation_id = await save_conversation(user_id, title, messages)

        # Assert
        assert conversation_id is not None

        # Verify the conversation was actually saved
        saved_conversation = await mongo_db.conversations.find_one(
            {"_id": conversation_id}
        )
        assert saved_conversation is not None
        assert saved_conversation["user_id"] == user_id
        assert saved_conversation["title"] == title
        assert len(saved_conversation["messages"]) == len(messages)
        assert "created_at" in saved_conversation
        assert "updated_at" in saved_conversation

    @pytest.mark.asyncio
    async def test_get_conversation(self, mongo_db):
        """Test retrieving a conversation by ID."""
        # Arrange
        user_id = "test-user-id"
        title = "Test Conversation for Retrieval"
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        # First, insert a conversation
        result = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": title,
                "messages": messages,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        conversation_id = result.inserted_id

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            retrieved_conversation = await get_conversation(
                user_id, str(conversation_id)
            )

        # Assert
        assert retrieved_conversation is not None
        assert retrieved_conversation["title"] == title
        assert retrieved_conversation["user_id"] == user_id
        assert len(retrieved_conversation["messages"]) == 2

    @pytest.mark.asyncio
    async def test_get_user_conversations(self, mongo_db):
        """Test retrieving all conversations for a user."""
        # Arrange
        user_id = "test-user-for-multiple-convos"

        # Insert multiple conversations for this user
        conversation_count = 3
        for i in range(conversation_count):
            await mongo_db.conversations.insert_one(
                {
                    "user_id": user_id,
                    "title": f"Conversation {i+1}",
                    "messages": [
                        {"role": "user", "content": f"Message {i+1}"},
                    ],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            )

        # Also add a conversation for a different user
        await mongo_db.conversations.insert_one(
            {
                "user_id": "different-user",
                "title": "Different User's Conversation",
                "messages": [
                    {"role": "user", "content": "This shouldn't be retrieved"}
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            conversations = await get_user_conversations(user_id)

        # Assert
        assert conversations is not None
        assert len(conversations) == conversation_count
        assert all(conv["user_id"] == user_id for conv in conversations)

    @pytest.mark.asyncio
    async def test_update_conversation_title(self, mongo_db):
        """Test updating a conversation title."""
        # Arrange
        user_id = "test-user-id"
        original_title = "Original Title"
        new_title = "Updated Title"

        # Insert a conversation
        result = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": original_title,
                "messages": [{"role": "user", "content": "Hello"}],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        conversation_id = result.inserted_id

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            success = await update_conversation_title(
                user_id, str(conversation_id), new_title
            )

        # Assert
        assert success is True

        # Verify the title was updated
        updated_conversation = await mongo_db.conversations.find_one(
            {"_id": conversation_id}
        )
        assert updated_conversation["title"] == new_title
        assert updated_conversation["title"] != original_title

    @pytest.mark.asyncio
    async def test_delete_conversation(self, mongo_db):
        """Test deleting a conversation."""
        # Arrange
        user_id = "test-user-id"
        title = "Conversation to Delete"

        # Insert a conversation
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

        # Verify it exists before deletion
        before_delete = await mongo_db.conversations.find_one({"_id": conversation_id})
        assert before_delete is not None

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            success = await delete_conversation(user_id, str(conversation_id))

        # Assert
        assert success is True

        # Verify the conversation was deleted
        after_delete = await mongo_db.conversations.find_one({"_id": conversation_id})
        assert after_delete is None

    @pytest.mark.asyncio
    async def test_get_conversation_nonexistent(self, mongo_db):
        """Test retrieving a nonexistent conversation."""
        # Arrange
        user_id = "test-user-id"
        nonexistent_id = "nonexistent-conversation-id"

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            result = await get_conversation(user_id, nonexistent_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_conversation_wrong_user(self, mongo_db):
        """Test updating a conversation with wrong user ID."""
        # Arrange
        user_id = "original-user-id"
        wrong_user_id = "wrong-user-id"
        title = "Original Title"
        new_title = "This Update Should Fail"

        # Insert a conversation
        result = await mongo_db.conversations.insert_one(
            {
                "user_id": user_id,
                "title": title,
                "messages": [{"role": "user", "content": "Hello"}],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        conversation_id = result.inserted_id

        # Act
        # Patch the get_mongo_db function to return our mock db
        with patch("app.db.database.get_mongo_db", return_value=mongo_db):
            success = await update_conversation_title(
                wrong_user_id, str(conversation_id), new_title
            )

        # Assert
        assert success is False

        # Verify the title was not updated
        conversation = await mongo_db.conversations.find_one({"_id": conversation_id})
        assert conversation["title"] == title  # Still the original title
