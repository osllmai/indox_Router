"""
Constants for the IndoxRouter client.
"""

# API settings
DEFAULT_API_VERSION = "v1"
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 60

# Error messages
ERROR_INVALID_API_KEY = "API key must be provided either as an argument or as the INDOXROUTER_API_KEY environment variable"
ERROR_NETWORK = "Network error occurred while communicating with the IndoxRouter API"
ERROR_RATE_LIMIT = "Rate limit exceeded for the IndoxRouter API"
ERROR_PROVIDER_NOT_FOUND = "Provider not found"
ERROR_MODEL_NOT_FOUND = "Model not found"
ERROR_INVALID_PARAMETERS = "Invalid parameters provided"
