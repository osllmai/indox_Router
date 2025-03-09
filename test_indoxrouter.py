"""
Test script for IndoxRouter client with your server.
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

# Get API key from environment variable or set it directly
api_key = os.environ.get("INDOXROUTER_API_KEY", "your-test-api-key")


def test_health_check():
    """Test the health check endpoint."""
    try:
        # Create a client with the API key
        client = Client(api_key=api_key)

        # Make a simple request to test connectivity
        # This will use the base URL from constants.py which we've updated
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
            ]
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


if __name__ == "__main__":
    print(
        "Testing IndoxRouter client with server at:",
        os.environ.get("INDOXROUTER_BASE_URL", "default URL from constants.py"),
    )

    # Run tests
    health_check_result = test_health_check()
    print("\nHealth check test:", "PASSED" if health_check_result else "FAILED")

    if health_check_result:
        models_result = test_models()
        print("\nModels test:", "PASSED" if models_result else "FAILED")

        chat_result = test_chat()
        print("\nChat test:", "PASSED" if chat_result else "FAILED")
