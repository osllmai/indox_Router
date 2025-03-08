"""
Unit tests for the constants module.
"""

import os
import pytest

from indoxRouter.constants import (
    # API related constants
    DEFAULT_API_VERSION,
    DEFAULT_TIMEOUT,
    DEFAULT_BASE_URL,
    
    # Model related constants
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_PRESENCE_PENALTY,
    
    # Image generation related constants
    DEFAULT_IMAGE_SIZE,
    DEFAULT_IMAGE_COUNT,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_STYLE,
    
    # Embedding related constants
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_DIMENSIONS,
    
    # Database related constants
    DEFAULT_DB_PATH,
    DEFAULT_POSTGRES_CONNECTION,
    
    # Configuration related constants
    DEFAULT_CONFIG_DIR,
    DEFAULT_CONFIG_PATH,
    
    # Error messages
    ERROR_INVALID_API_KEY,
    ERROR_MODEL_NOT_FOUND,
    ERROR_PROVIDER_NOT_FOUND,
    ERROR_REQUEST_FAILED,
    ERROR_INVALID_PARAMETERS,
    ERROR_UNAUTHORIZED,
    ERROR_RATE_LIMIT,
    ERROR_QUOTA_EXCEEDED,
    ERROR_PROVIDER_KEY_NOT_FOUND,
    ERROR_FEATURE_NOT_SUPPORTED,
    ERROR_INVALID_IMAGE_SIZE,
    
    # Success messages
    SUCCESS_REQUEST,
    
    # Provider names
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_MISTRAL,
    PROVIDER_COHERE,
    PROVIDER_GOOGLE,
    
    # Model types
    MODEL_TYPE_CHAT,
    MODEL_TYPE_TEXT,
    MODEL_TYPE_EMBEDDING,
    MODEL_TYPE_IMAGE,
    
    # Response formats
    RESPONSE_FORMAT_JSON,
    RESPONSE_FORMAT_TEXT,
    
    # Database types
    DB_TYPE_SQLITE,
    DB_TYPE_POSTGRES,
)


class TestConstants:
    """Tests for the constants module."""

    def test_api_constants(self):
        """Test API related constants."""
        assert DEFAULT_API_VERSION == "v1"
        assert isinstance(DEFAULT_TIMEOUT, int)
        assert DEFAULT_TIMEOUT > 0
        assert DEFAULT_BASE_URL == "https://api.indoxrouter.com"

    def test_model_constants(self):
        """Test model related constants."""
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0.0 <= DEFAULT_TEMPERATURE <= 1.0
        assert isinstance(DEFAULT_MAX_TOKENS, int)
        assert DEFAULT_MAX_TOKENS > 0
        assert isinstance(DEFAULT_TOP_P, float)
        assert 0.0 <= DEFAULT_TOP_P <= 1.0
        assert isinstance(DEFAULT_FREQUENCY_PENALTY, float)
        assert isinstance(DEFAULT_PRESENCE_PENALTY, float)

    def test_image_constants(self):
        """Test image generation related constants."""
        assert DEFAULT_IMAGE_SIZE in ["256x256", "512x512", "1024x1024"]
        assert isinstance(DEFAULT_IMAGE_COUNT, int)
        assert DEFAULT_IMAGE_COUNT > 0
        assert DEFAULT_IMAGE_QUALITY in ["standard", "hd"]
        assert DEFAULT_IMAGE_STYLE in ["vivid", "natural"]

    def test_embedding_constants(self):
        """Test embedding related constants."""
        assert isinstance(DEFAULT_EMBEDDING_MODEL, str)
        assert len(DEFAULT_EMBEDDING_MODEL) > 0
        assert isinstance(DEFAULT_EMBEDDING_DIMENSIONS, int)
        assert DEFAULT_EMBEDDING_DIMENSIONS > 0

    def test_database_constants(self):
        """Test database related constants."""
        assert "~/.indoxRouter" in DEFAULT_DB_PATH
        assert "postgresql://" in DEFAULT_POSTGRES_CONNECTION

    def test_config_constants(self):
        """Test configuration related constants."""
        assert "~/.indoxRouter" in DEFAULT_CONFIG_DIR
        assert "config.json" in DEFAULT_CONFIG_PATH

    def test_error_messages(self):
        """Test error messages."""
        assert isinstance(ERROR_INVALID_API_KEY, str)
        assert isinstance(ERROR_MODEL_NOT_FOUND, str)
        assert isinstance(ERROR_PROVIDER_NOT_FOUND, str)
        assert isinstance(ERROR_REQUEST_FAILED, str)
        assert isinstance(ERROR_INVALID_PARAMETERS, str)
        assert isinstance(ERROR_UNAUTHORIZED, str)
        assert isinstance(ERROR_RATE_LIMIT, str)
        assert isinstance(ERROR_QUOTA_EXCEEDED, str)
        assert isinstance(ERROR_PROVIDER_KEY_NOT_FOUND, str)
        assert isinstance(ERROR_FEATURE_NOT_SUPPORTED, str)
        assert isinstance(ERROR_INVALID_IMAGE_SIZE, str)

    def test_success_messages(self):
        """Test success messages."""
        assert isinstance(SUCCESS_REQUEST, str)

    def test_provider_names(self):
        """Test provider names."""
        assert PROVIDER_OPENAI == "openai"
        assert PROVIDER_ANTHROPIC == "anthropic"
        assert PROVIDER_MISTRAL == "mistral"
        assert PROVIDER_COHERE == "cohere"
        assert PROVIDER_GOOGLE == "google"

    def test_model_types(self):
        """Test model types."""
        assert MODEL_TYPE_CHAT == "chat"
        assert MODEL_TYPE_TEXT == "text"
        assert MODEL_TYPE_EMBEDDING == "embedding"
        assert MODEL_TYPE_IMAGE == "image"

    def test_response_formats(self):
        """Test response formats."""
        assert RESPONSE_FORMAT_JSON == "json"
        assert RESPONSE_FORMAT_TEXT == "text"

    def test_database_types(self):
        """Test database types."""
        assert DB_TYPE_SQLITE == "sqlite"
        assert DB_TYPE_POSTGRES == "postgres" 