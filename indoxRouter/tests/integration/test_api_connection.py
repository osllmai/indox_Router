import os
import pytest
from unittest.mock import patch

from indoxRouter import Client
from indoxRouter.exceptions import AuthenticationError


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
