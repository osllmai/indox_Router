# IndoxRouter Database Setup

IndoxRouter now uses a hybrid database approach with PostgreSQL and MongoDB to provide the best of both worlds:

- **PostgreSQL**: Handles all relational data such as users, API keys, billing, and subscriptions
- **MongoDB**: Stores document-oriented data such as conversations, embeddings, and model outputs

## Database Schema

### PostgreSQL Tables

- **users**: Stores user account information
- **api_keys**: API keys for authentication
- **api_requests**: Logs of all API requests
- **billing_transactions**: Record of all billing transactions
- **usage_daily_summary**: Daily usage statistics
- **pricing_plans**: Available subscription plans
- **user_subscriptions**: User subscription information
- **providers**: Configuration for AI providers
- **models**: Available AI models
- **system_settings**: Global system configuration

### MongoDB Collections

- **conversations**: Stores chat conversations
- **embeddings**: Stores vector embeddings
- **user_datasets**: Custom user datasets
- **model_outputs**: Cache for model responses

## Setup Options

You have three ways to set up the databases:

### 1. Docker Compose (Recommended for Production)

The simplest way to run the complete IndoxRouter stack:

```bash
docker-compose up -d
```

This sets up:

- IndoxRouter server
- PostgreSQL
- MongoDB

### 2. Local Development Containers

For development, you can run just the databases:

```bash
# Make the script executable
chmod +x run_local_db.sh

# Run the databases
./run_local_db.sh
```

Then set these environment variables:

```bash
export DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/indoxrouter
export MONGODB_URI=mongodb://localhost:27017/indoxrouter
export MONGODB_DATABASE=indoxrouter
export INDOXROUTER_LOCAL_MODE=true
```

### 3. External Database Connections

You can also connect to existing database servers:

1. Set up your PostgreSQL and MongoDB instances
2. Configure the connection details in your `.env` file
3. Ensure the databases and permissions are properly configured

## Database Schema Creation

The schema is automatically created when the server starts in local mode. To manually create tables:

```bash
# Clone the IndoxRouter repository
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter/indoxRouter_server

# Run the database test script to initialize and verify the databases
python test_db.py
```

## Testing the Database Connection

You can verify your database connections are working:

```bash
python test_db.py
```

This script:

1. Connects to both PostgreSQL and MongoDB
2. Creates test data in each database
3. Verifies the data can be retrieved

## Migrating from External Website Database

If you previously used an external website database and want to migrate to the integrated database:

1. Export your data from the current database
2. Set up the new PostgreSQL database
3. Import your data
4. Update your `.env` file to use the new database
5. Set `INDOXROUTER_LOCAL_MODE=true`

## Choosing Between PostgreSQL and MongoDB

- **PostgreSQL** is used for:

  - User accounts and authentication
  - Transaction records
  - Billing and subscriptions
  - API usage tracking
  - Configuration storage

- **MongoDB** is used for:
  - Conversations (chat history)
  - Embeddings (vector data)
  - Response caching
  - User datasets

This hybrid approach gives you the strong consistency and relations of PostgreSQL where needed, with the flexibility and scaling of MongoDB for document storage.

## Backup and Restore

### PostgreSQL Backup

```bash
# With docker
docker exec indoxrouter-postgres pg_dump -U postgres indoxrouter > pg_backup.sql

# Without docker
pg_dump -U postgres indoxrouter > pg_backup.sql
```

### MongoDB Backup

```bash
# With docker
docker exec indoxrouter-mongodb mongodump --db indoxrouter --out /dump
docker cp indoxrouter-mongodb:/dump ./mongo_backup

# Without docker
mongodump --db indoxrouter --out ./mongo_backup
```

## Troubleshooting

If you encounter issues with the database connection:

1. Verify the database services are running:

   ```bash
   docker ps | grep indoxrouter
   ```

2. Check the database logs:

   ```bash
   docker logs indoxrouter-postgres
   docker logs indoxrouter-mongodb
   ```

3. Ensure your connection strings in `.env` are correct

4. For MongoDB connection issues, try connecting with the MongoDB shell:

   ```bash
   docker exec -it indoxrouter-mongodb mongosh
   ```

5. For PostgreSQL connection issues, try connecting with psql:
   ```bash
   docker exec -it indoxrouter-postgres psql -U postgres indoxrouter
   ```
