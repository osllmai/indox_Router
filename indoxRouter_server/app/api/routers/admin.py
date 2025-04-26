"""
Admin router for the IndoxRouter server.
Provides endpoints for admin-only operations such as user management,
system statistics, and configuration.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_admin_user
from app.models.schemas import (
    UserResponse,
    ApiKeyResponse,
    TransactionResponse,
    UsageResponse,
    UserCreate,
)
from app.db.database import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    update_user_data,
    delete_user,
    add_user_credits,
    get_user_api_keys,
    revoke_api_key,
    enable_api_key,
    get_user_transactions,
    get_user_usage_stats,
    get_usage_analytics,
    get_system_stats,
    create_api_key,
    create_user,
    get_user_by_email,
    get_all_api_keys as db_get_all_api_keys,
    delete_api_key,
    extend_api_key_expiration,
)
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
async def admin_login(
    username: str = Body(...),
    password: str = Body(...),
):
    """
    Login for admin panel.
    Returns a token that can be used to authenticate admin API requests.
    """
    user = get_user_by_username(username)
    logger.debug(f"Login attempt for user: {username}")
    logger.debug(f"User found: {user is not None}")
    if user:
        logger.debug(f"User account tier: {user.get('account_tier')}")
        logger.debug(f"User is active: {user.get('is_active')}")

    # Check if user exists, is active, and has admin tier
    if (
        not user
        or not user.get("is_active", False)
        or user.get("account_tier") != "admin"
    ):
        logger.warning(
            f"Login failed for user {username}: Invalid credentials or insufficient privileges"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    logger.debug(f"Attempting password verification for user: {username}")
    logger.debug(f"Stored password hash: {user['password']}")

    # Verify the password hash
    password_verified = pwd_context.verify(password, user["password"])
    logger.debug(f"Password verification result: {password_verified}")

    if not password_verified:
        logger.warning(f"Password verification failed for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check if an API key already exists for the admin
    existing_keys = get_user_api_keys(user["id"])
    admin_key = next(
        (key for key in existing_keys if key["name"] == "Admin Panel Access"), None
    )

    if admin_key:
        # If key exists but is not active, re-enable it
        if not admin_key.get("is_active", True):
            logger.info(f"Re-enabling disabled admin API key for {username}")
            enable_api_key(user["id"], admin_key["id"])

        # Extend the expiration date to 90 days from now
        try:
            from datetime import datetime, timedelta

            new_expiration = datetime.now() + timedelta(days=90)
            logger.info(f"Extending admin API key expiration for {username}")
            extend_api_key_expiration(user["id"], admin_key["id"], new_expiration)
        except Exception as e:
            logger.error(f"Failed to extend admin API key expiration: {e}")
    else:
        logger.debug(f"Creating new admin API key for user: {username}")
        # Create a special API key for admin panel use if it doesn't exist
        admin_key = create_api_key(user["id"], name="Admin Panel Access")

    if not admin_key:
        logger.error(f"Failed to create admin API key for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin token",
        )

    logger.info(f"Successful login for admin user: {username}")
    response = JSONResponse(
        content={
            "success": True,
            "token": admin_key["api_key"],
            "user": {
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                or username,
                "avatar": f"https://www.gravatar.com/avatar/{secrets.token_hex(16)}?d=mp&f=y",
            },
        }
    )
    response.set_cookie(
        key="admin_api_key",
        value=admin_key["api_key"],
        httponly=True,
        secure=True,  # Ensure this is set to True in production
        samesite="Strict",
        max_age=60 * 60 * 24 * 90,  # 90 days
    )
    return response


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, description="Skip first N users"),
    limit: int = Query(100, description="Limit to N users"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get all users.
    Only accessible to admin users.
    """
    users = get_all_users(skip=skip, limit=limit, search=search)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., description="The user ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get a specific user by ID.
    Only accessible to admin users.
    """
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/users/{user_id}")
async def update_user(
    user_id: int = Path(..., description="The user ID"),
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    account_tier: Optional[str] = None,
    current_user: Dict = Depends(get_admin_user),
):
    """
    Update a user's information.
    Only accessible to admin users.
    """
    # Prepare update data
    update_data = {}
    if first_name is not None:
        update_data["first_name"] = first_name
    if last_name is not None:
        update_data["last_name"] = last_name
    if email is not None:
        update_data["email"] = email
    if is_active is not None:
        update_data["is_active"] = is_active
    if account_tier is not None:
        update_data["account_tier"] = account_tier

    updated_user = update_user_data(user_id, update_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed",
        )

    return {
        "status": "success",
        "message": "User updated successfully",
        "user": updated_user,
    }


@router.delete("/users/{user_id}")
async def remove_user(
    user_id: int = Path(..., description="The user ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Delete a user.
    Only accessible to admin users.
    """
    # Prevent self-deletion
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    success = delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or delete failed",
        )

    return {"status": "success", "message": f"User {user_id} deleted"}


@router.post("/users/{user_id}/credits", response_model=TransactionResponse)
async def add_credits(
    user_id: int = Path(..., description="The user ID"),
    amount: float = Body(..., description="The amount of credits to add"),
    payment_method: str = Body("admin_grant", description="The payment method"),
    reference_id: Optional[str] = Body(None, description="Optional reference ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Add credits to a user's account.
    Only accessible to admin users.
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive",
        )

    transaction = add_user_credits(
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        reference_id=reference_id or f"admin_grant_by_{current_user['id']}",
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or transaction failed",
        )

    # Adapt the response to match the TransactionResponse model
    # The database returns 'credits_added' but the model expects 'amount'
    response_data = {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["credits_added"],  # Rename the field to match the model
        "credits_added": transaction["credits_added"],
        "total_credits": transaction["total_credits"],
        "created_at": transaction["created_at"],
    }

    return response_data


@router.get("/api-keys", response_model=List[dict])
async def get_all_api_keys(
    limit: int = Query(100, description="The number of API keys to return"),
    offset: int = Query(0, description="The offset to start from"),
    search: Optional[str] = Query(None, description="Search term for username"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get all API keys across all users.
    Only accessible to admin users.
    """
    keys = db_get_all_api_keys(limit=limit, offset=offset, search=search)
    return keys


@router.get("/users/{user_id}/api-keys", response_model=List[ApiKeyResponse])
async def get_api_keys(
    user_id: int = Path(..., description="The user ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get all API keys for a user.
    Only accessible to admin users.
    """
    keys = get_user_api_keys(user_id)
    return keys


@router.post("/users/{user_id}/api-keys/{key_id}/revoke")
async def revoke_key(
    user_id: int = Path(..., description="The user ID"),
    key_id: int = Path(..., description="The API key ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Revoke an API key.
    Only accessible to admin users.
    """
    # Get the API key details first to check its name
    keys = get_user_api_keys(user_id)
    target_key = next((k for k in keys if k["id"] == key_id), None)

    # Prevent revoking admin panel access keys
    if target_key and target_key.get("name") == "Admin Panel Access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke Admin Panel Access key. Create a new admin key first.",
        )

    success = revoke_api_key(user_id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or API key not found",
        )

    return {"status": "success", "message": f"API key {key_id} revoked"}


@router.post("/users/{user_id}/api-keys/{key_id}/enable")
async def enable_key(
    user_id: int = Path(..., description="The user ID"),
    key_id: int = Path(..., description="The API key ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Enable a previously revoked API key.
    Only accessible to admin users.
    """
    success = enable_api_key(user_id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or API key not found",
        )

    return {"status": "success", "message": f"API key {key_id} enabled"}


@router.post("/users/{user_id}/api-keys/{key_id}/extend")
async def extend_key_expiration(
    user_id: int = Path(..., description="The user ID"),
    key_id: int = Path(..., description="The API key ID"),
    days: int = Body(30, description="Number of days to extend the expiration"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Extend the expiration date of an API key.
    Only accessible to admin users.
    """
    from datetime import datetime, timedelta

    # Extend from current expiration date or from now if no expiration is set
    new_expiration = datetime.now() + timedelta(days=days)

    # Call database function to update expiration date - we need to implement this
    success, expires_at = extend_api_key_expiration(user_id, key_id, new_expiration)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or API key not found",
        )

    return {
        "status": "success",
        "message": f"API key {key_id} expiration extended to {expires_at.isoformat()}",
        "expires_at": expires_at.isoformat(),
    }


@router.delete("/users/{user_id}/api-keys/{key_id}")
async def delete_key(
    user_id: int = Path(..., description="The user ID"),
    key_id: int = Path(..., description="The API key ID"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Permanently delete an API key.
    Only accessible to admin users.
    """
    # Get the API key details first to check its name
    keys = get_user_api_keys(user_id)
    target_key = next((k for k in keys if k["id"] == key_id), None)

    # Prevent deleting admin panel access keys
    if target_key and target_key.get("name") == "Admin Panel Access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete Admin Panel Access key. Create a new admin key first.",
        )

    success = delete_api_key(user_id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or API key not found",
        )

    return {"status": "success", "message": f"API key {key_id} permanently deleted"}


@router.get("/users/{user_id}/transactions")
async def get_transactions(
    user_id: int = Path(..., description="The user ID"),
    limit: int = Query(20, description="Maximum number of transactions"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get transactions for a user.
    Only accessible to admin users.
    """
    transactions = get_user_transactions(user_id, limit, offset)
    return {"transactions": transactions, "count": len(transactions)}


@router.get("/users/{user_id}/usage", response_model=UsageResponse)
async def get_usage(
    user_id: int = Path(..., description="The user ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get usage statistics for a user.
    Only accessible to admin users.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()

    stats = get_user_usage_stats(user_id, start_date, end_date)
    return stats


@router.get("/system/stats")
async def system_statistics(
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get system-wide statistics.
    Only accessible to admin users.
    """
    stats = get_system_stats()
    return stats


@router.get("/analytics")
async def get_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: str = Query(
        "date", description="Group by: date, model, provider, endpoint"
    ),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model: Optional[str] = Query(None, description="Filter by model"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    include_content: bool = Query(
        False, description="Include request/response content"
    ),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get detailed analytics data.
    Only accessible to admin users.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()

    analytics = get_usage_analytics(
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
        provider=provider,
        model=model,
        endpoint=endpoint,
        include_content=include_content,
    )

    return {
        "data": analytics,
        "count": len(analytics),
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "group_by": group_by,
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
        },
    }


@router.get("/models")
async def get_models(
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get models data with usage statistics from MongoDB.
    Only accessible to admin users.
    """
    try:
        # from app.providers.factory import get_all_providers
        import json
        import os
        from app.core.config import settings
        import pymongo

        # Get models from JSON files for OpenAI, Mistral, and DeepSeek
        models_data = {}
        providers = ["openai", "mistral", "deepseek"]

        # Base directory for provider JSON files
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "providers",
            "json",
        )

        # Load model definitions from JSON files
        for provider in providers:
            json_path = os.path.join(base_dir, f"{provider}.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    models_data[provider] = json.load(f)
            else:
                models_data[provider] = []

        # Connect to MongoDB to get usage statistics
        mongo_uri = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/indoxrouter?authSource=admin"
        mongo_client = pymongo.MongoClient(mongo_uri)
        db = mongo_client.indoxrouter

        # Get usage stats for models
        model_stats = list(
            db.requests.aggregate(
                [
                    {
                        "$group": {
                            "_id": {"provider": "$provider", "model": "$model"},
                            "requests": {"$sum": 1},
                            "input_tokens": {"$sum": "$input_tokens"},
                            "output_tokens": {"$sum": "$output_tokens"},
                            "cost": {"$sum": "$cost"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "provider": "$_id.provider",
                            "model": "$_id.model",
                            "requests": 1,
                            "input_tokens": 1,
                            "output_tokens": 1,
                            "cost": 1,
                        }
                    },
                ]
            )
        )

        # Create a mapping of model stats
        stats_map = {}
        for stat in model_stats:
            key = f"{stat['provider']}:{stat['model']}"
            stats_map[key] = {
                "requests": stat["requests"],
                "input_tokens": stat["input_tokens"],
                "output_tokens": stat["output_tokens"],
                "total_tokens": stat["input_tokens"] + stat["output_tokens"],
                "cost": stat["cost"],
            }

        # Add usage stats to models
        for provider, models in models_data.items():
            for model in models:
                model_key = f"{provider}:{model['modelName']}"
                if model_key in stats_map:
                    model["usage"] = stats_map[model_key]
                else:
                    model["usage"] = {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "cost": 0,
                    }

                # Add provider name for reference
                model["provider"] = provider

        return models_data
    except Exception as e:
        logger.error(f"Error getting models data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models data: {str(e)}",
        )


@router.post("/users/create")
async def create_new_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    first_name: Optional[str] = Body(None),
    last_name: Optional[str] = Body(None),
    account_tier: str = Body("free"),
    is_active: bool = Body(True),
    initial_credits: float = Body(0),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Create a new user.
    Only accessible to admin users.
    """
    try:
        # Validate inputs
        if not username or not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username, email, and password are required",
            )

        # Check if username or email already exists
        existing_user_by_username = get_user_by_username(username)
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{username}' already exists",
            )

        existing_user_by_email = get_user_by_email(email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{email}' already exists",
            )

        # Hash the password
        hashed_password = pwd_context.hash(password)

        # Create the user
        new_user = create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )

        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user. Database error occurred.",
            )

        logger.info(f"User created: {username} (ID: {new_user['id']})")

        # Update the account tier if different from default
        if account_tier != "free":
            update_data = {"account_tier": account_tier}
            if not is_active:
                update_data["is_active"] = is_active

            updated_user = update_user_data(new_user["id"], update_data)
            if not updated_user:
                logger.error(f"Failed to update account tier for user {new_user['id']}")

        # Add initial credits if specified
        if initial_credits > 0:
            transaction = add_user_credits(
                user_id=new_user["id"],
                amount=initial_credits,
                payment_method="admin_grant",
                reference_id=f"initial_credits_by_{current_user['id']}",
            )

            if not transaction:
                logger.error(f"Failed to add initial credits for user {new_user['id']}")

        return {
            "status": "success",
            "message": "User created successfully",
            "id": new_user["id"],
        }
    except HTTPException as e:
        # Rethrow HTTP exceptions as they already have the right format
        raise e
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


class ApiKeyCreate(BaseModel):
    name: str = "Admin Generated Key"


@router.post("/users/{user_id}/api-keys", response_model=ApiKeyResponse)
async def create_user_api_key(
    user_id: int = Path(..., description="The user ID"),
    api_key_data: ApiKeyCreate = Body(...),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Create a new API key for a user.
    Only accessible to admin users.
    """
    api_key_data = create_api_key(user_id, name=api_key_data.name)
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or failed to create API key",
        )
    return api_key_data


@router.get("/transactions")
async def get_all_transactions(
    limit: int = Query(100, description="Maximum number of transactions"),
    offset: int = Query(0, description="Offset for pagination"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: Dict = Depends(get_admin_user),
):
    """
    Get all transactions across all users.
    Only accessible to admin users.
    """
    try:
        transactions = get_user_transactions(None, limit=limit, offset=offset)
        return {"transactions": transactions, "count": len(transactions)}
    except Exception as e:
        logger.error(f"Error getting all transactions: {e}")
        # Return empty list instead of error to prevent frontend from breaking
        return {"transactions": [], "count": 0}
