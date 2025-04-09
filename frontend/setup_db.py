#!/usr/bin/env python3
"""
Database setup script for IndoxRouter Dashboard.
This script ensures all necessary database tables and columns are created.
"""

import logging
import os
import sys
import psycopg2
import uuid
from pymongo import MongoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dashboard_setup")

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def setup_database():
    """
    Set up the databases for the IndoxRouter Dashboard.
    
    This function:
    1. Connects to PostgreSQL
    2. Creates all necessary tables if they don't exist
    3. Ensures all required columns exist in each table
    4. Connects to MongoDB and ensures indexes
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    pg_success = setup_postgres()
    mongo_success = setup_mongodb()
    
    return pg_success or mongo_success

def setup_postgres():
    """Set up PostgreSQL database and tables."""
    try:
        # Connect to PostgreSQL
        logger.info(f"Connecting to PostgreSQL: {config.POSTGRES_URI}")
        conn = psycopg2.connect(config.POSTGRES_URI)
        
        with conn.cursor() as cur:
            # Test connection
            cur.execute("SELECT 1")
            
            # Create tables if they don't exist
            # Users table
            cur.execute("""
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
            """)
            logger.info("Ensured users table exists")
            
            # API Keys table
            cur.execute("""
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
            """)
            logger.info("Ensured api_keys table exists")
            
            # Check if billing_transactions table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'billing_transactions'
                )
            """)
            table_exists = cur.fetchone()[0]
            
            if table_exists:
                # Check if transaction_id column exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                          AND table_name = 'billing_transactions' 
                          AND column_name = 'transaction_id'
                    )
                """)
                transaction_id_exists = cur.fetchone()[0]
                
                if not transaction_id_exists:
                    # Add transaction_id column
                    logger.info("Adding transaction_id column to billing_transactions table")
                    cur.execute("""
                        ALTER TABLE billing_transactions 
                        ADD COLUMN transaction_id VARCHAR(255) UNIQUE
                    """)
                    
                    # Populate with UUIDs for existing rows
                    cur.execute("SELECT id FROM billing_transactions")
                    rows = cur.fetchall()
                    logger.info(f"Populating transaction_id for {len(rows)} existing transactions")
                    for row in rows:
                        transaction_id = str(uuid.uuid4())
                        cur.execute(
                            "UPDATE billing_transactions SET transaction_id = %s WHERE id = %s",
                            (transaction_id, row[0])
                        )
                    
                    # Make it NOT NULL after populating
                    cur.execute("""
                        ALTER TABLE billing_transactions 
                        ALTER COLUMN transaction_id SET NOT NULL
                    """)
                    logger.info("transaction_id column added and populated")
                
                # Check if transaction_type column exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                          AND table_name = 'billing_transactions' 
                          AND column_name = 'transaction_type'
                    )
                """)
                transaction_type_exists = cur.fetchone()[0]
                
                if not transaction_type_exists:
                    # Add transaction_type column
                    logger.info("Adding transaction_type column to billing_transactions table")
                    cur.execute("""
                        ALTER TABLE billing_transactions 
                        ADD COLUMN transaction_type VARCHAR(50) NOT NULL DEFAULT 'purchase'
                    """)
                    logger.info("transaction_type column added with default value 'purchase'")
            else:
                # Create the billing_transactions table
                cur.execute("""
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
                """)
                logger.info("Created billing_transactions table")
            
            conn.commit()
            logger.info("PostgreSQL setup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"PostgreSQL setup failed: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def setup_mongodb():
    """Set up MongoDB database and collections."""
    try:
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB: {config.MONGODB_URI}")
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        
        # Get database
        db = client[config.MONGODB_DATABASE]
        
        # Create indexes on collections if they exist
        if "api_requests" in db.list_collection_names():
            db.api_requests.create_index("user_id")
            db.api_requests.create_index("created_at")
            logger.info("Created indexes on api_requests collection")
        
        if "model_usage" in db.list_collection_names():
            db.model_usage.create_index("user_id")
            db.model_usage.create_index("date")
            logger.info("Created indexes on model_usage collection")
        
        logger.info("MongoDB setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"MongoDB setup failed: {e}")
        return False
    finally:
        if 'client' in locals() and client:
            client.close()

if __name__ == "__main__":
    logger.info("Starting database setup")
    success = setup_database()
    if success:
        logger.info("Database setup completed successfully")
        sys.exit(0)
    else:
        logger.error("Database setup failed")
        sys.exit(1)
