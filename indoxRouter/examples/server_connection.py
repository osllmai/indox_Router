#!/usr/bin/env python
"""
Example showing how to connect to the indoxRouter server in different environments.
"""

import os
import sys
from indoxrouter import Client, NetworkError

# Get API key from environment or command line
API_KEY = os.environ.get("INDOX_ROUTER_API_KEY", None)
if len(sys.argv) > 1:
    API_KEY = sys.argv[1]

if not API_KEY:
    print(
        "Please provide an API key as an argument or set the INDOX_ROUTER_API_KEY environment variable"
    )
    sys.exit(1)

# List of potential server URLs to try
SERVER_URLS = [
    "http://localhost:8000",  # Local development (direct)
    "http://indoxrouter-server:8000",  # Inside Docker network
    "http://host.docker.internal:8000",  # From Docker container to host
]

if len(sys.argv) > 2:
    # If a specific URL is provided, use only that
    SERVER_URLS = [sys.argv[2]]


def test_connection(base_url):
    """Test connection to the specified server URL."""
    print(f"\nTrying to connect to {base_url}...")

    try:
        # Create client with the specified base URL
        client = Client(api_key=API_KEY, base_url=base_url)

        # Test the connection by fetching available models
        response = client.models()

        print(f"✅ Successfully connected to {base_url}")
        print(
            f"   Found {sum(len(provider['models']) for provider in response)} models from {len(response)} providers"
        )

        # Get list of available models
        for provider in response:
            print(f"\n   Provider: {provider['name']}")
            for model in provider["models"][:3]:  # Show first 3 models only
                print(f"     - {model['id']}")

            if len(provider["models"]) > 3:
                print(f"     - ... and {len(provider['models']) - 3} more")

        # Test a simple chat completion
        chat_response = client.chat(
            messages=[{"role": "user", "content": "Hello! Just a quick test."}],
            model="openai/gpt-4o-mini",
            max_tokens=20,
        )

        content = chat_response["choices"][0]["message"]["content"]
        print(f"\n   Test message response: {content}")

        return True

    except NetworkError as e:
        print(f"❌ Failed to connect to {base_url}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error when connecting to {base_url}: {e}")
        return False


def main():
    """Test connection to various potential server URLs."""
    print("IndoxRouter Server Connection Test")
    print("=================================")

    for url in SERVER_URLS:
        if test_connection(url):
            # Stop after first successful connection
            break
    else:
        print("\n❌ Failed to connect to any server URL")
        print("Please ensure the server is running and accessible")
        sys.exit(1)

    print("\n✅ Connection test completed successfully")


if __name__ == "__main__":
    main()
