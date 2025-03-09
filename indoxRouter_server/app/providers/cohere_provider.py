# """
# Cohere provider implementation for indoxRouter server.
# """

# import json
# import os
# from typing import Dict, List, Any, Optional, Union, AsyncGenerator

# import cohere
# from cohere import AsyncClient, Client

# from app.providers.base_provider import BaseProvider


# class CohereProvider(BaseProvider):
#     """Cohere provider implementation."""

#     def __init__(self, api_key: str, model_name: str):
#         """
#         Initialize the Cohere provider.

#         Args:
#             api_key: The API key for Cohere.
#             model_name: The name of the model to use.
#         """
#         super().__init__(api_key, model_name)
#         self.client = Client(api_key=api_key)
#         self.async_client = AsyncClient(api_key=api_key)

#         # Model capabilities mapping
#         self.model_capabilities = {
#             "command": ["chat", "completion"],
#             "command-light": ["chat", "completion"],
#             "command-r": ["chat", "completion"],
#             "command-r-plus": ["chat", "completion"],
#             "embed-english": ["embedding"],
#             "embed-multilingual": ["embedding"],
#             "embed-english-light": ["embedding"],
#             "embed-multilingual-light": ["embedding"],
#             "embed-english-v3.0": ["embedding"],
#             "embed-multilingual-v3.0": ["embedding"],
#         }

#     def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
#         """
#         Send a chat request to Cohere.

#         Args:
#             messages: A list of message dictionaries with 'role' and 'content' keys.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Returns:
#             A dictionary containing the response from Cohere.
#         """
#         try:
#             # Convert OpenAI-style messages to Cohere format
#             cohere_messages = self._convert_messages(messages)

#             # Extract parameters
#             temperature = kwargs.pop("temperature", 0.7)
#             max_tokens = kwargs.pop("max_tokens", 1024)

#             response = self.client.chat(
#                 model=self.model_name,
#                 message=cohere_messages[-1]["message"] if cohere_messages else "",
#                 chat_history=cohere_messages[:-1] if len(cohere_messages) > 1 else None,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 **kwargs,
#             )

#             # Estimate token usage (Cohere doesn't provide this directly)
#             prompt_text = " ".join([msg.get("message", "") for msg in cohere_messages])
#             prompt_tokens = self._estimate_tokens(prompt_text)
#             completion_tokens = self._estimate_tokens(response.text)

#             # Format the response
#             return {
#                 "choices": [
#                     {
#                         "message": {
#                             "role": "assistant",
#                             "content": response.text,
#                         },
#                         "index": 0,
#                         "finish_reason": "stop",
#                     }
#                 ],
#                 "usage": {
#                     "prompt_tokens": prompt_tokens,
#                     "completion_tokens": completion_tokens,
#                     "total_tokens": prompt_tokens + completion_tokens,
#                 },
#             }
#         except cohere.error.CohereError as e:
#             raise Exception(f"Cohere API error: {str(e)}")
#         except Exception as e:
#             raise Exception(f"Error in chat completion: {str(e)}")

#     async def chat_stream(
#         self, messages: List[Dict[str, str]], **kwargs
#     ) -> AsyncGenerator[str, None]:
#         """
#         Send a streaming chat request to Cohere.

#         Args:
#             messages: A list of message dictionaries with 'role' and 'content' keys.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Yields:
#             Chunks of the response from Cohere.
#         """
#         try:
#             # Convert OpenAI-style messages to Cohere format
#             cohere_messages = self._convert_messages(messages)

#             # Extract parameters
#             temperature = kwargs.pop("temperature", 0.7)
#             max_tokens = kwargs.pop("max_tokens", 1024)

#             stream_response = await self.async_client.chat(
#                 model=self.model_name,
#                 message=cohere_messages[-1]["message"] if cohere_messages else "",
#                 chat_history=cohere_messages[:-1] if len(cohere_messages) > 1 else None,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 stream=True,
#                 **kwargs,
#             )

#             async for chunk in stream_response:
#                 if hasattr(chunk, "text") and chunk.text:
#                     # Format the chunk as a JSON string
#                     yield json.dumps(
#                         {
#                             "choices": [
#                                 {
#                                     "delta": {
#                                         "content": chunk.text,
#                                     },
#                                     "index": 0,
#                                     "finish_reason": None,
#                                 }
#                             ]
#                         }
#                     )
#         except Exception as e:
#             yield json.dumps({"error": str(e)})

#     def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
#         """
#         Send a completion request to Cohere.

#         Args:
#             prompt: The prompt to complete.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Returns:
#             A dictionary containing the response from Cohere.
#         """
#         try:
#             # Extract parameters
#             temperature = kwargs.pop("temperature", 0.7)
#             max_tokens = kwargs.pop("max_tokens", 1024)

#             response = self.client.generate(
#                 model=self.model_name,
#                 prompt=prompt,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 **kwargs,
#             )

#             # Estimate token usage
#             prompt_tokens = self._estimate_tokens(prompt)
#             completion_tokens = self._estimate_tokens(response.generations[0].text)

#             # Format the response
#             return {
#                 "choices": [
#                     {
#                         "text": generation.text,
#                         "index": i,
#                         "finish_reason": "stop",
#                     }
#                     for i, generation in enumerate(response.generations)
#                 ],
#                 "usage": {
#                     "prompt_tokens": prompt_tokens,
#                     "completion_tokens": completion_tokens,
#                     "total_tokens": prompt_tokens + completion_tokens,
#                 },
#             }
#         except cohere.error.CohereError as e:
#             raise Exception(f"Cohere API error: {str(e)}")
#         except Exception as e:
#             raise Exception(f"Error in text completion: {str(e)}")

#     async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
#         """
#         Send a streaming completion request to Cohere.

#         Args:
#             prompt: The prompt to complete.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Yields:
#             Chunks of the response from Cohere.
#         """
#         try:
#             # Extract parameters
#             temperature = kwargs.pop("temperature", 0.7)
#             max_tokens = kwargs.pop("max_tokens", 1024)

#             stream_response = await self.async_client.generate(
#                 model=self.model_name,
#                 prompt=prompt,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 stream=True,
#                 **kwargs,
#             )

#             async for chunk in stream_response:
#                 if hasattr(chunk, "text") and chunk.text:
#                     # Format the chunk as a JSON string
#                     yield json.dumps(
#                         {
#                             "choices": [
#                                 {
#                                     "text": chunk.text,
#                                     "index": 0,
#                                     "finish_reason": None,
#                                 }
#                             ]
#                         }
#                     )
#         except Exception as e:
#             yield json.dumps({"error": str(e)})

#     def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
#         """
#         Send an embedding request to Cohere.

#         Args:
#             text: The text to embed. Can be a single string or a list of strings.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Returns:
#             A dictionary containing the embeddings from Cohere.
#         """
#         try:
#             # Ensure text is a list
#             if isinstance(text, str):
#                 text_list = [text]
#             else:
#                 text_list = text

#             response = self.client.embed(
#                 model=self.model_name, texts=text_list, **kwargs
#             )

#             # Get embeddings
#             embeddings = response.embeddings

#             # Estimate token usage
#             prompt_tokens = sum(self._estimate_tokens(t) for t in text_list)

#             # Format the response
#             return {
#                 "embeddings": embeddings,
#                 "dimensions": len(embeddings[0]) if embeddings else 0,
#                 "usage": {
#                     "prompt_tokens": prompt_tokens,
#                     "total_tokens": prompt_tokens,
#                 },
#             }
#         except cohere.error.CohereError as e:
#             raise Exception(f"Cohere API error: {str(e)}")
#         except Exception as e:
#             raise Exception(f"Error in embedding: {str(e)}")

#     def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
#         """
#         Generate an image from a prompt.
#         Note: As of now, Cohere doesn't provide a public image generation API.
#         This method raises an exception.

#         Args:
#             prompt: The prompt to generate an image from.
#             **kwargs: Additional parameters to pass to the Cohere API.

#         Returns:
#             A dictionary containing the image URL or data.
#         """
#         raise Exception("Image generation is not supported by Cohere API")

#     def get_token_count(self, text: str) -> int:
#         """
#         Get the number of tokens in a text.
#         Note: Cohere doesn't provide a public token counting API, so we estimate.

#         Args:
#             text: The text to count tokens for.

#         Returns:
#             The estimated number of tokens in the text.
#         """
#         return self._estimate_tokens(text)

#     def get_model_info(self) -> Dict[str, Any]:
#         """
#         Get information about the model.

#         Returns:
#             A dictionary containing information about the model.
#         """
#         # Get model capabilities
#         model_id = self.model_name.lower()
#         capabilities = []

#         # Check if model is in our capabilities mapping
#         for model_prefix, model_capabilities in self.model_capabilities.items():
#             if model_id.startswith(model_prefix):
#                 capabilities = model_capabilities
#                 break

#         # Basic model information
#         model_info = {
#             "id": self.model_name,
#             "name": self.model_name,
#             "provider": "cohere",
#             "capabilities": capabilities,
#         }

#         return model_info

#     def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
#         """
#         Convert OpenAI-style messages to Cohere format.

#         Args:
#             messages: A list of message dictionaries with 'role' and 'content' keys.

#         Returns:
#             A list of Cohere-style messages.
#         """
#         cohere_messages = []

#         # Extract system message if present
#         system_content = None
#         for message in messages:
#             if message["role"] == "system":
#                 system_content = message["content"]
#                 break

#         # Process messages
#         for i, message in enumerate(messages):
#             if message["role"] == "system":
#                 continue  # Skip system messages

#             role = "USER" if message["role"] == "user" else "CHATBOT"

#             # Add system message as preamble to the first user message
#             content = message["content"]
#             if (
#                 role == "USER"
#                 and system_content
#                 and not any(m["role"] == "USER" for m in cohere_messages)
#             ):
#                 content = f"{system_content}\n\n{content}"

#             cohere_messages.append(
#                 {
#                     "role": role,
#                     "message": content,
#                 }
#             )

#         return cohere_messages

#     def _estimate_tokens(self, text: str) -> int:
#         """
#         Estimate the number of tokens in a text.
#         This is a rough estimate based on the common rule of thumb that 1 token ≈ 4 characters.

#         Args:
#             text: The text to estimate tokens for.

#         Returns:
#             The estimated number of tokens.
#         """
#         return len(text) // 4 + 1
