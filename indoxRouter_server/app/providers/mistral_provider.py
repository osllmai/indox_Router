"""
Mistral provider implementation for indoxRouter server.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

import mistralai
from mistralai.client import MistralClient
from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage

from app.providers.base_provider import BaseProvider


class MistralProvider(BaseProvider):
    """Mistral provider implementation."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Mistral provider.

        Args:
            api_key: The API key for Mistral.
            model_name: The name of the model to use.
        """
        # Clean up model name if needed (remove any provider prefix)
        if "/" in model_name:
            _, model_name = model_name.split("/", 1)

        super().__init__(api_key, model_name)
        self.client = MistralClient(api_key=api_key)
        self.async_client = MistralAsyncClient(api_key=api_key)

        # Model capabilities mapping
        self.model_capabilities = {
            "mistral-tiny": ["chat", "completion"],
            "mistral-small": ["chat", "completion"],
            "mistral-medium": ["chat", "completion"],
            "mistral-large": ["chat", "completion"],
            "open-mistral": ["chat", "completion"],
            "open-mixtral": ["chat", "completion"],
            "mistral-embed": ["embedding"],
        }

        # Model context window sizes
        self.context_window_sizes = {
            "mistral-tiny": 32000,
            "mistral-small": 32000,
            "mistral-medium": 32000,
            "mistral-large": 32000,
            "open-mistral": 8000,
            "open-mixtral": 32000,
        }

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to Mistral.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the response from Mistral.
        """
        try:
            # Convert OpenAI-style messages to Mistral format
            mistral_messages = self._convert_messages(messages)

            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            response = self.client.chat(
                model=self.model_name,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Format the response
            return {
                "choices": [
                    {
                        "message": {
                            "role": response.choices[0].message.role,
                            "content": response.choices[0].message.content,
                        },
                        "index": 0,
                        "finish_reason": response.choices[0].finish_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except mistralai.exceptions.MistralAPIException as e:
            raise Exception(f"Mistral API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to Mistral.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Mistral API.

        Yields:
            Chunks of the response from Mistral.
        """
        try:
            # Convert OpenAI-style messages to Mistral format
            mistral_messages = self._convert_messages(messages)

            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            stream_response = await self.async_client.chat_stream(
                model=self.model_name,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            async for chunk in stream_response:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        # Format the chunk as a JSON string
                        yield json.dumps(
                            {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": delta.content,
                                        },
                                        "index": 0,
                                        "finish_reason": chunk.choices[0].finish_reason,
                                    }
                                ]
                            }
                        )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a completion request to Mistral.
        Note: Mistral doesn't have a dedicated completion API, so we use the chat API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the response from Mistral.
        """
        try:
            # Convert prompt to a message
            messages = [{"role": "user", "content": prompt}]

            # Use the chat method
            chat_response = self.chat(messages, **kwargs)

            # Convert chat response to completion format
            return {
                "choices": [
                    {
                        "text": chat_response["choices"][0]["message"]["content"],
                        "index": 0,
                        "finish_reason": chat_response["choices"][0]["finish_reason"],
                    }
                ],
                "usage": chat_response["usage"],
            }
        except Exception as e:
            raise Exception(f"Error in text completion: {str(e)}")

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Send a streaming completion request to Mistral.
        Note: Mistral doesn't have a dedicated completion API, so we use the chat API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Mistral API.

        Yields:
            Chunks of the response from Mistral.
        """
        try:
            # Convert prompt to a message
            messages = [{"role": "user", "content": prompt}]

            # Use the chat_stream method
            async for chunk_str in self.chat_stream(messages, **kwargs):
                # Parse the chunk
                chunk = json.loads(chunk_str)

                # Convert chat chunk to completion format
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    yield json.dumps(
                        {
                            "choices": [
                                {
                                    "text": chunk["choices"][0]["delta"]["content"],
                                    "index": chunk["choices"][0]["index"],
                                    "finish_reason": chunk["choices"][0][
                                        "finish_reason"
                                    ],
                                }
                            ]
                        }
                    )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """
        Send an embedding request to Mistral.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the embeddings from Mistral.
        """
        try:
            # Ensure text is a list
            if isinstance(text, str):
                text_list = [text]
            else:
                text_list = text

            # Generate embeddings
            response = self.client.embeddings(
                model="mistral-embed",  # Mistral only has one embedding model
                input=text_list,
                **kwargs,
            )

            # Extract embeddings
            embeddings = [data.embedding for data in response.data]

            # Format the response
            return {
                "embeddings": embeddings,
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except mistralai.exceptions.MistralAPIException as e:
            raise Exception(f"Mistral API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in embedding: {str(e)}")

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt.
        Note: As of now, Mistral doesn't provide a public image generation API.
        This method raises an exception.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the image URL or data.
        """
        raise Exception("Image generation is not supported by Mistral API")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text.
        Note: Mistral doesn't provide a public token counting API, so we estimate.

        Args:
            text: The text to count tokens for.

        Returns:
            The estimated number of tokens in the text.
        """
        return self._estimate_tokens(text)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing information about the model.
        """
        # Get model capabilities
        model_id = self.model_name.lower()
        capabilities = []

        # Check if model is in our capabilities mapping
        for model_prefix, model_capabilities in self.model_capabilities.items():
            if model_id.startswith(model_prefix):
                capabilities = model_capabilities
                break

        # Get context window size
        context_window = self.context_window_sizes.get(model_id, 8000)

        # Basic model information
        model_info = {
            "id": self.model_name,
            "name": self.model_name,
            "provider": "mistral",
            "capabilities": capabilities,
            "max_tokens": context_window,
        }

        return model_info

    def _convert_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[MistralChatMessage]:
        """
        Convert OpenAI-style messages to Mistral format.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.

        Returns:
            A list of Mistral-style messages.
        """
        mistral_messages = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            # Mistral supports the same roles as OpenAI: system, user, assistant
            mistral_messages.append(MistralChatMessage(role=role, content=content))

        return mistral_messages

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        This is a rough estimate based on the common rule of thumb that 1 token ≈ 4 characters.

        Args:
            text: The text to estimate tokens for.

        Returns:
            The estimated number of tokens.
        """
        return len(text) // 4 + 1
