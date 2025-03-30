"""
Resources package for indoxRouter.
This package contains resource classes for various AI functionalities.
"""

from .base import BaseResource
from .chat import Chat
from .completion import Completions
from .embedding import Embeddings
from .image import Images

__all__ = ["BaseResource", "Chat", "Completions", "Embeddings", "Images"]
