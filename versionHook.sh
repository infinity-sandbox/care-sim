#!/bin/bash

#################### Update version on realtime merge

# Path to the version file
VERSION_FILE="backend/version"
chmod +rw $VERSION_FILE

# Read current version and build date from the version file
current_version=$(head -n 1 "$VERSION_FILE")
build_date=$(date +"%Y%m%d%H%M%S")

# Function to increment the version
increment_version() {
    IFS='.' read -r major minor patch <<< "$1"
    
    # Increment patch version
    if [ "$patch" -lt 99 ]; then
        ((patch++))
    elif [ "$minor" -lt 99 ]; then
        ((minor++))
        patch=0
    elif [ "$major" -lt 9 ]; then
        ((major++))
        minor=0
        patch=0
    else
        echo "Version limit reached!"
        exit 1
    fi
    
    echo "$major.$minor.$patch"
}

# Increment version
new_version=$(increment_version "$current_version")

# Update the version file with the new version and build date
{
    echo "$new_version"
    echo "$build_date"
} > "$VERSION_FILE"

# Check if the tag already exists
if git rev-parse "v$new_version" >/dev/null 2>&1; then
    echo "Tag v$new_version already exists. Skipping tag creation."
else
    # Create a new tag if it doesn't already exist
    git tag -a "v$new_version" -m "Version $new_version"
    git push origin "v$new_version"
    echo "Updated version to $new_version and created tag v$new_version"
fi


