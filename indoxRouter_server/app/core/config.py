"""
Configuration settings for the IndoxRouter server.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IndoxRouter Server"

    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # Security settings
    SECRET_KEY: str = Field(
        default="indoxrouter-local-dev-secret-2024", env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # IP restrictions
    IP_ALLOWLIST: List[str] = Field(default=[], env="IP_ALLOWLIST")
    IP_BLOCKLIST: List[str] = Field(default=[], env="IP_BLOCKLIST")
    ENABLE_IP_FILTERING: bool = Field(default=False, env="ENABLE_IP_FILTERING")

    # CORS settings
    CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    # PostgreSQL Database settings
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DB_MIN_CONNECTIONS: int = Field(default=1, env="DB_MIN_CONNECTIONS")
    DB_MAX_CONNECTIONS: int = Field(default=10, env="DB_MAX_CONNECTIONS")

    # MongoDB settings
    MONGODB_URI: Optional[str] = Field(default=None, env="MONGODB_URI")
    MONGODB_DATABASE: str = Field(default="indoxrouter", env="MONGODB_DATABASE")

    # Provider API keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    MISTRAL_API_KEY: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")

    # Default provider and model
    DEFAULT_PROVIDER: str = Field(default="openai", env="DEFAULT_PROVIDER")
    DEFAULT_CHAT_MODEL: str = Field(default="gpt-3.5-turbo", env="DEFAULT_CHAT_MODEL")
    DEFAULT_COMPLETION_MODEL: str = Field(
        default="gpt-3.5-turbo-instruct", env="DEFAULT_COMPLETION_MODEL"
    )
    DEFAULT_EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002", env="DEFAULT_EMBEDDING_MODEL"
    )

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD_SECONDS: int = Field(default=60, env="RATE_LIMIT_PERIOD_SECONDS")

    # Redis settings for rate limiting
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Caching
    ENABLE_RESPONSE_CACHE: bool = Field(default=True, env="ENABLE_RESPONSE_CACHE")
    CACHE_TTL_DAYS: int = Field(default=7, env="CACHE_TTL_DAYS")

    # Local mode (for running without external database)
    LOCAL_MODE: bool = Field(default=False, env="INDOXROUTER_LOCAL_MODE")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
        "env_nested_delimiter": "__",
        "validate_default": True,
        "str_strip_whitespace": True,
        "arbitrary_types_allowed": True,
    }

    def model_post_init(self, *args, **kwargs):
        """Post-initialize processing for settings."""
        # Handle IP list parsing
        if hasattr(self, "IP_ALLOWLIST") and isinstance(self.IP_ALLOWLIST, str):
            if self.IP_ALLOWLIST in (None, "", "[]"):
                self.IP_ALLOWLIST = []
            elif self.IP_ALLOWLIST.startswith("[") and self.IP_ALLOWLIST.endswith("]"):
                # Parse JSON-like format
                value = self.IP_ALLOWLIST[1:-1]  # Remove brackets
                if not value:
                    self.IP_ALLOWLIST = []
                else:
                    self.IP_ALLOWLIST = [
                        ip.strip().strip("\"'") for ip in value.split(",") if ip.strip()
                    ]
            else:
                # Parse comma-separated format
                self.IP_ALLOWLIST = [
                    ip.strip() for ip in self.IP_ALLOWLIST.split(",") if ip.strip()
                ]

        if hasattr(self, "IP_BLOCKLIST") and isinstance(self.IP_BLOCKLIST, str):
            if self.IP_BLOCKLIST in (None, "", "[]"):
                self.IP_BLOCKLIST = []
            elif self.IP_BLOCKLIST.startswith("[") and self.IP_BLOCKLIST.endswith("]"):
                # Parse JSON-like format
                value = self.IP_BLOCKLIST[1:-1]  # Remove brackets
                if not value:
                    self.IP_BLOCKLIST = []
                else:
                    self.IP_BLOCKLIST = [
                        ip.strip().strip("\"'") for ip in value.split(",") if ip.strip()
                    ]
            else:
                # Parse comma-separated format
                self.IP_BLOCKLIST = [
                    ip.strip() for ip in self.IP_BLOCKLIST.split(",") if ip.strip()
                ]


settings = Settings()
