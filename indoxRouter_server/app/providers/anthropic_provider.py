"""
Anthropic (Claude) provider implementation for indoxRouter server.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

import anthropic
from anthropic import Anthropic
from anthropic.types import MessageParam

from app.providers.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic (Claude) provider implementation."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Anthropic provider.

        Args:
            api_key: The API key for Anthropic.
            model_name: The name of the model to use.
        """
        super().__init__(api_key, model_name)
        self.client = Anthropic(api_key=api_key)

        # Claude models have different max token limits
        self.max_tokens_map = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 100000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
            "claude-instant-1.1": 100000,
            "claude-instant-1.0": 100000,
        }

        # Default to 100k if model not found
        self.max_tokens = self.max_tokens_map.get(self.model_name, 100000)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to Anthropic.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Returns:
            A dictionary containing the response from Anthropic.
        """
        try:
            # Convert OpenAI-style messages to Anthropic format
            anthropic_messages = self._convert_messages(messages)

            # Extract parameters
            max_tokens = kwargs.pop("max_tokens", 1024)
            temperature = kwargs.pop("temperature", 0.7)

            response = self.client.messages.create(
                model=self.model_name,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Calculate token usage (Anthropic doesn't provide this directly)
            prompt_tokens = self._estimate_prompt_tokens(messages)
            completion_tokens = self._estimate_completion_tokens(
                response.content[0].text
            )

            # Format the response
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.content[0].text,
                        },
                        "index": 0,
                        "finish_reason": response.stop_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
        except anthropic.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except anthropic.APIError as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to Anthropic.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Yields:
            Chunks of the response from Anthropic.
        """
        try:
            # Convert OpenAI-style messages to Anthropic format
            anthropic_messages = self._convert_messages(messages)

            # Extract parameters
            max_tokens = kwargs.pop("max_tokens", 1024)
            temperature = kwargs.pop("temperature", 0.7)

            with self.client.messages.stream(
                model=self.model_name,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            ) as stream:
                for chunk in stream:
                    if chunk.type == "content_block_delta" and chunk.delta.text:
                        # Format the chunk as a JSON string
                        yield json.dumps(
                            {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": chunk.delta.text,
                                        },
                                        "index": 0,
                                        "finish_reason": None,
                                    }
                                ]
                            }
                        )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a completion request to Anthropic.
        Note: Anthropic doesn't have a dedicated completion API, so we use the chat API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Returns:
            A dictionary containing the response from Anthropic.
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
        Send a streaming completion request to Anthropic.
        Note: Anthropic doesn't have a dedicated completion API, so we use the chat API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Yields:
            Chunks of the response from Anthropic.
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
        Send an embedding request to Anthropic.
        Note: As of now, Anthropic doesn't provide a public embedding API.
        This method raises an exception.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Returns:
            A dictionary containing the embeddings from Anthropic.
        """
        raise Exception("Embedding is not supported by Anthropic API")

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt.
        Note: As of now, Anthropic doesn't provide a public image generation API.
        This method raises an exception.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the Anthropic API.

        Returns:
            A dictionary containing the image URL or data.
        """
        raise Exception("Image generation is not supported by Anthropic API")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text using Anthropic's tokenizer.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        return self.client.count_tokens(text)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing information about the model.
        """
        # Basic model information
        model_info = {
            "id": self.model_name,
            "name": self.model_name,
            "provider": "anthropic",
            "capabilities": ["chat", "completion"],
            "max_tokens": self.max_tokens,
        }

        return model_info

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[MessageParam]:
        """
        Convert OpenAI-style messages to Anthropic format.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.

        Returns:
            A list of Anthropic-style messages.
        """
        anthropic_messages = []

        # Extract system message if present
        system_content = None
        for message in messages:
            if message["role"] == "system":
                system_content = message["content"]
                break

        # Add non-system messages
        for message in messages:
            if message["role"] != "system":
                role = "user" if message["role"] == "user" else "assistant"
                anthropic_messages.append(
                    {
                        "role": role,
                        "content": message["content"],
                    }
                )

        return anthropic_messages

    def _estimate_prompt_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate the number of tokens in the prompt.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.

        Returns:
            The estimated number of tokens.
        """
        # Join all messages into a single string
        text = " ".join([msg["content"] for msg in messages])
        return self.client.count_tokens(text)

    def _estimate_completion_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the completion.

        Args:
            text: The completion text.

        Returns:
            The estimated number of tokens.
        """
        return self.client.count_tokens(text)
