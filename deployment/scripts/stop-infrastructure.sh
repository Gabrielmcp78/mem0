#!/bin/bash

# Mem0 Infrastructure Stop Script

set -e

echo "🛑 Stopping Mem0 Infrastructure Services..."

# Stop the infrastructure stack
if [ -f "deployment/docker/docker-compose.simple.yml" ]; then
    docker compose -f deployment/docker/docker-compose.simple.yml down
    echo "✅ Infrastructure services stopped"
else
    echo "❌ Simple Docker Compose file not found!"
    exit 1
fi

# Optional: Remove volumes (uncomment if needed)
# echo "🗑️  Removing volumes..."
# docker compose -f deployment/docker/docker-compose.simple.yml down -v

echo "🎉 Mem0 Infrastructure Services Stopped Successfully!"