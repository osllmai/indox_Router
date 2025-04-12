"""
User router for the IndoxRouter server.
Provides endpoints for user management and statistics.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import UsageResponse
from app.api.dependencies import get_current_user
from app.db.database import get_user_usage_stats

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint for the user router.
    """
    return {"status": "ok", "router": "user"}


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get usage statistics for the current user.

    Data is aggregated from both PostgreSQL and MongoDB.
    """
    # Set default date range if not provided (last 30 days)
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Make sure start_date is before end_date
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date",
        )

    # Get usage statistics from the database
    user_id = current_user["id"]
    usage_stats = get_user_usage_stats(user_id, start_date, end_date)

    return usage_stats
