"""
Database utility module for IndoxRouter.
Provides functions for connecting to the database and executing queries.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy Base
Base = declarative_base()

# Global connection pool
_pool = None

# SQLAlchemy engine and session
_engine = None
_Session = None


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        raise


def get_connection_pool() -> ThreadedConnectionPool:
    """Get or create the database connection pool."""
    global _pool

    if _pool is None:
        config = load_config()
        db_config = config["database"]

        try:
            _pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=db_config.get("pool_size", 5),
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 5432),
                user=db_config.get("user", "postgres"),
                password=db_config.get("password", ""),
                database=db_config.get("database", "indoxrouter"),
            )
            logger.info("Database connection pool created successfully")
        except psycopg2.Error as e:
            logger.error(f"Error creating database connection pool: {e}")
            raise

    return _pool


def get_connection():
    """Get a connection from the pool."""
    pool = get_connection_pool()
    try:
        return pool.getconn()
    except psycopg2.Error as e:
        logger.error(f"Error getting connection from pool: {e}")
        raise


def release_connection(conn):
    """Release a connection back to the pool."""
    pool = get_connection_pool()
    try:
        pool.putconn(conn)
    except psycopg2.Error as e:
        logger.error(f"Error releasing connection to pool: {e}")
        raise


def execute_query(
    query: str, params: Optional[Tuple] = None, fetch: bool = True
) -> Union[List[Dict[str, Any]], None]:
    """
    Execute a SQL query and return the results.

    Args:
        query: SQL query to execute
        params: Parameters for the query
        fetch: Whether to fetch and return results

    Returns:
        List of dictionaries representing rows if fetch is True, None otherwise
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)

            if fetch:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return None
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            release_connection(conn)


def execute_batch(query: str, params_list: List[Tuple]) -> None:
    """
    Execute a batch SQL query.

    Args:
        query: SQL query template
        params_list: List of parameter tuples for the query
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            execute_values(cursor, query, params_list)
            conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database batch error: {e}")
        raise
    finally:
        if conn:
            release_connection(conn)


def get_by_id(table: str, id_value: int) -> Optional[Dict[str, Any]]:
    """
    Get a record by ID.

    Args:
        table: Table name
        id_value: ID value to look up

    Returns:
        Dictionary representing the row or None if not found
    """
    query = f"SELECT * FROM {table} WHERE id = %s"
    results = execute_query(query, (id_value,))
    return results[0] if results else None


def insert(table: str, data: Dict[str, Any]) -> Optional[int]:
    """
    Insert a record and return the ID.

    Args:
        table: Table name
        data: Dictionary of column names and values

    Returns:
        ID of the inserted record or None on failure
    """
    columns = list(data.keys())
    values = [data[col] for col in columns]
    placeholders = [f"%s" for _ in columns]

    query = f"""
    INSERT INTO {table} ({', '.join(columns)})
    VALUES ({', '.join(placeholders)})
    RETURNING id
    """

    results = execute_query(query, tuple(values))
    return results[0]["id"] if results else None


def update(table: str, id_value: int, data: Dict[str, Any]) -> bool:
    """
    Update a record by ID.

    Args:
        table: Table name
        id_value: ID of the record to update
        data: Dictionary of column names and values to update

    Returns:
        True if successful, False otherwise
    """
    if not data:
        return False

    set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
    values = list(data.values()) + [id_value]

    query = f"""
    UPDATE {table}
    SET {set_clause}
    WHERE id = %s
    """

    execute_query(query, tuple(values), fetch=False)
    return True


def delete(table: str, id_value: int) -> bool:
    """
    Delete a record by ID.

    Args:
        table: Table name
        id_value: ID of the record to delete

    Returns:
        True if successful, False otherwise
    """
    query = f"DELETE FROM {table} WHERE id = %s"
    execute_query(query, (id_value,), fetch=False)
    return True


def close_all_connections():
    """Close all database connections in the pool."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("All database connections closed")


class DatabaseManager:
    """
    Database manager class for the dashboard.
    Provides high-level methods for interacting with the database.
    """

    def __init__(self):
        """Initialize the database manager."""
        self.config = load_config()
        # Ensure the connection pool is initialized
        get_connection_pool()

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.

        Args:
            username: Username
            password: Password

        Returns:
            User data if authentication is successful, None otherwise
        """
        # For the dashboard, we're using a simple authentication mechanism
        # In a real application, this would query the database
        if username == self.config.get("dashboard", {}).get(
            "username", "admin"
        ) and password == self.config.get("dashboard", {}).get("password", "admin"):
            return {
                "id": "admin",
                "name": "Administrator",
                "email": "admin@example.com",
                "is_admin": True,
            }
        return None

    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get all users.

        Returns:
            List of users
        """
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return execute_query(query)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User data if found, None otherwise
        """
        return get_by_id("users", user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.

        Args:
            email: User email

        Returns:
            User data if found, None otherwise
        """
        query = "SELECT * FROM users WHERE email = %s"
        results = execute_query(query, (email,))
        return results[0] if results else None

    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str = None,
        last_name: str = None,
        is_admin: bool = False,
    ) -> Optional[int]:
        """
        Create a new user.

        Args:
            email: User email
            password_hash: Hashed password
            first_name: First name
            last_name: Last name
            is_admin: Whether the user is an admin

        Returns:
            User ID if successful, None otherwise
        """
        data = {
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": is_admin,
            "is_active": True,
        }
        return insert("users", data)

    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Update a user.

        Args:
            user_id: User ID
            data: Data to update

        Returns:
            True if successful, False otherwise
        """
        return update("users", user_id, data)

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        return delete("users", user_id)

    def get_api_keys(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get API keys.

        Args:
            user_id: User ID to filter by (optional)

        Returns:
            List of API keys
        """
        if user_id:
            query = "SELECT * FROM api_keys WHERE user_id = %s ORDER BY created_at DESC"
            return execute_query(query, (user_id,))
        else:
            query = "SELECT * FROM api_keys ORDER BY created_at DESC"
            return execute_query(query)

    def get_api_key_by_id(self, key_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an API key by ID.

        Args:
            key_id: API key ID

        Returns:
            API key data if found, None otherwise
        """
        return get_by_id("api_keys", key_id)

    def create_api_key(
        self,
        user_id: int,
        key_name: str,
        key_prefix: str,
        key_hash: str,
        expires_at: Optional[datetime] = None,
    ) -> Optional[int]:
        """
        Create a new API key.

        Args:
            user_id: User ID
            key_name: Key name
            key_prefix: Key prefix
            key_hash: Hashed key
            expires_at: Expiry date (optional)

        Returns:
            API key ID if successful, None otherwise
        """
        data = {
            "user_id": user_id,
            "key_name": key_name,
            "key_prefix": key_prefix,
            "key_hash": key_hash,
            "is_active": True,
            "expires_at": expires_at,
        }
        return insert("api_keys", data)

    def update_api_key(self, key_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an API key.

        Args:
            key_id: API key ID
            data: Data to update

        Returns:
            True if successful, False otherwise
        """
        return update("api_keys", key_id, data)

    def delete_api_key(self, key_id: int) -> bool:
        """
        Delete an API key.

        Args:
            key_id: API key ID

        Returns:
            True if successful, False otherwise
        """
        return delete("api_keys", key_id)

    def get_request_logs(
        self, limit: int = 100, user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get request logs.

        Args:
            limit: Maximum number of logs to return
            user_id: User ID to filter by (optional)

        Returns:
            List of request logs
        """
        if user_id:
            query = """
            SELECT * FROM request_logs 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            return execute_query(query, (user_id, limit))
        else:
            query = "SELECT * FROM request_logs ORDER BY created_at DESC LIMIT %s"
            return execute_query(query, (limit,))

    def get_provider_stats(self) -> List[Dict[str, Any]]:
        """
        Get provider usage statistics.

        Returns:
            List of provider statistics
        """
        query = """
        SELECT 
            provider, 
            COUNT(*) as request_count,
            SUM(tokens_input) as total_input_tokens,
            SUM(tokens_output) as total_output_tokens,
            AVG(latency_ms) as avg_latency
        FROM request_logs
        GROUP BY provider
        ORDER BY request_count DESC
        """
        return execute_query(query)

    def get_provider_configs(self) -> List[Dict[str, Any]]:
        """
        Get provider configurations.

        Returns:
            List of provider configurations
        """
        query = "SELECT * FROM provider_configs WHERE is_active = TRUE"
        return execute_query(query)

    def update_provider_config(
        self, provider_name: str, config_json: Dict[str, Any]
    ) -> Optional[int]:
        """
        Update a provider configuration.

        Args:
            provider_name: Provider name
            config_json: Configuration JSON

        Returns:
            Provider config ID if successful, None otherwise
        """
        existing = self.get_provider_config(provider_name)
        if existing:
            data = {"config_json": config_json}
            update("provider_configs", existing["id"], data)
            return existing["id"]
        else:
            data = {
                "provider_name": provider_name,
                "config_json": config_json,
                "is_active": True,
            }
            return insert("provider_configs", data)

    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a provider configuration.

        Args:
            provider_name: Provider name

        Returns:
            Provider configuration if found, None otherwise
        """
        query = "SELECT * FROM provider_configs WHERE provider_name = %s"
        results = execute_query(query, (provider_name,))
        return results[0] if results else None

    def close(self):
        """Close all database connections."""
        close_all_connections()


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine

    if _engine is None:
        config = load_config()
        db_config = config["database"]

        if db_config.get("type", "sqlite") == "sqlite":
            db_path = db_config.get("path", "indoxrouter.db")
            db_url = f"sqlite:///{db_path}"
        else:
            host = db_config.get("host", "localhost")
            port = db_config.get("port", 5432)
            user = db_config.get("user", "postgres")
            password = db_config.get("password", "")
            database = db_config.get("database", "indoxrouter")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        _engine = create_engine(db_url, echo=False)

    return _engine


def get_session():
    """Get a SQLAlchemy session."""
    global _Session

    if _Session is None:
        engine = get_engine()
        _Session = scoped_session(sessionmaker(bind=engine))

    return _Session()
