"""
Mistral provider implementation for indoxRouter server.
"""

import json
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Generator

import mistralai
from mistralai import Mistral
from mistralai.models import UserMessage, AssistantMessage, SystemMessage
from app.providers.base_provider import BaseProvider
from app.constants import MISTRAL_EMBEDDING_MODEL


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
        self.client = Mistral(api_key=api_key)

        try:
            available_models = [model.id for model in self.client.models.list().data]
            self._available_models = available_models

            if model_name not in available_models:
                similar_models = [m for m in available_models if model_name in m]
                if similar_models:
                    if len(similar_models) > 0:
                        self.model_name = similar_models[0]
        except Exception as e:
            self._available_models = []

        try:
            import os

            json_path = os.path.join(os.path.dirname(__file__), "json", "mistral.json")
            with open(json_path, "r") as f:
                model_data = json.load(f)

            self.model_capabilities = {}
            self.context_window_sizes = {}

            for model in model_data:
                model_id = model["modelName"]
                capabilities = ["chat", "completion"]
                if model["type"] == "Embedding":
                    capabilities = ["embedding"]
                elif "Vision" in model["type"]:
                    capabilities.append("vision")

                self.model_capabilities[model_id] = capabilities

                if "contextWindows" in model and "Tokens" in model["contextWindows"]:
                    context_str = model["contextWindows"]
                    if "k" in context_str:
                        # Handle formats like "128k (Pricey) Tokens"
                        try:
                            # First extract the part before any parentheses
                            size_part = context_str.split("(")[0].strip()
                            # Then extract the number before 'k'
                            context_size = int(float(size_part.replace("k", "")) * 1000)
                            self.context_window_sizes[model_id] = context_size
                        except Exception as e:
                            print(
                                f"Warning: Failed to parse context window '{context_str}': {str(e)}"
                            )
                            # Fall back to default sizes
        except Exception as e:
            self.model_capabilities = {
                "mistral-tiny": ["chat", "completion"],
                "mistral-small": ["chat", "completion"],
                "mistral-medium": ["chat", "completion"],
                "mistral-large": ["chat", "completion"],
                "mistral-embed": ["embedding"],
            }
            self.context_window_sizes = {
                "mistral-tiny": 32000,
                "mistral-small": 128000,
                "mistral-medium": 32000,
                "mistral-large": 128000,
                "mistral-embed": 8000,
            }

    def chat(self, messages: List[Any], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to Mistral.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys or ChatMessage objects.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the response from Mistral.
        """
        try:
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

                            # Convert messages to our format if they're not already dictionaries
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
                                        f"Warning: Unknown message type: {type(msg).__name__}"
                                    )

                            mistral_messages = self._convert_messages(
                                normalized_messages
                            )

                            # Extract parameters from kwargs to avoid duplication
                            temperature = kwargs.get("temperature", 0.7)
                            max_tokens = kwargs.get("max_tokens", None)

                            # Create a clean copy of kwargs without the extracted parameters
                            cleaned_kwargs = {
                                k: v
                                for k, v in kwargs.items()
                                if k not in ["temperature", "max_tokens"]
                            }

                            # Define an async function to process the stream
                            async def process_stream():
                                try:
                                    # Create the streaming request - Mistral's stream() returns a regular EventStream, not an awaitable
                                    stream_response = self.client.chat.stream(
                                        model=self.model_name,
                                        messages=mistral_messages,
                                        temperature=temperature,
                                        max_tokens=max_tokens,
                                        **cleaned_kwargs,
                                    )

                                    # Process each chunk - use regular for loop, not async for
                                    for chunk in stream_response:
                                        if (
                                            hasattr(chunk, "data")
                                            and hasattr(chunk.data, "choices")
                                            and chunk.data.choices
                                        ):
                                            choice = chunk.data.choices[0]
                                            if hasattr(choice, "delta") and hasattr(
                                                choice.delta, "content"
                                            ):
                                                delta_content = choice.delta.content
                                                if delta_content is not None:
                                                    # Format chunk and put in queue
                                                    json_chunk = json.dumps(
                                                        {
                                                            "choices": [
                                                                {
                                                                    "delta": {
                                                                        "content": delta_content
                                                                    },
                                                                    "index": 0,
                                                                    "finish_reason": None,
                                                                }
                                                            ]
                                                        }
                                                    )
                                                    result_queue.put(json_chunk)

                                            # Handle finish reason if available
                                            if (
                                                hasattr(choice, "finish_reason")
                                                and choice.finish_reason is not None
                                            ):
                                                json_chunk = json.dumps(
                                                    {
                                                        "choices": [
                                                            {
                                                                "delta": {
                                                                    "content": ""
                                                                },
                                                                "index": 0,
                                                                "finish_reason": choice.finish_reason,
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

            # Normal non-streaming request handling
            # Convert messages to our format if they're not already dictionaries
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

            mistral_messages = self._convert_messages(normalized_messages)
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            response = self.client.chat.complete(
                model=self.model_name,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            content = response.choices[0].message.content
            return {
                "choices": [
                    {
                        "message": {
                            "role": response.choices[0].message.role,
                            "content": content,
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
        except Exception as e:
            error_message = str(e)
            print(f"Mistral API Error: {error_message}")

            if "model_not_found" in error_message or "does not exist" in error_message:
                try:
                    available_models = [
                        model.id for model in self.client.models.list().data
                    ]
                    self._available_models = available_models

                    similar_models = [
                        m
                        for m in available_models
                        if self.model_name in m or m in self.model_name
                    ]
                    if similar_models:
                        alt_model = similar_models[0]

                        response = self.client.chat.complete(
                            model=alt_model,
                            messages=mistral_messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs,
                        )

                        self.model_name = alt_model

                        content = response.choices[0].message.content
                        return {
                            "choices": [
                                {
                                    "message": {
                                        "role": response.choices[0].message.role,
                                        "content": content,
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
                except Exception as retry_error:
                    print(f"Error during retry: {str(retry_error)}")
                    pass

                avail_msg = (
                    ", ".join(self._available_models)
                    if self._available_models
                    else "Check your API key permissions"
                )
                raise Exception(
                    f"Model not found: {self.model_name}. Available models: {avail_msg}"
                )
            raise Exception(f"Mistral API error: {error_message}")

    def chat_stream(
        self, messages: List[Any], **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat request to Mistral.

        Args:
            messages: A list of message dictionaries or ChatMessage objects.
            **kwargs: Additional parameters to pass to the Mistral API.

        Yields:
            Dictionaries containing response chunks from Mistral.
        """
        try:
            # Convert messages to dictionaries if they're not already
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
                        f"Warning: Unknown message type in chat_stream: {type(msg).__name__}"
                    )

            mistral_messages = self._convert_messages(normalized_messages)
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            stream = self.client.chat.stream(
                model=self.model_name,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            for chunk in stream:
                if (
                    hasattr(chunk, "data")
                    and hasattr(chunk.data, "choices")
                    and chunk.data.choices
                ):
                    choice = chunk.data.choices[0]
                    if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                        delta_content = choice.delta.content
                        if delta_content is not None:
                            yield {
                                "choices": [
                                    {
                                        "delta": {
                                            "role": "assistant",
                                            "content": delta_content,
                                        },
                                        "index": 0,
                                        "finish_reason": None,
                                    }
                                ],
                                "usage": None,
                            }

                    if (
                        hasattr(choice, "finish_reason")
                        and choice.finish_reason is not None
                    ):
                        yield {
                            "choices": [
                                {
                                    "delta": {"role": "assistant", "content": ""},
                                    "index": 0,
                                    "finish_reason": choice.finish_reason,
                                }
                            ],
                            "usage": None,
                        }
        except Exception as e:
            error_message = str(e)
            if "model_not_found" in error_message or "does not exist" in error_message:
                available_models = "mistral-large-latest, mistral-small-latest, mistral-tiny, pixtral-large-latest"
                raise Exception(
                    f"Model not found: {self.model_name}. Available models for Mistral include: {available_models}"
                )
            raise Exception(f"Mistral API error: {error_message}")

    def complete(self, prompt: str, **kwargs):
        """
        Send a completion request to Mistral.

        Mistral only supports the chat API, so we convert the completion request
        to a chat request and then format the response to match the completions API format.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Mistral API.

        Returns:
            A dictionary containing the response from Mistral in completions API format.
        """
        try:
            # Check if streaming is requested
            stream = kwargs.pop("stream", False)
            if stream:
                return self.complete_stream(prompt, **kwargs)

            # Remove the model parameter from kwargs if it exists, as we'll use self.model_name instead
            # to avoid duplicate model parameters when calling the chat method
            if "model" in kwargs:
                kwargs.pop("model")

            # Convert to a chat message
            messages = [{"role": "user", "content": prompt}]

            # Call the chat method with current model name
            chat_response = self.chat(messages=messages, **kwargs)

            # Check if we got a generator (which would happen if stream=True somehow)
            if hasattr(chat_response, "__iter__") and not isinstance(
                chat_response, dict
            ):
                # We unexpectedly got a generator - consume it and return the final result
                last_chunk = None
                content = ""
                for chunk in chat_response:
                    if isinstance(chunk, str):
                        try:
                            last_chunk = json.loads(chunk)
                            if (
                                "choices" in last_chunk
                                and last_chunk["choices"]
                                and "delta" in last_chunk["choices"][0]
                            ):
                                delta = last_chunk["choices"][0]["delta"]
                                if "content" in delta:
                                    content += delta["content"]
                        except:
                            pass

                # Create a basic response with the content we collected
                return {
                    "choices": [{"text": content, "index": 0, "finish_reason": "stop"}],
                    "usage": {
                        "prompt_tokens": self.get_token_count(prompt),
                        "completion_tokens": self.get_token_count(content),
                        "total_tokens": self.get_token_count(prompt)
                        + self.get_token_count(content),
                    },
                }

            # Extract content from the first choice if available
            content = ""
            if "choices" in chat_response and len(chat_response["choices"]) > 0:
                message = chat_response["choices"][0].get("message", {})
                content = message.get("content", "")

            # Format as a completions response
            usage_data = chat_response.get(
                "usage",
                {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            )

            # If the token counts are missing, try to use our tokenizer to count them
            if usage_data.get("prompt_tokens", 0) == 0 and prompt:
                try:
                    # Get accurate token count using the appropriate tokenizer for this model
                    prompt_tokens = self.get_token_count(prompt)
                    usage_data["prompt_tokens"] = prompt_tokens
                except Exception as e:
                    # Just log the error but don't stop execution
                    print(f"Warning: Failed to count prompt tokens: {str(e)}")

            if usage_data.get("completion_tokens", 0) == 0 and content:
                try:
                    # Get accurate token count using the appropriate tokenizer for this model
                    completion_tokens = self.get_token_count(content)
                    usage_data["completion_tokens"] = completion_tokens
                except Exception as e:
                    # Just log the error but don't stop execution
                    print(f"Warning: Failed to count completion tokens: {str(e)}")

            # Update total if needed
            if usage_data.get("total_tokens", 0) == 0:
                usage_data["total_tokens"] = usage_data.get(
                    "prompt_tokens", 0
                ) + usage_data.get("completion_tokens", 0)

            return {
                "choices": [
                    {
                        "text": content,
                        "index": i,
                        "finish_reason": choice.get("finish_reason", "stop"),
                    }
                    for i, choice in enumerate(chat_response.get("choices", []))
                ],
                "usage": usage_data,
            }
        except Exception as e:
            error_message = str(e)
            if "model_not_found" in error_message or "does not exist" in error_message:
                available_models = (
                    ", ".join(self._available_models)
                    if self._available_models
                    else "mistral-large-latest, mistral-small-latest, mistral-tiny"
                )
                raise Exception(
                    f"Model not found: {self.model_name}. Available models for Mistral include: {available_models}"
                )
            raise Exception(f"Mistral API error: {error_message}")

    async def chat_stream(
        self, messages: List[Any], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to Mistral (async version).

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Mistral API.

        Yields:
            Chunks of the response from Mistral.
        """
        try:
            # Convert messages to our format if they're not already dictionaries
            normalized_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    normalized_messages.append(msg)
                elif hasattr(msg, "role") and hasattr(msg, "content"):
                    normalized_messages.append(
                        {"role": msg.role, "content": msg.content}
                    )
                else:
                    raise ValueError(f"Unknown message type: {type(msg).__name__}")

            mistral_messages = self._convert_messages(normalized_messages)

            # Extract parameters from kwargs to avoid duplication
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", None)

            # Create a clean copy of kwargs without the extracted parameters
            cleaned_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in ["temperature", "max_tokens"]
            }

            # Create the streaming request - Note: Mistral's stream() method returns a regular EventStream, not an awaitable
            stream_response = self.client.chat.stream(
                model=self.model_name,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **cleaned_kwargs,
            )

            # Process each chunk - No 'async for' needed for Mistral's EventStream
            for chunk in stream_response:
                if (
                    hasattr(chunk, "data")
                    and hasattr(chunk.data, "choices")
                    and chunk.data.choices
                ):
                    choice = chunk.data.choices[0]
                    if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                        delta_content = choice.delta.content
                        if delta_content is not None:
                            # Format chunk
                            yield json.dumps(
                                {
                                    "choices": [
                                        {
                                            "delta": {"content": delta_content},
                                            "index": 0,
                                            "finish_reason": None,
                                        }
                                    ]
                                }
                            )

                    # Handle finish reason if available
                    if (
                        hasattr(choice, "finish_reason")
                        and choice.finish_reason is not None
                    ):
                        yield json.dumps(
                            {
                                "choices": [
                                    {
                                        "delta": {"content": ""},
                                        "index": 0,
                                        "finish_reason": choice.finish_reason,
                                    }
                                ]
                            }
                        )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def complete_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Send a streaming completion request to Mistral.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Mistral API.

        Yields:
            Chunks of the response from Mistral.
        """
        try:
            # Mistral doesn't have a separate completions API, so we use chat
            messages = [{"role": "user", "content": prompt}]

            # Generate the streaming response
            for chunk in self.chat(messages=messages, stream=True, **kwargs):
                if isinstance(chunk, str):
                    # Try to parse it as JSON
                    try:
                        chunk_data = json.loads(chunk)

                        # Convert delta format to text format if needed
                        if "choices" in chunk_data and chunk_data["choices"]:
                            choice = chunk_data["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                # Format as completions API response
                                yield json.dumps(
                                    {
                                        "choices": [
                                            {
                                                "text": choice["delta"]["content"],
                                                "index": choice.get("index", 0),
                                                "finish_reason": choice.get(
                                                    "finish_reason"
                                                ),
                                            }
                                        ]
                                    }
                                )
                        elif "error" in chunk_data:
                            yield json.dumps({"error": chunk_data["error"]})
                            break
                    except json.JSONDecodeError:
                        # Just pass through the raw chunk
                        yield chunk
                else:
                    # Pass through the chunk (though this shouldn't happen)
                    yield json.dumps({"error": "Unexpected chunk format"})
        except Exception as e:
            yield json.dumps({"error": f"Error in text completion stream: {str(e)}"})

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
            text_list = [text] if isinstance(text, str) else text

            # Use the constant for the embedding model
            embed_model = MISTRAL_EMBEDDING_MODEL

            # Try to get the available models to check if embedding is supported
            try:
                # Find embedding-capable models from available models
                available_models = getattr(self, "_available_models", [])
                embedding_models = [m for m in available_models if "embed" in m.lower()]

                if embedding_models:
                    # Use the first available embedding model if we found one
                    embed_model = embedding_models[0]
            except Exception as model_error:
                print(
                    f"Warning: Could not determine embedding model, using default: {embed_model}"
                )
                print(f"Error was: {str(model_error)}")

            response = self.client.embeddings.create(
                model=embed_model,
                inputs=text_list,
                **kwargs,
            )

            embeddings = [data.embedding for data in response.data]
            return {
                "embeddings": embeddings,
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as e:
            error_msg = str(e)
            if (
                "model_not_found" in error_msg.lower()
                or "does not exist" in error_msg.lower()
            ):
                raise Exception(
                    f"Embedding model not found or not accessible. Please check your API key permissions. Error: {error_msg}"
                )
            raise Exception(f"Error in embedding: {error_msg}")

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

    def _get_tokenizer_for_model(self, model_name: str):
        """
        Get the appropriate tokenizer for a specific model based on model.json data.

        Args:
            model_name: The name of the model to get the tokenizer for.

        Returns:
            The appropriate MistralTokenizer instance for the model.
        """
        from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

        # Normalize model name
        model_name_lower = model_name.lower()

        # Direct matching with exact model IDs from our JSON file
        # v1 tokenizer models
        v1_models = ["mistral-embed", "mistral-embed-v1"]

        # v2 tokenizer models
        v2_models = [
            "mistral-small-latest",
            "mistral-large-latest",
            "mistral-medium-2407",
            "mistral-saba-latest",
            "codestral-latest",
            "mistral-ocr-latest",
            "mistral-moderation-latest",
            "pixtral-large-latest",
        ]

        # v3 tokenizer with tekken=True
        v3_tekken_models = [
            "open-mistral-nemo",
            "ministral-8b-latest",
            "ministral-3b-latest",
        ]

        # Try to find an exact match with normalized strings
        if any(model.lower() == model_name_lower for model in v1_models):
            return MistralTokenizer.v1()

        if any(model.lower() == model_name_lower for model in v2_models):
            return MistralTokenizer.v2()

        if any(model.lower() == model_name_lower for model in v3_tekken_models):

            return MistralTokenizer.v3(is_tekken=True)

        # Check for substring matches if no exact match
        if any(model.lower() in model_name_lower for model in v1_models):
            return MistralTokenizer.v1()

        if any(model.lower() in model_name_lower for model in v2_models):
            return MistralTokenizer.v2()

        if any(model.lower() in model_name_lower for model in v3_tekken_models):
            return MistralTokenizer.v3(is_tekken=True)

        # For all other models, use v3 tokenizer which is the latest
        return MistralTokenizer.v3()

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text using the official MistralTokenizer.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        try:
            # Get the appropriate tokenizer for this model
            tokenizer = self._get_tokenizer_for_model(self.model_name)

            # Count tokens using the appropriate tokenizer
            token_ids = tokenizer.encode(text)
            return len(token_ids)

        except ImportError:
            # Fallback to approximate token counting if mistral_common is not available
            return self._estimate_tokens(text)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing information about the model.
        """
        model_id = self.model_name
        capabilities = self.model_capabilities.get(model_id, [])

        if not capabilities:
            for model_prefix, model_caps in self.model_capabilities.items():
                if model_id.startswith(model_prefix):
                    capabilities = model_caps
                    break

        context_window = self.context_window_sizes.get(model_id, 32000)

        model_info = {
            "id": self.model_name,
            "name": self.model_name,
            "provider": "mistral",
            "capabilities": capabilities,
            "max_tokens": context_window,
        }

        return model_info

    def _convert_messages(
        self, messages: List[Any]
    ) -> List[Union[UserMessage, AssistantMessage, SystemMessage]]:
        """
        Convert OpenAI-style messages or ChatMessage objects to Mistral format.

        Args:
            messages: A list of message dictionaries or ChatMessage objects.

        Returns:
            A list of Mistral-style messages.
        """
        mistral_messages = []

        for i, message in enumerate(messages):
            # Handle different types of input messages
            if hasattr(message, "role") and hasattr(message, "content"):
                # This is a ChatMessage object from resources layer
                role = message.role
                content = message.content
            elif isinstance(message, dict):
                # This is a dictionary
                role = message.get("role", "user")  # Default to user if role is missing
                content = message.get(
                    "content", ""
                )  # Default to empty string if content is missing
            else:
                continue

            if role == "system":
                mistral_messages.append(SystemMessage(content=content))
            elif role == "user":
                mistral_messages.append(UserMessage(content=content))
            elif role == "assistant":
                mistral_messages.append(AssistantMessage(content=content))
            else:
                mistral_messages.append(UserMessage(content=f"{role}: {content}"))

        # Ensure there's at least one message
        if not mistral_messages:
            mistral_messages.append(UserMessage(content="Hello"))

        # Mistral API requires at least one UserMessage
        user_message_exists = any(isinstance(m, UserMessage) for m in mistral_messages)
        if not user_message_exists:
            mistral_messages.append(UserMessage(content="Please respond to the above"))

        return mistral_messages
