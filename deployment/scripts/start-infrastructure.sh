#!/bin/bash

# Mem0 Infrastructure Startup Script
# This script starts the supporting services (PostgreSQL, Redis, Qdrant, Ollama)

set -e

echo "🚀 Starting Mem0 Infrastructure Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required files exist
if [ ! -f "deployment/docker/docker-compose.simple.yml" ]; then
    echo "❌ Simple Docker Compose file not found!"
    exit 1
fi

# Start the infrastructure stack
echo "📦 Starting infrastructure containers..."
docker compose -f deployment/docker/docker-compose.simple.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Health checks
echo "🔍 Performing health checks..."

# Check PostgreSQL
if docker exec $(docker compose -f deployment/docker/docker-compose.simple.yml ps -q postgres) pg_isready -U mem0 -d mem0 > /dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "⚠️  PostgreSQL health check failed"
fi

# Check Redis
if docker exec $(docker compose -f deployment/docker/docker-compose.simple.yml ps -q redis) redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "⚠️  Redis health check failed"
fi

# Check Qdrant
if curl -s http://localhost:26333/health > /dev/null; then
    echo "✅ Qdrant is healthy"
else
    echo "⚠️  Qdrant health check failed"
fi

# Check Ollama (system service)
if curl -s http://localhost:11434/api/version > /dev/null; then
    echo "✅ Ollama is healthy (system service)"
else
    echo "⚠️  Ollama health check failed"
fi

echo ""
echo "🎉 Mem0 Infrastructure Services Started Successfully!"
echo ""
echo "📊 Service URLs:"
echo "   PostgreSQL: localhost:25432 (user: mem0, db: mem0)"
echo "   Redis:      localhost:26379"
echo "   Qdrant:     http://localhost:26333"
echo "   Ollama:     http://localhost:11434 (system service)"
echo ""
echo "📝 Logs: docker compose -f deployment/docker/docker-compose.simple.yml logs -f"
echo "🛑 Stop:  ./deployment/scripts/stop-infrastructure.sh"
echo ""
echo "💡 Next steps:"
echo "   1. Install Mem0: pip install mem0ai"
echo "   2. Configure environment variables"
echo "   3. Run your Mem0 application"