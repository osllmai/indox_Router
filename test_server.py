#!/usr/bin/env python
"""
Test script for diagnosing IndoxRouter server issues.
This script tries different model formats to identify which one works with the server.
"""

import json
import requests
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Server configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "api/v1"
CHAT_ENDPOINT = "chat/completions"

# Test data
MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
]

# Different model formats to try
MODEL_FORMATS = [
    # Format 1: Standard provider/model format
    "openai/gpt-4o-mini",
    # Format 2: JSON object with provider and model
    json.dumps({"provider": "openai", "model": "gpt-4o-mini"}),
    # Format 3: Just the model name (server might add default provider)
    "gpt-4o-mini",
    # Format 4: Tuple-like string
    "('openai', 'gpt-4o-mini')",
    # Format 5: Dictionary-like string
    "{'provider': 'openai', 'model': 'gpt-4o-mini'}",
    # Format 6: Try a different provider/model
    "anthropic/claude-3-haiku",
]


def test_model_format(model_format):
    """Test a specific model format."""
    url = f"{BASE_URL}/{API_VERSION}/{CHAT_ENDPOINT}"
    headers = {"Content-Type": "application/json"}

    data = {
        "messages": MESSAGES,
        "model": model_format,
        "temperature": 0.7,
        "max_tokens": None,
        "stream": False,
        "additional_params": {},
    }

    logger.info(f"Testing model format: {model_format}")
    logger.info(f"Request URL: {url}")
    logger.info(f"Request data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Success! Status code: {response.status_code}")
        logger.info("Response data:")
        pprint(response.json())
        return True
    except requests.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        try:
            error_data = e.response.json()
            logger.error(f"Error response: {json.dumps(error_data, indent=2)}")
        except:
            logger.error(f"Error response (not JSON): {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Main function to test all model formats."""
    logger.info("Starting IndoxRouter server test")

    # First, check if the server is running
    try:
        response = requests.get(f"{BASE_URL}")
        logger.info(f"Server is running. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Server connection error: {e}")
        logger.error("Make sure the server is running before continuing.")
        return

    # Test each model format
    success = False
    for model_format in MODEL_FORMATS:
        if test_model_format(model_format):
            logger.info(f"Found working model format: {model_format}")
            success = True
            break
        logger.info("---")

    if not success:
        logger.error("None of the tested model formats worked.")
        logger.info("Try checking the server logs for more details.")


if __name__ == "__main__":
    main()
