"""
Constants for the IndoxRouter client.
"""

# API settings
DEFAULT_API_VERSION = "v1"
DEFAULT_BASE_URL = "https://api.indoxrouter.com"  # Production server URL with HTTPS
# DEFAULT_BASE_URL = "http://localhost:9050"  # Local server
# DEFAULT_BASE_URL = "https://dev-api.indoxrouter.com"  # development server
DEFAULT_TIMEOUT = (
    1200  
)
USE_COOKIES = True  
# Default models
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_IMAGE_MODEL = "openai/dall-e-3"
DEFAULT_TTS_MODEL = "openai/tts-1"
DEFAULT_STT_MODEL = "openai/whisper-1"
DEFAULT_VIDEO_MODEL = "google/veo-3.0-generate-001"
GOOGLE_IMAGE_MODEL = "google/imagen-3.0-generate-002"
XAI_IMAGE_MODEL = "xai/grok-2-image"
XAI_IMAGE_LATEST_MODEL = "xai/grok-2-image-latest"
XAI_IMAGE_SPECIFIC_MODEL = "xai/grok-2-image-1212"

# API endpoints
CHAT_ENDPOINT = "chat/completions"
COMPLETION_ENDPOINT = "completions"
EMBEDDING_ENDPOINT = "embeddings"
IMAGE_ENDPOINT = "images/generations"
VIDEO_ENDPOINT = "videos/generations"
TTS_ENDPOINT = "audio/tts/generations"
STT_ENDPOINT = "audio/stt/transcriptions"
STT_TRANSLATION_ENDPOINT = "audio/stt/translations"
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
