#!/bin/bash

echo "🛑 Stopping Enhanced Memory Ecosystem (Updated Ports)..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Kill background processes
print_info "Stopping background processes..."

if [ -f mcp.pid ]; then
    kill $(cat mcp.pid) 2>/dev/null || true
    rm mcp.pid
    print_status "MCP server stopped"
fi

if [ -f api.pid ]; then
    kill $(cat api.pid) 2>/dev/null || true
    rm api.pid
    print_status "Enhanced API server stopped"
fi

if [ -f ui.pid ]; then
    kill $(cat ui.pid) 2>/dev/null || true
    rm ui.pid
    print_status "Enhanced UI stopped"
fi

# Stop Docker containers with updated names
print_info "Stopping Docker containers..."

containers=(
    "memory-qdrant-updated"
    "memory-neo4j-updated"
    "memory-redis-updated"
    "memory-postgres-updated"
    "openmemory-mcp-updated"
    "openmemory-ui-updated"
)

for container in "${containers[@]}"; do
    if docker ps -q -f name="$container" | grep -q .; then
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
        print_status "Stopped $container"
    fi
done

# Optional: Stop Ollama (uncomment if you want to stop Ollama too)
# print_info "Stopping Ollama..."
# pkill -f "ollama serve" 2>/dev/null || true
# print_status "Ollama stopped"

echo ""
print_status "All Enhanced Memory Ecosystem services stopped"
echo ""
echo "📍 To restart:"
echo "  ./start_updated_system.sh"