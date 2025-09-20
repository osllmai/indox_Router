import pytest
from unittest.mock import patch, MagicMock, mock_open
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

    def test_speech_to_text_with_file_path(self, client):
        """Test speech-to-text with file path."""
        mock_response = {
            "text": "Hello, this is a test transcription.",
            "success": True,
            "message": "Audio transcribed successfully",
        }

        # Mock file reading
        mock_file_data = b"fake_audio_data"
        with patch("builtins.open", mock_open(read_data=mock_file_data)):
            with patch.object(
                client, "_request", return_value=mock_response
            ) as mock_request:
                # Call the speech_to_text method
                response = client.speech_to_text("test_audio.mp3")

                # Verify the response
                assert response == mock_response

                # Verify the request parameters
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[0][0] == "POST"  # Method
                assert "stt" in call_args[0][1]  # Endpoint contains 'stt'

                # Check that files parameter was passed
                assert "files" in call_args[1]
                files_param = call_args[1]["files"]
                assert "file" in files_param

    def test_speech_to_text_with_bytes(self, client):
        """Test speech-to-text with audio bytes."""
        mock_response = {
            "text": "Hello, this is a test transcription.",
            "success": True,
            "message": "Audio transcribed successfully",
        }

        # Mock audio data as bytes
        audio_data = b"fake_audio_data"

        with patch.object(
            client, "_request", return_value=mock_response
        ) as mock_request:
            # Call the speech_to_text method with bytes
            response = client.speech_to_text(audio_data)

            # Verify the response
            assert response == mock_response

            # Verify the request parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # Method
            assert "stt" in call_args[0][1]  # Endpoint contains 'stt'

            # Check that files parameter was passed
            assert "files" in call_args[1]
            files_param = call_args[1]["files"]
            assert "file" in files_param

    def test_speech_to_text_with_optional_params(self, client):
        """Test speech-to-text with optional parameters."""
        mock_response = {
            "text": "Hello, this is a test transcription.",
            "language": "en",
            "success": True,
        }

        audio_data = b"fake_audio_data"

        with patch.object(
            client, "_request", return_value=mock_response
        ) as mock_request:
            # Call with optional parameters
            response = client.speech_to_text(
                audio_data,
                model="openai/whisper-1",
                language="en",
                response_format="verbose_json",
                temperature=0.5,
                timestamp_granularities=["word", "segment"],
            )

            # Verify the response
            assert response == mock_response

            # Verify the request parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            data_param = call_args[1]["data"]

            # Check that optional parameters were included
            assert data_param["language"] == "en"
            assert data_param["response_format"] == "verbose_json"
            assert data_param["temperature"] == 0.5
            assert "timestamp_granularities" in data_param

    def test_translate_audio(self, client):
        """Test audio translation functionality."""
        mock_response = {
            "text": "Hello, this is a translated text in English.",
            "success": True,
            "message": "Audio translated successfully",
        }

        audio_data = b"fake_audio_data"

        with patch.object(
            client, "_request", return_value=mock_response
        ) as mock_request:
            # Call the translate_audio method
            response = client.translate_audio(audio_data)

            # Verify the response
            assert response == mock_response

            # Verify the request parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # Method
            assert "translations" in call_args[0][1]  # Endpoint contains 'translations'

            # Check that files parameter was passed
            assert "files" in call_args[1]
            files_param = call_args[1]["files"]
            assert "file" in files_param

    def test_speech_to_text_file_not_found(self, client):
        """Test speech-to-text with non-existent file path."""
        from indoxRouter.exceptions import InvalidParametersError

        with pytest.raises(InvalidParametersError, match="File not found"):
            client.speech_to_text("non_existent_file.mp3")

    def test_speech_to_text_invalid_file_type(self, client):
        """Test speech-to-text with invalid file parameter."""
        from indoxRouter.exceptions import InvalidParametersError

        with pytest.raises(
            InvalidParametersError, match="File must be either a file path"
        ):
            client.speech_to_text(123)  # Invalid type
