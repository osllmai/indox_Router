"""
Models module for indoxRouter.
This module contains data models used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


@dataclass
class ChatMessage:
    """A chat message."""

    role: str
    content: str


@dataclass
class Usage:
    """Usage information for a response."""

    tokens_prompt: int = 0
    tokens_completion: int = 0
    tokens_total: int = 0
    cost: float = 0.0
    latency: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatResponse:
    """Response from a chat request."""

    # Required fields (no defaults)
    data: str
    model: str
    provider: str
    success: bool
    message: str

    # Fields with defaults
    usage: Usage = field(default_factory=Usage)
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class CompletionResponse:
    """Response from a completion request."""

    # Required fields (no defaults)
    data: str
    model: str
    provider: str
    success: bool
    message: str

    # Fields with defaults
    usage: Usage = field(default_factory=Usage)
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingResponse:
    """Response from an embedding request."""

    data: Union[List[Dict[str, Any]], List[List[float]], List[float]]
    model: str
    provider: str
    success: bool
    message: str

    # Fields with defaults
    usage: Usage = field(default_factory=Usage)
    dimensions: int = 0
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class ImageResponse:
    """Response from an image generation request."""

    images: List[str]  # URLs or base64 encoded images
    model: str
    provider: str

    # Fields with defaults
    usage: Usage = field(default_factory=Usage)
    sizes: List[str] = field(default_factory=list)
    formats: List[str] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class ModelInfo:
    """Information about a model."""

    name: str
    provider: str
    type: str
    description: Optional[str] = None
    input_price_per_1k_tokens: float = 0.0
    output_price_per_1k_tokens: float = 0.0
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    recommended: bool = False
    commercial: bool = False
    pricey: bool = False
    raw_info: Optional[Dict[str, Any]] = None
