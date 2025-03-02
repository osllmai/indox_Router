#!/usr/bin/env python
# Example usage of multiple providers

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.auth import AuthManager
from indoxRouter.client import Client


def setup_environment():
    """Set up environment variables for testing"""
    # Set up dummy provider API keys for testing
    os.environ["OPENAI_API_KEY"] = "sk-dummy-openai-key"
    os.environ["ANTHROPIC_API_KEY"] = "sk-dummy-anthropic-key"
    os.environ["MISTRAL_API_KEY"] = "sk-dummy-mistral-key"
    os.environ["COHERE_API_KEY"] = "sk-dummy-cohere-key"


def mock_provider(client, provider_name):
    """
    Mock a provider to avoid actual API calls

    Args:
        client: Client instance
        provider_name: Provider name to mock
    """
    # Store the original _get_provider method
    original_get_provider = client._get_provider

    # Create a mock provider class
    class MockProvider:
        def __init__(self, api_key, model_name):
            self.api_key = api_key
            self.model_name = model_name
            self.provider_name = provider_name

        def generate(self, prompt, **kwargs):
            tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
            cost = tokens * 0.0001  # Example cost calculation
            return {
                "text": f"[{self.provider_name.upper()}] This is a simulated response to: {prompt[:30]}...",
                "cost": cost,
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": kwargs.get("max_tokens", 100),
                    "total_tokens": len(prompt.split()) + kwargs.get("max_tokens", 100),
                },
            }

        def estimate_cost(self, prompt, max_tokens):
            return (len(prompt.split()) + max_tokens) * 0.0001

    # Replace the _get_provider method with a mock version
    def mock_get_provider(model_name):
        provider, model = model_name.split("/", 1)
        if provider == provider_name:
            return MockProvider(f"dummy-{provider}-key", model)
        return original_get_provider(model_name)

    # Set the mocked method
    client._get_provider = mock_get_provider

    return original_get_provider


def main():
    print("=== IndoxRouter Multi-Provider Example ===")

    # Create an instance of the AuthManager
    auth_manager = AuthManager()

    # Create a new user
    user_id, api_key = auth_manager.create_user(
        email="multi-provider-test@example.com",
        name="Multi-Provider Test User",
        initial_balance=100.0,
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

        # Mock all providers to avoid actual API calls
        original_get_provider = client._get_provider

        # Replace the _get_provider method with a mock version that handles all providers
        def mock_all_providers(model_name):
            provider, model = model_name.split("/", 1)

            class MockProvider:
                def __init__(self, provider_name, model_name):
                    self.provider_name = provider_name
                    self.model_name = model_name

                def generate(self, prompt, **kwargs):
                    tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
                    cost = tokens * 0.0001  # Example cost calculation
                    return {
                        "text": f"[{self.provider_name.upper()}] This is a simulated response from {self.model_name} to: {prompt[:30]}...",
                        "cost": cost,
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": kwargs.get("max_tokens", 100),
                            "total_tokens": len(prompt.split())
                            + kwargs.get("max_tokens", 100),
                        },
                    }

                def estimate_cost(self, prompt, max_tokens):
                    return (len(prompt.split()) + max_tokens) * 0.0001

            return MockProvider(provider, model)

        # Set the mocked method
        client._get_provider = mock_all_providers

        # Test with different providers
        providers = [
            ("openai", "gpt-4"),
            ("claude", "claude-3-opus-20240229"),
            ("mistral", "mistral-large-latest"),
            ("cohere", "command-r-plus"),
        ]

        prompt = "Explain quantum computing in simple terms"

        for provider, model in providers:
            model_name = f"{provider}/{model}"
            print(f"Testing provider: {model_name}")

            try:
                response = client.generate(
                    model_name=model_name, prompt=prompt, max_tokens=200
                )

                print(f"  Response: {response['text']}")
                print(f"  Cost: {response['cost']} credits")
                print(f"  Remaining balance: {response['remaining_credits']} credits")
                print()

            except Exception as e:
                print(f"  Error: {e}")
                print()

        # Restore the original _get_provider method
        client._get_provider = original_get_provider

        # Check final balance
        balance = client.get_balance()
        print(f"Final balance: {balance} credits")

    except ValueError as e:
        print(f"Client initialization failed: {e}")

    print("=== Example Complete ===")


if __name__ == "__main__":
    setup_environment()
    main()
