#!/usr/bin/env python
"""
Script to set up the configuration for indoxRouter.
"""

import os
import sys
import json
import argparse

# Add the parent directory to the path so we can import indoxRouter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from indoxRouter.config import get_config
from indoxRouter.constants import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_PATH


def setup_config(providers=None, config_path=None):
    """
    Set up the configuration for indoxRouter.

    Args:
        providers: List of providers to configure. If None, uses a default list.
        config_path: Path to save the configuration file. If None, uses the default path.

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Create the config directory if it doesn't exist
        config_dir = os.path.dirname(config_path or DEFAULT_CONFIG_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Get the configuration
        config = get_config(config_path)

        # Default list of providers
        if providers is None:
            providers = [
                "openai",
                "anthropic",
                "cohere",
                "google",
                "mistral",
                "meta",
                "claude",
                "ai21labs",
                "databricks",
                "nvidia",
                "deepseek",
                "qwen",
            ]

        # Ask for API keys for each provider
        for provider in providers:
            current_key = config.get_provider_key(provider)
            prompt = f"Enter API key for {provider}"
            if current_key:
                prompt += f" (current: {current_key[:4]}...{current_key[-4:]})"
            prompt += " (leave empty to skip): "

            api_key = input(prompt).strip()
            if api_key:
                config.set_provider_key(provider, api_key)

        # Save the configuration
        config.save_config(config_path)

        print(f"Configuration saved to {config_path or DEFAULT_CONFIG_PATH}")
        return True
    except Exception as e:
        print(f"Error setting up configuration: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set up the configuration for indoxRouter."
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        help="List of providers to configure. If not provided, uses a default list.",
    )
    parser.add_argument(
        "--config-path",
        help="Path to save the configuration file. If not provided, uses the default path.",
    )

    args = parser.parse_args()

    if setup_config(args.providers, args.config_path):
        print("Configuration setup successful!")
    else:
        print("Configuration setup failed.")
        sys.exit(1)
