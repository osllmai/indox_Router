"""
Configuration module for indoxRouter.
This module contains the Config class and related functions.
"""

import os
import json
from typing import Dict, Any, Optional

from .constants import DEFAULT_CONFIG_PATH


class Config:
    """Configuration class for indoxRouter."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration.

        Args:
            config_path: Path to the configuration file. If None, uses the default path.
        """
        self.config_path = config_path or os.path.expanduser(DEFAULT_CONFIG_PATH)
        self.config = {}
        self._load_config()

    def _load_config(self):
        """Load the configuration from the file and environment variables."""
        # First try to load from file
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            self.config = {}

        # Then load from environment variables
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Initialize provider_keys if it doesn't exist
        if "provider_keys" not in self.config:
            self.config["provider_keys"] = {}

        # Load provider API keys from environment variables
        env_mapping = {
            "OPENAI_API_KEY": "openai",
            "ANTHROPIC_API_KEY": "anthropic",
            "MISTRAL_API_KEY": "mistral",
            "COHERE_API_KEY": "cohere",
            "GOOGLE_API_KEY": "google",
        }

        for env_var, provider in env_mapping.items():
            api_key = os.environ.get(env_var)
            if api_key:
                self.config["provider_keys"][provider] = api_key

    def get_provider_key(self, provider: str) -> Optional[str]:
        """
        Get the API key for a provider.

        Args:
            provider: The name of the provider.

        Returns:
            The API key for the provider, or None if not found.
        """
        # Check if the provider key exists in the configuration
        if "provider_keys" in self.config and provider in self.config["provider_keys"]:
            return self.config["provider_keys"][provider]

        # Check environment variables as a fallback
        env_var = f"{provider.upper()}_API_KEY"
        return os.environ.get(env_var)

    def set_provider_key(self, provider: str, api_key: str):
        """
        Set the API key for a provider.

        Args:
            provider: The name of the provider.
            api_key: The API key for the provider.
        """
        if "provider_keys" not in self.config:
            self.config["provider_keys"] = {}

        self.config["provider_keys"][provider] = api_key

    def save_config(self, config_path: Optional[str] = None):
        """
        Save the configuration to a file.

        Args:
            config_path: Path to save the configuration to. If None, uses the current config_path.
        """
        save_path = config_path or self.config_path

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            with open(save_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config to {save_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: The key to get.
            default: The default value to return if the key is not found.

        Returns:
            The value for the key, or the default if not found.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a configuration value.

        Args:
            key: The key to set.
            value: The value to set.
        """
        self.config[key] = value


# Global configuration instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Path to the configuration file. If None, uses the default path.

    Returns:
        The global configuration instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
