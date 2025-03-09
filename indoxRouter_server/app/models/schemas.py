"""
Pydantic models for request and response schemas.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat completion request model."""

    messages: List[ChatMessage]
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CompletionRequest(BaseModel):
    """Text completion request model."""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    """Embedding request model."""

    text: Union[str, List[str]]
    provider: Optional[str] = None
    model: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ImageRequest(BaseModel):
    """Image generation request model."""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    size: Optional[str] = "1024x1024"
    n: Optional[int] = 1
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TokenRequest(BaseModel):
    """Token username/password request model."""

    username: str
    password: str


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ModelInfo(BaseModel):
    """Model information model."""

    id: str
    name: str
    provider: str
    capabilities: List[str]
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProviderInfo(BaseModel):
    """Provider information model."""

    id: str
    name: str
    description: Optional[str] = None
    capabilities: List[str]
    models: List[ModelInfo]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Base success response model."""

    request_id: str
    created_at: str
    duration_ms: float
    usage: Optional[Dict[str, Any]] = None


class ChatResponse(SuccessResponse):
    """Chat completion response model."""

    provider: str
    model: str
    choices: List[Dict[str, Any]]


class CompletionResponse(SuccessResponse):
    """Text completion response model."""

    provider: str
    model: str
    choices: List[Dict[str, Any]]


class EmbeddingResponse(SuccessResponse):
    """Embedding response model."""

    provider: str
    model: str
    embeddings: List[List[float]]
    dimensions: int


class ImageResponse(SuccessResponse):
    """Image generation response model."""

    provider: str
    model: str
    images: List[Dict[str, Any]]
