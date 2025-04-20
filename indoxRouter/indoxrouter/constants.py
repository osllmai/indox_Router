"""
Constants for the IndoxRouter client.
"""

# API settings
DEFAULT_API_VERSION = "v1"
# DEFAULT_BASE_URL = "http://91.107.253.133:8000"  # Production server IP
DEFAULT_BASE_URL = "http://localhost:8000"  # Local development server
DEFAULT_TIMEOUT = 60

# Default models
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_IMAGE_MODEL = "openai/dall-e-3"

# API endpoints
CHAT_ENDPOINT = "chat/completions"
COMPLETION_ENDPOINT = "completions"
EMBEDDING_ENDPOINT = "embeddings"
IMAGE_ENDPOINT = "images/generations"
MODEL_ENDPOINT = "models"
USAGE_ENDPOINT = "user/usage"

# Error messages
ERROR_INVALID_API_KEY = "API key must be provided either as an argument or as the INDOXROUTER_API_KEY environment variable"
ERROR_NETWORK = "Network error occurred while communicating with the IndoxRouter API"
ERROR_RATE_LIMIT = "Rate limit exceeded for the IndoxRouter API"
ERROR_PROVIDER_NOT_FOUND = "Provider not found"
ERROR_MODEL_NOT_FOUND = "Model not found"
ERROR_INVALID_PARAMETERS = "Invalid parameters provided"
ERROR_INSUFFICIENT_CREDITS = "Insufficient credits"
