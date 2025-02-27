# utils/auth.py
def validate_api_key(key: str):
    if not key.startswith("indox-"):
        raise AuthenticationError("Invalid API key format")
