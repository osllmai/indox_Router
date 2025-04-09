"""
Pytest configuration file for client tests.
This file contains fixtures that can be shared across multiple test files.
"""

import os
import sys
import json
import pytest
import logging
import requests
import requests_mock
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_api_key():
    """Return an API key for testing."""
    return os.environ.get("INDOX_ROUTER_API_KEY", "test_api_key")


@pytest.fixture(scope="function")
def mock_session():
    """Create a mocked requests session for testing."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture(scope="session")
def api_base_url():
    """Return the base URL for the IndoxRouter API."""
    return os.environ.get("INDOX_ROUTER_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def sample_models_response():
    """Return a sample response for the models endpoint."""
    return {
        "success": True,
        "models": [
            {
                "id": "gpt-4",
                "provider": "openai",
                "name": "GPT-4",
                "type": "chat",
                "capabilities": ["chat", "completion"],
                "context_length": 8192,
                "description": "OpenAI's GPT-4 model",
            },
            {
                "id": "gpt-3.5-turbo",
                "provider": "openai",
                "name": "GPT-3.5 Turbo",
                "type": "chat",
                "capabilities": ["chat", "completion"],
                "context_length": 4096,
                "description": "OpenAI's GPT-3.5 Turbo model",
            },
            {
                "id": "text-embedding-ada-002",
                "provider": "openai",
                "name": "Ada Embeddings",
                "type": "embedding",
                "capabilities": ["embedding"],
                "context_length": 8191,
                "description": "OpenAI's text embedding model",
            },
        ],
    }


@pytest.fixture(scope="session")
def sample_chat_response():
    """Return a sample response for the chat endpoint."""
    return {
        "success": True,
        "data": "This is a test response from the chat endpoint.",
        "usage": {"tokens_prompt": 10, "tokens_completion": 20, "tokens_total": 30},
    }


@pytest.fixture(scope="session")
def sample_completion_response():
    """Return a sample response for the completion endpoint."""
    return {
        "success": True,
        "data": "This is a test response from the completion endpoint.",
        "usage": {"tokens_prompt": 5, "tokens_completion": 15, "tokens_total": 20},
    }


@pytest.fixture(scope="session")
def sample_embedding_response():
    """Return a sample response for the embedding endpoint."""
    return {
        "success": True,
        "data": [[0.1, 0.2, 0.3, 0.4, 0.5]],
        "usage": {"tokens_prompt": 5, "tokens_total": 5},
    }


@pytest.fixture(scope="session")
def sample_error_response():
    """Return a sample error response."""
    return {
        "success": False,
        "error": {
            "message": "This is a test error message",
            "type": "test_error",
            "code": 400,
        },
    }
