"""
Database utilities for the IndoxRouter Dashboard.
"""

import logging
import bcrypt
import uuid
import secrets
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dashboard")

# Database connections
pg_conn = None
mongo_client = None
mongo_db = None


def init_db():
    """Initialize database connections."""
    global pg_conn, mongo_client, mongo_db

    pg_success = False
    mongo_success = False

    # Initialize PostgreSQL
    try:
        pg_conn = psycopg2.connect(config.POSTGRES_URI)
        # Test connection
        with pg_conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        logger.info("Connected to PostgreSQL")

        # Check if tables exist
        with pg_conn.cursor() as cur:
            # Check if users table exists
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users'
                )
                """
            )
            tables_exist = cur.fetchone()[0]
            if not tables_exist:
                logger.info("Creating database tables")
                create_tables()
            else:
                logger.info("Database tables already exist")

        pg_success = True
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        pg_conn = None

    # Initialize MongoDB
    try:
        mongo_client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection with timeout
        mongo_client.server_info()
        mongo_db = mongo_client[config.MONGODB_DATABASE]
        logger.info("Connected to MongoDB")
        mongo_success = True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_client = None
        mongo_db = None

    # Return True if at least one database is connected
    return pg_success or mongo_success


def create_tables():
    """Create necessary tables in PostgreSQL."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return False

    try:
        with pg_conn.cursor() as cur:
            # Users table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    credits DECIMAL(10, 4) NOT NULL DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    account_tier VARCHAR(50) DEFAULT 'free',
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    last_login_at TIMESTAMP
                )
                """
            )

            # API Keys table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    api_key VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMP,
                    last_used_at TIMESTAMP
                )
                """
            )

            # Billing Transactions table - Check if transaction_id column exists
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'billing_transactions'
                )
                """
            )
            
            if cur.fetchone()[0]:
                # Table exists, check if transaction_id column exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                          AND table_name = 'billing_transactions' 
                          AND column_name = 'transaction_id'
                    )
                    """
                )
                transaction_id_exists = cur.fetchone()[0]
                
                if not transaction_id_exists:
                    # Add transaction_id column
                    logger.info("Adding transaction_id column to billing_transactions table")
                    cur.execute(
                        """
                        ALTER TABLE billing_transactions 
                        ADD COLUMN transaction_id VARCHAR(255) UNIQUE
                        """
                    )
                    
                    # Populate with UUIDs for existing rows
                    cur.execute("SELECT id FROM billing_transactions")
                    rows = cur.fetchall()
                    for row in rows:
                        transaction_id = str(uuid.uuid4())
                        cur.execute(
                            "UPDATE billing_transactions SET transaction_id = %s WHERE id = %s",
                            (transaction_id, row[0])
                        )
                    
                    # Make it NOT NULL after populating
                    cur.execute(
                        """
                        ALTER TABLE billing_transactions 
                        ALTER COLUMN transaction_id SET NOT NULL
                        """
                    )
                
                # Check if transaction_type column exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                          AND table_name = 'billing_transactions' 
                          AND column_name = 'transaction_type'
                    )
                    """
                )
                transaction_type_exists = cur.fetchone()[0]
                
                if not transaction_type_exists:
                    # Add transaction_type column
                    logger.info("Adding transaction_type column to billing_transactions table")
                    cur.execute(
                        """
                        ALTER TABLE billing_transactions 
                        ADD COLUMN transaction_type VARCHAR(50) NOT NULL DEFAULT 'purchase'
                        """
                    )
                    logger.info("transaction_type column added with default value 'purchase'")
            else:
                # Create the table with transaction_id
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS billing_transactions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        transaction_id VARCHAR(255) NOT NULL UNIQUE,
                        amount DECIMAL(10, 4) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'USD',
                        transaction_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'completed',
                        payment_method VARCHAR(50),
                        description TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                    """
                )

            pg_conn.commit()
            logger.info("Tables created/updated successfully")
            return True
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error creating/updating tables: {e}")
        return False


def create_user(username, email, password, account_tier="free"):
    """Create a new user in the database."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return None

    try:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Get credits based on tier
        credits = config.PRICING_TIERS.get(account_tier, config.PRICING_TIERS["free"])[
            "credits"
        ]

        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (username, email, password, credits, account_tier, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id, username, email, credits, account_tier, created_at
                """,
                (username, email, password_hash, credits, account_tier),
            )

            user = cur.fetchone()
            pg_conn.commit()

            # Create an API key for the user
            if user:
                api_key = create_api_key(user["id"], "Default Key")
                if api_key:
                    user["api_key"] = api_key

            return user
    except psycopg2.errors.UniqueViolation:
        pg_conn.rollback()
        logger.error(f"User with username {username} or email {email} already exists")
        return None
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error creating user: {e}")
        return None


def create_api_key(user_id, name, expires_days=None):
    """Create a new API key for a user."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return None

    try:
        # Generate a secure API key
        api_key = f"indox_{secrets.token_urlsafe(32)}"

        # Set expiration date if provided
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)

        with pg_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO api_keys (user_id, api_key, name, created_at, expires_at)
                VALUES (%s, %s, %s, NOW(), %s)
                RETURNING api_key
                """,
                (user_id, api_key, name, expires_at),
            )

            result = cur.fetchone()
            pg_conn.commit()

            return result[0] if result else None
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error creating API key: {e}")
        return None


def get_user_by_id(user_id):
    """Get a user by ID."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return None

    try:
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, email, credits, is_active, account_tier, created_at, updated_at, last_login_at
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )

            return cur.fetchone()
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


def get_user_by_username(username):
    """Get a user by username."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return None

    try:
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, email, password, credits, is_active, account_tier, created_at, updated_at, last_login_at
                FROM users
                WHERE username = %s
                """,
                (username,),
            )

            return cur.fetchone()
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


def get_user_api_keys(user_id):
    """Get all API keys for a user."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return []

    try:
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, api_key, name, is_active, created_at, expires_at, last_used_at
                FROM api_keys
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )

            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting user API keys: {e}")
        return []


def add_transaction(
    user_id, amount, transaction_type, description=None, payment_method="credit_card"
):
    """Record a billing transaction."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return False

    try:
        # Generate a transaction ID
        transaction_id = str(uuid.uuid4())

        # Check if the transaction_id column exists
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'billing_transactions' AND column_name = 'transaction_id'
                """
            )
            has_transaction_id = cur.fetchone() is not None

            # Prepare the SQL based on available columns
            if has_transaction_id:
                # Original SQL with transaction_id
                cur.execute(
                    """
                    INSERT INTO billing_transactions (
                        user_id, transaction_id, amount, transaction_type, 
                        payment_method, description, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        user_id,
                        transaction_id,
                        amount,
                        transaction_type,
                        payment_method,
                        description,
                    ),
                )
            else:
                # SQL without transaction_id
                cur.execute(
                    """
                    INSERT INTO billing_transactions (
                        user_id, amount, transaction_type, 
                        payment_method, description, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                    (user_id, amount, transaction_type, payment_method, description),
                )

            # Update user credits if purchasing credits
            if transaction_type == "purchase":
                cur.execute(
                    """
                    UPDATE users
                    SET credits = credits + %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (amount, user_id),
                )

            pg_conn.commit()
            return True
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error adding transaction: {e}")
        return False


def validate_login(username, password):
    """Validate user login credentials."""
    user = get_user_by_username(username)

    if not user:
        return None

    # Verify password
    try:
        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            # Update last login time
            with pg_conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET last_login_at = NOW()
                    WHERE id = %s
                    """,
                    (user["id"],),
                )
                pg_conn.commit()

            # Remove password from user object
            user.pop("password")
            return user

        return None
    except Exception as e:
        logger.error(f"Error validating login: {e}")
        return None


def get_user_transactions(user_id, limit=10):
    """Get recent transactions for a user."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return []

    try:
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check what columns exist in the table
            cur.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'billing_transactions'
                """
            )
            columns = [col[0] for col in cur.fetchall()]

            # Adjust query based on available columns
            if "transaction_id" in columns and "transaction_type" in columns:
                # Full query with all columns
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
            elif "transaction_id" in columns and "transaction_type" not in columns:
                # Query with transaction_id but without transaction_type
                cur.execute(
                    """
                    SELECT id, transaction_id, amount, currency, 'purchase' as transaction_type, 
                           status, payment_method, description, created_at
                    FROM billing_transactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
            elif "transaction_id" not in columns and "transaction_type" in columns:
                # Query with transaction_type but without transaction_id
                cur.execute(
                    """
                    SELECT id, amount, currency, transaction_type, 
                           status, payment_method, description, created_at
                    FROM billing_transactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
            else:
                # Fallback query without transaction_id and transaction_type
                cur.execute(
                    """
                    SELECT id, amount, currency, 'purchase' as transaction_type, 
                           status, payment_method, description, created_at
                    FROM billing_transactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )

            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting user transactions: {e}")
        return []


def get_model_usage(user_id=None):
    """Get model usage statistics from MongoDB."""
    global mongo_db

    if mongo_db is None:
        logger.error("MongoDB connection not initialized")
        return []

    try:
        query = {}
        if user_id:
            query["user_id"] = user_id

        # Group by model and provider
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {"provider": "$provider", "model": "$model"},
                    "tokens_total": {"$sum": "$tokens_total"},
                    "cost": {"$sum": "$cost"},
                    "requests": {"$sum": 1},
                }
            },
            {"$sort": {"cost": -1}},
        ]

        results = list(mongo_db.model_usage.aggregate(pipeline))

        # Format the results
        usage_data = []
        for item in results:
            usage_data.append(
                {
                    "provider": item["_id"]["provider"],
                    "model": item["_id"]["model"],
                    "tokens_total": item["tokens_total"],
                    "cost": item["cost"],
                    "requests": item["requests"],
                }
            )

        return usage_data
    except Exception as e:
        logger.error(f"Error getting model usage: {e}")
        return []


def update_user_tier(user_id, new_tier):
    """Update a user's account tier and add appropriate credits."""
    if not pg_conn:
        logger.error("PostgreSQL connection not initialized")
        return False

    try:
        # Get tier info
        tier_info = config.PRICING_TIERS.get(new_tier)
        if not tier_info:
            logger.error(f"Invalid tier: {new_tier}")
            return False

        with pg_conn.cursor() as cur:
            # Update user tier
            cur.execute(
                """
                UPDATE users
                SET account_tier = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (new_tier, user_id),
            )

            # Add credits from tier
            cur.execute(
                """
                UPDATE users
                SET credits = credits + %s
                WHERE id = %s
                """,
                (tier_info["credits"], user_id),
            )

            pg_conn.commit()
            return True
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error updating user tier: {e}")
        return False
