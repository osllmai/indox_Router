"""
Google provider implementation for indoxRouter server.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.providers.base_provider import BaseProvider


class GoogleProvider(BaseProvider):
    """Google provider implementation."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Google provider.

        Args:
            api_key: The API key for Google.
            model_name: The name of the model to use.
        """
        # Clean up model name if needed (remove any provider prefix)
        if "/" in model_name:
            _, model_name = model_name.split("/", 1)

        super().__init__(api_key, model_name)
        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel(model_name=model_name)

        # Model capabilities mapping
        self.model_capabilities = {
            "gemini-pro": ["chat", "completion"],
            "gemini-pro-vision": ["chat", "completion", "image"],
            "embedding-001": ["embedding"],
        }

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to Google.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Google API.

        Returns:
            A dictionary containing the response from Google.
        """
        try:
            # Convert OpenAI-style messages to Google format
            google_messages = self._convert_messages(messages)

            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            # Create generation config
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.pop("top_p", 1.0),
                "top_k": kwargs.pop("top_k", 40),
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create safety settings (default to medium)
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # Create chat session
            chat = self.model.start_chat(history=google_messages[:-1])

            # Send the last message
            response = chat.send_message(
                google_messages[-1]["parts"][0],
                generation_config=generation_config,
                safety_settings=safety_settings,
                **kwargs,
            )

            # Estimate token usage
            prompt_text = " ".join(
                [msg.get("parts", [""])[0] for msg in google_messages]
            )
            prompt_tokens = self._estimate_tokens(prompt_text)
            completion_tokens = self._estimate_tokens(response.text)

            # Format the response
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.text,
                        },
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to Google.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the Google API.

        Yields:
            Chunks of the response from Google.
        """
        try:
            # Convert OpenAI-style messages to Google format
            google_messages = self._convert_messages(messages)

            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            # Create generation config
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.pop("top_p", 1.0),
                "top_k": kwargs.pop("top_k", 40),
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create safety settings (default to medium)
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # Create chat session
            chat = self.model.start_chat(history=google_messages[:-1])

            # Send the last message with streaming
            response = chat.send_message(
                google_messages[-1]["parts"][0],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
                **kwargs,
            )

            # Process the streaming response
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    # Format the chunk as a JSON string
                    yield json.dumps(
                        {
                            "choices": [
                                {
                                    "delta": {
                                        "content": chunk.text,
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
        Send a completion request to Google.
        Note: Google doesn't have a dedicated completion API, so we use the chat API.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Google API.

        Returns:
            A dictionary containing the response from Google.
        """
        try:
            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            # Create generation config
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.pop("top_p", 1.0),
                "top_k": kwargs.pop("top_k", 40),
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create safety settings (default to medium)
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # Generate text
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
                **kwargs,
            )

            # Estimate token usage
            prompt_tokens = self._estimate_tokens(prompt)
            completion_tokens = self._estimate_tokens(response.text)

            # Format the response
            return {
                "choices": [
                    {
                        "text": response.text,
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
        except Exception as e:
            raise Exception(f"Error in text completion: {str(e)}")

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Send a streaming completion request to Google.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the Google API.

        Yields:
            Chunks of the response from Google.
        """
        try:
            # Extract parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", None)

            # Create generation config
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.pop("top_p", 1.0),
                "top_k": kwargs.pop("top_k", 40),
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create safety settings (default to medium)
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # Generate text with streaming
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
                **kwargs,
            )

            # Process the streaming response
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    # Format the chunk as a JSON string
                    yield json.dumps(
                        {
                            "choices": [
                                {
                                    "text": chunk.text,
                                    "index": 0,
                                    "finish_reason": None,
                                }
                            ]
                        }
                    )
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """
        Send an embedding request to Google.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the Google API.

        Returns:
            A dictionary containing the embeddings from Google.
        """
        try:
            # Ensure text is a list
            if isinstance(text, str):
                text_list = [text]
            else:
                text_list = text

            # Get embedding model
            embedding_model = genai.get_model("embedding-001")

            # Generate embeddings
            embeddings = []
            for t in text_list:
                result = embedding_model.embed_content(
                    content=t, task_type="RETRIEVAL_QUERY", **kwargs
                )
                embeddings.append(result["embedding"])

            # Estimate token usage
            prompt_tokens = sum(self._estimate_tokens(t) for t in text_list)

            # Format the response
            return {
                "embeddings": embeddings,
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "total_tokens": prompt_tokens,
                },
            }
        except Exception as e:
            raise Exception(f"Error in embedding: {str(e)}")

    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt.
        Note: Google's Gemini can generate images, but the API is different.
        This implementation is a placeholder.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the Google API.

        Returns:
            A dictionary containing the image URL or data.
        """
        raise Exception("Image generation is not yet implemented for Google provider")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text.
        Note: Google doesn't provide a public token counting API, so we estimate.

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

        # Basic model information
        model_info = {
            "id": self.model_name,
            "name": self.model_name,
            "provider": "google",
            "capabilities": capabilities,
        }

        return model_info

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI-style messages to Google format.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.

        Returns:
            A list of Google-style messages.
        """
        google_messages = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                # Add system message as a user message
                google_messages.append(
                    {
                        "role": "user",
                        "parts": [content],
                    }
                )
                # Add an empty assistant response to maintain the conversation flow
                google_messages.append(
                    {
                        "role": "model",
                        "parts": ["I'll help you with that."],
                    }
                )
            elif role == "user":
                google_messages.append(
                    {
                        "role": "user",
                        "parts": [content],
                    }
                )
            elif role == "assistant":
                google_messages.append(
                    {
                        "role": "model",
                        "parts": [content],
                    }
                )

        return google_messages

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
