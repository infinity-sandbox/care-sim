#!/bin/bash

echo "Stopping frontend container..."
docker-compose -f docker-compose.yml down --timeout 60

echo "Building frontend container..."
docker-compose -f docker-compose.yml build

echo "Installing frontend container..."
docker-compose -f docker-compose.yml up --remove-orphans --force-recreate -d

echo "Frontend container installed successfully!"
