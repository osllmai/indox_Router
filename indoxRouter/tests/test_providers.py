import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from indoxRouter.providers.base_provider import BaseProvider
from indoxRouter.utils.exceptions import ModelNotFoundError, RateLimitError


# Test implementation of BaseProvider for testing
class TestProvider(BaseProvider):
    def __init__(self, api_key, model_name):
        super().__init__(api_key, model_name)
        self.model_config = {
            "modelName": model_name,
            "inputPricePer1KTokens": 0.01,
            "outputPricePer1KTokens": 0.02,
        }

    def generate(self, prompt, **kwargs):
        tokens = len(prompt.split()) + kwargs.get("max_tokens", 100)
        cost = self.estimate_cost(prompt, kwargs.get("max_tokens", 100))
        return {
            "text": f"Test response to: {prompt[:30]}...",
            "cost": cost,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": kwargs.get("max_tokens", 100),
                "total_tokens": tokens,
            },
        }

    def estimate_cost(self, prompt, max_tokens):
        prompt_tokens = len(prompt.split())
        prompt_cost = (prompt_tokens / 1000) * self.model_config[
            "inputPricePer1KTokens"
        ]
        completion_cost = (max_tokens / 1000) * self.model_config[
            "outputPricePer1KTokens"
        ]
        return prompt_cost + completion_cost


class TestBaseProvider:
    """Test suite for the BaseProvider class"""

    def test_init(self):
        """Test initializing the base provider"""
        provider = TestProvider("test-api-key", "test-model")
        assert provider.api_key == "test-api-key"
        assert provider.model_name == "test-model"

    def test_validate_response_valid(self):
        """Test validating a valid response"""
        provider = TestProvider("test-api-key", "test-model")
        response = {
            "text": "Test response",
            "cost": 0.01,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }
        validated = provider.validate_response(response)
        assert validated == response

    def test_validate_response_missing_text(self):
        """Test validating a response with missing text field"""
        provider = TestProvider("test-api-key", "test-model")
        response = {
            "cost": 0.01,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }
        with pytest.raises(ValueError, match="missing 'text' field"):
            provider.validate_response(response)

    def test_validate_response_missing_cost(self):
        """Test validating a response with missing cost field"""
        provider = TestProvider("test-api-key", "test-model")
        response = {
            "text": "Test response",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }
        with pytest.raises(ValueError, match="missing 'cost' field"):
            provider.validate_response(response)

    def test_estimate_cost(self):
        """Test estimating the cost of a completion"""
        provider = TestProvider("test-api-key", "test-model")
        prompt = "This is a test prompt with multiple words to count tokens"
        max_tokens = 100
        cost = provider.estimate_cost(prompt, max_tokens)

        # Calculate expected cost
        prompt_tokens = len(prompt.split())
        prompt_cost = (prompt_tokens / 1000) * 0.01
        completion_cost = (max_tokens / 1000) * 0.02
        expected_cost = prompt_cost + completion_cost

        assert cost == expected_cost

    def test_generate(self):
        """Test generating a completion"""
        provider = TestProvider("test-api-key", "test-model")
        prompt = "This is a test prompt"
        max_tokens = 50

        response = provider.generate(prompt, max_tokens=max_tokens)

        assert "text" in response
        assert "cost" in response
        assert "usage" in response
        assert response["text"].startswith("Test response to: This is a test prompt")

        # Check that cost is calculated correctly
        prompt_tokens = len(prompt.split())
        prompt_cost = (prompt_tokens / 1000) * 0.01
        completion_cost = (max_tokens / 1000) * 0.02
        expected_cost = prompt_cost + completion_cost

        assert response["cost"] == expected_cost


# Mock classes for testing specific providers
class MockOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key

    def chat_completions(self, *args, **kwargs):
        return MagicMock()


class MockAnthropic:
    def __init__(self, api_key):
        self.api_key = api_key

    def messages(self):
        return MagicMock()


class MockMistralClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def chat(self, *args, **kwargs):
        return MagicMock()


class MockCohereClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def chat(self, *args, **kwargs):
        return MagicMock()


@pytest.mark.parametrize(
    "provider_name,model_name,mock_class,mock_module",
    [
        ("openai", "gpt-4", MockOpenAI, "openai"),
        ("claude", "claude-3-opus-20240229", MockAnthropic, "anthropic"),
        ("mistral", "mistral-large-latest", MockMistralClient, "mistralai.client"),
        ("cohere", "command-r-plus", MockCohereClient, "cohere"),
    ],
)
def test_provider_initialization(
    provider_name, model_name, mock_class, mock_module, monkeypatch, tmp_path
):
    """Test initializing specific providers"""
    # Create a mock config file
    config_dir = tmp_path / "providers"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / f"{provider_name}.json"
    config_data = [
        {
            "modelName": model_name,
            "type": "chat",
            "inputPricePer1KTokens": 0.01,
            "outputPricePer1KTokens": 0.02,
        }
    ]

    with open(config_file, "w") as f:
        json.dump(config_data, f)

    # Mock the provider module
    mock_module_obj = MagicMock()
    mock_module_obj.Provider = MagicMock()

    # Mock the client class
    monkeypatch.setattr(
        f"indoxRouter.providers.{provider_name}.Path.__file__",
        config_dir / f"{provider_name}.py",
    )

    # Import the provider module
    try:
        module = __import__(
            f"indoxRouter.providers.{provider_name}", fromlist=["Provider"]
        )

        # Mock the client initialization
        monkeypatch.setattr(module, mock_module, mock_class)

        # Initialize the provider
        provider = module.Provider("test-api-key", model_name)

        # Check that the provider was initialized correctly
        assert provider.api_key == "test-api-key"
        assert provider.model_name == model_name

    except ImportError:
        pytest.skip(f"Provider module {provider_name} not available")


def test_provider_model_not_found(tmp_path):
    """Test that ModelNotFoundError is raised when model is not found"""
    # Create a mock config file
    config_dir = tmp_path / "providers"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "test_provider.json"
    config_data = [
        {
            "modelName": "existing-model",
            "type": "chat",
            "inputPricePer1KTokens": 0.01,
            "outputPricePer1KTokens": 0.02,
        }
    ]

    with open(config_file, "w") as f:
        json.dump(config_data, f)

    # Create a test provider that loads from the config file
    class ConfigTestProvider(TestProvider):
        def _load_model_config(self, model_name):
            with open(config_file, "r") as f:
                models = json.load(f)

            for model in models:
                if model.get("modelName") == model_name:
                    return model

            raise ModelNotFoundError(f"Model {model_name} not found")

    # Test with existing model
    provider = ConfigTestProvider("test-api-key", "existing-model")
    assert provider.model_name == "existing-model"

    # Test with non-existing model
    with pytest.raises(ModelNotFoundError):
        ConfigTestProvider("test-api-key", "non-existing-model")
