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
    DEBUG: bool = Field(default=False, env="DEBUG")

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

    # CORS settings
    CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    # Database settings
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")

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

    # Test API key for local development
    TEST_API_KEY: Optional[str] = Field(
        default="test-api-key-for-local-development", env="TEST_API_KEY"
    )

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
