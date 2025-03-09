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

router = APIRouter(prefix="/models", tags=["Models"])


# Load provider and model information from JSON files
def load_provider_data():
    """Load provider data from JSON files."""
    providers = {}
    provider_dir = os.path.join(
        os.path.dirname(__file__), "../../../app/providers/json"
    )

    for filename in os.listdir(provider_dir):
        if filename.endswith(".json"):
            provider_id = filename.split(".")[0]
            with open(os.path.join(provider_dir, filename), "r") as f:
                provider_data = json.load(f)
                providers[provider_id] = provider_data

    return providers


PROVIDERS = load_provider_data()


@router.get("/", response_model=List[ProviderInfo])
async def get_providers(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all available providers."""
    result = []

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
async def get_model(
    provider_id: str,
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get information about a specific model."""
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
