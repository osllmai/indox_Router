"""
Caching utilities for indoxRouter.
This module contains functions for caching API responses.
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client if caching is enabled
redis_client = None

if settings.ENABLE_RESPONSE_CACHE:
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=False  # Need binary for storing complex objects
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis connection initialized for caching")
    except Exception as e:
        logger.error(f"Failed to initialize Redis for caching: {e}")
        redis_client = None


def generate_cache_key(
    endpoint: str,
    provider: str,
    model: str,
    input_data: Union[str, List[str], Dict[str, Any]],
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a cache key for a request.

    Args:
        endpoint: The API endpoint (chat, completion, embedding, image).
        provider: The provider ID.
        model: The model ID.
        input_data: The input data (prompt, messages, text, etc.).
        params: Additional parameters affecting the output.

    Returns:
        A cache key for the request.
    """
    # Create a dictionary with all parameters affecting the output
    key_dict = {
        "endpoint": endpoint,
        "provider": provider,
        "model": model,
        "input": input_data
    }

    # Include relevant parameters if provided
    if params:
        # Filter to only include parameters that affect the output
        relevant_params = {}
        for param, value in params.items():
            # Skip parameters that don't affect the output or shouldn't be cached
            if param in ["stream", "user", "api_key", "request_id"]:
                continue
            relevant_params[param] = value
            
        if relevant_params:
            key_dict["params"] = relevant_params

    # Convert to JSON and hash
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


def get_cached_response(
    endpoint: str,
    provider: str,
    model: str,
    input_data: Union[str, List[str], Dict[str, Any]],
    params: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a cached response.

    Args:
        endpoint: The API endpoint (chat, completion, embedding, image).
        provider: The provider ID.
        model: The model ID.
        input_data: The input data (prompt, messages, text, etc.).
        params: Additional parameters affecting the output.

    Returns:
        The cached response, or None if not found.
    """
    if not settings.ENABLE_RESPONSE_CACHE or not redis_client:
        return None

    # Generate cache key
    cache_key = generate_cache_key(endpoint, provider, model, input_data, params)
    
    try:
        # Get the cached response
        cached_data = redis_client.get(cache_key)
        if cached_data:
            response = json.loads(cached_data)
            logger.info(f"Cache hit for {endpoint} request to {provider}/{model}")
            return response
    except Exception as e:
        logger.error(f"Error getting cached response: {e}")
    
    return None


def cache_response(
    endpoint: str,
    provider: str,
    model: str,
    input_data: Union[str, List[str], Dict[str, Any]],
    response: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None,
    ttl_days: Optional[int] = None
) -> bool:
    """
    Cache a response.

    Args:
        endpoint: The API endpoint (chat, completion, embedding, image).
        provider: The provider ID.
        model: The model ID.
        input_data: The input data (prompt, messages, text, etc.).
        response: The response to cache.
        params: Additional parameters affecting the output.
        ttl_days: Time-to-live in days. If None, uses the default from settings.

    Returns:
        True if successful, False otherwise.
    """
    if not settings.ENABLE_RESPONSE_CACHE or not redis_client:
        return False

    # Don't cache if the response indicates an error
    if not response.get("success", True):
        return False

    # Generate cache key
    cache_key = generate_cache_key(endpoint, provider, model, input_data, params)
    
    try:
        # Get TTL in seconds
        ttl = (ttl_days or settings.CACHE_TTL_DAYS) * 86400  # days to seconds
        
        # Cache the response
        cached_data = json.dumps(response)
        redis_client.setex(cache_key, ttl, cached_data)
        logger.info(f"Cached {endpoint} response for {provider}/{model} (TTL: {ttl_days or settings.CACHE_TTL_DAYS} days)")
        return True
    except Exception as e:
        logger.error(f"Error caching response: {e}")
        return False 