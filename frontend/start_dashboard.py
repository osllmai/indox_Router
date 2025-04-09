#!/usr/bin/env python3
"""
Start script for the IndoxRouter Dashboard.
This script ensures the database is properly set up before launching the dashboard.
"""

import os
import sys
import logging
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dashboard_starter")

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import streamlit
        import psycopg2
        import pymongo
        import pandas
        import plotly
        import bcrypt
        logger.info("All required dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return False

def setup_database():
    """Run the database setup script."""
    logger.info("Setting up database...")
    try:
        # Import the setup module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import setup_db
        
        # Run the setup
        success = setup_db.setup_database()
        if success:
            logger.info("Database setup completed successfully")
            return True
        else:
            logger.warning("Database setup failed, but will try to continue")
            return False
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        logger.warning("Will try to continue despite database setup error")
        return False

def check_database_connections():
    """Check if the database connections are working."""
    try:
        # Import the configuration and database modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import config
        import database
        
        # Try to initialize the database connections
        connected = database.init_db()
        return connected
    except Exception as e:
        logger.error(f"Error checking database connections: {e}")
        return False

def start_dashboard():
    """Start the Streamlit dashboard."""
    try:
        logger.info("Starting IndoxRouter Dashboard...")
        dashboard_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        
        # Start Streamlit
        subprocess.run(["streamlit", "run", dashboard_file], check=True)
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Error starting dashboard: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error starting dashboard: {e}")
        return False

def main():
    """Main entry point for starting the dashboard."""
    logger.info("Starting IndoxRouter Dashboard initialization...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies. Please install all required packages.")
        logger.info("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup database
    setup_database()
    
    # Check database connections
    if not check_database_connections():
        logger.warning("Database connections failed")
        proceed = input("Database connections failed. Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            logger.info("Exiting as requested")
            sys.exit(1)
    
    # Start the dashboard
    success = start_dashboard()
    if not success:
        logger.error("Failed to start the dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
