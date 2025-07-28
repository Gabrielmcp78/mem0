#!/bin/bash

# Production Mem0 Memory System Startup Script
# This script starts the complete Mem0 memory ecosystem in production mode

set -e

echo "🚀 Starting Mem0 Production Memory System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required files exist
if [ ! -f "deployment/docker/docker-compose.production.yml" ]; then
    echo "❌ Production Docker Compose file not found!"
    exit 1
fi

# Start the production stack
echo "📦 Starting Docker containers..."
docker compose -f deployment/docker/docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
echo "🔍 Performing health checks..."

# Check Qdrant
if curl -s http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is healthy"
else
    echo "⚠️  Qdrant health check failed"
fi

# Check Ollama
if curl -s http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama is healthy"
else
    echo "⚠️  Ollama health check failed"
fi

# Check Memory API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Memory API is healthy"
else
    echo "⚠️  Memory API health check failed"
fi

echo ""
echo "🎉 Mem0 Production System Started Successfully!"
echo ""
echo "📊 Service URLs:"
echo "   Memory API: http://localhost:8000"
echo "   Memory UI:  http://localhost:3000"
echo "   Qdrant:     http://localhost:6333"
echo "   Ollama:     http://localhost:11434"
echo ""
echo "📝 Logs: docker compose -f deployment/docker/docker-compose.production.yml logs -f"
echo "🛑 Stop:  ./deployment/scripts/stop-production.sh"