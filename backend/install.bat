@echo off

echo "Stopping backend container..."
docker-compose -f docker-compose.yml down --timeout 60

echo "Creating backend network..."
docker network create backend_network

echo "Building backend container with no cache..."
docker-compose build --no-cache

echo "Starting backend container..."
docker-compose -f docker-compose.yml up -d

echo "Backend container started successfully!"
