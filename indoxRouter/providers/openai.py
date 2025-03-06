"""
OpenAI provider for indoxRouter.
"""

import os
from typing import Dict, List, Any, Optional, Union

import openai
from openai import OpenAI
from datetime import datetime
from .base_provider import BaseProvider
from ..exceptions import AuthenticationError, RequestError, RateLimitError
from ..utils import calculate_cost, get_model_info
from ..models import ChatMessage


class Provider(BaseProvider):
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
        self.model_info = get_model_info("openai", model_name)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to OpenAI.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the response from OpenAI.
            If stream=True and return_generator=True, returns a generator that yields chunks of the response.

        Raises:
            AuthenticationError: If the API key is invalid.
            RequestError: If the request fails.
            RateLimitError: If the rate limit is exceeded.
        """
        try:
            # Check if streaming is requested
            stream = kwargs.pop("stream", False)
            # Check if we should return a generator
            return_generator = kwargs.pop("return_generator", False)

            # If streaming is requested, we need to handle it differently
            if stream:
                # Remove stream from kwargs to avoid passing it twice
                openai_messages = []
                for msg in messages:
                    if isinstance(msg, ChatMessage):
                        openai_messages.append(
                            {"role": msg.role, "content": msg.content}
                        )
                    else:
                        openai_messages.append(msg)

                # Create the streaming response
                stream_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=openai_messages,
                    stream=True,
                    **kwargs,
                )

                # If return_generator is True, return a generator that yields chunks
                if return_generator:
                    # Create a streaming generator with usage tracking
                    return StreamingGenerator(
                        stream_response=stream_response,
                        model_name=self.model_name,
                        messages=messages,
                    )

                # Otherwise, collect the full response content from the stream
                content = ""
                for chunk in stream_response:
                    if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content is not None:
                            content += delta.content

                # For streaming responses, we don't have usage information directly
                # We'll provide a minimal response with the content
                return {
                    "data": content,
                    "model": self.model_name,
                    "provider": "openai",
                    "success": True,
                    "message": "Successfully completed streaming chat request",
                    "cost": 0.0,  # We don't have cost information for streaming responses
                    "timestamp": datetime.now().isoformat(),
                    "usage": {
                        "tokens_prompt": 0,  # We don't have token information for streaming responses
                        "tokens_completion": 0,
                        "tokens_total": 0,
                    },
                    "finish_reason": "stop",  # Default finish reason
                    "raw_response": None,  # We don't have the raw response for streaming
                }

            # Handle non-streaming responses as before
            openai_messages = []
            for msg in messages:
                if isinstance(msg, ChatMessage):
                    openai_messages.append({"role": msg.role, "content": msg.content})
                else:
                    openai_messages.append(msg)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                **kwargs,
            )
            # Extract the response content
            content = response.choices[0].message.content

            # Extract usage information from the response
            prompt_tokens = (
                response.usage.prompt_tokens
                if hasattr(response.usage, "prompt_tokens")
                else 0
            )
            completion_tokens = (
                response.usage.completion_tokens
                if hasattr(response.usage, "completion_tokens")
                else 0
            )
            total_tokens = (
                response.usage.total_tokens
                if hasattr(response.usage, "total_tokens")
                else 0
            )

            cost = calculate_cost(
                f"openai/{self.model_name}",
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
            )

            # Create a response dictionary with the extracted information
            return {
                "data": content,
                "model": self.model_name,
                "provider": "openai",
                "success": True,
                "message": "Successfully completed chat request",
                "cost": cost,
                "timestamp": datetime.now().isoformat(),
                # Add usage as dict with consistent field names
                "usage": {
                    "tokens_prompt": prompt_tokens,
                    "tokens_completion": completion_tokens,
                    "tokens_total": total_tokens,
                },
                # Optional fields
                "finish_reason": response.choices[0].finish_reason,
                "raw_response": response.model_dump(),
            }

        except openai.AuthenticationError:
            raise AuthenticationError("Invalid OpenAI API key.")
        except openai.RateLimitError:
            raise RateLimitError("OpenAI rate limit exceeded.")
        except Exception as e:
            raise RequestError(f"OpenAI request failed: {str(e)}")

    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a completion request to OpenAI.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the response from OpenAI.
            If stream=True and return_generator=True, returns a generator that yields chunks of the response.

        Raises:
            AuthenticationError: If the API key is invalid.
            RequestError: If the request fails.
            RateLimitError: If the rate limit is exceeded.
        """
        # Check if streaming is requested
        stream = kwargs.pop("stream", False)
        return_generator = kwargs.pop("return_generator", False)

        # For OpenAI, we'll use the chat API for completions as well
        messages = [{"role": "user", "content": prompt}]

        # If streaming is requested, handle it through the chat method
        if stream:
            return self.chat(
                messages, stream=True, return_generator=return_generator, **kwargs
            )

        # Otherwise, use the regular chat method
        return self.chat(messages, **kwargs)

    def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """
        Send an embedding request to OpenAI.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the embeddings from OpenAI.

        Raises:
            AuthenticationError: If the API key is invalid.
            RequestError: If the request fails.
            RateLimitError: If the rate limit is exceeded.
        """
        try:
            # Ensure text is a list
            if isinstance(text, str):
                text = [text]

            # Use the embedding model
            response = self.client.embeddings.create(
                model=self.model_name, input=text, **kwargs
            )

            # Extract embeddings
            embeddings = [item.embedding for item in response.data]

            # Create a list of embedding objects with the expected structure
            embedding_objects = []
            for i, embedding in enumerate(embeddings):
                embedding_objects.append(
                    {
                        "embedding": embedding,
                        "index": i,
                        "text": text[i] if i < len(text) else "",
                    }
                )

            # Extract usage information from the response
            prompt_tokens = (
                response.usage.prompt_tokens
                if hasattr(response.usage, "prompt_tokens")
                else 0
            )
            total_tokens = (
                response.usage.total_tokens
                if hasattr(response.usage, "total_tokens")
                else 0
            )

            embedding_price_per_1k = get_model_info("openai", self.model_name).get(
                "inputPricePer1KTokens"
            )

            # Calculate the cost
            cost = (prompt_tokens / 1000) * embedding_price_per_1k

            # Create usage information
            usage = {
                "tokens_prompt": prompt_tokens,
                "tokens_completion": 0,
                "tokens_total": total_tokens,
                "cost": cost,
                "latency": 0.0,  # We don't have latency information from the API
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "data": embedding_objects,
                "model": self.model_name,
                "provider": "openai",
                "success": True,
                "message": "Successfully generated embeddings",
                "usage": usage,
                "raw_response": response.model_dump(),
            }
        except openai.AuthenticationError:
            raise AuthenticationError("Invalid OpenAI API key.")
        except openai.RateLimitError:
            raise RateLimitError("OpenAI rate limit exceeded.")
        except Exception as e:
            raise RequestError(f"OpenAI embedding request failed: {str(e)}")

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt using OpenAI.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            A dictionary containing the image URL or data.

        Raises:
            AuthenticationError: If the API key is invalid.
            RequestError: If the request fails.
            RateLimitError: If the rate limit is exceeded.
        """
        try:
            # Use DALL-E model
            model = kwargs.get("model", "dall-e-3")
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")
            n = kwargs.get("n", 1)

            response = self.client.images.generate(
                model=model, prompt=prompt, size=size, quality=quality, n=n
            )

            # Extract image URLs
            images = [item.url for item in response.data]

            # For image generation, we don't have token usage, so we'll estimate cost
            # based on the model and parameters
            cost = calculate_cost(
                f"openai/{model}",  # e.g., "openai/dall-e-3"
                input_tokens=n,  # Number of images
                output_tokens=0,
            )

            # Create usage information
            usage = {
                "tokens_prompt": 0,  # We don't have token information for images
                "tokens_completion": 0,
                "tokens_total": 0,
                "cost": cost,
                "latency": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "data": images,
                "model": model,
                "provider": "openai",
                "success": True,
                "message": "Successfully generated images",
                "usage": usage,
                "sizes": [size] * n,
                "formats": ["url"] * n,
                "raw_response": response.model_dump(),
            }

        except openai.AuthenticationError:
            raise AuthenticationError("Invalid OpenAI API key.")
        except openai.RateLimitError:
            raise RateLimitError("OpenAI rate limit exceeded.")
        except Exception as e:
            raise RequestError(f"OpenAI image generation request failed: {str(e)}")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text using OpenAI's tokenizer.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        try:
            # Use tiktoken for token counting
            import tiktoken

            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to a simple approximation if tiktoken is not available
            return len(text.split()) * 1.3  # Rough approximation

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing information about the model.
        """
        return self.model_info


class StreamingGenerator:
    """
    A generator class that yields chunks of text from a streaming response
    and provides methods to get usage information at any point.
    """

    def __init__(self, stream_response, model_name, messages):
        """
        Initialize the streaming generator.

        Args:
            stream_response: The streaming response from the provider.
            model_name: The name of the model being used.
            messages: The messages sent to the provider.
        """
        self.stream_response = stream_response
        self.model_name = model_name
        self.messages = messages
        self.full_content = ""
        self.finish_reason = None
        self.is_finished = False

        # Try to initialize tiktoken for token counting
        try:
            import tiktoken

            self.encoding = tiktoken.encoding_for_model(model_name)
            self.has_tiktoken = True
        except (ImportError, Exception):
            self.has_tiktoken = False

        # Estimate prompt tokens
        self.prompt_tokens = self._count_prompt_tokens()

    def _count_prompt_tokens(self):
        """Count tokens in the prompt messages."""
        if self.has_tiktoken:
            # Use tiktoken for accurate token counting
            prompt_text = " ".join(
                [
                    msg.get("content", "") if isinstance(msg, dict) else msg.content
                    for msg in self.messages
                ]
            )
            return len(self.encoding.encode(prompt_text))
        else:
            # Fallback to character-based estimation
            prompt_text = " ".join(
                [
                    msg.get("content", "") if isinstance(msg, dict) else msg.content
                    for msg in self.messages
                ]
            )
            return len(prompt_text) // 4  # Rough estimate: 4 chars per token

    def _count_completion_tokens(self):
        """Count tokens in the completion text."""
        if self.has_tiktoken:
            # Use tiktoken for accurate token counting
            return len(self.encoding.encode(self.full_content))
        else:
            # Fallback to character-based estimation
            return len(self.full_content) // 4  # Rough estimate: 4 chars per token

    def get_usage_info(self):
        """
        Get usage information based on the current state.

        Returns:
            A dictionary with usage information.
        """
        completion_tokens = self._count_completion_tokens()
        total_tokens = self.prompt_tokens + completion_tokens

        # Calculate cost
        cost = calculate_cost(
            f"openai/{self.model_name}",
            input_tokens=self.prompt_tokens,
            output_tokens=completion_tokens,
        )

        return {
            "usage": {
                "tokens_prompt": self.prompt_tokens,
                "tokens_completion": completion_tokens,
                "tokens_total": total_tokens,
            },
            "cost": cost,
            "model": self.model_name,
            "provider": "openai",
            "finish_reason": self.finish_reason,
            "is_finished": self.is_finished,
        }

    def __iter__(self):
        return self

    def __next__(self):
        """Get the next chunk from the stream."""
        if self.is_finished:
            raise StopIteration

        try:
            chunk = next(self.stream_response)

            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                # Check for finish reason
                if (
                    hasattr(chunk.choices[0], "finish_reason")
                    and chunk.choices[0].finish_reason
                ):
                    self.finish_reason = chunk.choices[0].finish_reason

                # Get content delta
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content is not None:
                    content_chunk = delta.content
                    self.full_content += content_chunk
                    return content_chunk

                # If we got a chunk with no content but with finish_reason, we're done
                if self.finish_reason:
                    self.is_finished = True
                    raise StopIteration

            # If we got here, try the next chunk
            return next(self)

        except StopIteration:
            self.is_finished = True
            raise
