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
import traceback

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
        # Log the MongoDB URI being used (with password removed for security)
        uri = settings.MONGODB_URI
        if uri and ":" in uri and "@" in uri:
            # Mask the password in the log
            masked_uri = uri.split(":")
            masked_uri[2] = "****" + masked_uri[2].split("@", 1)[1]
            logger.info(f"Connecting to MongoDB with URI: {':'.join(masked_uri)}")
        else:
            logger.warning(f"MongoDB URI not properly formatted: {uri}")

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
        logger.error(
            f"MongoDB connection details - Host: {settings.MONGO_HOST}, DB: {settings.MONGODB_DATABASE}"
        )
        logger.debug(traceback.format_exc())
        return False


def create_mongo_indexes():
    """Create MongoDB indexes."""
    try:
        if mongo_db is not None:
            # Create indexes for model_usage collection
            mongo_db.model_usage.create_index([("user_id", 1)])
            mongo_db.model_usage.create_index([("provider", 1)])
            mongo_db.model_usage.create_index([("model", 1)])
            mongo_db.model_usage.create_index([("timestamp", -1)])
            mongo_db.model_usage.create_index([("date", 1)])
            mongo_db.model_usage.create_index([("request_id", 1)], unique=True)

            # Add indexes for new fields
            mongo_db.model_usage.create_index([("session_id", 1)])
            mongo_db.model_usage.create_index([("client_info.ip", 1)])
            mongo_db.model_usage.create_index([("request.endpoint", 1)])
            mongo_db.model_usage.create_index([("cache.cache_hit", 1)])

            # Compound indexes for analytics
            mongo_db.model_usage.create_index([("user_id", 1), ("date", 1)])
            mongo_db.model_usage.create_index(
                [("user_id", 1), ("provider", 1), ("model", 1)]
            )
            mongo_db.model_usage.create_index([("user_id", 1), ("session_id", 1)])

            # Create indexes for model_cache collection
            mongo_db.model_cache.create_index([("request_hash", 1)], unique=True)
            mongo_db.model_cache.create_index([("expires_at", 1)], expireAfterSeconds=0)

            # Create indexes for models collection
            mongo_db.models.create_index([("provider", 1), ("name", 1)], unique=True)

            # Create indexes for conversations collection
            mongo_db.conversations.create_index([("user_id", 1)])
            mongo_db.conversations.create_index([("created_at", -1)])

            # Create indexes for embeddings collection
            mongo_db.embeddings.create_index([("user_id", 1)])
            mongo_db.embeddings.create_index([("model", 1)])

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
                    SELECT id, username, email, first_name, last_name, is_active, credits, account_tier, 
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


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username from PostgreSQL."""
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, username, email, first_name, last_name, password, is_active, credits, account_tier, 
                           created_at, last_login_at
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )
                user = cur.fetchone()
                return dict(user) if user else None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email from PostgreSQL."""
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, username, email, first_name, last_name, password, is_active, credits, account_tier, 
                           created_at, last_login_at
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )
                user = cur.fetchone()
                return dict(user) if user else None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


def create_user(
    username: str,
    email: str,
    hashed_password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new user in PostgreSQL."""
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if username or email already exists
                cur.execute(
                    """
                    SELECT id FROM users WHERE username = %s OR email = %s
                    """,
                    (username, email),
                )
                if cur.fetchone():
                    return None  # User already exists

                # Insert new user
                cur.execute(
                    """
                    INSERT INTO users (username, email, password, first_name, last_name, credits, is_active, account_tier)
                    VALUES (%s, %s, %s, %s, %s, 0, TRUE, 'free')
                    RETURNING id, username, email, first_name, last_name, is_active, credits, account_tier, created_at
                    """,
                    (username, email, hashed_password, first_name, last_name),
                )
                conn.commit()
                new_user = cur.fetchone()
                return dict(new_user) if new_user else None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


def update_last_login(user_id: int) -> bool:
    """Update the last login timestamp for a user."""
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET last_login_at = NOW()
                    WHERE id = %s
                    """,
                    (user_id,),
                )
                conn.commit()
                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        return False


def create_or_update_google_user(
    email: str, google_id: str, name: str
) -> Optional[Dict[str, Any]]:
    """Create or update a user authenticated with Google."""
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if user with this email exists
                cur.execute(
                    """
                    SELECT id, username, email, is_active, credits, account_tier, created_at
                    FROM users 
                    WHERE email = %s
                    """,
                    (email,),
                )
                user = cur.fetchone()

                if user:
                    # User exists, update google_id if needed
                    cur.execute(
                        """
                        UPDATE users
                        SET google_id = %s, last_login_at = NOW()
                        WHERE id = %s
                        """,
                        (google_id, user["id"]),
                    )
                    conn.commit()
                    return dict(user)

                # Create new user
                username = email.split("@")[0]
                # Make sure username is unique
                cur.execute(
                    """
                    SELECT COUNT(*) as count FROM users WHERE username LIKE %s
                    """,
                    (f"{username}%",),
                )
                count = cur.fetchone()["count"]
                if count > 0:
                    username = f"{username}{count}"

                cur.execute(
                    """
                    INSERT INTO users (username, email, google_id, credits, is_active, account_tier)
                    VALUES (%s, %s, %s, 0, TRUE, 'free')
                    RETURNING id, username, email, is_active, credits, account_tier, created_at
                    """,
                    (username, email, google_id),
                )
                conn.commit()
                new_user = cur.fetchone()
                return dict(new_user) if new_user else None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error creating/updating Google user: {e}")
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
            logger.debug("MongoDB not initialized for saving conversations")
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
            logger.debug("MongoDB not initialized for retrieving conversations")
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
            logger.debug("MongoDB not initialized for retrieving conversation")
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
            logger.debug("MongoDB not initialized for saving embeddings")
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
            logger.debug("MongoDB not initialized for retrieving embedding")
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
            logger.debug("MongoDB not initialized for saving model info")
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
            logger.debug("MongoDB not initialized for retrieving models")
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
            logger.debug("MongoDB not initialized for retrieving model")
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
    session_id: str = None,
    request_data: Dict[str, Any] = None,
    response_data: Dict[str, Any] = None,
    client_info: Dict[str, Any] = None,
    performance_metrics: Dict[str, Any] = None,
    content_analysis: Dict[str, Any] = None,
) -> bool:
    """
    Log detailed model usage to MongoDB.

    Args:
        user_id: User ID
        provider: Provider name (e.g., "openai")
        model: Model name (e.g., "openai/gpt-4o-mini")
        tokens_prompt: Number of prompt tokens
        tokens_completion: Number of completion tokens
        cost: Cost of the request
        latency: Total request latency
        request_id: Unique request ID
        session_id: Session ID for grouping related requests
        request_data: Request details including endpoint, messages, parameters
        response_data: Response details including status code, content length, finish reason
        client_info: Client information like IP, user agent, device type
        performance_metrics: Detailed timing metrics for different stages of request processing
        content_analysis: Content analysis results like topics, languages, sentiment

    Returns:
        True if logging was successful, False otherwise
    """
    try:
        if mongo_db is None:
            logger.debug("MongoDB not initialized for logging model usage")
            return False

        # Create timestamp
        current_time = datetime.now()

        # Build the base usage document
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
            "timestamp": current_time,
            "date": current_time.date().isoformat(),
        }

        # Add session ID if provided
        if session_id:
            usage_doc["session_id"] = session_id

        # Add request data if provided
        if request_data:
            # Sanitize request data - remove any sensitive information
            if "messages" in request_data and isinstance(
                request_data["messages"], list
            ):
                # Make a copy to avoid modifying the original
                sanitized_messages = []
                for msg in request_data["messages"]:
                    # Include role and a truncated content
                    if isinstance(msg, dict):
                        sanitized_msg = {"role": msg.get("role", "user")}
                        content = msg.get("content", "")
                        # Truncate content if it's too long
                        if len(content) > 1000:
                            sanitized_msg["content"] = content[:1000] + "..."
                            sanitized_msg["content_truncated"] = True
                        else:
                            sanitized_msg["content"] = content
                        sanitized_messages.append(sanitized_msg)

                request_data = {**request_data, "messages": sanitized_messages}

            usage_doc["request"] = request_data

        # Add response data if provided
        if response_data:
            usage_doc["response"] = response_data

        # Add client information if provided
        if client_info:
            usage_doc["client_info"] = client_info

        # Add performance metrics if provided
        if performance_metrics:
            usage_doc["performance"] = performance_metrics

        # Add content analysis if provided
        if content_analysis:
            usage_doc["content_analysis"] = content_analysis

        # Add cache information (default to no cache hit)
        usage_doc["cache"] = {"cache_hit": False, "cached_id": None}

        # Insert into MongoDB
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
            logger.debug("MongoDB not initialized for retrieving user model usage")
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


def get_usage_analytics(
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_by: str = "date",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    session_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    include_content: bool = False,
) -> List[Dict[str, Any]]:
    """
    Get advanced usage analytics with flexible grouping and filtering.

    Args:
        user_id: Optional user ID to filter by
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        group_by: Field to group by (date, model, provider, endpoint, session_id)
        provider: Optional provider to filter by
        model: Optional model to filter by
        session_id: Optional session ID to filter by
        endpoint: Optional endpoint to filter by (chat, completion, embedding, image)
        include_content: Whether to include request/response content in results

    Returns:
        List of aggregated usage statistics
    """
    try:
        if mongo_db is None:
            logger.debug("MongoDB not initialized for advanced analytics")
            return []

        # Build the match filter
        match_filter = {}

        if user_id:
            match_filter["user_id"] = user_id

        if start_date and end_date:
            match_filter["date"] = {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat(),
            }

        if provider:
            match_filter["provider"] = provider

        if model:
            match_filter["model"] = model

        if session_id:
            match_filter["session_id"] = session_id

        if endpoint:
            match_filter["request.endpoint"] = endpoint

        # Define group by field
        group_fields = {
            "date": "$date",
            "model": "$model",
            "provider": "$provider",
            "endpoint": "$request.endpoint",
            "session_id": "$session_id",
            "client_ip": "$client_info.ip",
        }

        group_by_field = group_fields.get(group_by, "$date")

        # Build the aggregation pipeline
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": group_by_field,
                    "count": {"$sum": 1},
                    "total_cost": {"$sum": "$cost"},
                    "total_tokens_prompt": {"$sum": "$tokens_prompt"},
                    "total_tokens_completion": {"$sum": "$tokens_completion"},
                    "total_tokens": {"$sum": "$tokens_total"},
                    "avg_latency": {"$avg": "$latency"},
                    "min_latency": {"$min": "$latency"},
                    "max_latency": {"$max": "$latency"},
                    "first_timestamp": {"$min": "$timestamp"},
                    "last_timestamp": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"first_timestamp": 1}},
        ]

        # If content is requested, include sample requests/responses
        if include_content and not group_by:
            # For non-grouped queries, we can include the full content
            projection = {
                "_id": 0,
                "user_id": 1,
                "provider": 1,
                "model": 1,
                "tokens_total": 1,
                "cost": 1,
                "latency": 1,
                "timestamp": 1,
                "request": 1,
                "response": 1,
                "client_info": 1,
                "performance": 1,
                "content_analysis": 1,
            }
            results = list(mongo_db.model_usage.find(match_filter, projection))
        else:
            # For grouped queries, run the aggregation
            results = list(mongo_db.model_usage.aggregate(pipeline))

            # Format the results
            for item in results:
                item["group_value"] = item.pop("_id")

        return results
    except Exception as e:
        logger.error(f"Error getting usage analytics: {e}")
        return []


def get_user_usage_stats(
    user_id: int, start_date: date = None, end_date: date = None
) -> Dict[str, Any]:
    """
    Get user usage statistics from both PostgreSQL and MongoDB.

    Args:
        user_id: The user ID.
        start_date: Optional start date for filtering.
        end_date: Optional end date for filtering.

    Returns:
        A dictionary with usage statistics.
    """
    try:
        result = {
            "total_requests": 0,
            "total_cost": 0,
            "remaining_credits": 0,
            "endpoints": {},
            "providers": {},
            "models": {},
            "daily_usage": [],
        }

        # Get user current credits from PostgreSQL
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get user remaining credits
                cur.execute(
                    """
                    SELECT credits FROM users WHERE id = %s
                    """,
                    (user_id,),
                )
                user_data = cur.fetchone()
                if user_data:
                    result["remaining_credits"] = float(user_data["credits"])

                # Get aggregated usage from daily summary
                date_filter = ""
                params = [user_id]

                if start_date and end_date:
                    date_filter = "AND date >= %s AND date <= %s"
                    params.extend([start_date, end_date])

                cur.execute(
                    f"""
                    SELECT 
                        SUM(total_requests) as total_requests,
                        SUM(total_tokens_input) as total_tokens_input,
                        SUM(total_tokens_output) as total_tokens_output,
                        SUM(total_tokens) as total_tokens,
                        SUM(total_cost) as total_cost
                    FROM usage_daily_summary
                    WHERE user_id = %s {date_filter}
                    """,
                    params,
                )
                summary = cur.fetchone()

                if summary:
                    result["total_requests"] = summary["total_requests"] or 0
                    result["total_cost"] = float(summary["total_cost"] or 0)
                    result["total_tokens"] = {
                        "input": summary["total_tokens_input"] or 0,
                        "output": summary["total_tokens_output"] or 0,
                        "total": summary["total_tokens"] or 0,
                    }

                # Get daily usage data
                cur.execute(
                    f"""
                    SELECT 
                        date,
                        total_requests,
                        total_tokens_input,
                        total_tokens_output,
                        total_tokens,
                        total_cost
                    FROM usage_daily_summary
                    WHERE user_id = %s {date_filter}
                    ORDER BY date DESC
                    """,
                    params,
                )
                daily_data = cur.fetchall()

                if daily_data:
                    result["daily_usage"] = [
                        {
                            "date": item["date"].isoformat(),
                            "requests": item["total_requests"],
                            "tokens": {
                                "input": item["total_tokens_input"],
                                "output": item["total_tokens_output"],
                                "total": item["total_tokens"],
                            },
                            "cost": float(item["total_cost"]),
                        }
                        for item in daily_data
                    ]
        finally:
            release_pg_connection(conn)

        # Get detailed usage from MongoDB
        if mongo_db is not None:
            # Build MongoDB query
            match_filter = {"user_id": user_id}
            if start_date and end_date:
                match_filter["date"] = {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat(),
                }

            # Get endpoint stats
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": "$request.endpoint",
                        "requests": {"$sum": 1},
                        "cost": {"$sum": "$cost"},
                        "tokens_input": {"$sum": "$tokens_prompt"},
                        "tokens_output": {"$sum": "$tokens_completion"},
                    }
                },
            ]

            endpoint_stats = list(mongo_db.model_usage.aggregate(pipeline))

            for stat in endpoint_stats:
                endpoint = stat["_id"] or "unknown"
                result["endpoints"][endpoint] = {
                    "requests": stat["requests"],
                    "cost": round(stat["cost"], 6),
                    "tokens": {
                        "input": stat["tokens_input"],
                        "output": stat["tokens_output"],
                        "total": stat["tokens_input"] + stat["tokens_output"],
                    },
                }

            # Get provider stats
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": "$provider",
                        "requests": {"$sum": 1},
                        "cost": {"$sum": "$cost"},
                        "tokens_input": {"$sum": "$tokens_prompt"},
                        "tokens_output": {"$sum": "$tokens_completion"},
                    }
                },
            ]

            provider_stats = list(mongo_db.model_usage.aggregate(pipeline))

            for stat in provider_stats:
                provider = stat["_id"] or "unknown"
                result["providers"][provider] = {
                    "requests": stat["requests"],
                    "cost": round(stat["cost"], 6),
                    "tokens": {
                        "input": stat["tokens_input"],
                        "output": stat["tokens_output"],
                        "total": stat["tokens_input"] + stat["tokens_output"],
                    },
                }

            # Get model stats
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": {"provider": "$provider", "model": "$model"},
                        "requests": {"$sum": 1},
                        "cost": {"$sum": "$cost"},
                        "tokens_input": {"$sum": "$tokens_prompt"},
                        "tokens_output": {"$sum": "$tokens_completion"},
                    }
                },
            ]

            model_stats = list(mongo_db.model_usage.aggregate(pipeline))

            for stat in model_stats:
                provider = stat["_id"]["provider"] or "unknown"
                model = stat["_id"]["model"] or "unknown"
                model_key = f"{provider}/{model}"

                result["models"][model_key] = {
                    "provider": provider,
                    "model": model,
                    "requests": stat["requests"],
                    "cost": round(stat["cost"], 6),
                    "tokens": {
                        "input": stat["tokens_input"],
                        "output": stat["tokens_output"],
                        "total": stat["tokens_input"] + stat["tokens_output"],
                    },
                }

        return result
    except Exception as e:
        logger.error(f"Error getting user usage stats: {e}")
        logger.error(traceback.format_exc())
        return {
            "total_requests": 0,
            "total_cost": 0,
            "remaining_credits": 0,
            "endpoints": {},
            "providers": {},
            "models": {},
            "daily_usage": [],
        }


def create_api_key(user_id: int, name: str = "API Key") -> Optional[Dict[str, Any]]:
    """
    Create a new API key for a user with one month expiration.

    Args:
        user_id: The user ID.
        name: A name/description for the API key.

    Returns:
        Dictionary containing the API key info if successful, None otherwise.
    """
    try:
        # Generate a new API key with prefix "indox-"
        import secrets
        import string
        import uuid

        # Generate a random string for the key
        random_part = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        api_key = f"indox-{random_part}"

        # Set expiration to one month from now
        expires_at = datetime.now() + timedelta(days=30)

        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO api_keys
                    (user_id, api_key, name, is_active, created_at, expires_at)
                    VALUES (%s, %s, %s, TRUE, NOW(), %s)
                    RETURNING id, api_key, name, created_at, expires_at
                    """,
                    (user_id, api_key, name, expires_at),
                )

                conn.commit()
                api_key_data = cur.fetchone()

                if api_key_data:
                    return dict(api_key_data)
                return None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        return None


def get_user_api_keys(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all API keys for a user.

    Args:
        user_id: The user ID.

    Returns:
        List of API keys.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, api_key, name, is_active, created_at, 
                           expires_at, last_used_at
                    FROM api_keys
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )

                keys = cur.fetchall()
                return [dict(key) for key in keys] if keys else []
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        return []


def revoke_api_key(user_id: int, api_key_id: int) -> bool:
    """
    Revoke an API key.

    Args:
        user_id: The user ID.
        api_key_id: The API key ID.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # Verify the API key belongs to the user
                cur.execute(
                    """
                    SELECT id
                    FROM api_keys
                    WHERE id = %s AND user_id = %s
                    """,
                    (api_key_id, user_id),
                )

                if not cur.fetchone():
                    # Key doesn't exist or doesn't belong to the user
                    return False

                cur.execute(
                    """
                    UPDATE api_keys
                    SET is_active = FALSE
                    WHERE id = %s
                    """,
                    (api_key_id,),
                )

                conn.commit()
                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        return False


def enable_api_key(user_id: int, api_key_id: int) -> bool:
    """
    Enable a previously revoked API key.

    Args:
        user_id: The user ID.
        api_key_id: The API key ID.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # Verify the API key belongs to the user
                cur.execute(
                    """
                    SELECT id
                    FROM api_keys
                    WHERE id = %s AND user_id = %s
                    """,
                    (api_key_id, user_id),
                )

                if not cur.fetchone():
                    # Key doesn't exist or doesn't belong to the user
                    return False

                cur.execute(
                    """
                    UPDATE api_keys
                    SET is_active = TRUE
                    WHERE id = %s
                    """,
                    (api_key_id,),
                )

                conn.commit()
                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error enabling API key: {e}")
        return False


def delete_api_key(user_id: int, api_key_id: int) -> bool:
    """
    Permanently delete an API key.

    Args:
        user_id: The user ID.
        api_key_id: The API key ID.

    Returns:
        True if successful, False otherwise.
    """
    logger.info(
        f"Attempting to delete API key: api_key_id={api_key_id}, user_id={user_id}"
    )
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # First, check if the API key exists at all
                cur.execute(
                    """
                    SELECT id, user_id
                    FROM api_keys
                    WHERE id = %s
                    """,
                    (api_key_id,),
                )
                key_result = cur.fetchone()

                if not key_result:
                    logger.warning(f"API key not found: api_key_id={api_key_id}")
                    return False

                actual_user_id = key_result[1]
                if int(actual_user_id) != int(user_id):
                    logger.warning(
                        f"API key belongs to different user: api_key_id={api_key_id}, belongs_to={actual_user_id}, requested_by={user_id}"
                    )
                    return False

                # Proceed with deletion
                cur.execute(
                    """
                    DELETE FROM api_keys
                    WHERE id = %s
                    RETURNING id
                    """,
                    (api_key_id,),
                )

                deleted = cur.fetchone()
                conn.commit()

                if deleted:
                    logger.info(
                        f"Successfully deleted API key: api_key_id={api_key_id}, user_id={user_id}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to delete API key: api_key_id={api_key_id}, user_id={user_id}"
                    )
                    return False
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(
            f"Error deleting API key: api_key_id={api_key_id}, user_id={user_id}, error={e}"
        )
        return False


def add_user_credits(
    user_id: int,
    amount: float,
    payment_method: str = "credit_card",
    transaction_id: str = None,
    reference_id: str = None,
) -> Optional[Dict[str, Any]]:
    """
    Add credits to a user's account and record the transaction.

    Args:
        user_id: The user ID.
        amount: The amount of credits to add.
        payment_method: The payment method used.
        transaction_id: Optional external transaction ID.
        reference_id: Optional reference ID.

    Returns:
        Dictionary containing the transaction info if successful, None otherwise.
    """
    try:
        if amount < 10:
            logger.error(f"Credit amount must be at least 10, got {amount}")
            return None

        # Generate a transaction ID if not provided
        if not transaction_id:
            import uuid

            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"

        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Start transaction
                conn.autocommit = False

                # Update user credits
                cur.execute(
                    """
                    UPDATE users
                    SET credits = credits + %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, username, email, credits
                    """,
                    (amount, user_id),
                )

                user = cur.fetchone()
                if not user:
                    conn.rollback()
                    return None

                # Record the transaction
                cur.execute(
                    """
                    INSERT INTO billing_transactions
                    (user_id, transaction_id, amount, currency, transaction_type, status, payment_method, description, reference_id)
                    VALUES (%s, %s, %s, 'USD', 'credit_purchase', 'completed', %s, %s, %s)
                    RETURNING id, transaction_id, amount, created_at
                    """,
                    (
                        user_id,
                        transaction_id,
                        amount,
                        payment_method,
                        f"Purchase of {amount} credits",
                        reference_id,
                    ),
                )

                transaction = cur.fetchone()

                # Commit the transaction
                conn.commit()

                # Combine user and transaction info
                result = {
                    "user_id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "credits_added": amount,
                    "total_credits": user["credits"],
                    "transaction_id": transaction["transaction_id"],
                    "created_at": transaction["created_at"],
                }

                return result
        finally:
            conn.autocommit = True
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error adding credits to user: {e}")
        return None


def get_user_transactions(
    user_id: Optional[int], limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get transactions for a user or all users if user_id is None.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if user_id is not None:
                    cur.execute(
                        """
                        SELECT t.*, u.username, u.email
                        FROM billing_transactions t
                        JOIN users u ON t.user_id = u.id
                        WHERE t.user_id = %s
                        ORDER BY t.created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, limit, offset),
                    )
                else:
                    cur.execute(
                        """
                        SELECT t.*, u.username, u.email
                        FROM billing_transactions t
                        JOIN users u ON t.user_id = u.id
                        ORDER BY t.created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (limit, offset),
                    )
                transactions = cur.fetchall()
                return [dict(t) for t in transactions]
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return []


def get_all_users(
    skip: int = 0, limit: int = 100, search: str = None
) -> List[Dict[str, Any]]:
    """
    Get all users with pagination and optional search.

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        search: Optional search term for username or email

    Returns:
        List of user objects
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT id, username, email, first_name, last_name, 
                           is_active, credits, account_tier, created_at, last_login_at
                    FROM users
                """
                params = []

                # Add search condition if provided
                if search:
                    query += " WHERE username ILIKE %s OR email ILIKE %s"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])

                    # Add search on first/last name if they exist
                    query += " OR first_name ILIKE %s OR last_name ILIKE %s"
                    params.extend([search_pattern, search_pattern])

                # Add pagination
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, skip])

                cur.execute(query, params)
                users = cur.fetchall()
                return [dict(user) for user in users] if users else []
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []


def update_user_data(
    user_id: int, update_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update user data.

    Args:
        user_id: The user ID
        update_data: Dictionary with fields to update

    Returns:
        Updated user data if successful, None otherwise
    """
    try:
        if not update_data:
            return None

        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build SET clause dynamically based on update_data
                set_clauses = []
                params = []

                for key, value in update_data.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                # Always update the updated_at timestamp
                set_clauses.append("updated_at = NOW()")

                # Finalize query
                query = f"""
                    UPDATE users 
                    SET {', '.join(set_clauses)}
                    WHERE id = %s
                    RETURNING id, username, email, first_name, last_name,
                              is_active, credits, account_tier, created_at, updated_at, last_login_at
                """
                params.append(user_id)

                cur.execute(query, params)
                conn.commit()
                updated_user = cur.fetchone()
                return dict(updated_user) if updated_user else None
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error updating user data: {e}")
        return None


def delete_user(user_id: int) -> bool:
    """
    Delete a user.

    Args:
        user_id: The user ID

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                # Check if user exists
                cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                if not cur.fetchone():
                    return False

                # Delete user (cascade will handle related records due to foreign keys)
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()

                return True
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False


def get_system_stats() -> Dict[str, Any]:
    """
    Get system-wide statistics.

    Returns:
        Dictionary with system statistics
    """
    try:
        stats = {
            "users": {
                "total": 0,
                "active": 0,
                "new_last_30_days": 0,
            },
            "api_keys": {
                "total": 0,
                "active": 0,
            },
            "usage": {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "requests_today": 0,
                "tokens_today": 0,
                "cost_today": 0,
            },
            "providers": {},
            "models": {},
        }

        # PostgreSQL statistics
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # User statistics
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total_users,
                        SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_users,
                        SUM(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END) as new_users
                    FROM users
                """
                )
                user_stats = cur.fetchone()

                if user_stats:
                    stats["users"]["total"] = user_stats["total_users"]
                    stats["users"]["active"] = user_stats["active_users"]
                    stats["users"]["new_last_30_days"] = user_stats["new_users"]

                # API key statistics
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total_keys,
                        SUM(CASE WHEN is_active AND (expires_at IS NULL OR expires_at > NOW()) THEN 1 ELSE 0 END) as active_keys
                    FROM api_keys
                """
                )
                key_stats = cur.fetchone()

                if key_stats:
                    stats["api_keys"]["total"] = key_stats["total_keys"]
                    stats["api_keys"]["active"] = key_stats["active_keys"]

                # Total usage statistics
                cur.execute(
                    """
                    SELECT
                        SUM(total_requests) as total_requests,
                        SUM(total_tokens) as total_tokens,
                        SUM(total_cost) as total_cost
                    FROM usage_daily_summary
                """
                )
                usage_stats = cur.fetchone()

                if usage_stats:
                    stats["usage"]["total_requests"] = (
                        usage_stats["total_requests"] or 0
                    )
                    stats["usage"]["total_tokens"] = usage_stats["total_tokens"] or 0
                    stats["usage"]["total_cost"] = float(usage_stats["total_cost"] or 0)

                # Today's usage statistics
                cur.execute(
                    """
                    SELECT
                        SUM(total_requests) as requests_today,
                        SUM(total_tokens) as tokens_today,
                        SUM(total_cost) as cost_today
                    FROM usage_daily_summary
                    WHERE date = CURRENT_DATE
                """
                )
                today_stats = cur.fetchone()

                if today_stats:
                    stats["usage"]["requests_today"] = (
                        today_stats["requests_today"] or 0
                    )
                    stats["usage"]["tokens_today"] = today_stats["tokens_today"] or 0
                    stats["usage"]["cost_today"] = float(today_stats["cost_today"] or 0)
        finally:
            release_pg_connection(conn)

        # MongoDB statistics (if available)
        if mongo_db is not None:
            # Provider statistics
            provider_stats = list(
                mongo_db.model_usage.aggregate(
                    [
                        {
                            "$group": {
                                "_id": "$provider",
                                "requests": {"$sum": 1},
                                "tokens": {"$sum": "$tokens_total"},
                                "cost": {"$sum": "$cost"},
                            }
                        }
                    ]
                )
            )

            for item in provider_stats:
                provider = item["_id"] or "unknown"
                stats["providers"][provider] = {
                    "requests": item["requests"],
                    "tokens": item["tokens"],
                    "cost": item["cost"],
                }

            # Model statistics
            model_stats = list(
                mongo_db.model_usage.aggregate(
                    [
                        {
                            "$group": {
                                "_id": {"provider": "$provider", "model": "$model"},
                                "requests": {"$sum": 1},
                                "tokens": {"$sum": "$tokens_total"},
                                "cost": {"$sum": "$cost"},
                            }
                        },
                        {"$sort": {"requests": -1}},
                        {"$limit": 10},
                    ]
                )
            )

            for item in model_stats:
                provider = item["_id"]["provider"] or "unknown"
                model = item["_id"]["model"] or "unknown"
                model_key = f"{provider}/{model}"

                stats["models"][model_key] = {
                    "provider": provider,
                    "model": model,
                    "requests": item["requests"],
                    "tokens": item["tokens"],
                    "cost": item["cost"],
                }

        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            "users": {"total": 0, "active": 0, "new_last_30_days": 0},
            "api_keys": {"total": 0, "active": 0},
            "usage": {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "requests_today": 0,
                "tokens_today": 0,
                "cost_today": 0,
            },
            "providers": {},
            "models": {},
        }


def get_all_api_keys(
    limit: int = 100, offset: int = 0, search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all API keys with associated user information.

    Args:
        limit: Maximum number of API keys to return
        offset: Offset to start from
        search: Optional search term to filter by username

    Returns:
        List of API keys with user information
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT k.id, k.api_key, k.name, k.is_active, k.created_at, k.expires_at, k.last_used_at,
                           u.id as user_id, u.username, u.email,
                           (SELECT COUNT(*) FROM api_requests WHERE api_key_id = k.id) as request_count
                    FROM api_keys k
                    JOIN users u ON k.user_id = u.id
                """

                params = []

                if search:
                    query += " WHERE u.username ILIKE %s OR u.email ILIKE %s"
                    search_term = f"%{search}%"
                    params.extend([search_term, search_term])

                query += " ORDER BY k.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cur.execute(query, params)
                api_keys = cur.fetchall()

                # Format the response
                result = []
                for key in api_keys:
                    result.append(
                        {
                            "id": key["id"],
                            "key": key["api_key"],  # Full key for admin view
                            "name": key["name"],
                            "active": key["is_active"],
                            "created_at": key["created_at"],
                            "expires_at": key["expires_at"],
                            "last_used_at": key["last_used_at"],
                            "request_count": key["request_count"],
                            "user": {
                                "id": key["user_id"],
                                "username": key["username"],
                                "email": key["email"],
                            },
                        }
                    )

                return result
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting all API keys: {e}")
        return []


def get_api_key_request_count(api_key_id: int) -> int:
    """
    Get the number of requests made with a specific API key.

    Args:
        api_key_id: The API key ID.

    Returns:
        The number of requests made with the API key.
    """
    try:
        conn = get_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) as request_count
                    FROM api_requests
                    WHERE api_key_id = %s
                    """,
                    (api_key_id,),
                )
                result = cur.fetchone()
                return result[0] if result else 0
        finally:
            release_pg_connection(conn)
    except Exception as e:
        logger.error(f"Error getting API key request count: {e}")
        return 0
