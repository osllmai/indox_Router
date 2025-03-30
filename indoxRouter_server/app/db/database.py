"""
Database connection module for IndoxRouter server.
This module connects to the database and provides functions for database operations.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime, date

from app.core.config import settings

logger = logging.getLogger(__name__)

# Connection pool
pool = None


def init_db():
    """Initialize the database connection pool."""
    global pool
    try:
        # Create a connection pool
        pool = ThreadedConnectionPool(
            minconn=settings.DB_MIN_CONNECTIONS,
            maxconn=settings.DB_MAX_CONNECTIONS,
            dsn=settings.DATABASE_URL,
        )
        logger.info("Database connection pool initialized")

        # Test the connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("Database connection test successful")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {e}")
        return False


def get_connection():
    """Get a connection from the pool."""
    if pool is None:
        raise Exception("Database connection pool not initialized")
    return pool.getconn()


def release_connection(conn):
    """Release a connection back to the pool."""
    if pool is not None:
        pool.putconn(conn)


# User Management Functions


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, username, email, is_active, credits, account_tier, 
                           created_at, last_login_at
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )
                user = cur.fetchone()
                return dict(user) if user else None
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Get a user by API key."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT u.id, u.username, u.email, u.is_active, u.credits, 
                           u.account_tier, k.id as api_key_id
                    FROM users u
                    JOIN api_keys k ON u.id = k.user_id
                    WHERE k.api_key = %s AND k.is_active = TRUE 
                          AND (k.expires_at IS NULL OR k.expires_at > NOW())
                    """,
                    (api_key,),
                )
                user = cur.fetchone()

                if user:
                    # Update last_used_at for the API key
                    cur.execute(
                        """
                        UPDATE api_keys
                        SET last_used_at = NOW()
                        WHERE api_key = %s
                        """,
                        (api_key,),
                    )
                    conn.commit()

                return dict(user) if user else None
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by API key: {e}")
        return None


def validate_api_key(api_key: str) -> bool:
    """Validate an API key."""
    user = get_user_by_api_key(api_key)
    return user is not None and user["is_active"]


# API Request Tracking Functions


def log_api_request(
    user_id: int,
    api_key_id: Optional[int],
    request_id: str,
    endpoint: str,
    model: str,
    provider: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    cost: float = 0.0,
    duration_ms: int = 0,
    status_code: int = 200,
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_params: Optional[Dict] = None,
    response_summary: Optional[str] = None,
) -> bool:
    """
    Log an API request to the database.

    Args:
        user_id: The user ID.
        api_key_id: The API key ID.
        request_id: The unique request ID.
        endpoint: The endpoint that was called.
        model: The model that was used.
        provider: The provider that was used.
        tokens_input: The number of input tokens.
        tokens_output: The number of output tokens.
        cost: The cost of the request.
        duration_ms: The duration of the request in milliseconds.
        status_code: The HTTP status code.
        error_message: The error message, if any.
        ip_address: The IP address of the client.
        user_agent: The user agent of the client.
        request_params: The request parameters.
        response_summary: A summary of the response.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                tokens_total = tokens_input + tokens_output

                cur.execute(
                    """
                    INSERT INTO api_requests (
                        user_id, api_key_id, request_id, endpoint, model, provider,
                        tokens_input, tokens_output, tokens_total, cost, duration_ms,
                        status_code, error_message, ip_address, user_agent,
                        created_at, request_params, response_summary
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        NOW(), %s, %s
                    )
                    """,
                    (
                        user_id,
                        api_key_id,
                        request_id,
                        endpoint,
                        model,
                        provider,
                        tokens_input,
                        tokens_output,
                        tokens_total,
                        cost,
                        duration_ms,
                        status_code,
                        error_message,
                        ip_address,
                        user_agent,
                        request_params,
                        response_summary,
                    ),
                )
                conn.commit()
                return True
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error logging API request: {e}")
        return False


def update_user_credit(
    user_id: int,
    cost: float,
    endpoint: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    model: str = "",
    provider: str = "",
) -> bool:
    """
    Update a user's credit in the database and log the transaction.

    Args:
        user_id: The user ID.
        cost: The cost of the request.
        endpoint: The endpoint that was called.
        tokens_input: The number of input tokens.
        tokens_output: The number of output tokens.
        model: The model that was used.
        provider: The provider that was used.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Generate a unique request ID
                request_id = str(uuid.uuid4())

                # Update the user's credit
                cur.execute(
                    """
                    UPDATE users
                    SET credits = credits - %s
                    WHERE id = %s AND credits >= %s
                    RETURNING id, credits
                    """,
                    (cost, user_id, cost),
                )

                result = cur.fetchone()

                # If no rows were updated, the user doesn't have enough credits
                if not result:
                    logger.warning(
                        f"User {user_id} doesn't have enough credits for this request"
                    )
                    # Rollback the transaction
                    conn.rollback()
                    return False

                # Log the credit usage in billing_transactions
                cur.execute(
                    """
                    INSERT INTO billing_transactions (
                        user_id, transaction_id, amount, transaction_type, 
                        description, created_at
                    )
                    VALUES (
                        %s, %s, %s, 'credit_usage', %s, NOW()
                    )
                    """,
                    (
                        user_id,
                        f"usage-{request_id}",
                        cost,
                        f"API usage: {endpoint} ({model})",
                    ),
                )

                # Update daily usage summary
                today = date.today()
                tokens_total = tokens_input + tokens_output

                # Try to update existing record for today
                cur.execute(
                    """
                    UPDATE usage_daily_summary
                    SET total_requests = total_requests + 1,
                        total_tokens_input = total_tokens_input + %s,
                        total_tokens_output = total_tokens_output + %s,
                        total_tokens = total_tokens + %s,
                        total_cost = total_cost + %s
                    WHERE user_id = %s AND date = %s
                    RETURNING id
                    """,
                    (tokens_input, tokens_output, tokens_total, cost, user_id, today),
                )

                # If no record exists for today, create one
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        INSERT INTO usage_daily_summary (
                            user_id, date, total_requests, total_tokens_input,
                            total_tokens_output, total_tokens, total_cost
                        )
                        VALUES (
                            %s, %s, 1, %s, %s, %s, %s
                        )
                        """,
                        (
                            user_id,
                            today,
                            tokens_input,
                            tokens_output,
                            tokens_total,
                            cost,
                        ),
                    )

                # Commit the transaction
                conn.commit()
                logger.info(
                    f"Updated credits for user {user_id}. New balance: {result[1]}"
                )
                return True
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error updating user credit: {e}")
        return False


# Model and Provider Functions


def get_available_models() -> List[Dict[str, Any]]:
    """Get all available models."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT m.id, m.name, m.display_name, p.name as provider,
                           m.capabilities, m.max_tokens, 
                           m.input_cost_per_1k_tokens, m.output_cost_per_1k_tokens
                    FROM models m
                    JOIN providers p ON m.provider_id = p.id
                    WHERE m.is_active = TRUE AND p.is_active = TRUE
                    ORDER BY p.name, m.name
                    """
                )
                models = cur.fetchall()
                return [dict(model) for model in models]
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []


def get_model_info(provider: str, model_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific model."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT m.id, m.name, m.display_name, p.name as provider,
                           m.capabilities, m.max_tokens, 
                           m.input_cost_per_1k_tokens, m.output_cost_per_1k_tokens
                    FROM models m
                    JOIN providers p ON m.provider_id = p.id
                    WHERE p.name = %s AND m.name = %s
                    """,
                    (provider, model_name),
                )
                model = cur.fetchone()
                return dict(model) if model else None
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return None


# User API Key Management


def get_user_api_keys(user_id: int) -> List[Dict[str, Any]]:
    """Get all API keys for a user."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, api_key, name, is_active, created_at, expires_at, last_used_at
                    FROM api_keys
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )
                keys = cur.fetchall()
                return [dict(key) for key in keys]
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user API keys: {e}")
        return []


def create_api_key(user_id: int, name: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Create a new API key for a user."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO api_keys (user_id, api_key, name, created_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING id, api_key, name, is_active, created_at, expires_at
                    """,
                    (user_id, api_key, name),
                )
                key = cur.fetchone()
                conn.commit()
                return dict(key) if key else None
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        return None


# Billing and Subscription Functions


def add_user_credits(
    user_id: int, amount: float, transaction_type: str, description: str
) -> bool:
    """Add credits to a user's account."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Generate a transaction ID
                transaction_id = f"credit-{uuid.uuid4()}"

                # Update the user's credits
                cur.execute(
                    """
                    UPDATE users
                    SET credits = credits + %s
                    WHERE id = %s
                    RETURNING id, credits
                    """,
                    (amount, user_id),
                )

                result = cur.fetchone()
                if not result:
                    logger.warning(f"User {user_id} not found")
                    conn.rollback()
                    return False

                # Log the transaction
                cur.execute(
                    """
                    INSERT INTO billing_transactions (
                        user_id, transaction_id, amount, transaction_type, 
                        description, created_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, NOW()
                    )
                    """,
                    (user_id, transaction_id, amount, transaction_type, description),
                )

                conn.commit()
                logger.info(
                    f"Added {amount} credits to user {user_id}. New balance: {result[1]}"
                )
                return True
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error adding user credits: {e}")
        return False


def get_user_billing_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get billing history for a user."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, transaction_id, amount, currency, transaction_type,
                           status, payment_method, description, created_at
                    FROM billing_transactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                transactions = cur.fetchall()
                return [dict(tx) for tx in transactions]
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user billing history: {e}")
        return []


# Usage Analytics Functions


def get_user_usage_summary(
    user_id: int, start_date: date, end_date: date
) -> List[Dict[str, Any]]:
    """Get usage summary for a user within a date range."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT date, total_requests, total_tokens_input, 
                           total_tokens_output, total_tokens, total_cost
                    FROM usage_daily_summary
                    WHERE user_id = %s AND date BETWEEN %s AND %s
                    ORDER BY date
                    """,
                    (user_id, start_date, end_date),
                )
                summary = cur.fetchall()
                return [dict(day) for day in summary]
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user usage summary: {e}")
        return []


def get_user_model_usage(
    user_id: int, start_date: datetime, end_date: datetime
) -> List[Dict[str, Any]]:
    """Get model usage for a user within a date range."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT model, provider, COUNT(*) as request_count,
                           SUM(tokens_input) as total_tokens_input,
                           SUM(tokens_output) as total_tokens_output,
                           SUM(tokens_total) as total_tokens,
                           SUM(cost) as total_cost
                    FROM api_requests
                    WHERE user_id = %s AND created_at BETWEEN %s AND %s
                    GROUP BY model, provider
                    ORDER BY total_cost DESC
                    """,
                    (user_id, start_date, end_date),
                )
                usage = cur.fetchall()
                return [dict(model) for model in usage]
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user model usage: {e}")
        return []
