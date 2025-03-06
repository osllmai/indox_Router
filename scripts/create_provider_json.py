#!/usr/bin/env python
"""
Script to generate a new provider JSON file.
"""

import os
import sys
import json
import argparse

# Add the parent directory to the path so we can import indoxRouter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def create_provider_json(provider_name, output_path=None):
    """
    Create a new provider JSON file with template data.

    Args:
        provider_name: The name of the provider.
        output_path: The path to save the JSON file. If None, saves to the providers directory.

    Returns:
        The path to the created JSON file.
    """
    # Create a template for the provider JSON
    provider_data = [
        {
            "modelName": f"{provider_name.lower()}-chat-large",
            "name": f"{provider_name} Chat Large",
            "type": "Chat",
            "description": f"Large language model from {provider_name}.",
            "inputPricePer1KTokens": 0.01,
            "outputPricePer1KTokens": 0.03,
            "contextWindow": "16K",
            "maxOutputTokens": 4096,
            "recommended": True,
            "commercial": True,
            "pricey": False,
        },
        {
            "modelName": f"{provider_name.lower()}-chat-small",
            "name": f"{provider_name} Chat Small",
            "type": "Chat",
            "description": f"Small language model from {provider_name}.",
            "inputPricePer1KTokens": 0.001,
            "outputPricePer1KTokens": 0.002,
            "contextWindow": "8K",
            "maxOutputTokens": 2048,
            "recommended": False,
            "commercial": True,
            "pricey": False,
        },
        {
            "modelName": f"{provider_name.lower()}-embedding",
            "name": f"{provider_name} Embedding",
            "type": "Embedding",
            "description": f"Embedding model from {provider_name}.",
            "inputPricePer1KTokens": 0.0001,
            "outputPricePer1KTokens": 0.0,
            "contextWindow": "8K",
            "maxOutputTokens": 0,
            "recommended": True,
            "commercial": True,
            "pricey": False,
        },
    ]

    # Determine the output path
    if output_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(
            current_dir, "indoxRouter", "providers", f"{provider_name.lower()}.json"
        )

    # Write the JSON file
    with open(output_path, "w") as f:
        json.dump(provider_data, f, indent=2)

    print(f"Created provider JSON file: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new provider JSON file.")
    parser.add_argument("provider_name", help="The name of the provider.")
    parser.add_argument(
        "--output-path",
        help="The path to save the JSON file. If not provided, saves to the providers directory.",
    )

    args = parser.parse_args()

    create_provider_json(args.provider_name, args.output_path)
