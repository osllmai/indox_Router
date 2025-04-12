"""
Constants for the IndoxRouter server.
"""

# Default model parameters
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TOP_P = 1.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

# Default embedding parameters
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
DEFAULT_EMBEDDING_DIMENSIONS = 1536

# Provider-specific embedding models
MISTRAL_EMBEDDING_MODEL = "mistral-embed-v1"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
COHERE_EMBEDDING_MODEL = "embed-english-v3.0"

# Default image parameters
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_COUNT = 1
DEFAULT_IMAGE_QUALITY = "standard"
DEFAULT_IMAGE_STYLE = "vivid"

# Error messages
ERROR_INVALID_PARAMETERS = "Invalid parameters"
ERROR_PROVIDER_NOT_FOUND = "Provider not found"
ERROR_MODEL_NOT_FOUND = "Model not found"
ERROR_INVALID_IMAGE_SIZE = "Invalid image size"
ERROR_INSUFFICIENT_CREDITS = "Insufficient credits"

# Available Providers
AVAILABLE_PROVIDERS = ["openai", "mistral", "deepseek"]
