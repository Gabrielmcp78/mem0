#!/bin/bash

# Production Mem0 Memory System Stop Script

set -e

echo "🛑 Stopping Mem0 Production Memory System..."

# Stop the production stack
if [ -f "deployment/docker/docker-compose.production.yml" ]; then
    docker compose -f deployment/docker/docker-compose.production.yml down
    echo "✅ Production services stopped"
else
    echo "❌ Production Docker Compose file not found!"
    exit 1
fi

# Optional: Remove volumes (uncomment if needed)
# echo "🗑️  Removing volumes..."
# docker compose -f deployment/docker/docker-compose.production.yml down -v

echo "🎉 Mem0 Production System Stopped Successfully!"