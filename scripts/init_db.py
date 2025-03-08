#!/usr/bin/env python
"""
Database initialization script for indoxRouter.
This script creates the necessary tables and initial data for the indoxRouter application.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Get database URL from environment variable or use default
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/indoxrouter')

def init_db():
    """Initialize the database with the required tables and initial data."""
    print("Initializing database...")
    
    # Connect to the database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("Connected to the database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)
    
    # Read and execute the SQL script
    try:
        with open(os.path.join(os.path.dirname(__file__), 'init_db.sql'), 'r') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        print("Database schema created successfully.")
    except Exception as e:
        print(f"Error executing SQL script: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
    
    print("Database initialization completed.")

if __name__ == "__main__":
    init_db() 