"""
Pytest configuration file for the IndoxRouter server tests.
This file contains fixtures and settings shared across multiple test files.
"""

import os
import sys
import pytest
import logging
from dotenv import load_dotenv
import motor.motor_asyncio  # noqa
from mongomock_motor import AsyncMongoMockClient
from unittest.mock import patch, MagicMock

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


# Define a mock get_db_client function if it doesn't exist in database.py
def mock_get_db_client():
    """Mock function for MongoDB client."""
    return AsyncMongoMockClient()


# Import database functions
from app.db.database import (
    init_db,
    get_pg_connection,
    release_pg_connection,
    get_mongo_db,
    init_mongodb,
)
from app.core.config import settings


@pytest.fixture(scope="session")
def db_initialized():
    """Initialize database connections for the test session."""
    logger.info("Initializing database connections for tests")
    if not init_db():
        pytest.fail("Failed to initialize database connections")
    return True


@pytest.fixture(scope="function")
def pg_connection(db_initialized):
    """
    Get a PostgreSQL connection for the test.

    The connection is released after the test, even if it fails.
    """
    conn = get_pg_connection()
    yield conn
    release_pg_connection(conn)


@pytest.fixture(scope="function")
def mongo_db(db_initialized):
    """Get a MongoDB database connection for the test."""
    if not settings.MONGODB_URI:
        pytest.skip("MongoDB URI not configured")
    db = get_mongo_db()
    return db


@pytest.fixture(scope="function")
def test_user(pg_connection):
    """
    Create a test user for testing.

    Returns a dictionary with the user's ID and API key.
    """
    with pg_connection.cursor() as cur:
        # Check if test user exists
        cur.execute("SELECT id FROM users WHERE username = 'test_user'")
        user = cur.fetchone()

        if not user:
            # Create test user
            cur.execute(
                """
                INSERT INTO users (username, email, password, credits, is_active)
                VALUES ('test_user', 'test@example.com', 'password', 100.0, TRUE)
                RETURNING id
                """
            )
            user_id = cur.fetchone()[0]
            pg_connection.commit()
        else:
            user_id = user[0]

        # Create a test API key
        cur.execute(
            """
            INSERT INTO api_keys (user_id, api_key, name)
            VALUES (%s, 'test-api-key-pytest', 'Test Key')
            ON CONFLICT (api_key) DO NOTHING
            RETURNING id, api_key
            """,
            (user_id,),
        )
        result = cur.fetchone()
        if result:
            api_key_id, api_key = result
        else:
            # Key already exists, retrieve it
            cur.execute(
                """
                SELECT id, api_key FROM api_keys 
                WHERE user_id = %s AND name = 'Test Key'
                """,
                (user_id,),
            )
            api_key_id, api_key = cur.fetchone()

        pg_connection.commit()

        return {"id": user_id, "api_key": api_key, "api_key_id": api_key_id}


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "full_name": "Test User",
        "disabled": False,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "api_keys": [
            {
                "key": "test-api-key",
                "name": "Test API Key",
                "created_at": "2023-01-01T00:00:00",
            }
        ],
    }


@pytest.fixture
async def mongo_db():
    """Fixture to provide a mock MongoDB connection for testing."""
    # Create a mock MongoDB client
    mock_client = AsyncMongoMockClient()
    db = mock_client["indoxrouter"]

    # Patch the get_db_client function to return our mock client
    with patch("app.db.database.get_db_client", return_value=mock_client) as _:
        # First try to patch the existing function, but if it doesn't exist,
        # we'll add our mock implementation
        try:
            # Initialize collections
            await init_mongodb(mock_client)
        except AttributeError:
            # If get_db_client doesn't exist in database.py, use our mock
            with patch("app.db.database", new_callable=MagicMock) as mock_db:
                mock_db.get_db_client = mock_get_db_client
                await init_mongodb(mock_client)

        # Populate test data
        # Users collection
        await db.users.insert_one(
            {
                "id": "test-user-id",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "$2b$12$test-hash",  # Dummy hashed password
                "disabled": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "api_keys": [
                    {
                        "key": "test-api-key",
                        "name": "Test API Key",
                        "created_at": "2023-01-01T00:00:00",
                    }
                ],
            }
        )

        # Models collection
        models = [
            {
                "provider": "openai",
                "name": "gpt-4o-mini",
                "display_name": "GPT-4o Mini",
                "description": "Test model for OpenAI",
                "endpoints": ["chat", "completion"],
                "context_window": 128000,
                "pricing": {"input": 0.00005, "output": 0.00015},
            },
            {
                "provider": "mistral",
                "name": "mistral-large",
                "display_name": "Mistral Large",
                "description": "Test model for Mistral",
                "endpoints": ["chat"],
                "context_window": 32000,
                "pricing": {"input": 0.00008, "output": 0.00024},
            },
            {
                "provider": "anthropic",
                "name": "claude-3-opus",
                "display_name": "Claude 3 Opus",
                "description": "Test model for Anthropic",
                "endpoints": ["chat"],
                "context_window": 200000,
                "pricing": {"input": 0.00015, "output": 0.00075},
            },
        ]

        await db.models.insert_many(models)

        # Provider info collection
        providers = [
            {
                "name": "openai",
                "display_name": "OpenAI",
                "description": "Provider for OpenAI models",
                "endpoints": ["chat", "completion", "embedding", "image"],
                "models": ["gpt-4o-mini"],
            },
            {
                "name": "mistral",
                "display_name": "Mistral AI",
                "description": "Provider for Mistral AI models",
                "endpoints": ["chat", "embedding"],
                "models": ["mistral-large"],
            },
            {
                "name": "anthropic",
                "display_name": "Anthropic",
                "description": "Provider for Anthropic models",
                "endpoints": ["chat"],
                "models": ["claude-3-opus"],
            },
        ]

        await db.providers.insert_many(providers)

        # Usage collection - create some test usage data
        usage_entries = [
            {
                "user_id": "test-user-id",
                "request_id": "test-request-1",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "endpoint": "chat",
                "tokens": 100,
                "cost": 0.002,
                "latency": 1.5,
                "created_at": "2023-01-01T00:00:00",
            },
            {
                "user_id": "test-user-id",
                "request_id": "test-request-2",
                "provider": "mistral",
                "model": "mistral-large",
                "endpoint": "chat",
                "tokens": 200,
                "cost": 0.005,
                "latency": 2.1,
                "created_at": "2023-01-02T00:00:00",
            },
        ]

        await db.usage.insert_many(usage_entries)

        # Conversations collection - create a test conversation
        conversations = [
            {
                "id": "test-conversation-1",
                "user_id": "test-user-id",
                "title": "Test Conversation",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T01:00:00",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "created_at": "2023-01-01T00:00:00",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi there! How can I help you?",
                        "created_at": "2023-01-01T00:00:05",
                    },
                ],
            }
        ]

        await db.conversations.insert_many(conversations)

        yield db


@pytest.fixture
def patch_providers():
    """Patch the provider classes for testing."""
    # Create a MagicMock for each provider class
    with (
        patch("app.providers.openai_provider.OpenAIProvider") as mock_openai,
        patch("app.providers.mistral_provider.MistralProvider") as mock_mistral,
        patch("app.providers.anthropic_provider.AnthropicProvider") as mock_anthropic,
    ):

        # Configure the mocks
        mock_providers = {
            "openai": mock_openai,
            "mistral": mock_mistral,
            "anthropic": mock_anthropic,
        }

        yield mock_providers
