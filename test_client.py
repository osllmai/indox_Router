#!/usr/bin/env python
"""
Test script for the IndoxRouter client.
This script tests if the changes to the client fixed the issues with the server.
"""

import logging
from indoxrouter import Client
from indoxrouter import (
    IndoxRouterError,
    AuthenticationError,
    NetworkError,
    ProviderError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_chat_completion(client):
    """Test chat completion with the updated client."""
    try:
        logger.info("Testing chat completion...")
        response = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
            model="openai/gpt-4o-mini",
        )
        logger.info("Success! Response received.")
        logger.info(f"Response: {response}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main function to test the client."""
    logger.info("Starting IndoxRouter client test")

    # Initialize the client with API key
    # Replace with your actual API key
    api_key = "your_api_key"  # Replace this with your actual API key

    try:
        client = Client(api_key=api_key)

        # Enable debug mode to see detailed logs
        client.enable_debug()

        # Test connection to the server
        logger.info("Testing connection to the server...")
        connection_info = client.test_connection()
        logger.info(f"Connection status: {connection_info}")

        # Test chat completion
        success = test_chat_completion(client)

        if success:
            logger.info("All tests passed!")
        else:
            logger.error("Some tests failed. Check the logs for details.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Close the client
        if "client" in locals():
            client.close()
            logger.info("Client closed.")


if __name__ == "__main__":
    main()
