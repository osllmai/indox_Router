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
        # Clean up model name if needed (remove any provider prefix)
        if "/" in model_name:
            _, model_name = model_name.split("/", 1)

        super().__init__(api_key, model_name)
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

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
        # Check if streaming is requested
        stream = kwargs.pop("stream", False)

        # If streaming is requested, handle it separately
        if stream:
            # Create a very simple synchronous generator that doesn't use event loops
            def sync_stream_generator():
                import asyncio
                import threading
                import queue

                # Create a queue to communicate between threads
                result_queue = queue.Queue()

                # Function to run in a separate thread
                def run_async_stream():
                    try:
                        # Create a new loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        # Define an async function to process the stream
                        async def process_stream():
                            try:
                                # Create the streaming request
                                stream_response = (
                                    await self.async_client.chat.completions.create(
                                        model=self.model_name,
                                        messages=messages,
                                        stream=True,
                                        **kwargs,
                                    )
                                )

                                # Process each chunk
                                async for chunk in stream_response:
                                    if chunk.choices and len(chunk.choices) > 0:
                                        delta = chunk.choices[0].delta
                                        if hasattr(delta, "content") and delta.content:
                                            # Format chunk and put in queue
                                            json_chunk = json.dumps(
                                                {
                                                    "choices": [
                                                        {
                                                            "delta": {
                                                                "content": delta.content
                                                            },
                                                            "index": chunk.choices[
                                                                0
                                                            ].index,
                                                            "finish_reason": chunk.choices[
                                                                0
                                                            ].finish_reason,
                                                        }
                                                    ]
                                                }
                                            )
                                            result_queue.put(json_chunk)
                            except Exception as e:
                                result_queue.put(json.dumps({"error": str(e)}))
                            finally:
                                # Signal that we're done
                                result_queue.put(None)

                        # Run the async function to completion
                        loop.run_until_complete(process_stream())
                    except Exception as e:
                        result_queue.put(json.dumps({"error": str(e)}))
                        result_queue.put(None)  # Signal we're done
                    finally:
                        loop.close()

                # Start a thread to run the async code
                thread = threading.Thread(target=run_async_stream)
                thread.daemon = (
                    True  # Allow the thread to exit when the main thread exits
                )
                thread.start()

                # Yield results from the queue as they arrive
                while True:
                    chunk = result_queue.get()
                    if chunk is None:  # End of stream signal
                        break
                    yield chunk

            # Return the synchronous generator
            return sync_stream_generator()

        # Non-streaming request
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
            # Check if streaming is requested
            stream = kwargs.pop("stream", False)
            if stream:
                return self._stream_completion(prompt, **kwargs)

            # OpenAi completions require the beta API
            messages = [{"role": "user", "content": prompt}]

            # Pass through relevant parameters
            chat_kwargs = {}
            for key, value in kwargs.items():
                if key in [
                    "temperature",
                    "max_tokens",
                    "top_p",
                    "frequency_penalty",
                    "presence_penalty",
                    "n",
                    "stop",
                ]:
                    chat_kwargs[key] = value

            # Try using the completions API first
            try:
                # Check if we have a beta client
                if hasattr(self, "beta_client"):
                    response = self.beta_client.completions.create(
                        model=self.model_name, prompt=prompt, **chat_kwargs
                    )
                else:
                    # Fall back to regular client for completions
                    response = self.client.completions.create(
                        model=self.model_name, prompt=prompt, **chat_kwargs
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
            except Exception as completion_error:
                # Fallback to chat API
                response = self.client.chat.completions.create(
                    model=self.model_name, messages=messages, **chat_kwargs
                )

                # Format the response to match completions API format
                return {
                    "choices": [
                        {
                            "text": choice.message.content,
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

    def _stream_completion(self, prompt: str, **kwargs):
        """Internal helper for streaming completions"""

        def sync_stream_generator():
            import asyncio
            import threading
            import queue

            # Create a queue to communicate between threads
            result_queue = queue.Queue()

            # Function to run in a separate thread
            def run_async_stream():
                try:
                    # Create a new loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    # Define an async function to process the stream
                    async def process_stream():
                        try:
                            # Try beta endpoint first if it exists
                            if hasattr(self, "async_beta_client"):
                                try:
                                    stream = (
                                        await self.async_beta_client.completions.create(
                                            model=self.model_name,
                                            prompt=prompt,
                                            stream=True,
                                            **kwargs,
                                        )
                                    )

                                    async for chunk in stream:
                                        if (
                                            hasattr(chunk, "choices")
                                            and chunk.choices
                                            and len(chunk.choices) > 0
                                        ):
                                            json_chunk = json.dumps(
                                                {
                                                    "choices": [
                                                        {
                                                            "text": chunk.choices[
                                                                0
                                                            ].text,
                                                            "index": chunk.choices[
                                                                0
                                                            ].index,
                                                            "finish_reason": chunk.choices[
                                                                0
                                                            ].finish_reason,
                                                        }
                                                    ]
                                                }
                                            )
                                            result_queue.put(json_chunk)
                                except Exception as beta_error:
                                    result_queue.put(
                                        json.dumps(
                                            {
                                                "error": f"Beta client error: {str(beta_error)}"
                                            }
                                        )
                                    )
                                    # Continue to fallback

                            # Fallback to chat API
                            messages = [{"role": "user", "content": prompt}]
                            stream = await self.async_client.chat.completions.create(
                                model=self.model_name,
                                messages=messages,
                                stream=True,
                                **kwargs,
                            )

                            async for chunk in stream:
                                if (
                                    hasattr(chunk, "choices")
                                    and chunk.choices
                                    and len(chunk.choices) > 0
                                ):
                                    delta = chunk.choices[0].delta
                                    if hasattr(delta, "content") and delta.content:
                                        json_chunk = json.dumps(
                                            {
                                                "choices": [
                                                    {
                                                        "text": delta.content,
                                                        "index": chunk.choices[0].index,
                                                        "finish_reason": chunk.choices[
                                                            0
                                                        ].finish_reason,
                                                    }
                                                ]
                                            }
                                        )
                                        result_queue.put(json_chunk)
                        except Exception as e:
                            result_queue.put(json.dumps({"error": str(e)}))
                        finally:
                            # Signal that we're done
                            result_queue.put(None)

                    # Run the async function
                    loop.run_until_complete(process_stream())
                except Exception as e:
                    result_queue.put(json.dumps({"error": str(e)}))
                    result_queue.put(None)  # Signal we're done
                finally:
                    loop.close()

            # Start a thread to run the async code
            thread = threading.Thread(target=run_async_stream)
            thread.daemon = True
            thread.start()

            # Yield results from the queue as they arrive
            while True:
                chunk = result_queue.get()
                if chunk is None:  # End of stream signal
                    break
                yield chunk

        # Return the synchronous generator
        return sync_stream_generator()

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
            # Check if we're using a newer model that doesn't support completions API
            newer_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o"]
            is_newer_model = any(
                model in self.model_name.lower() for model in newer_models
            )

            if is_newer_model:
                # For newer models, use the chat completions API
                messages = [{"role": "user", "content": prompt}]

                # Pass through relevant parameters
                chat_kwargs = {k: v for k, v in kwargs.items() if k not in ["stream"]}

                # Create chat stream
                stream = await self.async_client.chat.completions.create(
                    model=self.model_name, messages=messages, stream=True, **chat_kwargs
                )

                # Process each chunk and convert to completions format
                async for chunk in stream:
                    if (
                        hasattr(chunk, "choices")
                        and chunk.choices
                        and len(chunk.choices) > 0
                    ):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            # Format as completions API response
                            yield json.dumps(
                                {
                                    "choices": [
                                        {
                                            "text": delta.content,
                                            "index": chunk.choices[0].index,
                                            "finish_reason": chunk.choices[
                                                0
                                            ].finish_reason,
                                        }
                                    ]
                                }
                            )
            else:
                # Use legacy completions API for supported models
                stream = await self.async_client.completions.create(
                    model=self.model_name, prompt=prompt, stream=True, **kwargs
                )

                async for chunk in stream:
                    if (
                        hasattr(chunk, "choices")
                        and chunk.choices
                        and len(chunk.choices) > 0
                    ):
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
        except openai.APIError as e:
            if "Invalid URL" in str(e) and "completions" in str(e):
                # Fallback to chat completions for streaming
                try:
                    messages = [{"role": "user", "content": prompt}]

                    # Pass through relevant parameters
                    chat_kwargs = {
                        k: v for k, v in kwargs.items() if k not in ["stream"]
                    }

                    # Create chat stream
                    stream = await self.async_client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        stream=True,
                        **chat_kwargs,
                    )

                    # Process each chunk and convert to completions format
                    async for chunk in stream:
                        if (
                            hasattr(chunk, "choices")
                            and chunk.choices
                            and len(chunk.choices) > 0
                        ):
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                # Format as completions API response
                                yield json.dumps(
                                    {
                                        "choices": [
                                            {
                                                "text": delta.content,
                                                "index": chunk.choices[0].index,
                                                "finish_reason": chunk.choices[
                                                    0
                                                ].finish_reason,
                                            }
                                        ]
                                    }
                                )
                except Exception as chat_error:
                    yield json.dumps(
                        {
                            "error": f"Failed to use chat API for streaming: {str(chat_error)}"
                        }
                    )
            else:
                yield json.dumps({"error": str(e)})
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
