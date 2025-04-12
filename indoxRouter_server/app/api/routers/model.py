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
from app.constants import AVAILABLE_PROVIDERS

router = APIRouter(prefix="/models", tags=["Models"])


# Load provider and model information from JSON files and save to MongoDB
def load_provider_data():
    """Load provider data from JSON files and ensure it's in MongoDB."""
    providers = {}
    provider_dir = os.path.join(
        os.path.dirname(__file__), "../../../app/providers/json"
    )

    # Check if directory exists
    if not os.path.exists(provider_dir):
        print(f"Warning: Provider directory not found: {provider_dir}")
        return providers

    # Track all processed files
    processed_files = []

    try:
        # Only process JSON files if the directory exists
        for filename in os.listdir(provider_dir):
            if filename.endswith(".json"):
                provider_id = filename.split(".")[0]

                # Only process if it's in the allowed providers
                if provider_id not in AVAILABLE_PROVIDERS:
                    print(
                        f"Skipping provider {provider_id} as it's not in AVAILABLE_PROVIDERS"
                    )
                    continue

                processed_files.append(filename)
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
                                if not isinstance(model, dict):
                                    print(
                                        f"Warning: Model entry is not a dictionary in {filename}"
                                    )
                                    continue

                                # Ensure model_type is a string to avoid NoneType errors
                                model_type = model.get("type", "")
                                if model_type is None:
                                    model_type = ""
                                    print(
                                        f"Warning: Model type is None for {model.get('modelName', 'unknown')} in {provider_id}"
                                    )

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

                                # Safe get model properties
                                model_name = model.get("modelName", "")
                                model_display_name = model.get("name", "")

                                # Explicitly add vision capability for OpenAI models that support it
                                if (
                                    provider_id == "openai"
                                    and model_name is not None
                                    and (
                                        "gpt-4o" in model_name
                                        or (
                                            isinstance(model_name, str)
                                            and "vision" in model_name.lower()
                                        )
                                        or (
                                            isinstance(model_display_name, str)
                                            and "Vision" in model_display_name
                                        )
                                    )
                                ):
                                    if "capabilities" not in model:
                                        model["capabilities"] = []
                                    if "vision" not in model["capabilities"]:
                                        model["capabilities"].append("vision")
                                        provider_capabilities.add("vision")

                                # Add max_tokens from contextWindows
                                if "contextWindows" in model:
                                    context_str = model.get("contextWindows", "")
                                    if context_str is not None:  # Check for None
                                        if "k Tokens" in context_str:
                                            # Extract the number (e.g., "128k Tokens" -> 128000)
                                            try:
                                                size = float(context_str.split("k")[0])
                                                model["max_tokens"] = int(size * 1000)
                                            except (ValueError, TypeError) as e:
                                                print(
                                                    f"Error parsing context window '{context_str}': {e}"
                                                )
                                                model["max_tokens"] = 32000  # Default
                                        elif "Tokens" in context_str:
                                            # Handle case without 'k' but with Tokens
                                            try:
                                                size = float(context_str.split(" ")[0])
                                                model["max_tokens"] = int(size)
                                            except (ValueError, TypeError) as e:
                                                print(
                                                    f"Error parsing context window '{context_str}': {e}"
                                                )
                                                model["max_tokens"] = 32000  # Default

                                # Set model ID to modelName if it exists
                                if model_name:
                                    model["id"] = model_name

                                    # Special handling for Mistral embedding model
                                    if (
                                        model_name == "mistral-embed"
                                        and provider_id == "mistral"
                                    ):
                                        # Add the v1 version explicitly
                                        # Create a copy of the model for the v1 version
                                        v1_model = model.copy()
                                        v1_model["modelName"] = "mistral-embed-v1"
                                        v1_model["id"] = "mistral-embed-v1"
                                        v1_model["name"] = "Mistral Embed v1"
                                        v1_model["description"] = (
                                            model.get("description", "") + " (v1)"
                                        )
                                        data.append(v1_model)
                                        print(
                                            f"Added mistral-embed-v1 model based on mistral-embed"
                                        )

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
                except json.JSONDecodeError as json_error:
                    print(f"Error: Invalid JSON format in {filename}: {json_error}")
                    continue
                except Exception as e:
                    print(f"Error loading provider data from {filename}: {e}")
                    print(f"Full exception: {traceback.format_exc()}")
                    continue

        # Now try to save models to MongoDB if configured
        try:
            for provider_id, provider_data in providers.items():
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

                        # Format pricing information
                        pricing = model_data.get("pricing")
                        if not pricing and (
                            "inputPricePer1KTokens" in model_data
                            or "outputPricePer1KTokens" in model_data
                        ):
                            # Create pricing object from input/output fields
                            input_price = model_data.get("inputPricePer1KTokens", 0)
                            output_price = model_data.get("outputPricePer1KTokens", 0)
                            pricing = {"input": input_price, "output": output_price}

                        save_model_info(
                            provider=provider_id,
                            name=model_name,
                            capabilities=capabilities,
                            description=model_data.get("description"),
                            max_tokens=model_data.get("max_tokens"),
                            pricing=pricing,
                            metadata=model_data.get("metadata", {}),
                        )
                    except Exception as e:
                        print(f"Warning: Could not save model to MongoDB: {e}")
        except Exception as e:
            print(f"Error saving models to MongoDB: {e}")
            print(f"Full exception: {traceback.format_exc()}")
            # Continue without crashing - MongoDB saving is optional

    except Exception as e:
        print(f"Unhandled error in load_provider_data: {e}")
        print(f"Full exception: {traceback.format_exc()}")

    # Print summary
    print(
        f"Processed {len(processed_files)} provider files: {', '.join(processed_files)}"
    )
    print(f"Loaded {len(providers)} providers: {', '.join(providers.keys())}")

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
                # Skip if not in available providers
                if provider_id not in AVAILABLE_PROVIDERS:
                    continue

                if provider_id not in provider_models:
                    provider_models[provider_id] = []
                provider_models[provider_id].append(model)

            # Create provider info for each provider
            for provider_id, models in provider_models.items():
                try:
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
                except Exception as provider_error:
                    print(
                        f"Error creating provider info for {provider_id}: {provider_error}"
                    )
                    # Continue to next provider instead of crashing

            # Return early if we have data from MongoDB
            if result:
                return result
    except Exception as e:
        print(f"Error getting models from MongoDB: {e}")

    # Fallback to JSON data if MongoDB fails or has no data
    try:
        for provider_id, provider_data in PROVIDERS.items():
            try:
                # Validate and fill in missing data
                if not provider_data.get("name"):
                    provider_data["name"] = provider_id.capitalize()

                if not provider_data.get("capabilities"):
                    provider_data["capabilities"] = ["chat", "completion"]

                if not provider_data.get("models") or not isinstance(
                    provider_data["models"], list
                ):
                    provider_data["models"] = []
                    print(f"Warning: No models found for provider {provider_id}")
                    continue

                # Create model info objects
                models = []
                for model in provider_data["models"]:
                    try:
                        if not isinstance(model, dict):
                            print(f"Warning: Model data is not a dictionary: {model}")
                            continue

                        model_id = model.get("id") or model.get("modelName")
                        if not model_id:
                            print(f"Warning: Model missing ID for {provider_id}")
                            continue

                        model_name = model.get("modelName") or model_id

                        # Ensure pricing is properly formatted if it exists
                        pricing = None
                        if "pricing" in model:
                            # If pricing is already a dict, use it
                            if isinstance(model["pricing"], dict):
                                pricing = model["pricing"]
                            else:
                                # Try to create pricing from inputPricePer1KTokens and outputPricePer1KTokens
                                input_price = model.get("inputPricePer1KTokens", 0)
                                output_price = model.get("outputPricePer1KTokens", 0)
                                pricing = {"input": input_price, "output": output_price}
                        elif (
                            "inputPricePer1KTokens" in model
                            or "outputPricePer1KTokens" in model
                        ):
                            input_price = model.get("inputPricePer1KTokens", 0)
                            output_price = model.get("outputPricePer1KTokens", 0)
                            pricing = {"input": input_price, "output": output_price}

                        # Create the model info
                        models.append(
                            ModelInfo(
                                id=model_id,
                                name=model_name,
                                provider=provider_id,
                                capabilities=model.get("capabilities", []),
                                description=model.get("description"),
                                max_tokens=model.get("max_tokens"),
                                pricing=pricing,
                                metadata=model.get("metadata", {}),
                            )
                        )
                    except Exception as model_error:
                        print(
                            f"Error processing model for {provider_id}: {model_error}"
                        )
                        continue

                provider_info = ProviderInfo(
                    id=provider_id,
                    name=provider_data["name"],
                    description=provider_data.get("description"),
                    capabilities=provider_data["capabilities"],
                    models=models,
                    metadata=provider_data.get("metadata", {}),
                )
                result.append(provider_info)
            except Exception as provider_error:
                print(f"Error processing provider {provider_id}: {provider_error}")
                continue
    except Exception as e:
        print(f"Error processing providers from JSON: {e}")
        print(traceback.format_exc())
        # Return empty list instead of crashing
        return []

    return result


@router.get("/{provider_id}", response_model=ProviderInfo)
async def get_provider(
    provider_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get information about a specific provider."""

    # Check if provider is in available providers
    if provider_id not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found or not available",
        )

    try:
        # Try to get models from MongoDB first
        try:
            mongo_models = get_models(provider=provider_id)
            if mongo_models and len(mongo_models) > 0:
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
                            pricing=model.get("pricing", {"input": 0, "output": 0}),
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

        # Validate the provider data
        if not provider_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Provider data for '{provider_id}' is empty",
            )

        # Make sure required fields are present
        if not provider_data.get("name"):
            provider_data["name"] = provider_id.capitalize()

        if not provider_data.get("capabilities"):
            provider_data["capabilities"] = ["chat", "completion"]

        # Validate models
        models = []
        if "models" in provider_data and isinstance(provider_data["models"], list):
            for model in provider_data["models"]:
                try:
                    if not isinstance(model, dict):
                        print(
                            f"Warning: Model entry is not a dictionary for {provider_id}"
                        )
                        continue

                    model_id = model.get("id") or model.get("modelName")
                    if not model_id:
                        print(f"Warning: Model missing ID for {provider_id}")
                        continue

                    model_name = model.get("modelName") or model.get("name") or model_id

                    # Ensure pricing is properly formatted if it exists
                    pricing = None
                    if "pricing" in model:
                        # If pricing is already a dict, use it
                        if isinstance(model["pricing"], dict):
                            pricing = model["pricing"]
                        else:
                            # Try to create pricing from inputPricePer1KTokens and outputPricePer1KTokens
                            input_price = model.get("inputPricePer1KTokens", 0)
                            output_price = model.get("outputPricePer1KTokens", 0)
                            pricing = {"input": input_price, "output": output_price}
                    elif (
                        "inputPricePer1KTokens" in model
                        or "outputPricePer1KTokens" in model
                    ):
                        input_price = model.get("inputPricePer1KTokens", 0)
                        output_price = model.get("outputPricePer1KTokens", 0)
                        pricing = {"input": input_price, "output": output_price}

                    # Create the model info
                    models.append(
                        ModelInfo(
                            id=model_id,
                            name=model_name,
                            provider=provider_id,
                            capabilities=model.get("capabilities", []),
                            description=model.get("description"),
                            max_tokens=model.get("max_tokens"),
                            pricing=pricing,
                            metadata=model.get("metadata", {}),
                        )
                    )
                except Exception as model_error:
                    print(f"Error processing model for {provider_id}: {model_error}")
                    continue

        return ProviderInfo(
            id=provider_id,
            name=provider_data["name"],
            description=provider_data.get("description"),
            capabilities=provider_data["capabilities"],
            models=models,
            metadata=provider_data.get("metadata", {}),
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unhandled error in get_provider for {provider_id}: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving provider information: {str(e)}",
        )


@router.get("/{provider_id}/{model_id}", response_model=ModelInfo)
async def get_model_info(
    provider_id: str,
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get information about a specific model."""
    # Check if provider is available
    if provider_id not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found or not available",
        )

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
            # Format pricing information
            pricing = model.get("pricing")
            if not pricing and (
                "inputPricePer1KTokens" in model or "outputPricePer1KTokens" in model
            ):
                # Create pricing object from input/output fields
                input_price = model.get("inputPricePer1KTokens", 0)
                output_price = model.get("outputPricePer1KTokens", 0)
                pricing = {"input": input_price, "output": output_price}

            return ModelInfo(
                id=model["id"],
                name=model["modelName"],
                provider=provider_id,
                capabilities=model["capabilities"],
                description=model.get("description"),
                max_tokens=model.get("max_tokens"),
                pricing=pricing,
                metadata=model.get("metadata", {}),
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model '{model_id}' not found for provider '{provider_id}'",
    )
