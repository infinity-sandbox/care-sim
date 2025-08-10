#!/bin/bash

# Change to backend directory
cd backend || { echo "Failed to change to backend directory"; exit 1; }

# Call install.sh instead of changing permissions (no need to change file permissions in this case)
chmod 777 install.sh
./install.sh

# Change back to the original directory
# cd ..

# # Change to frontend directory
# cd frontend || { echo "Failed to change to frontend directory"; exit 1; }

# # Call install.sh for the frontend
# chmod 777 install.sh
# ./install.sh

# # List all running Docker containers
# echo "Listing all running containers..."
# docker ps
