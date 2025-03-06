"""
Resources module for indoxRouter.
This module contains resource classes for different API endpoints.
"""

from .base import BaseResource
from .chat import Chat
from .completion import Completions
from .embedding import Embeddings
from .image import Images
from .models import Models

__all__ = [
    "BaseResource",
    "Chat",
    "Completions",
    "Embeddings",
    "Images",
    "Models",
]
