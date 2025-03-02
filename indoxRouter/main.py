"""
Main FastAPI application for IndoxRouter.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Import utility modules
from .utils.database import execute_query, close_all_connections
from .utils.auth import (
    verify_api_key,
    authenticate_user,
    generate_jwt_token,
    verify_jwt_token,
    AuthManager,
)
from .models.database import User, ApiKey, RequestLog, ProviderConfig
from .utils.config import get_config
from .providers import get_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Load configuration
def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        return {}


config = load_config()

# Create FastAPI app
app = FastAPI(
    title="IndoxRouter",
    description="A unified API for multiple LLM providers",
    version="1.0.0",
)

# Add CORS middleware
cors_origins = config.get("api", {}).get("cors_origins", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

# Create the auth manager
auth_manager = AuthManager()


# Define request and response models
class CompletionRequest(BaseModel):
    provider: str = Field(..., description="The LLM provider to use")
    model: str = Field(..., description="The model to use")
    prompt: str = Field(..., description="The prompt to send to the model")
    max_tokens: Optional[int] = Field(
        None, description="Maximum number of tokens to generate"
    )
    temperature: Optional[float] = Field(0.7, description="Temperature for sampling")
    top_p: Optional[float] = Field(1.0, description="Top-p sampling parameter")
    stop: Optional[List[str]] = Field(
        None, description="Sequences where the API will stop generating"
    )
    stream: Optional[bool] = Field(False, description="Whether to stream the response")


class CompletionResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the completion")
    provider: str = Field(..., description="The provider used")
    model: str = Field(..., description="The model used")
    text: str = Field(..., description="The generated text")
    usage: Dict[str, int] = Field(..., description="Token usage information")
    created_at: datetime = Field(..., description="Timestamp of creation")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user_id: int = Field(..., description="User ID")
    is_admin: bool = Field(False, description="Whether the user is an admin")


class ApiKeyRequest(BaseModel):
    key_name: str = Field(..., description="Name for the API key")
    expires_days: Optional[int] = Field(
        None, description="Days until expiry (None for no expiry)"
    )


class ApiKeyResponse(BaseModel):
    key: str = Field(..., description="The generated API key")
    key_id: int = Field(..., description="ID of the API key")
    key_name: str = Field(..., description="Name of the API key")
    expires_at: Optional[datetime] = Field(None, description="Expiry date")


# Authentication dependency
async def get_current_user(authorization: str = None):
    """
    Get the current user from the API key.

    Args:
        authorization: Authorization header

    Returns:
        User data
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="API key is required")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    api_key = authorization.replace("Bearer ", "")

    user_data = auth_manager.verify_api_key(api_key)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_data


# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to IndoxRouter", "version": "1.0.0"}


@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    user_data: Dict[str, Any] = Depends(get_current_user),
    req: Request = None,
):
    """Create a completion using the specified provider."""
    try:
        # Get the provider
        provider_instance = get_provider(request.provider)
        if not provider_instance:
            raise HTTPException(
                status_code=400, detail=f"Provider '{request.provider}' not found"
            )

        # Generate the completion
        start_time = time.time()
        response = provider_instance.generate(
            model=request.model,
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            stop=request.stop,
        )
        process_time = time.time() - start_time

        # Log the request
        from indoxRouter.utils.database import get_session

        session = get_session()
        try:
            log = RequestLog(
                user_id=user_data["id"],
                api_key_id=user_data["api_key_id"],
                provider=request.provider,
                model=request.model,
                prompt=request.prompt,
                response=response,
                tokens_input=len(request.prompt.split()),
                tokens_output=len(response.split()),
                latency_ms=int(process_time * 1000),
                status_code=200,
                ip_address=req.client.host if req else None,
                user_agent=req.headers.get("User-Agent") if req else None,
            )
            session.add(log)
            session.commit()
        except Exception as e:
            logger.error(f"Error logging request: {e}")
            session.rollback()
        finally:
            session.close()

        # Return the response
        return {
            "id": f"cmpl-{int(time.time())}",
            "provider": request.provider,
            "model": request.model,
            "text": response,
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(request.prompt.split()) + len(response.split()),
            },
            "created_at": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Error creating completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating completion: {str(e)}",
        )


@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint to get JWT tokens."""
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token, expires_in, _ = generate_jwt_token(
        user["id"], user["is_admin"]
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user_id": user["id"],
        "is_admin": user["is_admin"],
    }


@app.post("/auth/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_token: str):
    """Refresh an access token using a refresh token."""
    result = verify_jwt_token(refresh_token)
    if not result or result.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get new access token
    access_token, expires_in = result

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@app.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    request: ApiKeyRequest, user_data: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new API key for the current user."""
    try:
        api_key, key_id = auth_manager.generate_api_key(
            user_id=user_data["id"],
            key_name=request.key_name,
            expires_days=request.expires_days,
        )

        # Get the key record
        key_record = ApiKey.get_by_id(key_id)

        return {
            "key": api_key,
            "key_id": key_id,
            "key_name": key_record["key_name"],
            "expires_at": key_record["expires_at"],
        }
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}",
        )


@app.get("/api-keys", response_model=List[Dict[str, Any]])
async def list_api_keys(user_data: Dict[str, Any] = Depends(get_current_user)):
    """List all API keys for the current user."""
    try:
        keys = ApiKey.list_by_user(user_data["id"])
        return keys
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing API keys: {str(e)}",
        )


@app.delete("/api-keys/{key_id}", response_model=Dict[str, bool])
async def delete_api_key(
    key_id: int, user_data: Dict[str, Any] = Depends(get_current_user)
):
    """Delete an API key."""
    try:
        # Check if the key belongs to the user
        key = ApiKey.get_by_id(key_id)
        if not key or key["user_id"] != user_data["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Delete the key
        success = ApiKey.delete_key(key_id)
        return {"success": success}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting API key: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting IndoxRouter application")

    # TODO: Initialize any resources needed at startup


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down IndoxRouter application")

    # Close database connections
    close_all_connections()


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


# If this file is run directly, start the application with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
