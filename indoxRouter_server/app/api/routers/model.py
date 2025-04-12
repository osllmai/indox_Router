"""
Model router for the IndoxRouter server.
This module provides endpoints for accessing model information.
"""

import json
import os
import traceback
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.models.schemas import ModelInfo, ProviderInfo
from app.api.dependencies import get_current_user
from app.db.database import (
    get_models,
    get_model,
    save_model_info,
    get_mongo_db,
)

router = APIRouter(prefix="/models", tags=["Models"])


# Load provider and model information from JSON files and save to MongoDB
def load_provider_data():
    """Load provider data from JSON files and ensure it's in MongoDB."""
    providers = {}
    provider_dir = os.path.join(
        os.path.dirname(__file__), "../../../app/providers/json"
    )

    # Only process JSON files if the directory exists
    if os.path.exists(provider_dir):
        for filename in os.listdir(provider_dir):
            if filename.endswith(".json"):
                provider_id = filename.split(".")[0]
                try:
                    with open(os.path.join(provider_dir, filename), "r") as f:
                        data = json.load(f)

                        # Handle different JSON formats
                        if isinstance(data, list):
                            # If the data is a list, convert it to the expected format
                            print(f"Converting list format for {provider_id}")

                            # Create capabilities based on model types
                            provider_capabilities = set()
                            for model in data:
                                model_type = model.get("type", "")

                                # Set capability based on model type
                                if "Text" in model_type and "Vision" not in model_type:
                                    model["capabilities"] = ["chat", "completion"]
                                    provider_capabilities.update(["chat", "completion"])
                                elif "Embedding" in model_type:
                                    model["capabilities"] = ["embedding"]
                                    provider_capabilities.update(["embedding"])
                                elif "Vision" in model_type:
                                    model["capabilities"] = [
                                        "chat",
                                        "completion",
                                        "vision",
                                    ]
                                    provider_capabilities.update(
                                        ["chat", "completion", "vision"]
                                    )
                                else:
                                    model["capabilities"] = ["chat", "completion"]
                                    provider_capabilities.update(["chat", "completion"])

                                # Add max_tokens from contextWindows
                                if "contextWindows" in model:
                                    context_str = model.get("contextWindows", "")
                                    if "k Tokens" in context_str:
                                        # Extract the number (e.g., "128k Tokens" -> 128000)
                                        try:
                                            size = float(context_str.split("k")[0])
                                            model["max_tokens"] = int(size * 1000)
                                        except (ValueError, TypeError):
                                            model["max_tokens"] = 32000  # Default
                                    elif "Tokens" in context_str:
                                        # Handle case without 'k' but with Tokens
                                        try:
                                            size = float(context_str.split(" ")[0])
                                            model["max_tokens"] = int(size)
                                        except (ValueError, TypeError):
                                            model["max_tokens"] = 32000  # Default

                                # Set model ID
                                model["id"] = model.get("modelName")

                            # Convert to the expected format
                            provider_data = {
                                "name": provider_id.capitalize(),
                                "description": f"{provider_id.capitalize()} Language Models",
                                "capabilities": list(provider_capabilities),
                                "models": data,
                                "metadata": {},
                            }
                        else:
                            # Assume it's already in the expected format with "models" key
                            provider_data = data

                        # Store the provider data
                        providers[provider_id] = provider_data
                        print(f"Loaded provider data for {provider_id}")

                    # Save models to MongoDB if possible
                    models_to_save = []

                    # Check if we have a "models" key with a list of models
                    if "models" in provider_data and isinstance(
                        provider_data["models"], list
                    ):
                        models_to_save = provider_data["models"]
                    elif isinstance(provider_data, list):
                        # If provider_data is a list, assume it's a list of models
                        models_to_save = provider_data

                    for model_data in models_to_save:
                        try:
                            # Verify model_data is a dictionary
                            if not isinstance(model_data, dict):
                                print(
                                    f"Warning: Model data is not a dictionary: {model_data}"
                                )
                                continue

                            # Extract model properties with proper error handling
                            model_id = model_data.get("id", model_data.get("modelName"))
                            model_name = model_data.get("name", model_id)

                            if not model_id:
                                print(f"Warning: Model missing ID: {model_data}")
                                continue

                            capabilities = model_data.get("capabilities", [])
                            if not isinstance(capabilities, list):
                                capabilities = []

                            save_model_info(
                                provider=provider_id,
                                name=model_name,
                                capabilities=capabilities,
                                description=model_data.get("description"),
                                max_tokens=model_data.get("max_tokens"),
                                pricing=model_data.get("pricing"),
                                metadata=model_data.get("metadata", {}),
                            )
                            print(f"Saved model {model_id} for {provider_id}")
                        except Exception as e:
                            print(f"Warning: Could not save model to MongoDB: {e}")
                except Exception as e:
                    print(f"Error loading provider data from {filename}: {e}")
                    print(f"Full exception: {traceback.format_exc()}")

    return providers


# Load provider data at startup
PROVIDERS = load_provider_data()


@router.get("/", response_model=List[ProviderInfo])
async def get_providers(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all available providers."""
    result = []

    # Try to get models from MongoDB first
    try:
        # Get all models from MongoDB and group by provider
        mongo_models = get_models()
        if mongo_models:
            # Group models by provider
            provider_models = {}
            for model in mongo_models:
                provider_id = model.get("provider")
                if provider_id not in provider_models:
                    provider_models[provider_id] = []
                provider_models[provider_id].append(model)

            # Create provider info for each provider
            for provider_id, models in provider_models.items():
                # Get provider metadata from JSON if available
                provider_name = provider_id.capitalize()  # Default
                provider_desc = None
                provider_capabilities = ["chat", "completion"]  # Default
                provider_metadata = {}

                # Check if we have JSON data for this provider
                if provider_id in PROVIDERS:
                    provider_data = PROVIDERS[provider_id]
                    provider_name = provider_data.get("name", provider_name)
                    provider_desc = provider_data.get("description")
                    provider_capabilities = provider_data.get(
                        "capabilities", provider_capabilities
                    )
                    provider_metadata = provider_data.get("metadata", {})

                # Create provider info with models from MongoDB
                provider_info = ProviderInfo(
                    id=provider_id,
                    name=provider_name,
                    description=provider_desc,
                    capabilities=provider_capabilities,
                    models=[
                        ModelInfo(
                            id=model.get("name"),  # Use name as ID
                            name=model.get("name"),
                            provider=provider_id,
                            capabilities=model.get("capabilities", []),
                            description=model.get("description"),
                            max_tokens=model.get("max_tokens"),
                            pricing=model.get("pricing"),
                            metadata=model.get("metadata", {}),
                        )
                        for model in models
                    ],
                    metadata=provider_metadata,
                )
                result.append(provider_info)

            # Return early if we have data from MongoDB
            if result:
                return result
    except Exception as e:
        print(f"Error getting models from MongoDB: {e}")

    # Fallback to JSON data if MongoDB fails or has no data
    for provider_id, provider_data in PROVIDERS.items():
        provider_info = ProviderInfo(
            id=provider_id,
            name=provider_data["name"],
            description=provider_data.get("description"),
            capabilities=provider_data["capabilities"],
            models=[
                ModelInfo(
                    id=model["id"],
                    name=model["modelName"],
                    provider=provider_id,
                    capabilities=model["capabilities"],
                    description=model.get("description"),
                    max_tokens=model.get("max_tokens"),
                    pricing=model.get("pricing"),
                    metadata=model.get("metadata", {}),
                )
                for model in provider_data["models"]
            ],
            metadata=provider_data.get("metadata", {}),
        )
        result.append(provider_info)

    return result


@router.get("/{provider_id}", response_model=ProviderInfo)
async def get_provider(
    provider_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get information about a specific provider."""
    # Try to get models from MongoDB first
    try:
        mongo_models = get_models(provider=provider_id)
        if mongo_models:
            # Get provider metadata from JSON if available
            provider_name = provider_id.capitalize()  # Default
            provider_desc = None
            provider_capabilities = ["chat", "completion"]  # Default
            provider_metadata = {}

            # Check if we have JSON data for this provider
            if provider_id in PROVIDERS:
                provider_data = PROVIDERS[provider_id]
                provider_name = provider_data.get("name", provider_name)
                provider_desc = provider_data.get("description")
                provider_capabilities = provider_data.get(
                    "capabilities", provider_capabilities
                )
                provider_metadata = provider_data.get("metadata", {})

            # Return provider info with models from MongoDB
            return ProviderInfo(
                id=provider_id,
                name=provider_name,
                description=provider_desc,
                capabilities=provider_capabilities,
                models=[
                    ModelInfo(
                        id=model.get("name"),  # Use name as ID
                        name=model.get("name"),
                        provider=provider_id,
                        capabilities=model.get("capabilities", []),
                        description=model.get("description"),
                        max_tokens=model.get("max_tokens"),
                        pricing=model.get("pricing"),
                        metadata=model.get("metadata", {}),
                    )
                    for model in mongo_models
                ],
                metadata=provider_metadata,
            )
    except Exception as e:
        print(f"Error getting models from MongoDB for provider {provider_id}: {e}")

    # Fallback to JSON data if MongoDB fails
    if provider_id not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    provider_data = PROVIDERS[provider_id]

    return ProviderInfo(
        id=provider_id,
        name=provider_data["name"],
        description=provider_data.get("description"),
        capabilities=provider_data["capabilities"],
        models=[
            ModelInfo(
                id=model["id"],
                name=model["modelName"],
                provider=provider_id,
                capabilities=model["capabilities"],
                description=model.get("description"),
                max_tokens=model.get("max_tokens"),
                pricing=model.get("pricing"),
                metadata=model.get("metadata", {}),
            )
            for model in provider_data["models"]
        ],
        metadata=provider_data.get("metadata", {}),
    )


@router.get("/{provider_id}/{model_id}", response_model=ModelInfo)
async def get_model_info(
    provider_id: str,
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get information about a specific model."""
    # Try to get model from MongoDB first
    try:
        mongo_model = get_model(provider=provider_id, name=model_id)
        if mongo_model:
            return ModelInfo(
                id=model_id,
                name=mongo_model.get("name"),
                provider=provider_id,
                capabilities=mongo_model.get("capabilities", []),
                description=mongo_model.get("description"),
                max_tokens=mongo_model.get("max_tokens"),
                pricing=mongo_model.get("pricing"),
                metadata=mongo_model.get("metadata", {}),
            )
    except Exception as e:
        print(f"Error getting model from MongoDB: {e}")

    # Fallback to JSON data if MongoDB fails
    if provider_id not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    provider_data = PROVIDERS[provider_id]

    for model in provider_data["models"]:
        if model["id"] == model_id:
            return ModelInfo(
                id=model["id"],
                name=model["modelName"],
                provider=provider_id,
                capabilities=model["capabilities"],
                description=model.get("description"),
                max_tokens=model.get("max_tokens"),
                pricing=model.get("pricing"),
                metadata=model.get("metadata", {}),
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model '{model_id}' not found for provider '{provider_id}'",
    )
