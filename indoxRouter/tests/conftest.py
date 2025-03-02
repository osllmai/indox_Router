import os
import pytest
from pathlib import Path
import json
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.auth import AuthManager
from indoxRouter.client import Client


@pytest.fixture
def auth_manager():
    """Fixture for AuthManager with test secret key"""
    return AuthManager(secret_key="test_secret_key")


@pytest.fixture
def test_user(auth_manager):
    """Fixture for creating a test user"""
    user_id, api_key = auth_manager.create_user(
        email="test@example.com", name="Test User", initial_balance=100.0
    )
    return {
        "id": user_id,
        "api_key": api_key,
        "email": "test@example.com",
        "name": "Test User",
        "balance": 100.0,
    }


@pytest.fixture
def mock_provider_configs():
    """Fixture for creating mock provider configs"""
    # Create a temporary directory for test configs
    test_dir = Path(__file__).parent / "test_configs"
    test_dir.mkdir(exist_ok=True)

    # Create mock provider configs
    providers = ["openai", "claude", "mistral", "cohere"]

    for provider in providers:
        config = [
            {
                "modelName": f"{provider}-test-model",
                "type": "chat",
                "inputPricePer1KTokens": 0.01,
                "outputPricePer1KTokens": 0.02,
                "description": f"Test model for {provider}",
                "maxTokens": 4096,
                "promptTemplate": "User: %1\n\nAssistant: %2",
                "systemPrompt": "You are a helpful assistant.",
            }
        ]

        config_path = test_dir / f"{provider}.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

    yield test_dir

    # Clean up
    for provider in providers:
        config_path = test_dir / f"{provider}.json"
        if config_path.exists():
            config_path.unlink()

    if test_dir.exists():
        test_dir.rmdir()


@pytest.fixture
def mock_environment():
    """Fixture for setting up test environment variables"""
    # Save original environment
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "sk-test-openai-key"
    os.environ["ANTHROPIC_API_KEY"] = "sk-test-anthropic-key"
    os.environ["MISTRAL_API_KEY"] = "sk-test-mistral-key"
    os.environ["COHERE_API_KEY"] = "sk-test-cohere-key"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_client(test_user, monkeypatch):
    """Fixture for creating a client with mocked provider"""
    client = Client(test_user["api_key"])

    # Store the original _get_provider method
    original_get_provider = client._get_provider

    # Create a mock provider class
    class MockProvider:
        def __init__(self, api_key, model_name):
            self.api_key = api_key
            self.model_name = model_name

        def generate(self, prompt, **kwargs):
            tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
            cost = tokens * 0.0001  # Example cost calculation
            return {
                "text": f"This is a test response to: {prompt[:30]}...",
                "cost": cost,
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": kwargs.get("max_tokens", 100),
                    "total_tokens": len(prompt.split()) + kwargs.get("max_tokens", 100),
                },
                "model": self.model_name,
            }

        def estimate_cost(self, prompt, max_tokens):
            return (len(prompt.split()) + max_tokens) * 0.0001

    # Replace the _get_provider method with a mock version
    def mock_get_provider(model_name):
        provider, model = model_name.split("/", 1)
        return MockProvider(f"test-{provider}-key", model)

    # Set the mocked method
    client._get_provider = mock_get_provider

    yield client

    # Restore the original method
    client._get_provider = original_get_provider
