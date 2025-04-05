"""
Model router for the IndoxRouter server.
"""

import json
import os
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
                with open(os.path.join(provider_dir, filename), "r") as f:
                    provider_data = json.load(f)
                    providers[provider_id] = provider_data

                # Save models to MongoDB if possible
                try:
                    for model_data in provider_data["models"]:
                        save_model_info(
                            provider=provider_id,
                            name=model_data["name"],
                            capabilities=model_data["capabilities"],
                            description=model_data.get("description"),
                            max_tokens=model_data.get("max_tokens"),
                            pricing=model_data.get("pricing"),
                            metadata=model_data.get("metadata", {}),
                        )
                except Exception as e:
                    print(f"Warning: Could not save model to MongoDB: {e}")

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
                    name=model["name"],
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
                name=model["name"],
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
                name=model["name"],
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
