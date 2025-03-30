#!/usr/bin/env python
"""
Test script for local testing of IndoxRouter client with server.
This script tests the basic functionality of the IndoxRouter client
against a locally running server.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add the parent directory to the path so we can import indoxrouter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from indoxrouter import Client

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv()

# Use the test API key for development mode
TEST_API_KEY = "test-api-key-for-local-development"


def get_auth_token():
    """Get an authentication token from the server."""
    try:
        # Default credentials from the mock users database in auth.py
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "admin"},
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        print(f"Failed to get authentication token: {e}")
        return None


def test_health():
    """Test the health check endpoint."""
    try:
        # Direct request to health check endpoint
        response = requests.get("http://localhost:8000/")
        response.raise_for_status()
        print("Health check response:", response.json())
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_models():
    """Test retrieving models."""
    try:
        # Create client with the test API key
        client = Client(api_key=TEST_API_KEY)
        models = client.models()

        print(f"Retrieved {len(models)} models:")
        for model in models[:5]:  # Print first 5 models
            print(f"- {model.get('id', 'Unknown')}")

        return True
    except Exception as e:
        print(f"Models retrieval failed: {e}")
        # If test API key fails, try with JWT token
        print("Trying with JWT token instead...")
        try:
            token = get_auth_token()
            if not token:
                print("Cannot test models without authentication token")
                return False

            client = Client(api_key=token)
            models = client.models()

            print(f"Retrieved {len(models)} models:")
            for model in models[:5]:  # Print first 5 models
                print(f"- {model.get('id', 'Unknown')}")

            return True
        except Exception as e2:
            print(f"JWT token attempt also failed: {e2}")
            return False


def test_chat():
    """Test chat completion."""
    try:
        # Create client with the test API key
        client = Client(api_key=TEST_API_KEY)
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
        # Create client with the test API key
        client = Client(api_key=TEST_API_KEY)
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
        # Create client with the test API key
        client = Client(api_key=TEST_API_KEY)
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
    print(f"Using test API key: {TEST_API_KEY}")
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
