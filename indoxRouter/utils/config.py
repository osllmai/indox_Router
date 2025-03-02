import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from .exceptions import ConfigurationError

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """
    Configuration manager for IndoxRouter

    Handles loading and accessing configuration settings from environment variables,
    configuration files, and default values.
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False,
            "workers": 4,
            "timeout": 60,
            "cors_origins": ["*"],
            "rate_limit": 100,  # requests per minute
            "max_request_size": 10 * 1024 * 1024,  # 10 MB
        },
        "auth": {
            "token_expiry": 86400,  # 24 hours in seconds
            "refresh_token_expiry": 2592000,  # 30 days in seconds
            "api_key_prefix": "indox_",
            "admin_email": "admin@example.com",
        },
        "providers": {
            "default_timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1,
            "cache_ttl": 300,  # 5 minutes in seconds
        },
        "database": {
            "type": "sqlite",  # sqlite, postgres, mysql
            # SQLite configuration
            "path": "indoxrouter.db",  # Path for SQLite database
            # PostgreSQL configuration
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "database": "indoxrouter",
            "url": "",  # Full connection URL (optional, overrides individual settings)
            # Connection pool settings
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 1800,  # Recycle connections after 30 minutes
            "pool_pre_ping": True,  # Check connection validity before using
            "echo": False,  # Echo SQL statements (for debugging)
            # Migration settings
            "auto_migrate": True,  # Automatically run migrations on startup
            # Backup settings
            "backup_enabled": False,  # Enable automatic backups
            "backup_interval": 86400,  # Backup interval in seconds (24 hours)
            "backup_path": "backups",  # Path for database backups
            "backup_retention": 7,  # Number of backups to retain
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "",
            "rotation": "1 day",
            "retention": "30 days",
        },
        "cache": {
            "type": "memory",  # memory, redis
            "url": "",
            "ttl": 300,  # 5 minutes in seconds
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager

        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # Load configuration from file if provided
        if config_path:
            self._load_from_file(config_path)

        # Override with environment variables
        self._load_from_env()

    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file

        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)

            # Update the configuration with values from the file
            self._update_nested_dict(self.config, file_config)
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {config_path}"
            )

    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables

        Environment variables should be in the format:
        INDOX_SECTION_KEY=value

        For example:
        INDOX_API_PORT=8080
        INDOX_DATABASE_URL=postgresql://user:pass@localhost/db
        """
        prefix = "INDOX_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split into section and key
                parts = key[len(prefix) :].lower().split("_", 1)

                if len(parts) == 2:
                    section, key = parts

                    # Check if section exists in config
                    if section in self.config:
                        # Check if key exists in section
                        if key in self.config[section]:
                            # Convert value to the appropriate type
                            original_value = self.config[section][key]

                            if isinstance(original_value, bool):
                                value = value.lower() in ("true", "1", "yes", "y")
                            elif isinstance(original_value, int):
                                value = int(value)
                            elif isinstance(original_value, float):
                                value = float(value)
                            elif isinstance(original_value, list):
                                value = value.split(",")

                            # Update the configuration
                            self.config[section][key] = value

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Update a nested dictionary with values from another dictionary

        Args:
            d: Dictionary to update
            u: Dictionary with new values

        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value

        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section

        Args:
            section: Configuration section

        Returns:
            Configuration section as a dictionary
        """
        return self.config.get(section, {})

    def get_provider_api_key(self, provider: str) -> str:
        """
        Get the API key for a provider

        Args:
            provider: Provider name

        Returns:
            Provider API key
        """
        # Try to get from environment variable first
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)

        if not api_key:
            # Try to get from configuration
            api_key = self.get("providers", f"{provider}_api_key")

        if not api_key:
            raise ConfigurationError(f"API key not found for provider: {provider}")

        return api_key

    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration

        Returns:
            Complete configuration dictionary
        """
        return self.config


# Create a global configuration instance
config = Config()


def get_config() -> Config:
    """
    Get the global configuration instance

    Returns:
        Configuration instance
    """
    return config


class ConfigManager:
    """
    Configuration Manager for IndoxRouter

    This class provides a wrapper around the Config class to maintain
    backward compatibility and provide additional functionality.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager

        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config = Config(config_path)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value

        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        return self.config.get(section, key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section

        Args:
            section: Configuration section

        Returns:
            Configuration section as a dictionary
        """
        return self.config.get_section(section)

    def get_provider_api_key(self, provider: str) -> str:
        """
        Get the API key for a provider

        Args:
            provider: Provider name

        Returns:
            Provider API key
        """
        return self.config.get_provider_api_key(provider)

    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration

        Returns:
            Complete configuration dictionary
        """
        return self.config.get_all()

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific provider

        Args:
            provider: Provider name

        Returns:
            Provider configuration
        """
        # Get provider-specific configuration
        provider_config = self.get_section("providers")

        # Add provider-specific API key
        provider_config[f"{provider}_api_key"] = self.get_provider_api_key(provider)

        return provider_config

    def is_provider_configured(self, provider: str) -> bool:
        """
        Check if a provider is configured

        Args:
            provider: Provider name

        Returns:
            True if the provider is configured, False otherwise
        """
        try:
            self.get_provider_api_key(provider)
            return True
        except ConfigurationError:
            return False

    def get_configured_providers(self) -> List[str]:
        """
        Get a list of configured providers

        Returns:
            List of configured provider names
        """
        # List of all supported providers
        all_providers = [
            "openai",
            "anthropic",
            "google",
            "azure",
            "cohere",
            "llama",
            "nvidia",
            "deepseek",
            "databricks",
            "mistral",
            "huggingface",
        ]

        # Filter to only include configured providers
        return [p for p in all_providers if self.is_provider_configured(p)]
