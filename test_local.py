#!/usr/bin/env python
"""
Test script for local testing of IndoxRouter client with server.
This script tests the basic functionality of the IndoxRouter client
against a locally running server.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import indoxrouter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from indoxrouter import Client

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv()

# Use a test API key or get from environment
api_key = os.environ.get("INDOXROUTER_API_KEY", "test-api-key-for-local-development")


def test_health():
    """Test the health check endpoint."""
    try:
        client = Client(api_key=api_key)
        response = client._request("GET", "/")
        print("Health check response:", response)
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_models():
    """Test retrieving models."""
    try:
        client = Client(api_key=api_key)
        models = client.models()
        print(f"Retrieved {len(models)} models:")
        for model in models[:5]:  # Print first 5 models
            print(f"- {model.get('id', 'Unknown')}")
        return True
    except Exception as e:
        print(f"Models retrieval failed: {e}")
        return False


def test_chat():
    """Test chat completion."""
    try:
        client = Client(api_key=api_key)
        response = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"},
            ],
            provider="openai",  # Specify provider for testing
            model="gpt-3.5-turbo",  # Specify model for testing
        )
        print("Chat response:")
        if "choices" in response and len(response["choices"]) > 0:
            print(response["choices"][0]["message"]["content"])
        else:
            print(response)
        return True
    except Exception as e:
        print(f"Chat completion failed: {e}")
        return False


def test_embeddings():
    """Test embeddings."""
    try:
        client = Client(api_key=api_key)
        response = client.embeddings(
            text="This is a test sentence for embeddings.",
            provider="openai",
            model="text-embedding-ada-002",
        )
        print(f"Embedding dimensions: {response.get('dimensions', 'Unknown')}")
        if "embeddings" in response and len(response["embeddings"]) > 0:
            print(f"First few values: {response['embeddings'][0][:5]}")
        else:
            print("No embeddings returned")
        return True
    except Exception as e:
        print(f"Embeddings test failed: {e}")
        return False


def test_images():
    """Test image generation."""
    try:
        client = Client(api_key=api_key)
        response = client.images(
            prompt="A beautiful sunset over mountains",
            provider="openai",
            model="dall-e-3",
        )
        print("Image generation response:")
        if "images" in response and len(response["images"]) > 0:
            print(f"Image URL: {response['images'][0].get('url', 'No URL')}")
        else:
            print(response)
        return True
    except Exception as e:
        print(f"Image generation test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing IndoxRouter client with local server")
    print(f"Using API key: {api_key}")
    print(
        f"Base URL from constants: {os.environ.get('INDOXROUTER_BASE_URL', 'default from constants.py')}"
    )

    # Run tests
    health_result = test_health()
    print("\nHealth check test:", "PASSED" if health_result else "FAILED")

    if health_result:
        models_result = test_models()
        print("\nModels test:", "PASSED" if models_result else "FAILED")

        chat_result = test_chat()
        print("\nChat test:", "PASSED" if chat_result else "FAILED")

        embeddings_result = test_embeddings()
        print("\nEmbeddings test:", "PASSED" if embeddings_result else "FAILED")

        images_result = test_images()
        print("\nImage generation test:", "PASSED" if images_result else "FAILED")

    print("\nAll tests completed.")
