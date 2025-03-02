import pytest
import os
import json
import tempfile
from pathlib import Path

from indoxRouter.utils.config import Config, get_config
from indoxRouter.utils.exceptions import ConfigurationError


class TestConfig:
    """Test suite for the Config class"""

    def test_init_default(self):
        """Test initializing with default configuration"""
        config = Config()
        assert config.config is not None
        assert "api" in config.config
        assert "auth" in config.config
        assert "providers" in config.config
        assert "database" in config.config
        assert "logging" in config.config
        assert "cache" in config.config

    def test_load_from_file(self):
        """Test loading configuration from a file"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {
                "api": {"port": 9000, "debug": True},
                "database": {
                    "type": "postgres",
                    "url": "postgresql://user:pass@localhost/db",
                },
            }
            json.dump(config_data, f)
            config_path = f.name

        try:
            # Load the configuration
            config = Config(config_path=config_path)

            # Check that values were loaded from the file
            assert config.get("api", "port") == 9000
            assert config.get("api", "debug") is True
            assert config.get("database", "type") == "postgres"
            assert (
                config.get("database", "url") == "postgresql://user:pass@localhost/db"
            )

            # Check that default values are still available for unspecified settings
            assert config.get("api", "host") == "0.0.0.0"  # Default value
            assert config.get("auth", "token_expiry") == 86400  # Default value
        finally:
            # Clean up
            os.unlink(config_path)

    def test_load_from_file_not_found(self):
        """Test loading configuration from a non-existent file"""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            Config(config_path="/path/to/nonexistent/config.json")

    def test_load_from_file_invalid_json(self):
        """Test loading configuration from a file with invalid JSON"""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("This is not valid JSON")
            config_path = f.name

        try:
            with pytest.raises(ConfigurationError, match="Invalid JSON"):
                Config(config_path=config_path)
        finally:
            # Clean up
            os.unlink(config_path)

    def test_load_from_env(self, monkeypatch):
        """Test loading configuration from environment variables"""
        # Set environment variables
        monkeypatch.setenv("INDOX_API_PORT", "9000")
        monkeypatch.setenv("INDOX_API_DEBUG", "true")
        monkeypatch.setenv("INDOX_DATABASE_TYPE", "postgres")
        monkeypatch.setenv("INDOX_DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv(
            "INDOX_API_CORS_ORIGINS", "http://localhost:3000,http://example.com"
        )

        # Load the configuration
        config = Config()

        # Check that values were loaded from environment variables
        assert config.get("api", "port") == 9000
        assert config.get("api", "debug") is True
        assert config.get("database", "type") == "postgres"
        assert config.get("database", "url") == "postgresql://user:pass@localhost/db"
        assert config.get("api", "cors_origins") == [
            "http://localhost:3000",
            "http://example.com",
        ]

    def test_get(self):
        """Test getting a configuration value"""
        config = Config()
        assert config.get("api", "port") == 8000
        assert config.get("api", "host") == "0.0.0.0"
        assert config.get("auth", "token_expiry") == 86400

    def test_get_default(self):
        """Test getting a configuration value with a default"""
        config = Config()
        assert config.get("api", "nonexistent", default="default") == "default"
        assert config.get("nonexistent", "key", default="default") == "default"

    def test_get_section(self):
        """Test getting a configuration section"""
        config = Config()
        api_section = config.get_section("api")
        assert api_section is not None
        assert "port" in api_section
        assert "host" in api_section
        assert api_section["port"] == 8000
        assert api_section["host"] == "0.0.0.0"

    def test_get_section_nonexistent(self):
        """Test getting a non-existent configuration section"""
        config = Config()
        section = config.get_section("nonexistent")
        assert section == {}

    def test_get_provider_api_key(self, monkeypatch):
        """Test getting a provider API key from environment variable"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
        config = Config()
        api_key = config.get_provider_api_key("openai")
        assert api_key == "sk-test-openai-key"

    def test_get_provider_api_key_from_config(self, monkeypatch):
        """Test getting a provider API key from configuration"""
        # Create a config with provider API keys
        config = Config()
        config.config["providers"]["openai_api_key"] = "sk-config-openai-key"

        # Test getting the API key
        api_key = config.get_provider_api_key("openai")
        assert api_key == "sk-config-openai-key"

    def test_get_provider_api_key_not_found(self):
        """Test getting a non-existent provider API key"""
        config = Config()
        with pytest.raises(ConfigurationError, match="API key not found for provider"):
            config.get_provider_api_key("nonexistent")

    def test_get_all(self):
        """Test getting the entire configuration"""
        config = Config()
        all_config = config.get_all()
        assert all_config is not None
        assert "api" in all_config
        assert "auth" in all_config
        assert "providers" in all_config
        assert "database" in all_config
        assert "logging" in all_config
        assert "cache" in all_config

    def test_get_config_function(self):
        """Test the get_config function"""
        config = get_config()
        assert config is not None
        assert isinstance(config, Config)
        assert "api" in config.config
        assert "auth" in config.config
