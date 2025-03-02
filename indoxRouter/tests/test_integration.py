import pytest
import os
from pathlib import Path

from indoxRouter.utils.auth import AuthManager
from indoxRouter.client import Client
from indoxRouter.utils.exceptions import InsufficientCreditsError


class TestIntegration:
    """Integration tests for the IndoxRouter system"""

    def test_end_to_end_flow(self, mock_environment):
        """Test the end-to-end flow from user creation to generation"""
        # Create an auth manager
        auth_manager = AuthManager()

        # Create a user with initial balance
        user_id, api_key = auth_manager.create_user(
            email="integration@example.com",
            name="Integration Test User",
            initial_balance=10.0,
        )

        # Create a client with the user's API key
        client = Client(api_key)

        # Store the original _get_provider method
        original_get_provider = client._get_provider

        # Create a mock provider class
        class MockProvider:
            def __init__(self, api_key, model_name):
                self.api_key = api_key
                self.model_name = model_name

            def generate(self, prompt, **kwargs):
                tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
                cost = 1.0  # Fixed cost for testing
                return {
                    "text": f"This is a test response to: {prompt[:30]}...",
                    "cost": cost,
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": kwargs.get("max_tokens", 100),
                        "total_tokens": tokens,
                    },
                    "model": self.model_name,
                }

            def estimate_cost(self, prompt, max_tokens):
                return 1.0  # Fixed cost for testing

        # Replace the _get_provider method with a mock version
        def mock_get_provider(model_name):
            provider, model = model_name.split("/", 1)
            return MockProvider(f"test-{provider}-key", model)

        # Set the mocked method
        client._get_provider = mock_get_provider

        try:
            # Generate a completion
            response = client.generate(
                model_name="openai/gpt-4",
                prompt="Test prompt for integration test",
                max_tokens=100,
            )

            # Check the response
            assert "text" in response
            assert "cost" in response
            assert "remaining_credits" in response
            assert "model" in response
            assert response["text"].startswith(
                "This is a test response to: Test prompt for integration"
            )
            assert response["cost"] == 1.0
            assert response["remaining_credits"] == 9.0  # 10.0 initial - 1.0 cost
            assert response["model"] == "openai/gpt-4"

            # Check that the user's balance was updated
            user = auth_manager.get_user_by_id(user_id)
            assert user["balance"] == 9.0

            # Generate another completion
            response = client.generate(
                model_name="claude/claude-3-opus",
                prompt="Another test prompt",
                max_tokens=100,
            )

            # Check the response
            assert response["cost"] == 1.0
            assert response["remaining_credits"] == 8.0  # 9.0 - 1.0

            # Check that the user's balance was updated
            user = auth_manager.get_user_by_id(user_id)
            assert user["balance"] == 8.0

            # Deduct credits to leave only 1.0
            auth_manager.deduct_credits(user_id, 7.0)

            # Generate another completion (should succeed with exactly enough credits)
            response = client.generate(
                model_name="mistral/mistral-large",
                prompt="Final test prompt",
                max_tokens=100,
            )

            # Check the response
            assert response["cost"] == 1.0
            assert response["remaining_credits"] == 0.0  # 1.0 - 1.0

            # Try to generate another completion (should fail with insufficient credits)
            with pytest.raises(ValueError, match="Insufficient credits"):
                client.generate(
                    model_name="cohere/command-r",
                    prompt="This should fail",
                    max_tokens=100,
                )

        finally:
            # Restore the original method
            client._get_provider = original_get_provider

    def test_multiple_users(self, mock_environment):
        """Test multiple users with different balances"""
        # Create an auth manager
        auth_manager = AuthManager()

        # Create two users with different balances
        user1_id, api_key1 = auth_manager.create_user(
            email="user1@example.com", name="User 1", initial_balance=5.0
        )

        user2_id, api_key2 = auth_manager.create_user(
            email="user2@example.com", name="User 2", initial_balance=20.0
        )

        # Create clients for both users
        client1 = Client(api_key1)
        client2 = Client(api_key2)

        # Mock the provider for both clients
        for client in [client1, client2]:
            # Store the original _get_provider method
            original_get_provider = client._get_provider

            # Create a mock provider class
            class MockProvider:
                def __init__(self, api_key, model_name):
                    self.api_key = api_key
                    self.model_name = model_name

                def generate(self, prompt, **kwargs):
                    tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
                    cost = 2.0  # Fixed cost for testing
                    return {
                        "text": f"This is a test response to: {prompt[:30]}...",
                        "cost": cost,
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": kwargs.get("max_tokens", 100),
                            "total_tokens": tokens,
                        },
                        "model": self.model_name,
                    }

                def estimate_cost(self, prompt, max_tokens):
                    return 2.0  # Fixed cost for testing

            # Replace the _get_provider method with a mock version
            def mock_get_provider(model_name):
                provider, model = model_name.split("/", 1)
                return MockProvider(f"test-{provider}-key", model)

            # Set the mocked method
            client._get_provider = mock_get_provider

        try:
            # User 1 generates a completion
            response1 = client1.generate(
                model_name="openai/gpt-4",
                prompt="Test prompt from user 1",
                max_tokens=100,
            )

            # Check the response
            assert response1["cost"] == 2.0
            assert response1["remaining_credits"] == 3.0  # 5.0 initial - 2.0 cost

            # User 2 generates a completion
            response2 = client2.generate(
                model_name="openai/gpt-4",
                prompt="Test prompt from user 2",
                max_tokens=100,
            )

            # Check the response
            assert response2["cost"] == 2.0
            assert response2["remaining_credits"] == 18.0  # 20.0 initial - 2.0 cost

            # User 1 tries to generate another completion (should fail with insufficient credits)
            with pytest.raises(ValueError, match="Insufficient credits"):
                client1.generate(
                    model_name="openai/gpt-4", prompt="This should fail", max_tokens=100
                )

            # User 2 generates another completion (should succeed)
            response2 = client2.generate(
                model_name="openai/gpt-4",
                prompt="Another test prompt from user 2",
                max_tokens=100,
            )

            # Check the response
            assert response2["cost"] == 2.0
            assert response2["remaining_credits"] == 16.0  # 18.0 - 2.0

            # Check that the users' balances were updated correctly
            user1 = auth_manager.get_user_by_id(user1_id)
            user2 = auth_manager.get_user_by_id(user2_id)

            assert user1["balance"] == 3.0
            assert user2["balance"] == 16.0

        finally:
            # Restore the original methods
            client1._get_provider = client1._get_provider
            client2._get_provider = client2._get_provider

    def test_api_key_deactivation(self, mock_environment):
        """Test that deactivated API keys cannot be used"""
        # Create an auth manager
        auth_manager = AuthManager()

        # Create a user
        user_id, api_key = auth_manager.create_user(
            email="deactivation@example.com",
            name="Deactivation Test User",
            initial_balance=10.0,
        )

        # Create a client with the user's API key
        client = Client(api_key)

        # Deactivate the API key
        auth_manager.deactivate_api_key(api_key)

        # Try to create a new client with the deactivated API key
        with pytest.raises(ValueError, match="Invalid API key or inactive account"):
            Client(api_key)

        # Try to use the existing client (should fail on authentication refresh)
        with pytest.raises(ValueError, match="Invalid API key or inactive account"):
            client.get_balance()
