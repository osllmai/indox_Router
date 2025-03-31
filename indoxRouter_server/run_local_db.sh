#!/bin/bash
# Script to run local PostgreSQL and MongoDB containers for development

# Set database passwords
PG_PASSWORD=${PG_PASSWORD:-"postgrespassword"}
MONGO_PORT=${MONGO_PORT:-27017}
PG_PORT=${PG_PORT:-5432}

# Create docker network if it doesn't exist
echo "Setting up Docker network..."
docker network inspect indoxrouter >/dev/null 2>&1 || docker network create indoxrouter

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
docker run --name indoxrouter-postgres \
  --network indoxrouter \
  -e POSTGRES_PASSWORD=$PG_PASSWORD \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=indoxrouter \
  -v indoxrouter_postgres_data:/var/lib/postgresql/data \
  -p $PG_PORT:5432 \
  -d postgres:15

# Start MongoDB container
echo "Starting MongoDB container..."
docker run --name indoxrouter-mongodb \
  --network indoxrouter \
  -v indoxrouter_mongodb_data:/data/db \
  -p $MONGO_PORT:27017 \
  -d mongo:6

echo "Containers are starting. Waiting 5 seconds for them to be ready..."
sleep 5

# Check container status
PG_STATUS=$(docker ps -f name=indoxrouter-postgres --format "{{.Status}}" | grep -c "Up")
MONGO_STATUS=$(docker ps -f name=indoxrouter-mongodb --format "{{.Status}}" | grep -c "Up")

if [ "$PG_STATUS" -eq 1 ] && [ "$MONGO_STATUS" -eq 1 ]; then
  echo "✅ Both database containers are running!"
  echo ""
  echo "PostgreSQL connection string: postgresql://postgres:$PG_PASSWORD@localhost:$PG_PORT/indoxrouter"
  echo "MongoDB connection string: mongodb://localhost:$MONGO_PORT/indoxrouter"
  echo ""
  echo "To use these databases, set the following environment variables:"
  echo "export DATABASE_URL=postgresql://postgres:$PG_PASSWORD@localhost:$PG_PORT/indoxrouter"
  echo "export MONGODB_URI=mongodb://localhost:$MONGO_PORT/indoxrouter"
  echo "export MONGODB_DATABASE=indoxrouter"
  echo "export INDOXROUTER_LOCAL_MODE=true"
else
  echo "❌ Some containers failed to start:"
  echo "PostgreSQL: $([ "$PG_STATUS" -eq 1 ] && echo "Running" || echo "Not running")"
  echo "MongoDB: $([ "$MONGO_STATUS" -eq 1 ] && echo "Running" || echo "Not running")"
  echo ""
  echo "To see container logs:"
  echo "docker logs indoxrouter-postgres"
  echo "docker logs indoxrouter-mongodb"
fi 