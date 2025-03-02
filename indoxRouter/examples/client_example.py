#!/usr/bin/env python
# Example usage of the client with authentication

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.auth import AuthManager
from indoxRouter.client import Client


def setup_environment():
    """Set up environment variables for testing"""
    # Set up a dummy provider API key for testing
    os.environ["OPENAI_API_KEY"] = "sk-dummy-openai-key"
    os.environ["ANTHROPIC_API_KEY"] = "sk-dummy-anthropic-key"


def main():
    print("=== IndoxRouter Client Example ===")

    # Create an instance of the AuthManager
    auth_manager = AuthManager()

    # Create a new user
    user_id, api_key = auth_manager.create_user(
        email="client-test@example.com", name="Client Test User", initial_balance=100.0
    )

    print(f"Created new user:")
    print(f"  User ID: {user_id}")
    print(f"  API Key: {api_key}")
    print(f"  Initial Balance: 100.0 credits")
    print()

    # Create a client with the user's API key
    try:
        client = Client(api_key)
        print(f"Client initialized successfully")
        print(f"  User: {client.user['name']}")
        print(f"  Balance: {client.user['balance']} credits")
        print()

        # Simulate a completion request
        # Note: In a real scenario, this would call the actual provider
        # For this example, we'll just simulate the process

        print("Simulating completion request...")

        # Mock the provider's generate method to avoid actual API calls
        # In a real scenario, you would use the actual provider
        def mock_generate(provider, prompt, **kwargs):
            tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
            cost = tokens * 0.0001  # Example cost calculation
            return {
                "text": f"This is a simulated response to: {prompt[:30]}...",
                "cost": cost,
                "tokens": tokens,
            }

        # Patch the _get_provider method to return a mock provider
        original_get_provider = client._get_provider

        class MockProvider:
            def __init__(self, api_key, model_name):
                self.api_key = api_key
                self.model_name = model_name

            def generate(self, prompt, **kwargs):
                return mock_generate(self, prompt, **kwargs)

            def estimate_cost(self, prompt, max_tokens):
                return (len(prompt.split()) + max_tokens) * 0.0001

        # Replace the _get_provider method with a mock version
        client._get_provider = lambda model_name: MockProvider(
            "dummy-key", model_name.split("/")[1]
        )

        # Simulate a completion request
        try:
            response = client.generate(
                model_name="openai/gpt-4",
                prompt="Explain quantum computing in simple terms",
                max_tokens=200,
            )

            print(f"Completion successful:")
            print(f"  Model: {response['model']}")
            print(f"  Response: {response['text']}")
            print(f"  Cost: {response['cost']} credits")
            print(f"  Remaining balance: {response['remaining_credits']} credits")
            print()

            # Check balance
            balance = client.get_balance()
            print(f"Current balance: {balance} credits")

            # Get user info
            user_info = client.get_user_info()
            print(f"User info:")
            print(f"  Name: {user_info['name']}")
            print(f"  Email: {user_info['email']}")
            print(f"  Balance: {user_info['balance']} credits")
            print()

        except ValueError as e:
            print(f"Error: {e}")

        # Restore the original _get_provider method
        client._get_provider = original_get_provider

    except ValueError as e:
        print(f"Client initialization failed: {e}")

    print("=== Example Complete ===")


if __name__ == "__main__":
    setup_environment()
    main()
