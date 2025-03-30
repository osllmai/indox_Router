"""
Database operations for the IndoxRouter dashboard.
"""

import os
import logging
import uuid
import bcrypt
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def close_connection(conn):
    """Close a database connection."""
    if conn:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, username, email, is_active
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )
                user = cur.fetchone()
                return user
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in get_user_by_email: {e}")
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, username, email, is_active
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )
                user = cur.fetchone()
                return user
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in get_user_by_username: {e}")
        return None


def create_user(username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
    """Create a new user."""
    try:
        # Check if user already exists
        if get_user_by_email(email) or get_user_by_username(username):
            return None

        # Hash the password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Create user
                cur.execute(
                    """
                    INSERT INTO users (username, email, is_active)
                    VALUES (%s, %s, TRUE)
                    RETURNING id, username, email, is_active
                    """,
                    (username, email),
                )
                user = cur.fetchone()

                # Add password to user_credentials table (create this table if it doesn't exist)
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_credentials (
                        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cur.execute(
                    """
                    INSERT INTO user_credentials (user_id, password_hash)
                    VALUES (%s, %s)
                    """,
                    (user["id"], hashed_password),
                )

                # Add initial credits to the user
                cur.execute(
                    """
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS credits FLOAT DEFAULT 10.0
                    """
                )

                cur.execute(
                    """
                    UPDATE users SET credits = 10.0 WHERE id = %s
                    """,
                    (user["id"],),
                )

                return user
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in create_user: {e}")
        return None


def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify user credentials."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get user
                cur.execute(
                    """
                    SELECT u.id, u.username, u.email, u.is_active, u.credits, c.password_hash
                    FROM users u
                    JOIN user_credentials c ON u.id = c.user_id
                    WHERE u.username = %s AND u.is_active = TRUE
                    """,
                    (username,),
                )
                user = cur.fetchone()

                if not user:
                    return None

                # Verify password
                if bcrypt.checkpw(
                    password.encode("utf-8"), user["password_hash"].encode("utf-8")
                ):
                    # Remove password_hash from returned user
                    del user["password_hash"]
                    return user

                return None
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in verify_user: {e}")
        return None


def get_user_api_keys(user_id: int) -> List[Dict[str, Any]]:
    """Get all API keys for a user."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, api_key, name, is_active, created_at, expires_at
                    FROM api_keys
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                keys = cur.fetchall()
                return keys
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in get_user_api_keys: {e}")
        return []


def create_api_key(user_id: int, name: str) -> Optional[Dict[str, Any]]:
    """Create a new API key for a user."""
    try:
        conn = get_connection()
        try:
            # Generate a unique API key
            api_key = f"ir-{uuid.uuid4()}"

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO api_keys (user_id, api_key, name, is_active)
                    VALUES (%s, %s, %s, TRUE)
                    RETURNING id, api_key, name, is_active, created_at, expires_at
                    """,
                    (user_id, api_key, name),
                )
                key = cur.fetchone()
                return key
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in create_api_key: {e}")
        return None


def get_user_chat_history(user_id: int) -> List[Dict[str, Any]]:
    """Get chat history for a user."""
    try:
        conn = get_connection()
        try:
            # Create chat_history table if it doesn't exist
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        model VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id SERIAL PRIMARY KEY,
                        chat_id INTEGER REFERENCES chat_history(id) ON DELETE CASCADE,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, title, model, created_at
                    FROM chat_history
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )
                chats = cur.fetchall()
                return chats
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in get_user_chat_history: {e}")
        return []


def create_chat(user_id: int, title: str, model: str) -> Optional[Dict[str, Any]]:
    """Create a new chat for a user."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO chat_history (user_id, title, model)
                    VALUES (%s, %s, %s)
                    RETURNING id, title, model, created_at
                    """,
                    (user_id, title, model),
                )
                chat = cur.fetchone()
                return chat
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in create_chat: {e}")
        return None


def add_chat_message(chat_id: int, role: str, content: str) -> Optional[Dict[str, Any]]:
    """Add a message to a chat."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO chat_messages (chat_id, role, content)
                    VALUES (%s, %s, %s)
                    RETURNING id, role, content, created_at
                    """,
                    (chat_id, role, content),
                )
                message = cur.fetchone()
                return message
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in add_chat_message: {e}")
        return None


def get_chat_messages(chat_id: int) -> List[Dict[str, Any]]:
    """Get all messages for a chat."""
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, role, content, created_at
                    FROM chat_messages
                    WHERE chat_id = %s
                    ORDER BY created_at ASC
                    """,
                    (chat_id,),
                )
                messages = cur.fetchall()
                return messages
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"Database error in get_chat_messages: {e}")
        return []
