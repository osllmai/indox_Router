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


class DeepSeekProvider(BaseProvider):
    """DeepSeek provider implementation."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the DeepSeek provider.

        Args:
            api_key: The API key for DeepSeek.
            model_name: The name of the model to use.
        """
        # Clean up model name if needed (remove any provider prefix)
        if "/" in model_name:
            _, model_name = model_name.split("/", 1)

        super().__init__(api_key, model_name)

        # DeepSeek base URL for API calls
        self.DEEPSEEK_BASE_URL = "https://api.deepseek.com"

        # Initialize OpenAI client with the DeepSeek base URL
        self.client = OpenAI(api_key=api_key, base_url=self.DEEPSEEK_BASE_URL)

        # Initialize async client
        self.async_client = AsyncOpenAI(
            api_key=api_key, base_url=self.DEEPSEEK_BASE_URL
        )

        # List of supported models based on the JSON configuration
        self.supported_models = [
            "deepseek-chat",
            "deepseek-coder-33b-instruct",
            "deepseek-coder-6.7b-instruct",
            "deepseek-math-7b",
            "deepseek-v2-base",
            "deepseek-vision-7b",
        ]

        print(f"Supported DeepSeek models: {self.supported_models}")

        if model_name not in self.supported_models:
            print(f"WARNING: Model '{model_name}' not found in supported models.")
            print(
                f"Will attempt to use it anyway, but it may fail if not supported by DeepSeek API."
            )

        # Set up tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fall back to cl100k_base for newer models not yet in tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chat(self, messages: List[Any], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to DeepSeek using the OpenAI SDK.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys or ChatMessage objects.
            **kwargs: Additional parameters to pass to the DeepSeek API.

        Returns:
            A dictionary containing the response from DeepSeek.
        """
        try:
            # Normalize messages to dictionary format if they're from another format
            normalized_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    normalized_messages.append(msg)
                elif hasattr(msg, "role") and hasattr(msg, "content"):
                    normalized_messages.append(
                        {"role": msg.role, "content": msg.content}
                    )
                else:
                    print(f"Warning: Unknown message type: {type(msg).__name__}")

            print(f"Sending chat request to DeepSeek using model: {self.model_name}")
            print(
                f"Request parameters: temperature={kwargs.get('temperature', 'default')}, max_tokens={kwargs.get('max_tokens', 'default')}"
            )
            print(f"Number of messages: {len(normalized_messages)}")

            # Configure OpenAI client with DeepSeek base URL
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=normalized_messages,
                **kwargs,
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
            print(f"DeepSeek Rate Limit Error: {str(e)}")
            raise Exception(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            print(f"DeepSeek API Error: {str(e)}")
            error_message = str(e)

            # Check for model not found errors
            if "does not exist" in error_message or "not found" in error_message:
                recommendations = ", ".join(self.supported_models)
                print(f"Model not found. Recommended models: {recommendations}")
                raise Exception(
                    f"API error: {str(e)}. Try one of these models instead: {recommendations}"
                )

            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            print(f"DeepSeek General Error: {str(e)}")
            raise Exception(f"Error in chat completion: {str(e)}")

    async def chat_stream(
        self, messages: List[Any], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to DeepSeek.

        Args:
            messages: A list of message dictionaries or ChatMessage objects.
            **kwargs: Additional parameters to pass to the DeepSeek API.

        Yields:
            Chunks of the response from DeepSeek.
        """
        try:
            # Normalize messages to dictionary format
            normalized_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    normalized_messages.append(msg)
                elif hasattr(msg, "role") and hasattr(msg, "content"):
                    normalized_messages.append(
                        {"role": msg.role, "content": msg.content}
                    )
                else:
                    print(
                        f"Warning: Unknown message type in streaming: {type(msg).__name__}"
                    )

            print(f"Streaming chat request to DeepSeek using model: {self.model_name}")

            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=normalized_messages,
                stream=True,
                **kwargs,
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
        Send a completion request to DeepSeek.
        For DeepSeek, we'll convert this to a chat request since that's their primary API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the DeepSeek API.

        Returns:
            A dictionary containing the response from DeepSeek.
        """
        try:
            print(
                f"Converting completion request to chat for DeepSeek with prompt: {prompt[:30]}..."
            )

            # Convert to message format for DeepSeek
            messages = [{"role": "user", "content": prompt}]

            # Use the chat API with the converted message
            chat_response = self.chat(messages=messages, **kwargs)

            # Extract content from the response
            if "choices" in chat_response and len(chat_response["choices"]) > 0:
                content = chat_response["choices"][0]["message"]["content"]

                # Format as completion response
                return {
                    "choices": [
                        {
                            "text": content,
                            "index": 0,
                            "finish_reason": chat_response["choices"][0][
                                "finish_reason"
                            ],
                        }
                    ],
                    "usage": chat_response["usage"],
                }

            # Return empty response if chat response is invalid
            return {
                "choices": [{"text": "", "index": 0, "finish_reason": "error"}],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }
        except Exception as e:
            raise Exception(f"Error in text completion: {str(e)}")

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion request to DeepSeek.
        For DeepSeek, we convert this to a chat request since that's their primary API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the DeepSeek API.

        Yields:
            Chunks of the response from DeepSeek.
        """
        try:
            print(
                f"Converting streaming completion to chat for DeepSeek: {prompt[:30]}..."
            )

            # Convert to message format for DeepSeek
            messages = [{"role": "user", "content": prompt}]

            # Use streaming chat with the converted message format
            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        # Format the chat chunk as a completion-style response
                        yield json.dumps(
                            {
                                "choices": [
                                    {
                                        "text": delta.content,
                                        "index": chunk.choices[0].index,
                                        "finish_reason": chunk.choices[0].finish_reason,
                                    }
                                ]
                            }
                        )
        except Exception as e:
            print(f"DeepSeek streaming error: {str(e)}")
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
                model=self.model_name,
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
            **kwargs: Additional parameters to pass to the DeepSeek API.

        Returns:
            A dictionary containing the image URL or data.
        """
        try:
            # Extract parameters
            size = kwargs.pop("size", "1024x1024")
            n = kwargs.pop("n", 1)

            response = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size=size,
                n=n,
                **kwargs,
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
