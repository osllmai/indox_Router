"""
Pydantic models for request and response schemas.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class Usage(BaseModel):
    """Usage information model."""

    tokens_prompt: int = 0
    tokens_completion: int = 0
    tokens_total: int = 0
    cost: float = 0.0
    latency: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


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
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CompletionRequest(BaseModel):
    """Text completion request model."""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
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
    token_type: str
    expires_in: int


class UserCreate(BaseModel):
    """User registration model."""

    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    credits: float
    account_tier: str
    created_at: datetime


class GoogleAuthRequest(BaseModel):
    """Google authentication request model."""

    token: str  # Google ID token


class AuthResponse(BaseModel):
    """Authentication response model."""

    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class PricingInfo(BaseModel):
    """Model pricing information."""

    input: float = 0.0
    output: float = 0.0
    currency: str = "USD"
    unit: str = "1K tokens"


class ModelInfo(BaseModel):
    """Model information model."""

    id: str
    name: str
    provider: str
    capabilities: List[str]
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    pricing: Optional[PricingInfo] = None
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
    provider: str
    model: str
    success: bool = True
    message: str = ""
    usage: Optional[Usage] = None
    raw_response: Optional[Dict[str, Any]] = None


class ChatResponse(SuccessResponse):
    """Chat completion response model."""

    data: str = ""
    finish_reason: Optional[str] = None


class CompletionResponse(SuccessResponse):
    """Text completion response model."""

    data: str = ""
    finish_reason: Optional[str] = None


class EmbeddingResponse(SuccessResponse):
    """Embedding response model."""

    data: List[List[float]] = Field(default_factory=list)
    dimensions: int = 0


class ImageResponse(SuccessResponse):
    """Image generation response model."""

    data: List[Dict[str, Any]] = Field(default_factory=list)


class TokenUsage(BaseModel):
    input: int
    output: int
    total: int


class UsageStats(BaseModel):
    requests: int
    cost: float
    tokens: TokenUsage


class DailyUsage(BaseModel):
    date: str
    requests: int
    cost: float
    tokens: TokenUsage


class UsageResponse(BaseModel):
    total_requests: int
    total_cost: float
    remaining_credits: float
    total_tokens: TokenUsage = None
    endpoints: Dict[str, UsageStats]
    providers: Dict[str, UsageStats]
    models: Dict[str, Dict[str, Any]]
    daily_usage: List[DailyUsage]


class ApiKeyCreate(BaseModel):
    """API key creation request model."""

    name: str = "API Key"


class ApiKeyResponse(BaseModel):
    """API key response model."""

    id: int
    api_key: str
    name: str
    created_at: datetime
    expires_at: datetime


class ApiKeyList(BaseModel):
    """API key list response model."""

    keys: List[ApiKeyResponse]


class CreditPurchase(BaseModel):
    """Credit purchase request model."""

    amount: float
    payment_method: str = "credit_card"
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response model."""

    transaction_id: str
    amount: float
    credits_added: float
    total_credits: float
    created_at: datetime


class TransactionItem(BaseModel):
    """Transaction item model for listing transactions."""

    id: int
    transaction_id: str
    amount: float
    currency: str
    transaction_type: str
    status: str
    payment_method: str
    description: Optional[str]
    created_at: datetime


class TransactionList(BaseModel):
    """Transaction list response model."""

    transactions: List[TransactionItem]
    total_count: int
