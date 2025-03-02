import os
import secrets
import hashlib
import hmac
import time
import base64
from typing import Dict, Optional, Tuple, Union

from .config import get_config


def generate_api_key(prefix: str = "indox") -> str:
    """
    Generate a secure API key with the given prefix.

    Args:
        prefix: Prefix for the API key

    Returns:
        Secure API key
    """
    # Generate 32 bytes of random data
    random_bytes = secrets.token_bytes(32)

    # Encode as base64
    encoded = base64.urlsafe_b64encode(random_bytes).decode().rstrip("=")

    # Add prefix
    return f"{prefix}_{encoded}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Args:
        api_key: API key to hash

    Returns:
        Hashed API key
    """
    # Use SHA-256 for hashing
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against a hashed key.

    Args:
        api_key: API key to verify
        hashed_key: Hashed API key to compare against

    Returns:
        True if the API key is valid, False otherwise
    """
    # Hash the API key and compare
    return hmac.compare_digest(hash_api_key(api_key), hashed_key)


def generate_hmac_signature(data: str, secret: str) -> str:
    """
    Generate an HMAC signature for the given data.

    Args:
        data: Data to sign
        secret: Secret key for signing

    Returns:
        HMAC signature
    """
    # Use HMAC-SHA256 for signing
    signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    return signature


def verify_hmac_signature(data: str, signature: str, secret: str) -> bool:
    """
    Verify an HMAC signature for the given data.

    Args:
        data: Data that was signed
        signature: Signature to verify
        secret: Secret key used for signing

    Returns:
        True if the signature is valid, False otherwise
    """
    # Generate the expected signature
    expected_signature = generate_hmac_signature(data, secret)

    # Compare signatures using constant-time comparison
    return hmac.compare_digest(signature, expected_signature)


def generate_request_signature(
    method: str,
    path: str,
    query_params: Dict[str, str],
    body: str,
    timestamp: int,
    api_key: str,
) -> str:
    """
    Generate a signature for an API request.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        query_params: Query parameters
        body: Request body
        timestamp: Request timestamp
        api_key: API key

    Returns:
        Request signature
    """
    # Sort query parameters
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))

    # Combine all elements
    data_to_sign = f"{method.upper()}\n{path}\n{sorted_params}\n{body}\n{timestamp}"

    # Generate signature
    return generate_hmac_signature(data_to_sign, api_key)


def verify_request_signature(
    method: str,
    path: str,
    query_params: Dict[str, str],
    body: str,
    timestamp: int,
    signature: str,
    api_key: str,
    max_age: int = 300,
) -> bool:
    """
    Verify a signature for an API request.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        query_params: Query parameters
        body: Request body
        timestamp: Request timestamp
        signature: Request signature
        api_key: API key
        max_age: Maximum age of the request in seconds

    Returns:
        True if the signature is valid, False otherwise
    """
    # Check if the request is too old
    current_time = int(time.time())
    if current_time - timestamp > max_age:
        return False

    # Generate the expected signature
    expected_signature = generate_request_signature(
        method, path, query_params, body, timestamp, api_key
    )

    # Compare signatures
    return hmac.compare_digest(signature, expected_signature)


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key for display.

    Args:
        api_key: API key to mask

    Returns:
        Masked API key
    """
    if not api_key:
        return ""

    # Split by underscore
    parts = api_key.split("_", 1)

    if len(parts) < 2:
        # No prefix, mask all but the first and last 4 characters
        prefix = ""
        key = api_key
    else:
        # Has prefix, mask all but the first and last 4 characters of the key
        prefix = parts[0]
        key = parts[1]

    # Mask the key
    if len(key) <= 8:
        masked_key = "*" * len(key)
    else:
        masked_key = key[:4] + "*" * (len(key) - 8) + key[-4:]

    # Combine prefix and masked key
    if prefix:
        return f"{prefix}_{masked_key}"
    else:
        return masked_key
