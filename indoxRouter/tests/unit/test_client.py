import pytest
from unittest.mock import patch, MagicMock
import os
import json

from indoxRouter import Client
from indoxRouter.exceptions import AuthenticationError


@pytest.mark.unit
class TestClient:
    """Unit tests for the Client class."""

    def test_init_with_api_key(self, api_key):
        """Test client initialization with API key as parameter."""
        client = Client(api_key=api_key)
        assert client.api_key == api_key
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == f"Bearer {api_key}"
        client.close()

    def test_init_with_env_var(self):
        """Test client initialization with API key from environment variable."""
        with patch.dict(os.environ, {"INDOX_ROUTER_API_KEY": "env_api_key"}):
            client = Client()
            assert client.api_key == "env_api_key"
            client.close()

    def test_init_without_api_key(self):
        """Test client initialization without API key raises error."""
        # Temporarily clear the environment variable if it exists
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Client()

    def test_request_success(self, client):
        """Test successful API request."""
        # Mock the response
        with patch("requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"result": "success"}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            # Call the method under test
            result = client._request("GET", "test_endpoint")

            # Verify the result
            assert result == {"result": "success"}
            mock_request.assert_called_once()

    def test_request_auth_error(self, client):
        """Test API request with authentication error."""
        # Mock the response for a 401 error
        with patch("requests.Session.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("401 Client Error")
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Invalid API key"}
            mock_request.return_value = mock_response

            # Patch the requests.HTTPError to simulate the error response
            with patch("requests.HTTPError", MagicMock()) as mock_http_error:
                mock_http_error.return_value.response = mock_response
                mock_response.raise_for_status.side_effect = mock_http_error

                # Call the method under test and verify it raises the correct exception
                with pytest.raises(AuthenticationError):
                    client._request("GET", "test_endpoint")

    def test_close(self, api_key):
        """Test close() method closes the session."""
        client = Client(api_key=api_key)
        with patch.object(client.session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_context_manager(self, api_key):
        """Test client as context manager."""
        with patch.object(Client, "close") as mock_close:
            with Client(api_key=api_key) as client:
                assert isinstance(client, Client)
            mock_close.assert_called_once()

    def test_chat_method(self, client):
        """Test chat method with mocked response."""
        # Create a mock response for the _request method
        mock_response = {
            "id": "chat-12345",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "openai/gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }

        # Mock the _request method
        with patch.object(
            client, "_request", return_value=mock_response
        ) as mock_request:
            # Call the chat method
            messages = [{"role": "user", "content": "Hello"}]
            response = client.chat(messages, model="openai/gpt-4o-mini")

            # Verify the response
            assert response == mock_response

            # Verify the request parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args[0]
            assert call_args[0] == "POST"  # Method
            assert "chat" in call_args[1]  # Endpoint contains 'chat'
