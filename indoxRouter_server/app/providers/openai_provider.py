"""
OpenAI provider implementation for indoxRouter server.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

import openai
from openai import OpenAI
from openai import AsyncOpenAI
import tiktoken

from app.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: The API key for OpenAI.
            model_name: The name of the model to use.
        """
        super().__init__(api_key, model_name)
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

        # Set up tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fall back to cl100k_base for newer models not yet in tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to OpenAI.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the response from OpenAI.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name, messages=messages, **kwargs
            )

            # Format the response
            return {
                "choices": [
                    {
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                        },
                        "index": choice.index,
                        "finish_reason": choice.finish_reason,
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except openai.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to OpenAI.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Yields:
            Chunks of the response from OpenAI.
        """
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model_name, messages=messages, stream=True, **kwargs
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
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
                                        "index": chunk.choices[0].index,
                                        "finish_reason": chunk.choices[0].finish_reason,
                                    }
                                ]
                            }
                        )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a completion request to OpenAI.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the response from OpenAI.
        """
        try:
            response = self.client.completions.create(
                model=self.model_name, prompt=prompt, **kwargs
            )

            # Format the response
            return {
                "choices": [
                    {
                        "text": choice.text,
                        "index": choice.index,
                        "finish_reason": choice.finish_reason,
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except openai.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in text completion: {str(e)}")

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Send a streaming completion request to OpenAI.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Yields:
            Chunks of the response from OpenAI.
        """
        try:
            stream = await self.async_client.completions.create(
                model=self.model_name, prompt=prompt, stream=True, **kwargs
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    # Format the chunk as a JSON string
                    yield json.dumps(
                        {
                            "choices": [
                                {
                                    "text": chunk.choices[0].text,
                                    "index": chunk.choices[0].index,
                                    "finish_reason": chunk.choices[0].finish_reason,
                                }
                            ]
                        }
                    )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """
        Send an embedding request to OpenAI.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the embeddings from OpenAI.
        """
        try:
            # Ensure text is a list
            if isinstance(text, str):
                text_list = [text]
            else:
                text_list = text

            response = self.client.embeddings.create(
                model=self.model_name, input=text_list, **kwargs
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
        except openai.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in embedding: {str(e)}")

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt using DALL-E.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the image URL or data.
        """
        try:
            # Extract parameters
            size = kwargs.pop("size", "1024x1024")
            n = kwargs.pop("n", 1)

            response = self.client.images.generate(
                model=self.model_name, prompt=prompt, size=size, n=n, **kwargs
            )

            # Format the response
            return {
                "images": [
                    {
                        "url": image.url,
                        "revised_prompt": getattr(image, "revised_prompt", None),
                    }
                    for image in response.data
                ],
            }
        except openai.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in image generation: {str(e)}")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text using tiktoken.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        return len(self.tokenizer.encode(text))

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
            "provider": "openai",
            "capabilities": [],
        }

        # Add capabilities based on model name
        if "gpt" in self.model_name.lower():
            model_info["capabilities"].append("chat")
            model_info["capabilities"].append("completion")
        elif "text-embedding" in self.model_name.lower():
            model_info["capabilities"].append("embedding")
        elif "dall-e" in self.model_name.lower():
            model_info["capabilities"].append("image")

        return model_info
