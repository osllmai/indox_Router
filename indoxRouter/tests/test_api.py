"""
Tests for the API.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from indoxRouter.main import app


class TestAPI(unittest.TestCase):
    """Test the API."""

    def setUp(self):
        """Set up the test case."""
        self.client = TestClient(app)

        # Mock the AuthManager
        self.auth_manager_mock = MagicMock()
        self.auth_manager_mock.verify_api_key.return_value = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_admin": False,
            "api_key_id": 1,
        }

        # Mock the get_provider function
        self.provider_mock = MagicMock()
        self.provider_mock.generate.return_value = "This is a test response."
        self.provider_mock.list_models.return_value = [
            {
                "id": "gpt-3.5-turbo",
                "provider": "openai",
                "name": "GPT-3.5 Turbo",
            }
        ]

        # Apply the patches
        self.auth_manager_patcher = patch(
            "indoxRouter.main.auth_manager", self.auth_manager_mock
        )
        self.get_provider_patcher = patch(
            "indoxRouter.main.get_provider", return_value=self.provider_mock
        )

        self.auth_manager_patcher.start()
        self.get_provider_patcher.start()

    def tearDown(self):
        """Tear down the test case."""
        self.auth_manager_patcher.stop()
        self.get_provider_patcher.stop()

    def test_root(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to IndoxRouter API"})

    def test_health(self):
        """Test the health endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_completions(self):
        """Test the completions endpoint."""
        response = self.client.post(
            "/v1/completions",
            headers={"Authorization": "Bearer test_api_key"},
            json={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "prompt": "Hello, world!",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["choices"][0]["text"], "This is a test response."
        )

    def test_completions_unauthorized(self):
        """Test the completions endpoint with an unauthorized request."""
        response = self.client.post(
            "/v1/completions",
            json={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "prompt": "Hello, world!",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["message"], "API key is required")

    def test_completions_invalid_api_key(self):
        """Test the completions endpoint with an invalid API key."""
        # Mock the verify_api_key method to return None
        self.auth_manager_mock.verify_api_key.return_value = None

        response = self.client.post(
            "/v1/completions",
            headers={"Authorization": "Bearer invalid_api_key"},
            json={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "prompt": "Hello, world!",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["message"], "Invalid API key")

    def test_list_models(self):
        """Test the list_models endpoint."""
        response = self.client.get(
            "/v1/models",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["id"], "gpt-3.5-turbo")

    def test_list_models_with_provider(self):
        """Test the list_models endpoint with a provider."""
        response = self.client.get(
            "/v1/models?provider=openai",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["id"], "gpt-3.5-turbo")

    def test_list_providers(self):
        """Test the list_providers endpoint."""
        # Mock the os.listdir method
        with patch(
            "os.listdir", return_value=["openai.json", "anthropic.json", "mistral.json"]
        ):
            response = self.client.get(
                "/v1/providers",
                headers={"Authorization": "Bearer test_api_key"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()["data"]), 3)
            self.assertEqual(response.json()["data"][0], "openai")
            self.assertEqual(response.json()["data"][1], "anthropic")
            self.assertEqual(response.json()["data"][2], "mistral")

    def test_get_user(self):
        """Test the get_user endpoint."""
        response = self.client.get(
            "/v1/user",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)
        self.assertEqual(response.json()["email"], "test@example.com")
        self.assertEqual(response.json()["first_name"], "Test")
        self.assertEqual(response.json()["last_name"], "User")
        self.assertEqual(response.json()["is_admin"], False)

    def test_get_user_api_keys(self):
        """Test the get_user_api_keys endpoint."""
        # Mock the get_user_api_keys method
        self.auth_manager_mock.get_user_api_keys.return_value = [
            {
                "id": 1,
                "key_name": "Test API Key",
                "key_prefix": "ir-",
                "is_active": True,
                "expires_at": None,
                "last_used_at": None,
                "created_at": "2021-01-01T00:00:00",
            }
        ]

        response = self.client.get(
            "/v1/user/api-keys",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["id"], 1)
        self.assertEqual(response.json()["data"][0]["key_name"], "Test API Key")

    def test_create_api_key(self):
        """Test the create_api_key endpoint."""
        # Mock the generate_api_key method
        self.auth_manager_mock.generate_api_key.return_value = ("ir-test", 1)

        response = self.client.post(
            "/v1/user/api-keys",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["api_key"], "ir-test")
        self.assertEqual(response.json()["key_id"], 1)

    def test_revoke_api_key(self):
        """Test the revoke_api_key endpoint."""
        # Mock the revoke_api_key method
        self.auth_manager_mock.revoke_api_key.return_value = True

        response = self.client.delete(
            "/v1/user/api-keys/1",
            headers={"Authorization": "Bearer test_api_key"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "API key revoked successfully")


if __name__ == "__main__":
    unittest.main()
