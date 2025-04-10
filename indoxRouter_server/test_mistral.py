#!/usr/bin/env python

import os
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage, AssistantMessage


def main():
    try:
        # Load API key directly from .env to bypass any server configuration
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("MISTRAL_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    print(f"Found MISTRAL_API_KEY: {api_key[:5]}...{api_key[-5:]}")

        if not api_key:
            print("Failed to find MISTRAL_API_KEY in .env file")
            return

        # Initialize the Mistral client
        client = Mistral(api_key=api_key)

        # List available models
        try:
            models = client.models.list()
            print("Available models:")
            for model in models.data:
                print(f"  - {model.id}")

            # Select a model to use
            model_id = "mistral-small-latest"
            print(f"\nUsing model: {model_id}")

            # Create messages array manually using the correct format
            messages = [UserMessage(content="What is the capital of France?")]

            # Send a test request
            print("Sending test request...")
            response = client.chat.complete(model=model_id, messages=messages)

            # Check response structure
            print("\nResponse structure:")
            print(f"  - choices[0].message.role: {response.choices[0].message.role}")
            print(
                f"  - choices[0].message.content: {response.choices[0].message.content}"
            )
            print(f"  - choices[0].finish_reason: {response.choices[0].finish_reason}")
            print(f"  - usage.prompt_tokens: {response.usage.prompt_tokens}")
            print(f"  - usage.completion_tokens: {response.usage.completion_tokens}")
            print(f"  - usage.total_tokens: {response.usage.total_tokens}")

        except Exception as e:
            print(f"Error listing models: {str(e)}")

    except Exception as e:
        print(f"General error: {str(e)}")


if __name__ == "__main__":
    main()
