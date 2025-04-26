"""
Rate limiting utilities for indoxRouter.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Default rate limits per user tier
DEFAULT_RATE_LIMITS = {
    "free": {"requests_per_minute": 10, "tokens_per_hour": 10000},
    "basic": {"requests_per_minute": 30, "tokens_per_hour": 50000},
    "premium": {"requests_per_minute": 100, "tokens_per_hour": 200000},
    "enterprise": {"requests_per_minute": 500, "tokens_per_hour": 1000000},
}

redis_client = None

if settings.RATE_LIMIT_ENABLED:
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis connection initialized for rate limiting")
    except Exception as e:
        logger.error(f"Failed to initialize Redis for rate limiting: {e}")
        redis_client = None


def check_rate_limit(
    user_id: int, user_tier: str = "free", tokens: int = 0
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a user has exceeded their rate limits.

    Args:
        user_id: The user ID.
        user_tier: The user's tier (free, basic, premium, enterprise).
        tokens: The number of tokens in the current request.

    Returns:
        Tuple containing:
            - Boolean indicating if the request should be allowed (True) or not (False)
            - Dictionary with rate limit information
    """
    # Admin tier users are exempt from rate limiting
    if user_tier == "admin":
        return True, {"allowed": True, "reason": "Admin tier exempt from rate limiting"}

    if not settings.RATE_LIMIT_ENABLED or not redis_client:
        # If rate limiting is disabled or Redis is not available, allow all requests
        return True, {"allowed": True, "reason": "Rate limiting disabled"}

    current_time = int(time.time())
    minute_window = current_time - (current_time % 60)  # Current minute
    hour_window = current_time - (current_time % 3600)  # Current hour

    # Get rate limits for the user's tier
    tier_limits = DEFAULT_RATE_LIMITS.get(user_tier, DEFAULT_RATE_LIMITS["free"])

    # Keys for Redis
    requests_key = f"rate:requests:{user_id}:{minute_window}"
    tokens_key = f"rate:tokens:{user_id}:{hour_window}"

    # Get current usage
    pipe = redis_client.pipeline()
    pipe.get(requests_key)
    pipe.get(tokens_key)
    results = pipe.execute()

    current_requests = int(results[0]) if results[0] else 0
    current_tokens = int(results[1]) if results[1] else 0

    # Check if limits are exceeded
    if current_requests >= tier_limits["requests_per_minute"]:
        return False, {
            "allowed": False,
            "reason": "Requests per minute exceeded",
            "limit": tier_limits["requests_per_minute"],
            "remaining": 0,
            "reset_after": 60 - (current_time % 60),  # Seconds until next minute
        }

    if current_tokens + tokens >= tier_limits["tokens_per_hour"]:
        return False, {
            "allowed": False,
            "reason": "Tokens per hour exceeded",
            "limit": tier_limits["tokens_per_hour"],
            "remaining": max(0, tier_limits["tokens_per_hour"] - current_tokens),
            "reset_after": 3600 - (current_time % 3600),  # Seconds until next hour
        }

    # Update usage counters
    pipe = redis_client.pipeline()
    pipe.incr(requests_key, 1)
    pipe.expire(requests_key, 60)  # Expire after 1 minute

    if tokens > 0:
        pipe.incr(tokens_key, tokens)
        pipe.expire(tokens_key, 3600)  # Expire after 1 hour

    pipe.execute()

    # Return success with rate limit information
    return True, {
        "allowed": True,
        "requests": {
            "limit": tier_limits["requests_per_minute"],
            "remaining": tier_limits["requests_per_minute"] - current_requests - 1,
            "reset_after": 60 - (current_time % 60),
        },
        "tokens": {
            "limit": tier_limits["tokens_per_hour"],
            "remaining": tier_limits["tokens_per_hour"] - current_tokens - tokens,
            "reset_after": 3600 - (current_time % 3600),
        },
    }


def get_rate_limit_headers(user_id: int, user_tier: str = "free") -> Dict[str, str]:
    """
    Get rate limit headers for the response.

    Args:
        user_id: The user ID.
        user_tier: The user's tier.

    Returns:
        Dictionary with rate limit headers.
    """
    if not settings.RATE_LIMIT_ENABLED or not redis_client:
        return {}

    current_time = int(time.time())
    minute_window = current_time - (current_time % 60)

    # Get rate limits for the user's tier
    tier_limits = DEFAULT_RATE_LIMITS.get(user_tier, DEFAULT_RATE_LIMITS["free"])

    # Key for Redis
    requests_key = f"rate:requests:{user_id}:{minute_window}"

    # Get current usage
    current_requests = int(redis_client.get(requests_key) or 0)

    # Calculate remaining requests
    remaining = max(0, tier_limits["requests_per_minute"] - current_requests)

    # Calculate reset time
    reset_time = minute_window + 60

    return {
        "X-RateLimit-Limit": str(tier_limits["requests_per_minute"]),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time),
    }
