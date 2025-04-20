"""
User router for the IndoxRouter server.
Provides endpoints for user management and statistics.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import (
    UsageResponse,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyList,
    CreditPurchase,
    TransactionResponse,
    TransactionItem,
    TransactionList,
)
from app.api.dependencies import get_current_user, get_current_user_from_token
from app.db.database import (
    get_user_usage_stats,
    create_api_key,
    get_user_api_keys,
    revoke_api_key,
    add_user_credits,
    get_user_transactions,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint for the user router.
    """
    return {"status": "ok", "router": "user"}


@router.post("/credits", response_model=TransactionResponse)
async def purchase_credits(
    purchase_data: CreditPurchase,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token),
):
    """
    Purchase credits for the user account.

    Args:
        purchase_data: The credit purchase data.
        current_user: The current authenticated user.

    Returns:
        Transaction details.
    """
    # Validate amount
    if purchase_data.amount < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum credit purchase amount is 10",
        )

    # Process the purchase
    result = add_user_credits(
        user_id=current_user["id"],
        amount=purchase_data.amount,
        payment_method=purchase_data.payment_method,
        reference_id=purchase_data.reference_id,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process credit purchase",
        )

    # Return transaction details
    return TransactionResponse(
        transaction_id=result["transaction_id"],
        amount=purchase_data.amount,
        credits_added=result["credits_added"],
        total_credits=result["total_credits"],
        created_at=result["created_at"],
    )


@router.get("/transactions", response_model=TransactionList)
async def list_transactions(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List the user's transaction history.

    Args:
        current_user: The current authenticated user.
        limit: Maximum number of transactions to return.
        offset: Offset for pagination.

    Returns:
        List of transactions.
    """
    transactions = get_user_transactions(
        user_id=current_user["id"], limit=limit, offset=offset
    )

    # In a real application, you would also get the total count
    # For simplicity, we'll just use the length of the transactions list
    return TransactionList(transactions=transactions, total_count=len(transactions))


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_new_api_key(
    api_key_data: ApiKeyCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token),
):
    """
    Create a new API key for the authenticated user.

    Args:
        api_key_data: The API key creation data.
        current_user: The current authenticated user.

    Returns:
        The newly created API key.
    """
    api_key = create_api_key(current_user["id"], api_key_data.name)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )

    return ApiKeyResponse(**api_key)


@router.get("/api-keys", response_model=ApiKeyList)
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token),
):
    """
    List all API keys for the authenticated user.

    Args:
        current_user: The current authenticated user.

    Returns:
        List of API keys.
    """
    api_keys = get_user_api_keys(current_user["id"])
    return ApiKeyList(keys=api_keys)


@router.delete("/api-keys/{api_key_id}", response_model=Dict[str, bool])
async def delete_api_key(
    api_key_id: int, current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Revoke an API key.

    Args:
        api_key_id: The API key ID to revoke.
        current_user: The current authenticated user.

    Returns:
        Success indicator.
    """
    success = revoke_api_key(current_user["id"], api_key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or already revoked",
        )

    return {"success": True}


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    Get usage statistics for the authenticated user.

    Args:
        current_user: The current authenticated user.
        start_date: Optional start date for filtering.
        end_date: Optional end date for filtering.

    Returns:
        Usage statistics.
    """
    stats = get_user_usage_stats(
        user_id=current_user["id"], start_date=start_date, end_date=end_date
    )

    return stats
