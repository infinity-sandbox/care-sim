#!/bin/bash

echo "Stopping backend container..."
docker-compose -f docker-compose.yml down --timeout 30

docker network create backend_network

# docker-compose build --no-cache
docker-compose build
  
# Start the backend container
echo "Starting backend container..."
docker-compose -f docker-compose.yml up -d

echo "Backend container started successfully!"
