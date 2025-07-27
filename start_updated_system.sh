#!/bin/bash
set -e

echo "🚀 Starting Enhanced Memory Ecosystem (Updated Ports 10000+)..."

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Start Ollama if not running
print_info "Checking Ollama..."
if ! pgrep -f "ollama serve" > /dev/null; then
    print_info "Starting Ollama..."
    ollama serve &
    sleep 3
    print_status "Ollama started"
else
    print_status "Ollama already running"
fi

# Start Qdrant with updated port
print_info "Starting Qdrant on port 16333..."
if ! docker ps | grep -q "memory-qdrant-updated"; then
    docker run -d \
        --name memory-qdrant-updated \
        -p 16333:6333 \
        -p 16334:6334 \
        -v $(pwd)/data/qdrant:/qdrant/storage \
        qdrant/qdrant
    sleep 5
    print_status "Qdrant started on port 16333"
else
    print_status "Qdrant already running"
fi

# Start Neo4j with updated port
print_info "Starting Neo4j on ports 17474/17687..."
if ! docker ps | grep -q "memory-neo4j-updated"; then
    docker run -d \
        --name memory-neo4j-updated \
        -p 17474:7474 \
        -p 17687:7687 \
        -e NEO4J_AUTH=neo4j/mem0production \
        -v $(pwd)/data/neo4j:/data \
        neo4j:latest
    sleep 10
    print_status "Neo4j started on ports 17474/17687"
else
    print_status "Neo4j already running"
fi

# Start Redis with updated port
print_info "Starting Redis on port 16379..."
if ! docker ps | grep -q "memory-redis-updated"; then
    docker run -d \
        --name memory-redis-updated \
        -p 16379:6379 \
        -v $(pwd)/data/redis:/data \
        redis:7-alpine redis-server --appendonly yes --requirepass mem0redis
    sleep 3
    print_status "Redis started on port 16379"
else
    print_status "Redis already running"
fi

# Start PostgreSQL with updated port
print_info "Starting PostgreSQL on port 15432..."
if ! docker ps | grep -q "memory-postgres-updated"; then
    docker run -d \
        --name memory-postgres-updated \
        -p 15432:5432 \
        -v $(pwd)/data/postgres:/var/lib/postgresql/data \
        -e POSTGRES_DB=mem0db \
        -e POSTGRES_USER=mem0user \
        -e POSTGRES_PASSWORD=mem0postgres \
        postgres:15-alpine
    sleep 5
    print_status "PostgreSQL started on port 15432"
else
    print_status "PostgreSQL already running"
fi

# Start OpenMemory containers with updated ports
print_info "Starting OpenMemory containers..."

# Update OpenMemory environment
if [ ! -f "openmemory/api/.env" ]; then
    cat > openmemory/api/.env << EOF
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
QDRANT_URL=http://localhost:16333
NEO4J_URI=bolt://localhost:17687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0production
REDIS_URL=redis://:mem0redis@localhost:16379
POSTGRES_URL=postgresql://mem0user:mem0postgres@localhost:15432/mem0db
USER=${USER}
NEXT_PUBLIC_API_URL=http://localhost:18765
NEXT_PUBLIC_USER_ID=${USER}
EOF
fi

# Start OpenMemory MCP server on updated port
if ! docker ps | grep -q "openmemory-mcp-updated"; then
    docker run -d \
        --name openmemory-mcp-updated \
        -p 18765:8765 \
        -v $(pwd)/openmemory/api:/usr/src/openmemory \
        --env-file openmemory/api/.env \
        mem0/openmemory-mcp:latest \
        uvicorn main:app --host 0.0.0.0 --port 8765 --reload --workers 4
    sleep 5
    print_status "OpenMemory MCP server started on port 18765"
else
    print_status "OpenMemory MCP server already running"
fi

# Start OpenMemory UI on updated port
if ! docker ps | grep -q "openmemory-ui-updated"; then
    docker run -d \
        --name openmemory-ui-updated \
        -p 13000:3000 \
        -e NEXT_PUBLIC_API_URL=http://localhost:18765 \
        -e NEXT_PUBLIC_USER_ID=${USER} \
        mem0/openmemory-ui:latest
    sleep 5
    print_status "OpenMemory UI started on port 13000"
else
    print_status "OpenMemory UI already running"
fi

# Start MCP server on updated port
print_info "Starting MCP server on port 18766..."
if [ -f "mcp_integration_system.py" ]; then
    python3 mcp_integration_system.py &
    MCP_PID=$!
    echo $MCP_PID > mcp.pid
    sleep 3
    print_status "MCP server started on port 18766"
else
    print_warning "MCP integration system not found"
fi

# Start enhanced API server on updated port
print_info "Starting enhanced API server on port 18767..."
if [ -f "custom_memory_api/enhanced_api_server.py" ]; then
    cd custom_memory_api
    python3 enhanced_api_server.py &
    API_PID=$!
    echo $API_PID > ../api.pid
    cd ..
    sleep 3
    print_status "Enhanced API server started on port 18767"
else
    print_warning "Enhanced API server not found"
fi

# Start enhanced UI on updated port
print_info "Starting enhanced UI on port 13001..."
if [ -d "custom_memory_ui" ]; then
    cd custom_memory_ui
    npm run dev &
    UI_PID=$!
    echo $UI_PID > ../ui.pid
    cd ..
    sleep 5
    print_status "Enhanced UI started on port 13001"
else
    print_warning "Enhanced UI not found"
fi

echo ""
echo "🎉 Enhanced Memory Ecosystem Started!"
echo "====================================="
echo ""
echo "📍 Access Points (Updated Ports):"
echo "  Enhanced UI:      http://localhost:13001"
echo "  Original UI:      http://localhost:13000"
echo "  Enhanced API:     http://localhost:18767"
echo "  OpenMemory API:   http://localhost:18765"
echo "  MCP Server:       ws://localhost:18766"
echo "  Qdrant Dashboard: http://localhost:16333/dashboard"
echo "  Neo4j Browser:    http://localhost:17474 (neo4j/mem0production)"
echo ""
echo "🧪 Test Commands:"
echo "  python3 test_updated_ports.py"
echo "  python3 demo_memory_system.py"
echo ""
echo "🛑 Stop All Services:"
echo "  ./stop_updated_system.sh"
echo ""
echo "📚 Port Reference: PORT_REFERENCE.md"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Stopping services..."
    
    # Kill background processes
    if [ -f mcp.pid ]; then
        kill $(cat mcp.pid) 2>/dev/null || true
        rm mcp.pid
    fi
    
    if [ -f api.pid ]; then
        kill $(cat api.pid) 2>/dev/null || true
        rm api.pid
    fi
    
    if [ -f ui.pid ]; then
        kill $(cat ui.pid) 2>/dev/null || true
        rm ui.pid
    fi
    
    print_status "Background processes stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for interrupt
wait