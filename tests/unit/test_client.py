"""
Unit tests for the Client class.
"""

import pytest
from unittest.mock import patch, MagicMock

from indoxRouter import Client
from indoxRouter.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_init_with_api_key(self, mock_jwt_decode, mock_requests_session):
        """Test client initialization with API key."""
        client = Client(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        assert client._auth_token is not None
        assert client.user_info is not None

    def test_init_with_env_var(self, mock_jwt_decode, mock_requests_session):
        """Test client initialization with environment variable."""
        with patch('os.getenv', return_value="env-api-key"):
            client = Client()
            assert client.api_key == "env-api-key"

    def test_init_without_api_key(self):
        """Test client initialization without API key."""
        with patch('os.getenv', return_value=None):
            with pytest.raises(AuthenticationError):
                Client()

    def test_init_with_custom_params(self, mock_jwt_decode, mock_requests_session):
        """Test client initialization with custom parameters."""
        client = Client(
            api_key="test-api-key",
            base_url="https://custom-api.example.com/v1",
            timeout=30,
            auto_refresh=False
        )
        assert client.base_url == "https://custom-api.example.com/v1"
        assert client.timeout == 30
        assert client.auto_refresh is False


class TestClientAuthentication:
    """Tests for client authentication."""

    def test_authentication_success(self, mock_jwt_decode, mock_requests_session):
        """Test successful authentication."""
        client = Client(api_key="test-api-key")
        assert client._auth_token == "test-token"
        assert client.user_info == {
            'id': 'test-user-id',
            'email': 'test@example.com',
            'plan': 'test-plan'
        }

    def test_authentication_failure(self, mock_jwt_decode):
        """Test authentication failure."""
        with patch('requests.Session') as mock_session:
            session_instance = MagicMock()
            session_instance.post.side_effect = Exception("Connection error")
            mock_session.return_value = session_instance
            
            with pytest.raises(NetworkError):
                Client(api_key="test-api-key")

    def test_token_refresh(self, mock_client):
        """Test token refresh."""
        # Set token to be expired
        mock_client._token_expiry = 0
        
        # Mock datetime.now to return a future time
        with patch('indoxRouter.client.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.timestamp.return_value = 1000
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromtimestamp.return_value = mock_now
            
            # Call a method that triggers token refresh
            mock_client._check_auth()
            
            # Verify that refresh was called
            mock_client.session.post.assert_called_with(
                f"{mock_client.base_url}/auth/refresh",
                timeout=mock_client.timeout
            )


class TestClientRequests:
    """Tests for client requests."""

    def test_make_request_success(self, mock_client):
        """Test successful request."""
        response = mock_client._make_request('GET', 'test-endpoint')
        assert response['data'] == 'test-result'
        mock_client.session.request.assert_called_with(
            method='GET',
            url=f"{mock_client.base_url}/test-endpoint",
            timeout=mock_client.timeout
        )

    def test_make_request_with_params(self, mock_client):
        """Test request with parameters."""
        response = mock_client._make_request(
            'POST', 
            'test-endpoint',
            json={"key": "value"},
            params={"query": "test"}
        )
        assert response['data'] == 'test-result'
        mock_client.session.request.assert_called_with(
            method='POST',
            url=f"{mock_client.base_url}/test-endpoint",
            timeout=mock_client.timeout,
            json={"key": "value"},
            params={"query": "test"}
        )

    def test_make_request_network_error(self, mock_client):
        """Test request with network error."""
        mock_client.session.request.side_effect = Exception("Connection error")
        
        with pytest.raises(NetworkError):
            mock_client._make_request('GET', 'test-endpoint')

    def test_make_request_rate_limit_error(self, mock_client):
        """Test request with rate limit error."""
        # Set rate limit to be exceeded
        mock_client.rate_limits = {
            'test-endpoint': {
                'remaining': 0,
                'reset': 1000
            }
        }
        
        with pytest.raises(RateLimitError):
            mock_client._make_request('GET', 'test-endpoint')


class TestClientMethods:
    """Tests for client methods."""

    def test_providers(self, mock_client):
        """Test providers method."""
        mock_client._make_request = MagicMock(return_value={'data': ['openai', 'anthropic']})
        
        providers = mock_client.providers()
        assert providers == ['openai', 'anthropic']
        mock_client._make_request.assert_called_with('GET', 'providers')

    def test_models(self, mock_client):
        """Test models method."""
        mock_client._make_request = MagicMock(return_value={'data': {'openai': ['gpt-4']}})
        
        # Test without provider
        models = mock_client.models()
        assert models == {'openai': ['gpt-4']}
        mock_client._make_request.assert_called_with('GET', 'models', params=None)
        
        # Test with provider
        models = mock_client.models(provider='openai')
        assert models == {'openai': ['gpt-4']}
        mock_client._make_request.assert_called_with('GET', 'models', params={'provider': 'openai'})

    def test_model_info(self, mock_client):
        """Test model_info method."""
        mock_client._make_request = MagicMock(return_value={'data': {'name': 'gpt-4'}})
        
        model_info = mock_client.model_info('openai', 'gpt-4')
        assert model_info == {'name': 'gpt-4'}
        mock_client._make_request.assert_called_with('GET', 'models/openai/gpt-4')

    def test_model_info_not_found(self, mock_client):
        """Test model_info method with model not found."""
        mock_client._make_request = MagicMock(side_effect=Exception("Model not found"))
        
        with pytest.raises(Exception):
            mock_client.model_info('openai', 'nonexistent-model')

    def test_get_usage(self, mock_client):
        """Test get_usage method."""
        mock_client._make_request = MagicMock(return_value={'data': {'total_tokens': 100}})
        
        usage = mock_client.get_usage()
        assert usage == {'total_tokens': 100}
        mock_client._make_request.assert_called_with('GET', 'usage')

    def test_get_user_info(self, mock_client):
        """Test get_user_info method."""
        mock_client.user_info = {'id': 'test-user-id', 'email': 'test@example.com'}
        
        user_info = mock_client.get_user_info()
        assert user_info == {'id': 'test-user-id', 'email': 'test@example.com'}
        # Ensure we get a copy, not the original
        assert user_info is not mock_client.user_info

    def test_close(self, mock_client):
        """Test close method."""
        mock_client.close()
        mock_client.session.close.assert_called_once()

    def test_context_manager(self, mock_jwt_decode, mock_requests_session):
        """Test client as context manager."""
        with patch('indoxRouter.client.get_config') as mock_get_config:
            config_instance = MagicMock()
            config_instance.JWT_PUBLIC_KEY = 'test-key'
            mock_get_config.return_value = config_instance
            
            with Client(api_key='test-api-key') as client:
                assert client._auth_token is not None
            
            # Verify session was closed
            mock_requests_session.close.assert_called_once() 