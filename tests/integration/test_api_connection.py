import os
import pytest
from unittest.mock import patch

from indoxhub import Client
from indoxhub.exceptions import AuthenticationError


@pytest.mark.integration
class TestAPIConnection:
    """Integration tests for API connections."""

    def test_test_connection(self, live_client):
        """Test the test_connection method."""
        # This should successfully connect to the API
        response = live_client.test_connection()

        # Verify the response contains the expected fields
        assert "status" in response
        assert response["status"] == "ok"

    @pytest.mark.skipif(
        not os.environ.get("RUN_LIVE_TESTS"), reason="Live tests disabled"
    )
    def test_models_endpoint(self, live_client):
        """Test the models endpoint (requires live API connection)."""
        response = live_client.models()

        # Verify the response contains the expected structure
        assert "models" in response
        assert isinstance(response["models"], list)

        # If there are models, check the first one has the expected fields
        if response["models"]:
            model = response["models"][0]
            assert "id" in model
            assert "provider" in model

    @pytest.mark.skipif(
        not os.environ.get("RUN_LIVE_TESTS"), reason="Live tests disabled"
    )
    def test_speech_to_text_endpoint_structure(self, live_client):
        """Test that speech-to-text endpoints are accessible (without actual audio file)."""
        # Create a minimal fake audio file data for testing endpoint structure
        fake_audio_data = b"fake_audio_content"

        try:
            # This will likely fail due to invalid audio format, but should reach the endpoint
            response = live_client.speech_to_text(fake_audio_data)
        except Exception as e:
            # We expect this to fail with audio format or validation error, not authentication
            error_msg = str(e).lower()
            # Should not be authentication errors
            assert "authentication" not in error_msg
            assert "unauthorized" not in error_msg
            # Should be a validation or format error
            assert any(
                keyword in error_msg
                for keyword in ["invalid", "format", "audio", "file", "validation"]
            )

    def test_speech_to_text_method_exists(self, live_client):
        """Test that speech-to-text methods exist in the client."""
        # Check that the methods exist
        assert hasattr(live_client, "speech_to_text")
        assert hasattr(live_client, "translate_audio")
        assert callable(getattr(live_client, "speech_to_text"))
        assert callable(getattr(live_client, "translate_audio"))
