@echo off

echo Stopping sphinx-docs container...
docker-compose -f docker-compose.yml down --timeout 60 sphinx-docs

echo Building sphinx-docs container...
docker-compose -f docker-compose.yml build sphinx-docs

echo Installing sphinx-docs container...
docker-compose -f docker-compose.yml up --remove-orphans --force-recreate -d sphinx-docs

echo sphinx-docs container installed successfully!
echo Sphinx documentation is available on port 8080, http://localhost:8080
