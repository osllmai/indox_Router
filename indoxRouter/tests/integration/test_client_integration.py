"""
Integration tests for the indoxRouter client.
These tests require a running indoxRouter server to connect to.
To run these tests:
1. Start the indoxRouter server (docker-compose up -d)
2. Set the INDOX_ROUTER_API_KEY environment variable
3. Run the tests with pytest
"""

import os
import sys
import unittest
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the client
from indoxrouter import Client
from indoxrouter.exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderNotFoundError,
    ModelNotFoundError,
)


class TestClientIntegration(unittest.TestCase):
    """Integration tests for the client."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Get API key from environment variable
        cls.api_key = os.environ.get("INDOX_ROUTER_API_KEY")
        if not cls.api_key:
            raise ValueError(
                "INDOX_ROUTER_API_KEY environment variable is required to run integration tests"
            )

        # Initialize the client
        cls.client = Client(api_key=cls.api_key)

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class."""
        # Close the client
        cls.client.close()

    def test_01_list_models(self):
        """Test listing available models."""
        # Get models
        models = self.client.models()

        # Verify response
        self.assertIn("models", models)
        self.assertTrue(len(models["models"]) > 0)

        # Verify model structure
        model = models["models"][0]
        self.assertIn("id", model)
        self.assertIn("provider", model)
        self.assertIn("name", model)

        # Save a model ID for later tests
        self.__class__.test_model = f"{model['provider']}/{model['id']}"
        logger.info(f"Using model {self.__class__.test_model} for tests")

    def test_02_chat_completion(self):
        """Test chat completion."""
        # Default model test
        response = self.client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say 'Hello, world!' without any extra words.",
                },
            ]
        )

        # Verify response
        self.assertTrue(response["success"])
        self.assertIn("Hello, world", response["data"])

        # Specific model test (if we have a model from the models test)
        if hasattr(self.__class__, "test_model"):
            response = self.client.chat(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "Say 'Hello, model!' without any extra words.",
                    },
                ],
                model=self.__class__.test_model,
            )

            # Verify response
            self.assertTrue(response["success"])
            self.assertIn("Hello, model", response["data"])

            # Verify usage data
            self.assertIn("usage", response)
            self.assertIn("tokens_prompt", response["usage"])
            self.assertIn("tokens_completion", response["usage"])
            self.assertIn("tokens_total", response["usage"])

    def test_03_completion(self):
        """Test text completion."""
        # Simple completion test
        response = self.client.complete("Complete this: Hello,")

        # Verify response
        self.assertTrue(response["success"])
        self.assertIsInstance(response["data"], str)

        # Specific model test (if we have a model from the models test)
        if hasattr(self.__class__, "test_model"):
            response = self.client.complete(
                "Complete this: Hello,", model=self.__class__.test_model
            )

            # Verify response
            self.assertTrue(response["success"])

    def test_04_embeddings(self):
        """Test text embeddings."""
        # Check if embedding models are available
        models = self.client.models()
        embedding_models = [
            f"{model['provider']}/{model['id']}"
            for model in models["models"]
            if "embedding" in model.get("type", "").lower()
        ]

        if not embedding_models:
            self.skipTest("No embedding models available")

        # Use the first available embedding model
        embedding_model = embedding_models[0]
        logger.info(f"Using embedding model {embedding_model}")

        # Get embeddings
        response = self.client.embeddings(
            "This is a test sentence for embeddings.", model=embedding_model
        )

        # Verify response
        self.assertTrue(response["success"])
        self.assertIsInstance(response["data"], list)

        # Check embedding dimensions
        embedding = response["data"][0]
        self.assertIsInstance(embedding, list)
        self.assertTrue(len(embedding) > 0)
        self.assertIsInstance(embedding[0], float)

    def test_05_invalid_model(self):
        """Test using an invalid model."""
        with self.assertRaises(ModelNotFoundError):
            self.client.chat(
                messages=[{"role": "user", "content": "Hello"}],
                model="nonexistent/model",
            )

    def test_06_invalid_provider(self):
        """Test using an invalid provider."""
        with self.assertRaises(ProviderNotFoundError):
            self.client.chat(
                messages=[{"role": "user", "content": "Hello"}],
                model="nonexistent/gpt-4",
            )


class TestClientWithInvalidAuth(unittest.TestCase):
    """Test client with invalid authentication."""

    def test_invalid_api_key(self):
        """Test using an invalid API key."""
        client = Client(api_key="invalid-api-key")

        with self.assertRaises(AuthenticationError):
            client.models()


if __name__ == "__main__":
    # Only run the tests if the API key is configured
    if os.environ.get("INDOX_ROUTER_API_KEY"):
        unittest.main()
    else:
        logger.error(
            "Skipping integration tests: INDOX_ROUTER_API_KEY environment variable is required"
        )
