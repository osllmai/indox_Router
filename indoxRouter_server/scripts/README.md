# IndoxRouter Scripts

This directory contains utility scripts for the IndoxRouter server deployment and maintenance.

## Deployment Scripts

- `remote_deploy.sh` - Deploys IndoxRouter to a remote server using SSH
- `deploy_integrated.sh` - Sets up IndoxRouter with integrated databases on a single server
- `setup_nginx.sh` - Configures Nginx as a reverse proxy for IndoxRouter

## Backup Scripts

- `backup_databases.sh` - Creates backups of PostgreSQL, MongoDB, and Redis databases
- `setup_backup_cron.sh` - Sets up a cron job for daily database backups

## Usage

### Remote Deployment

To deploy IndoxRouter to a remote server:

```bash
bash scripts/remote_deploy.sh
```

This script will:

1. Copy all necessary files to the remote server
2. Set up the environment
3. Start the application and databases
4. Configure Nginx as a reverse proxy
5. Set up automated database backups

### Database Backups

Backups are automatically configured to run daily at 2:00 AM when using the remote deployment script.

To manually trigger a backup:

```bash
bash scripts/backup_databases.sh
```

To set up the backup cron job manually:

```bash
bash scripts/setup_backup_cron.sh
```

Backups are stored in the following locations:

- PostgreSQL: `/opt/indoxrouter/backups/postgres/`
- MongoDB: `/opt/indoxrouter/backups/mongodb/`
- Redis: `/opt/indoxrouter/backups/redis/`

Backup logs are written to `/opt/indoxrouter/logs/backup.log`.

### Nginx Setup

To configure Nginx as a reverse proxy:

```bash
bash scripts/setup_nginx.sh
```

## Notes

- All scripts are designed to be run from the `indoxrouter_server` directory
- Scripts may require root privileges on the target system
- After deployment, configure your API keys in the `.env` file

## Available Scripts

### Deployment Scripts

**File:** `deploy_integrated.sh`

**Purpose:** Deploys the IndoxRouter server with integrated databases (PostgreSQL, MongoDB, Redis) on a single server.

**Usage:**

```bash
# Make executable
chmod +x deploy_integrated.sh

# Run as root
sudo ./deploy_integrated.sh
```

**File:** `setup_nginx.sh`

**Purpose:** Sets up Nginx as a reverse proxy with SSL/TLS for the IndoxRouter server.

**Usage:**

```bash
# Make executable
chmod +x setup_nginx.sh

# Run as root with your domain name
sudo ./setup_nginx.sh yourdomain.com
```

### Database Management

**File:** `db_clear.py`

**Purpose:** Resets both PostgreSQL and MongoDB databases, clearing all user data, API keys, and other data.

**Usage:**

```bash
# Run the script to clear all data
python scripts/db_clear.py
```

**File:** `db_test.py`

**Purpose:** Tests database connections and creates test data to verify that both PostgreSQL and MongoDB are working properly.

**Usage:**

```bash
# Test database connections and create test data
python scripts/db_test.py
```

**File:** `migrate_to_mongodb.py`

**Purpose:** Migrates data from PostgreSQL to MongoDB to support the hybrid database approach.

**Usage:**

```bash
# Run the migration (will make changes to MongoDB)
python scripts/migrate_to_mongodb.py

# Dry run (no changes will be made)
python scripts/migrate_to_mongodb.py --dry-run
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
