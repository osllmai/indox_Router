"""
Database connection module for IndoxRouter server.
This module connects to PostgreSQL and MongoDB databases and provides functions for database operations.
"""

import logging
import uuid
import os
from typing import Dict, List, Optional, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime, date, timedelta
from decimal import Decimal

# MongoDB imports
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from bson.objectid import ObjectId

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL Connection pool
pg_pool = None

# MongoDB client
mongo_client = None
mongo_db = None


def init_db():
    """Initialize database connections for both PostgreSQL and MongoDB."""
    success = init_postgres()

    # Initialize MongoDB regardless of PostgreSQL success
    # This allows us to operate with MongoDB even if PostgreSQL fails
    if settings.MONGODB_URI:
        mongo_success = init_mongodb()
        # If either database fails, we consider the init as failed
        success = success and mongo_success
    else:
        logger.warning("MongoDB URI not provided. MongoDB features will be disabled.")

    return success


def init_postgres():
    """Initialize the PostgreSQL database connection pool."""
    global pg_pool
    try:
        # Create a connection pool
        pg_pool = ThreadedConnectionPool(
            minconn=settings.DB_MIN_CONNECTIONS,
            maxconn=settings.DB_MAX_CONNECTIONS,
            dsn=settings.DATABASE_URL,
        )
        logger.info("PostgreSQL database connection pool initialized")

        # Test the connection
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("PostgreSQL database connection test successful")

                # Check if tables exist, create if they don't
                tables_exist = check_tables_exist(cur)
                if not tables_exist:
                    create_tables(conn)

        return True
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL database connection: {e}")
        return False


def init_mongodb():
    """Initialize the MongoDB connection."""
    global mongo_client, mongo_db
    try:
        mongo_client = MongoClient(settings.MONGODB_URI)
        mongo_db = mongo_client[settings.MONGODB_DATABASE]

        # Test the connection
        mongo_db.command("ping")
        logger.info("MongoDB connection initialized successfully")

        # Create indexes if needed
        create_mongo_indexes()

        return True
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB connection: {e}")
        return False


def create_mongo_indexes():
    """Create indexes for MongoDB collections."""
    try:
        # Conversations collection
        if "conversations" in mongo_db.list_collection_names():
            mongo_db.conversations.create_index("user_id")
            mongo_db.conversations.create_index(
                [("title", "text"), ("messages.content", "text")]
            )

        # Embeddings collection
        if "embeddings" in mongo_db.list_collection_names():
            mongo_db.embeddings.create_index("user_id")
            mongo_db.embeddings.create_index([("text", "text")])

        # User datasets collection
        if "user_datasets" in mongo_db.list_collection_names():
            mongo_db.user_datasets.create_index("user_id")

        # Model outputs collection (for caching)
        if "model_outputs" in mongo_db.list_collection_names():
            mongo_db.model_outputs.create_index("request_hash", unique=True)
            mongo_db.model_outputs.create_index("ttl", expireAfterSeconds=0)

        # Models collection
        if "models" in mongo_db.list_collection_names():
            mongo_db.models.create_index("provider")
            mongo_db.models.create_index("name")

        # Model usage statistics
        if "model_usage" in mongo_db.list_collection_names():
            mongo_db.model_usage.create_index("user_id")
            mongo_db.model_usage.create_index("model")
            mongo_db.model_usage.create_index("date")

        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")


def check_tables_exist(cursor) -> bool:
    """Check if the required tables exist in PostgreSQL."""
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users'
        )
    """
    )
    return cursor.fetchone()[0]


def create_tables(connection):
    """Create the necessary tables in PostgreSQL if they don't exist."""
    try:
        with connection.cursor() as cur:
            # Read schema SQL file and execute it
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

            if os.path.exists(schema_path):
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                    cur.execute(schema_sql)
                connection.commit()
                logger.info("Database tables created successfully")
            else:
                logger.error(f"Schema file not found at {schema_path}")
                raise FileNotFoundError(f"Schema file not found at {schema_path}")

    except Exception as e:
        connection.rollback()
        logger.error(f"Error creating database tables: {e}")
        raise


def get_pg_connection():
    """Get a PostgreSQL connection from the pool."""
    if pg_pool is None:
        raise Exception("PostgreSQL connection pool not initialized")
    return pg_pool.getconn()


def release_pg_connection(conn):
    """Release a PostgreSQL connection back to the pool."""
    if pg_pool is not None:
        pg_pool.putconn(conn)


def get_mongo_db() -> MongoDatabase:
    """Get the MongoDB database instance."""
    if mongo_db is None:
        raise Exception("MongoDB connection not initialized")
    return mongo_db


# User Management Functions (PostgreSQL)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID from PostgreSQL."""
    try:
        conn = get_pg_connection()
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
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Get a user by API key from PostgreSQL."""
    try:
        conn = get_pg_connection()
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
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by API key: {e}")
        return None


def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify an API key and return the associated user if valid.

    Args:
        api_key: The API key to verify.

    Returns:
        The user information if the API key is valid, None otherwise.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT u.id, u.username, u.email, u.is_active, u.credits, 
                           u.account_tier, k.id as api_key_id, k.name as key_name,
                           k.created_at as key_created_at
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
                    return dict(user)
                return None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error verifying API key: {e}")
        return None


def validate_api_key(api_key: str) -> bool:
    """Validate an API key against PostgreSQL."""
    user = get_user_by_api_key(api_key)
    return user is not None and user.get("is_active", False)


def update_api_key_last_used(api_key_id: int) -> bool:
    """
    Update the last_used_at timestamp for an API key.

    Args:
        api_key_id: The API key ID.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE api_keys
                    SET last_used_at = NOW()
                    WHERE id = %s
                    RETURNING id
                    """,
                    (api_key_id,),
                )
                result = cur.fetchone()
                conn.commit()
                return result is not None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error updating API key last used timestamp: {e}")
        return False


# Keep the rest of your original PostgreSQL functions...
# However, you should update all your functions to use get_pg_connection and release_pg_connection

# MongoDB specific functions


def save_conversation(user_id: int, title: str, messages: List[Dict[str, Any]]) -> str:
    """Save a conversation to MongoDB."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for saving conversations")
            return None

        conversation = {
            "user_id": user_id,
            "title": title,
            "messages": messages,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = mongo_db.conversations.insert_one(conversation)
        logger.info(f"Conversation saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        return None


def get_user_conversations(
    user_id: int, limit: int = 20, skip: int = 0
) -> List[Dict[str, Any]]:
    """Get user conversations from MongoDB."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving conversations")
            return []

        conversations = list(
            mongo_db.conversations.find(
                {"user_id": user_id},
                {"_id": 1, "title": 1, "created_at": 1, "updated_at": 1},
            )
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )

        # Convert ObjectId to string for JSON serialization
        for conv in conversations:
            conv["id"] = str(conv.pop("_id"))

        return conversations
    except Exception as e:
        logger.error(f"Error getting user conversations: {e}")
        return []


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific conversation from MongoDB by ID."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving conversation")
            return None

        conversation = mongo_db.conversations.find_one(
            {"_id": ObjectId(conversation_id)}
        )

        if conversation:
            conversation["id"] = str(conversation.pop("_id"))
            return conversation
        return None
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return None


def save_embedding(
    user_id: int,
    text: str,
    embedding: List[float],
    model: str,
    metadata: Dict[str, Any] = None,
) -> str:
    """Save an embedding to MongoDB."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for saving embeddings")
            return None

        embedding_doc = {
            "user_id": user_id,
            "text": text,
            "embedding": embedding,
            "model": model,
            "metadata": metadata or {},
            "created_at": datetime.now(),
        }

        result = mongo_db.embeddings.insert_one(embedding_doc)
        logger.info(f"Embedding saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving embedding: {e}")
        return None


def get_embedding(embedding_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific embedding from MongoDB by ID."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving embedding")
            return None

        embedding = mongo_db.embeddings.find_one({"_id": ObjectId(embedding_id)})

        if embedding:
            embedding["id"] = str(embedding.pop("_id"))
            return embedding
        return None
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        return None


def cache_model_output(
    request_hash: str,
    provider: str,
    model: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    ttl_days: int = 7,
) -> bool:
    """Cache model output to MongoDB for future use."""
    try:
        if mongo_db is None or not settings.ENABLE_RESPONSE_CACHE:
            return False

        # Calculate expiration time
        ttl = datetime.now() + timedelta(days=ttl_days)

        cache_entry = {
            "request_hash": request_hash,
            "provider": provider,
            "model": model,
            "input_data": input_data,
            "output_data": output_data,
            "ttl": ttl,
            "created_at": datetime.now(),
        }

        # Use upsert for idempotency
        result = mongo_db.model_outputs.update_one(
            {"request_hash": request_hash},
            {"$set": cache_entry},
            upsert=True,
        )

        return result.acknowledged
    except Exception as e:
        logger.error(f"Error caching model output: {e}")
        return False


def get_cached_model_output(request_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached model output from MongoDB."""
    try:
        if mongo_db is None or not settings.ENABLE_RESPONSE_CACHE:
            return None

        cached = mongo_db.model_outputs.find_one({"request_hash": request_hash})

        if cached:
            # Remove MongoDB-specific fields for clean data
            cached.pop("_id", None)
            return cached.get("output_data")

        return None
    except Exception as e:
        logger.error(f"Error retrieving cached model output: {e}")
        return None


# Model management functions (MongoDB)


def save_model_info(
    provider: str,
    name: str,
    capabilities: List[str],
    description: str = None,
    max_tokens: int = None,
    pricing: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
) -> str:
    """Save model information to MongoDB."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for saving model info")
            return None

        model_doc = {
            "provider": provider,
            "name": name,
            "capabilities": capabilities,
            "description": description,
            "max_tokens": max_tokens,
            "pricing": pricing or {},
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Use upsert to avoid duplicates
        result = mongo_db.models.update_one(
            {"provider": provider, "name": name},
            {"$set": model_doc},
            upsert=True,
        )

        if result.upserted_id:
            return str(result.upserted_id)
        else:
            # Find the existing document to return its ID
            existing = mongo_db.models.find_one({"provider": provider, "name": name})
            return str(existing["_id"]) if existing else None
    except Exception as e:
        logger.error(f"Error saving model info: {e}")
        return None


def get_models(provider: str = None) -> List[Dict[str, Any]]:
    """Get models from MongoDB, optionally filtered by provider."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving models")
            return []

        query = {}
        if provider:
            query["provider"] = provider

        models = list(mongo_db.models.find(query))

        # Convert ObjectId to string for JSON serialization
        for model in models:
            model["id"] = str(model.pop("_id"))

        return models
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return []


def get_model(provider: str, name: str) -> Optional[Dict[str, Any]]:
    """Get a specific model from MongoDB by provider and name."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving model")
            return None

        model = mongo_db.models.find_one({"provider": provider, "name": name})

        if model:
            model["id"] = str(model.pop("_id"))
            return model
        return None
    except Exception as e:
        logger.error(f"Error getting model: {e}")
        return None


def log_model_usage(
    user_id: int,
    provider: str,
    model: str,
    tokens_prompt: int = 0,
    tokens_completion: int = 0,
    cost: float = 0.0,
    latency: float = 0.0,
    request_id: str = None,
) -> bool:
    """Log model usage to MongoDB."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for logging model usage")
            return False

        usage_doc = {
            "user_id": user_id,
            "provider": provider,
            "model": model,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "tokens_total": tokens_prompt + tokens_completion,
            "cost": cost,
            "latency": latency,
            "request_id": request_id,
            "timestamp": datetime.now(),
            "date": datetime.now().date().isoformat(),
        }

        result = mongo_db.model_usage.insert_one(usage_doc)
        return result.acknowledged
    except Exception as e:
        logger.error(f"Error logging model usage: {e}")
        return False


def get_user_model_usage(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    provider: str = None,
    model: str = None,
) -> List[Dict[str, Any]]:
    """Get user model usage from MongoDB with optional filtering."""
    try:
        if mongo_db is None:
            logger.error("MongoDB not initialized for retrieving user model usage")
            return []

        query = {"user_id": user_id}

        if start_date and end_date:
            query["date"] = {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat(),
            }

        if provider:
            query["provider"] = provider

        if model:
            query["model"] = model

        usage = list(mongo_db.model_usage.find(query))

        # Convert ObjectId to string for JSON serialization
        for item in usage:
            item["id"] = str(item.pop("_id"))

        return usage
    except Exception as e:
        logger.error(f"Error getting user model usage: {e}")
        return []


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
    Update a user's credit in the database.

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
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # Get the user's current credit
                cur.execute(
                    """
                    SELECT credits FROM users WHERE id = %s
                    """,
                    (user_id,),
                )
                result = cur.fetchone()
                if not result:
                    logger.error(f"User {user_id} not found")
                    return False

                current_credit = result[0]
                # Convert float to Decimal to avoid type errors
                cost_decimal = Decimal(str(cost))
                new_credit = current_credit - cost_decimal

                # Check if the user has enough credits
                if new_credit < 0:
                    logger.warning(
                        f"User {user_id} doesn't have enough credits. Current: {current_credit}, Required: {cost_decimal}"
                    )
                    conn.rollback()
                    return False

                # Update the user's credit
                cur.execute(
                    """
                    UPDATE users 
                    SET credits = %s 
                    WHERE id = %s
                    """,
                    (new_credit, user_id),
                )

                # Calculate total tokens
                tokens_total = tokens_input + tokens_output

                # Update the daily usage
                today = datetime.now().date()
                cur.execute(
                    """
                    INSERT INTO usage_daily_summary 
                    (user_id, date, total_requests, total_tokens_input, 
                     total_tokens_output, total_tokens, total_cost)
                    VALUES (%s, %s, 1, %s, %s, %s, %s)
                    ON CONFLICT (user_id, date) DO UPDATE
                    SET 
                        total_requests = usage_daily_summary.total_requests + 1,
                        total_tokens_input = usage_daily_summary.total_tokens_input + %s,
                        total_tokens_output = usage_daily_summary.total_tokens_output + %s,
                        total_tokens = usage_daily_summary.total_tokens + %s,
                        total_cost = usage_daily_summary.total_cost + %s,
                        updated_at = NOW()
                    """,
                    (
                        user_id,
                        today,
                        tokens_input,
                        tokens_output,
                        tokens_total,
                        cost_decimal,
                        tokens_input,
                        tokens_output,
                        tokens_total,
                        cost_decimal,
                    ),
                )

                conn.commit()
                logger.info(
                    f"Updated credits for user {user_id}. Previous: {current_credit}, New: {new_credit}"
                )
                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error updating user credit: {e}")
        return False


def log_api_request(
    user_id: int,
    api_key_id: int,
    request_id: str,
    endpoint: str,
    model: str,
    provider: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    cost: float = 0.0,
    duration_ms: int = 0,
    status_code: int = 200,
    response_summary: str = None,
) -> bool:
    """
    Log an API request to the database.

    Args:
        user_id: User ID
        api_key_id: API key ID
        request_id: Unique request ID
        endpoint: API endpoint (e.g., 'chat', 'completion')
        model: Model name
        provider: Provider name
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        cost: Cost of the request
        duration_ms: Duration in milliseconds
        status_code: HTTP status code
        response_summary: Summary of the response (truncated)

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_pg_connection()
        try:
            tokens_total = tokens_input + tokens_output

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO api_requests (
                        user_id, api_key_id, request_id, endpoint, model, provider,
                        tokens_input, tokens_output, tokens_total, cost, duration_ms, 
                        status_code, response_summary, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
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
                        response_summary,
                    ),
                )
                conn.commit()
                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error logging API request: {e}")
        return False
