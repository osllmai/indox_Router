"""
Constants module for indoxRouter.
This module contains all the constants used throughout the application.
"""

import os

# API related constants
DEFAULT_API_VERSION = "v1"
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_BASE_URL = "https://api.indoxrouter.com"

# Model related constants
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TOP_P = 1.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

# Image generation related constants
DEFAULT_IMAGE_SIZE = "512x512"
DEFAULT_IMAGE_COUNT = 1
DEFAULT_IMAGE_QUALITY = "standard"
DEFAULT_IMAGE_STYLE = "vivid"

# Embedding related constants
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
DEFAULT_EMBEDDING_DIMENSIONS = 1536

# Database related constants
DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~/.indoxRouter"), "indoxRouter.db")
DEFAULT_POSTGRES_CONNECTION = (
    "postgresql://postgres:postgres@localhost:5432/indoxrouter"
)

# Configuration related constants
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.indoxRouter")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.json")

# Error messages
ERROR_INVALID_API_KEY = "Invalid API key provided."
ERROR_MODEL_NOT_FOUND = "Model not found."
ERROR_PROVIDER_NOT_FOUND = "Provider not found."
ERROR_REQUEST_FAILED = "Request to provider failed."
ERROR_INVALID_PARAMETERS = "Invalid parameters provided."
ERROR_UNAUTHORIZED = "Unauthorized. Please check your API key."
ERROR_RATE_LIMIT = "Rate limit exceeded. Please try again later."
ERROR_QUOTA_EXCEEDED = "Quota exceeded. Please check your usage."
ERROR_PROVIDER_KEY_NOT_FOUND = "Provider API key not found. Please configure it first."
ERROR_FEATURE_NOT_SUPPORTED = "This feature is not supported by the selected provider."
ERROR_INVALID_IMAGE_SIZE = (
    "Invalid image size. Please check the documentation for supported sizes."
)

# Success messages
SUCCESS_REQUEST = "Request successful."

# Provider names
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_MISTRAL = "mistral"
PROVIDER_COHERE = "cohere"
PROVIDER_GOOGLE = "google"

# Model types
MODEL_TYPE_CHAT = "chat"
MODEL_TYPE_TEXT = "text"
MODEL_TYPE_EMBEDDING = "embedding"
MODEL_TYPE_IMAGE = "image"

# Response formats
RESPONSE_FORMAT_JSON = "json"
RESPONSE_FORMAT_TEXT = "text"

# Database types
DB_TYPE_SQLITE = "sqlite"
DB_TYPE_POSTGRES = "postgres"

# Default paths
DEFAULT_CONFIG_PATH = "~/.indoxRouter/config.json"
DEFAULT_DB_PATH = "~/.indoxRouter/database.db"
