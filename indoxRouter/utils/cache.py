import os
import json
import hashlib
import time
from typing import Any, Dict, Optional, Union
import redis

from .config import get_config


class CacheManager:
    """
    Cache manager for IndoxRouter.

    Supports in-memory and Redis caching.
    """

    def __init__(self):
        """Initialize the cache manager."""
        self.config = get_config()
        self.cache_config = self.config.get_section("cache")

        self.cache_type = self.cache_config.get("type", "memory")
        self.ttl = int(self.cache_config.get("ttl", 3600))  # Default: 1 hour

        # Initialize the cache based on the type
        if self.cache_type == "redis":
            self._init_redis_cache()
        else:
            self._init_memory_cache()

    def _init_redis_cache(self):
        """Initialize Redis cache."""
        host = self.cache_config.get("host", "localhost")
        port = int(self.cache_config.get("port", 6379))
        password = self.cache_config.get("password", None)
        db = int(self.cache_config.get("db", 0))

        self.redis = redis.Redis(
            host=host, port=port, password=password, db=db, decode_responses=False
        )

        # Test the connection
        try:
            self.redis.ping()
            self.cache_available = True
        except redis.ConnectionError:
            print("Warning: Redis connection failed. Falling back to in-memory cache.")
            self._init_memory_cache()

    def _init_memory_cache(self):
        """Initialize in-memory cache."""
        self.cache_type = "memory"
        self.cache = {}
        self.cache_expiry = {}
        self.cache_available = True

    def _generate_key(
        self, provider: str, model: str, prompt: str, params: Dict[str, Any]
    ) -> str:
        """
        Generate a cache key based on the request parameters.

        Args:
            provider: Provider name
            model: Model name
            prompt: Prompt text
            params: Additional parameters

        Returns:
            Cache key
        """
        # Create a dictionary with all parameters
        key_dict = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "params": params,
        }

        # Convert to JSON and hash
        key_json = json.dumps(key_dict, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()

    def get(
        self, provider: str, model: str, prompt: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached response.

        Args:
            provider: Provider name
            model: Model name
            prompt: Prompt text
            params: Additional parameters

        Returns:
            Cached response or None if not found
        """
        if not self.cache_available:
            return None

        key = self._generate_key(provider, model, prompt, params)

        if self.cache_type == "redis":
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        else:
            # Check if the key exists and hasn't expired
            if key in self.cache and (
                key not in self.cache_expiry or self.cache_expiry[key] > time.time()
            ):
                return self.cache[key]

            # Remove expired keys
            if key in self.cache_expiry and self.cache_expiry[key] <= time.time():
                del self.cache[key]
                del self.cache_expiry[key]

        return None

    def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        params: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """
        Cache a response.

        Args:
            provider: Provider name
            model: Model name
            prompt: Prompt text
            params: Additional parameters
            response: Response to cache
        """
        if not self.cache_available:
            return

        key = self._generate_key(provider, model, prompt, params)

        if self.cache_type == "redis":
            self.redis.setex(key, self.ttl, json.dumps(response))
        else:
            self.cache[key] = response
            self.cache_expiry[key] = time.time() + self.ttl

    def clear(self) -> None:
        """Clear the cache."""
        if not self.cache_available:
            return

        if self.cache_type == "redis":
            self.redis.flushdb()
        else:
            self.cache = {}
            self.cache_expiry = {}

    def clear_for_provider(self, provider: str) -> None:
        """
        Clear the cache for a specific provider.

        Args:
            provider: Provider name
        """
        if not self.cache_available:
            return

        if self.cache_type == "redis":
            # This is inefficient for Redis, but there's no easy way to do pattern matching
            # without scanning all keys
            for key in self.redis.scan_iter("*"):
                data = self.redis.get(key)
                if data:
                    try:
                        response = json.loads(data)
                        if response.get("provider") == provider:
                            self.redis.delete(key)
                    except json.JSONDecodeError:
                        pass
        else:
            # For in-memory cache, we can iterate through all keys
            keys_to_delete = []
            for key in self.cache:
                if self.cache[key].get("provider") == provider:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del self.cache[key]
                if key in self.cache_expiry:
                    del self.cache_expiry[key]


# Singleton instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get the cache manager instance.

    Returns:
        Cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
