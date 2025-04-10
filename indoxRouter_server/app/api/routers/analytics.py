"""
Analytics router for the IndoxRouter server.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_user
from app.db.database import get_usage_analytics
from app.core.config import settings

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/usage")
async def get_usage_data(
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    group_by: str = Query(
        "date",
        description="Field to group results by (date, model, provider, endpoint, session_id, client_ip)",
    ),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model: Optional[str] = Query(None, description="Filter by model"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    endpoint: Optional[str] = Query(
        None, description="Filter by endpoint (chat, completion, embedding, image)"
    ),
    include_content: bool = Query(
        False,
        description="Include request/response content in results (only for non-grouped queries)",
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed usage analytics with flexible grouping and filtering.

    Returns:
        Usage analytics data based on the specified filters and grouping.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()

    # Get user ID from authenticated user
    user_id = current_user.get("id")

    # Check if the user is an admin
    is_admin = current_user.get("is_admin", False)

    # For non-admin users, force filter by their user ID
    if not is_admin:
        analytics_data = get_usage_analytics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            provider=provider,
            model=model,
            session_id=session_id,
            endpoint=endpoint,
            include_content=include_content,
        )
    else:
        # Admin users can view data for all users or filter by specific user ID
        filtered_user_id = int(user_id) if user_id else None
        analytics_data = get_usage_analytics(
            user_id=filtered_user_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            provider=provider,
            model=model,
            session_id=session_id,
            endpoint=endpoint,
            include_content=include_content,
        )

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "group_by": group_by,
        "filters": {
            "provider": provider,
            "model": model,
            "session_id": session_id,
            "endpoint": endpoint,
        },
        "results": analytics_data,
    }


@router.get("/sessions")
async def get_session_data(
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    session_id: Optional[str] = Query(
        None, description="Filter by specific session ID"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get session-based analytics showing conversation flows.

    Returns:
        Session analytics data showing sequences of interactions.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).date()
    if not end_date:
        end_date = datetime.now().date()

    # Get user ID from authenticated user
    user_id = current_user.get("id")

    # For session data, we want chronological listing without grouping
    # If session_id is provided, we'll get all interactions in that session
    session_data = get_usage_analytics(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        session_id=session_id,
        include_content=True,  # Include content for session analysis
    )

    # If a specific session was requested but not found
    if session_id and not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found or does not belong to the current user",
        )

    # For session listing (no specific session_id), group by session
    if not session_id:
        session_data = get_usage_analytics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            group_by="session_id",
        )

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "session_id": session_id,
        "results": session_data,
    }


@router.get("/models")
async def get_model_performance(
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get model performance analytics comparing different models.

    Returns:
        Model performance data grouped by model.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()

    # Get user ID from authenticated user
    user_id = current_user.get("id")

    # Get model performance data grouped by model
    model_data = get_usage_analytics(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        group_by="model",
        provider=provider,
    )

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "provider": provider,
        "results": model_data,
    }
