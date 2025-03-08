"""
Fixtures and configuration for pytest.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from indoxRouter import Client
from indoxRouter.models import ChatMessage, CompletionResponse, EmbeddingResponse, ImageResponse


@pytest.fixture
def mock_jwt_decode():
    """Mock JWT decode to return a valid token payload."""
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {
            'exp': 9999999999,  # Far future expiry
            'user': {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'plan': 'test-plan'
            },
            'rate_limits': {}
        }
        yield mock_decode


@pytest.fixture
def mock_requests_session():
    """Mock requests.Session to return predefined responses."""
    with patch('requests.Session') as mock_session:
        session_instance = MagicMock()
        
        # Mock auth response
        auth_response = MagicMock()
        auth_response.json.return_value = {
            'access_token': 'test-token'
        }
        auth_response.raise_for_status.return_value = None
        session_instance.post.return_value = auth_response
        
        # Mock get response
        get_response = MagicMock()
        get_response.json.return_value = {
            'result': 'test-result',
            'metadata': {}
        }
        get_response.raise_for_status.return_value = None
        session_instance.get.return_value = get_response
        
        # Mock request method
        request_response = MagicMock()
        request_response.json.return_value = {
            'result': 'test-result',
            'metadata': {}
        }
        request_response.raise_for_status.return_value = None
        session_instance.request.return_value = request_response
        
        # Set headers
        session_instance.headers = {}
        
        yield session_instance


@pytest.fixture
def mock_client(mock_jwt_decode, mock_requests_session):
    """Create a client with mocked dependencies."""
    with patch('indoxRouter.client.get_config') as mock_get_config:
        config_instance = MagicMock()
        config_instance.JWT_PUBLIC_KEY = 'test-key'
        mock_get_config.return_value = config_instance
        
        client = Client(api_key='test-api-key')
        yield client


@pytest.fixture
def chat_messages():
    """Sample chat messages for testing."""
    return [
        ChatMessage(role="user", content="Hello, who are you?")
    ]


@pytest.fixture
def mock_chat_response():
    """Sample chat response for testing."""
    return {
        'data': 'I am an AI assistant.',
        'model': 'gpt-4o-mini',
        'provider': 'openai',
        'success': True,
        'message': 'Successfully completed chat request',
        'usage': {
            'tokens_prompt': 10,
            'tokens_completion': 20,
            'tokens_total': 30,
            'cost': 0.0006,
        },
        'finish_reason': 'stop',
        'raw_response': {}
    }


@pytest.fixture
def mock_completion_response():
    """Sample completion response for testing."""
    return {
        'data': 'This is a test completion.',
        'model': 'claude-3-haiku',
        'provider': 'anthropic',
        'success': True,
        'message': 'Successfully completed text completion',
        'usage': {
            'tokens_prompt': 5,
            'tokens_completion': 15,
            'tokens_total': 20,
            'cost': 0.0004,
        },
        'finish_reason': 'stop',
        'raw_response': {}
    }


@pytest.fixture
def mock_embedding_response():
    """Sample embedding response for testing."""
    return {
        'data': [[0.1, 0.2, 0.3, 0.4, 0.5]],
        'model': 'text-embedding-3-small',
        'provider': 'openai',
        'success': True,
        'message': 'Successfully generated embeddings',
        'usage': {
            'tokens_prompt': 5,
            'tokens_completion': 0,
            'tokens_total': 5,
            'cost': 0.0001,
        },
        'dimensions': 5,
        'raw_response': {}
    }


@pytest.fixture
def mock_image_response():
    """Sample image response for testing."""
    return {
        'data': ['https://example.com/image.png'],
        'model': 'dall-e-3',
        'provider': 'openai',
        'success': True,
        'message': 'Successfully generated image',
        'usage': {
            'tokens_prompt': 10,
            'tokens_completion': 0,
            'tokens_total': 10,
            'cost': 0.02,
        },
        'raw_response': {}
    } 