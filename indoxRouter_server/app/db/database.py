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
from datetime import datetime, date

# MongoDB imports
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase

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

    # Only initialize MongoDB if PostgreSQL is successful
    if success and settings.MONGODB_URI:
        success = success and init_mongodb()

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


def validate_api_key(api_key: str) -> bool:
    """Validate an API key against PostgreSQL."""
    user = get_user_by_api_key(api_key)
    return user is not None and user.get("is_active", False)


# Keep the rest of your original PostgreSQL functions...
# However, you should update all your functions to use get_pg_connection and release_pg_connection

# MongoDB specific functions


def save_conversation(user_id: int, title: str, messages: List[Dict[str, Any]]) -> str:
    """
    Save a conversation to MongoDB.

    Args:
        user_id: The user ID
        title: Conversation title
        messages: List of message dictionaries

    Returns:
        The conversation ID
    """
    try:
        db = get_mongo_db()
        conversation = {
            "user_id": user_id,
            "title": title,
            "messages": messages,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = db.conversations.insert_one(conversation)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        return None


def get_user_conversations(
    user_id: int, limit: int = 20, skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get conversations for a user from MongoDB.

    Args:
        user_id: The user ID
        limit: Maximum number of conversations to return
        skip: Number of conversations to skip

    Returns:
        List of conversation dictionaries
    """
    try:
        db = get_mongo_db()
        cursor = (
            db.conversations.find({"user_id": user_id})
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return list(cursor)
    except Exception as e:
        logger.error(f"Error getting user conversations: {e}")
        return []


def save_embedding(
    user_id: int,
    text: str,
    embedding: List[float],
    model: str,
    metadata: Dict[str, Any] = None,
) -> str:
    """
    Save an embedding to MongoDB.

    Args:
        user_id: The user ID
        text: The original text
        embedding: Vector representation
        model: Model used for embedding
        metadata: Additional metadata

    Returns:
        The embedding ID
    """
    try:
        db = get_mongo_db()
        embedding_doc = {
            "user_id": user_id,
            "text": text,
            "embedding": embedding,
            "model": model,
            "dimensions": len(embedding),
            "created_at": datetime.now(),
            "metadata": metadata or {},
        }

        result = db.embeddings.insert_one(embedding_doc)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving embedding: {e}")
        return None


def cache_model_output(
    request_hash: str,
    provider: str,
    model: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    ttl_days: int = 7,
) -> bool:
    """
    Cache a model output in MongoDB.

    Args:
        request_hash: Hash of the request parameters
        provider: Model provider
        model: Model name
        input_data: Input request data
        output_data: Output response data
        ttl_days: Time to live in days

    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_mongo_db()
        now = datetime.now()
        ttl = datetime.now()
        ttl = ttl.replace(day=ttl.day + ttl_days)

        cache_doc = {
            "request_hash": request_hash,
            "provider": provider,
            "model": model,
            "input": input_data,
            "output": output_data,
            "created_at": now,
            "ttl": ttl,
        }

        # Use upsert to update if exists or insert if not
        result = db.model_outputs.update_one(
            {"request_hash": request_hash}, {"$set": cache_doc}, upsert=True
        )

        return result.acknowledged
    except Exception as e:
        logger.error(f"Error caching model output: {e}")
        return False


def get_cached_model_output(request_hash: str) -> Optional[Dict[str, Any]]:
    """
    Get a cached model output from MongoDB.

    Args:
        request_hash: Hash of the request parameters

    Returns:
        The cached output or None
    """
    try:
        db = get_mongo_db()
        result = db.model_outputs.find_one({"request_hash": request_hash})
        return result
    except Exception as e:
        logger.error(f"Error getting cached model output: {e}")
        return None


# Note: Some existing functions are not shown here to keep the edit shorter
# You would need to retain and update all your other PostgreSQL functions
