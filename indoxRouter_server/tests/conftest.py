"""
Pytest configuration file for the IndoxRouter server tests.
This file contains fixtures and settings shared across multiple test files.
"""

import os
import sys
import pytest
import logging
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import database functions
from app.db.database import (
    init_db,
    get_pg_connection,
    release_pg_connection,
    get_mongo_db,
)
from app.core.config import settings


@pytest.fixture(scope="session")
def db_initialized():
    """Initialize database connections for the test session."""
    logger.info("Initializing database connections for tests")
    if not init_db():
        pytest.fail("Failed to initialize database connections")
    return True


@pytest.fixture(scope="function")
def pg_connection(db_initialized):
    """
    Get a PostgreSQL connection for the test.

    The connection is released after the test, even if it fails.
    """
    conn = get_pg_connection()
    yield conn
    release_pg_connection(conn)


@pytest.fixture(scope="function")
def mongo_db(db_initialized):
    """Get a MongoDB database connection for the test."""
    if not settings.MONGODB_URI:
        pytest.skip("MongoDB URI not configured")
    db = get_mongo_db()
    return db


@pytest.fixture(scope="function")
def test_user(pg_connection):
    """
    Create a test user for testing.

    Returns a dictionary with the user's ID and API key.
    """
    with pg_connection.cursor() as cur:
        # Check if test user exists
        cur.execute("SELECT id FROM users WHERE username = 'test_user'")
        user = cur.fetchone()

        if not user:
            # Create test user
            cur.execute(
                """
                INSERT INTO users (username, email, password, credits, is_active)
                VALUES ('test_user', 'test@example.com', 'password', 100.0, TRUE)
                RETURNING id
                """
            )
            user_id = cur.fetchone()[0]
            pg_connection.commit()
        else:
            user_id = user[0]

        # Create a test API key
        cur.execute(
            """
            INSERT INTO api_keys (user_id, api_key, name)
            VALUES (%s, 'test-api-key-pytest', 'Test Key')
            ON CONFLICT (api_key) DO NOTHING
            RETURNING id, api_key
            """,
            (user_id,),
        )
        result = cur.fetchone()
        if result:
            api_key_id, api_key = result
        else:
            # Key already exists, retrieve it
            cur.execute(
                """
                SELECT id, api_key FROM api_keys 
                WHERE user_id = %s AND name = 'Test Key'
                """,
                (user_id,),
            )
            api_key_id, api_key = cur.fetchone()

        pg_connection.commit()

        return {"id": user_id, "api_key": api_key, "api_key_id": api_key_id}
