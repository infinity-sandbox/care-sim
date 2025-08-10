#!/bin/bash

# Set the target directory
# Set the target directories
TARGET_DIR_BE=bin/arm64/backend
TARGET_DIR_FE=bin/arm64/frontend
ZIP_FILE=bin/arm64

# Check if the zip file exists; if so, delete it
if [ -f "${ZIP_FILE}.zip" ]; then
    rm "${ZIP_FILE}.zip"
fi

# Check if the backend directory exists; if so, delete it
if [ -d "$TARGET_DIR_BE" ]; then
    rm -rf "$TARGET_DIR_BE"
fi

# Check if the frontend directory exists; if so, delete it
if [ -d "$TARGET_DIR_FE" ]; then
    rm -rf "$TARGET_DIR_FE"
fi

# Recreate the directory
mkdir -p "$TARGET_DIR_BE"
mkdir -p "$TARGET_DIR_FE"

# Copy all files (including hidden files) from backend to the target directory
cp -a ./backend/. "$TARGET_DIR_BE/"
cp -a ./frontend/. "$TARGET_DIR_FE/"

# Print success message
echo "The folder has been recreated and the contents, including hidden files, have been copied successfully!"

# Navigate into the target directory
cd "$TARGET_DIR_BE" || exit 1  # Exit if changing directory fails

echo "Deleting environments..."
rm -rf venv

echo "Deleting unwanted files..."
rm -rf logs/logs.log
rm -rf docs
rm -rf htmlcov
rm -rf dockerfile.sphinx
rm -rf sphinx_docs.sh
rm -rf test1
rm -rf build
rm -rf utils/dist
chmod 777 logs

echo "Deleting unwanted lines from .dockerignore..."
sed -i '' '/\*.pyc/d' .dockerignore
sed -i '' '/\*.pyo/d' .dockerignore
sed -i '' '/\*.pyd/d' .dockerignore
sed -i '' '/__pycache__/d' .dockerignore

echo "Unwanted lines deleted successfully!"

# Compile Python files to .pyc
python -m compileall .

# Move each .pyc file out of __pycache__ into its corresponding directory
find . -name "*.pyc" -exec sh -c '
    for pyc_file do
        # Get the directory containing the __pycache__
        parent_dir=$(dirname "$pyc_file")
        
        # Create target directory if not exists
        target_dir=${parent_dir/__pycache__/}
        mkdir -p "$target_dir"
        
        # Move the .pyc file into its corresponding target directory
        mv "$pyc_file" "$target_dir/$(basename "$pyc_file" | sed "s/\.cpython-312//")"
    done
' sh {} +

# Delete the __pycache__ directories and original .py files
rm -rf $(find . -name "__pycache__")
find . -name "*.py" -type f ! -name "setup.py" -delete

echo "Conversion process to binary for the backend completed!"

# Navigate back to the root directory
cd ../frontend || exit 1  # Exit if changing directory fails

echo "Deleting unwanted files from frontend..."
rm -rf build
rm -rf node_modules

echo "Conversion process to binary for the frontend completed!"

cd ../../.. || exit 1  # Exit if changing directory fails

cp initializeGenieSignals.sh ${ZIP_FILE}/initializeGenieSignals.sh
cp readme.md ${ZIP_FILE}/readme.md
cp setupEnv.sh ${ZIP_FILE}/setupEnv.sh

# Create the zip file containing all files (including hidden files) from both directories
zip -r "${ZIP_FILE}.zip" "${ZIP_FILE}/."

echo "The contents have been zipped into $ZIP_FILE.zip"

