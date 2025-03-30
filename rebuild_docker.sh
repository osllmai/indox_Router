#!/bin/bash

# Navigate to the server directory
cd indoxRouter_server

# Stop any running containers
echo "Stopping existing containers..."
docker-compose down

# Rebuild the container with the new changes
echo "Rebuilding the container..."
docker-compose build --no-cache

# Start the container
echo "Starting the container..."
docker-compose up -d

# Show the logs
echo "Showing logs (press Ctrl+C to exit)..."
docker-compose logs -f 