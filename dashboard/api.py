"""
API client for communicating with the IndoxRouter server.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_URL = os.getenv("INDOXROUTER_API_URL", "http://localhost:8000/api/v1")


class IndoxRouterClient:
    """Client for the IndoxRouter API."""

    def __init__(self, api_key: str):
        """
        Initialize the client.

        Args:
            api_key: The API key to use for authentication
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get_models(self) -> Dict[str, Any]:
        """
        Get available models.

        Returns:
            List of available models
        """
        try:
            response = requests.get(f"{API_URL}/models", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def chat(
        self, messages: List[Dict[str, str]], model: str = None, provider: str = None
    ) -> Dict[str, Any]:
        """
        Send a chat request.

        Args:
            messages: List of messages
            model: Optional model to use
            provider: Optional provider to use

        Returns:
            Chat response
        """
        try:
            data = {"messages": messages}
            if model:
                data["model"] = model
            if provider:
                data["provider"] = provider

            response = requests.post(f"{API_URL}/chat", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def generate_image(
        self, prompt: str, model: str = None, provider: str = None
    ) -> Dict[str, Any]:
        """
        Generate an image.

        Args:
            prompt: The image prompt
            model: Optional model to use
            provider: Optional provider to use

        Returns:
            Image generation response
        """
        try:
            data = {"prompt": prompt}
            if model:
                data["model"] = model
            if provider:
                data["provider"] = provider

            response = requests.post(
                f"{API_URL}/images/generate", headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def create_embedding(
        self, input_text: str, model: str = None, provider: str = None
    ) -> Dict[str, Any]:
        """
        Create an embedding.

        Args:
            input_text: The text to embed
            model: Optional model to use
            provider: Optional provider to use

        Returns:
            Embedding response
        """
        try:
            data = {"input": input_text}
            if model:
                data["model"] = model
            if provider:
                data["provider"] = provider

            response = requests.post(
                f"{API_URL}/embeddings", headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
