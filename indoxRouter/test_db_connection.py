#!/usr/bin/env python
"""
Script to test the database connection for IndoxRouter.
"""

import os
import sys
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        sys.exit(1)


def test_connection():
    """Test the database connection."""
    config = load_config()
    db_config = config["database"]

    logger.info("Testing database connection...")

    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 5432),
            user=db_config.get("user", "postgres"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "indoxrouter"),
        )

        # Create a cursor
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test a simple query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"Connected to PostgreSQL: {version['version']}")

            # Check if tables exist
            cursor.execute(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            )
            tables = cursor.fetchall()

            if tables:
                logger.info("Found the following tables:")
                for table in tables:
                    logger.info(f"  - {table['table_name']}")

                # Check row counts for each table
                for table in tables:
                    table_name = table["table_name"]
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
                    count = cursor.fetchone()["count"]
                    logger.info(f"  - {table_name}: {count} rows")
            else:
                logger.warning("No tables found in the database.")
                logger.info("You may need to run migrations to create the tables.")
                logger.info("Run: python indoxRouter/run_migration.py")

        # Close the connection
        conn.close()
        logger.info("Database connection test completed successfully.")
        return True

    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        logger.info("Please check your database configuration in config.json.")
        logger.info("Make sure PostgreSQL is running and the database exists.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Main function."""
    success = test_connection()
    if success:
        logger.info("Database connection test passed.")
        sys.exit(0)
    else:
        logger.error("Database connection test failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
