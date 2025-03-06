#!/usr/bin/env python
"""
Script to set up the PostgreSQL database for testing.
"""

import os
import sys
import argparse

# Add the parent directory to the path so we can import indoxRouter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 is not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)

from indoxRouter.database.postgres import PostgresDatabase


def setup_postgres(connection_string=None):
    """Set up the PostgreSQL database for testing."""
    try:
        print("Setting up PostgreSQL database...")
        db = PostgresDatabase(connection_string)

        # Get all users to verify the setup
        conn = psycopg2.connect(db.connection_string)
        cursor = conn.cursor()

        cursor.execute("SELECT id, api_key, name, email FROM users")
        users = cursor.fetchall()

        print(f"Database setup complete. {len(users)} test users created:")
        for user in users:
            print(
                f"  - ID: {user[0]}, API Key: {user[1]}, Name: {user[2]}, Email: {user[3]}"
            )

        conn.close()
        return True
    except Exception as e:
        print(f"Error setting up PostgreSQL database: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set up the PostgreSQL database for testing."
    )
    parser.add_argument(
        "--connection-string",
        help="PostgreSQL connection string. If not provided, uses the INDOX_ROUTER_DB_URL environment variable.",
    )

    args = parser.parse_args()

    if setup_postgres(args.connection_string):
        print("PostgreSQL database setup successful!")
    else:
        print("PostgreSQL database setup failed.")
        sys.exit(1)
