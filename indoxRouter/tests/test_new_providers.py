import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to the path to import from indoxRouter
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from indoxRouter.providers.llama import Provider as LlamaProvider
from indoxRouter.providers.nvidia import Provider as NvidiaProvider
from indoxRouter.providers.deepseek import Provider as DeepseekProvider
from indoxRouter.providers.databricks import Provider as DatabricksProvider


class TestNewProviders(unittest.TestCase):
    """Test the new providers added to IndoxRouter."""

    def setUp(self):
        """Set up the test environment."""
        # Mock API keys
        self.llama_api_key = "test_llama_api_key"
        self.nvidia_api_key = "test_nvidia_api_key"
        self.deepseek_api_key = "test_deepseek_api_key"
        self.databricks_api_key = "test_databricks_api_key"

        # Mock model names
        self.llama_model = "meta-llama-3-70b-instruct"
        self.nvidia_model = "nvidia-tensorrt-llm-mixtral-8x7b-instruct"
        self.deepseek_model = "deepseek-llm-67b-chat"
        self.databricks_model = "databricks-dbrx-instruct"

        # Mock model configs
        self.mock_model_config = {
            "modelName": "test-model",
            "displayName": "Test Model",
            "description": "Test model for unit tests",
            "inputPricePer1KTokens": 0.01,
            "outputPricePer1KTokens": 0.02,
            "contextLength": 8192,
            "systemPrompt": "You are a helpful assistant.",
        }

    @patch("indoxRouter.providers.llama.Provider._load_model_config")
    @patch("requests.post")
    def test_llama_provider(self, mock_post, mock_load_config):
        """Test the Llama provider."""
        # Mock the model config
        mock_load_config.return_value = self.mock_model_config

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"text": "This is a test response from Llama."}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create the provider
        provider = LlamaProvider(self.llama_api_key, self.llama_model)

        # Test generate method
        response = provider.generate("Test prompt")

        # Verify the response
        self.assertIn("text", response)
        self.assertIn("cost", response)
        self.assertIn("usage", response)
        self.assertEqual(response["text"], "This is a test response from Llama.")

        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("completions", args[0])
        self.assertIn("Bearer", kwargs["headers"]["Authorization"])

    @patch("indoxRouter.providers.nvidia.Provider._load_model_config")
    @patch("requests.post")
    def test_nvidia_provider(self, mock_post, mock_load_config):
        """Test the NVIDIA provider."""
        # Mock the model config
        mock_load_config.return_value = self.mock_model_config

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"text": "This is a test response from NVIDIA."}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create the provider
        provider = NvidiaProvider(self.nvidia_api_key, self.nvidia_model)

        # Test generate method
        response = provider.generate("Test prompt")

        # Verify the response
        self.assertIn("text", response)
        self.assertIn("cost", response)
        self.assertIn("usage", response)
        self.assertEqual(response["text"], "This is a test response from NVIDIA.")

        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("completions", args[0])
        self.assertIn("Bearer", kwargs["headers"]["Authorization"])

    @patch("indoxRouter.providers.deepseek.Provider._load_model_config")
    @patch("requests.post")
    def test_deepseek_provider(self, mock_post, mock_load_config):
        """Test the Deepseek provider."""
        # Mock the model config
        mock_load_config.return_value = self.mock_model_config

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"text": "This is a test response from Deepseek."}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create the provider
        provider = DeepseekProvider(self.deepseek_api_key, self.deepseek_model)

        # Test generate method
        response = provider.generate("Test prompt")

        # Verify the response
        self.assertIn("text", response)
        self.assertIn("cost", response)
        self.assertIn("usage", response)
        self.assertEqual(response["text"], "This is a test response from Deepseek.")

        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("completions", args[0])
        self.assertIn("Bearer", kwargs["headers"]["Authorization"])

    @patch("indoxRouter.providers.databricks.Provider._load_model_config")
    @patch("requests.post")
    def test_databricks_provider(self, mock_post, mock_load_config):
        """Test the Databricks provider."""
        # Mock the model config
        mock_load_config.return_value = self.mock_model_config

        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"text": "This is a test response from Databricks."}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create the provider
        provider = DatabricksProvider(self.databricks_api_key, self.databricks_model)

        # Test generate method
        response = provider.generate("Test prompt")

        # Verify the response
        self.assertIn("text", response)
        self.assertIn("cost", response)
        self.assertIn("usage", response)
        self.assertEqual(response["text"], "This is a test response from Databricks.")

        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("completions", args[0])
        self.assertIn("Bearer", kwargs["headers"]["Authorization"])


if __name__ == "__main__":
    unittest.main()
