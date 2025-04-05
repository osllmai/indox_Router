# IndoxRouter Server Scripts

This directory contains utility scripts for the IndoxRouter server.

## Available Scripts

### MongoDB Migration Script

**File:** `migrate_to_mongodb.py`

**Purpose:** Migrates data from PostgreSQL to MongoDB to support the hybrid database approach. This script helps transition model-related data from PostgreSQL to MongoDB while keeping user data in PostgreSQL.

**Usage:**

```bash
# Run the migration (will make changes to MongoDB)
python migrate_to_mongodb.py

# Dry run (no changes will be made)
python migrate_to_mongodb.py --dry-run
```

**What it does:**

1. Connects to both PostgreSQL and MongoDB databases
2. Migrates model definitions from PostgreSQL to MongoDB
3. Migrates recent API request data to MongoDB for model usage statistics
4. Provides verbose logging to track the migration process

**Requirements:**

- Both PostgreSQL and MongoDB must be properly configured in the .env file
- The script must be run from within the IndoxRouter server directory

## Adding New Scripts

When adding new utility scripts to this directory:

1. Use the same imports pattern as existing scripts to ensure proper module resolution
2. Add proper command-line arguments with argparse
3. Include detailed docstrings and comments
4. Add the script to this README with usage instructions
