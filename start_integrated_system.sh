#!/bin/bash
set -e

echo "🚀 Starting Integrated Mem0 System with Knowledge Graph UI"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "mem0/__init__.py" ]; then
    print_error "Please run this script from the mem0 project root directory"
    
    # Attempt to change directory to the project root
    if cd "$(dirname "$0")"; then
        print_info "Changed directory to project root: $(pwd)"
    else
        print_error "Failed to change directory to project root"
        exit 1
    fi
    
    # Check again if we're in the right directory
    if [ ! -f "mem0/__init__.py" ]; then
        print_error "Still not in the mem0 project root directory"
        exit 1
    fi
    
    print_info "Continuing from project root directory"
    
    # Re-source the script to update environment
    source "$0"
    exit 0
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start service if port is not in use
start_service_if_needed() {
    local port=$1
    local name=$2
    local command=$3
    
    if check_port $port; then
        print_warning "$name is already running on port $port"
    else
        print_info "Starting $name on port $port..."
        eval $command &
        sleep 2
        if check_port $port; then
            print_status "$name started successfully"
        else
            print_error "Failed to start $name"
        fi
    fi
}

# Clean up function
cleanup() {
    print_info "Shutting down services..."
    
    # Kill background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Kill specific processes if they exist
    pkill -f "unified_mcp_server.py" 2>/dev/null || true
    pkill -f "python -m http.server" 2>/dev/null || true
    
    print_status "Services stopped"
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

print_info "Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if mem0 package is available
if ! python3 -c "import mem0" &> /dev/null; then
    print_warning "Installing mem0 package..."
    pip install -e . || {
        print_error "Failed to install mem0 package"
        exit 1
    }
fi

print_status "System requirements check passed"

# Start database containers if needed
print_info "Checking database containers..."

# Check Qdrant
if ! check_port 10333; then
    print_info "Starting Qdrant..."
    if command -v docker &> /dev/null; then
        # Stop existing container if it exists
        docker stop qdrant-standardized 2>/dev/null || true
        docker rm qdrant-standardized 2>/dev/null || true
        
        # Start new container
        docker run -d \
            --name qdrant-standardized \
            -p 10333:6333 \
            -p 10334:6334 \
            qdrant/qdrant:latest || print_warning "Failed to start Qdrant container"
        
        # Wait for Qdrant to be ready
        print_info "Waiting for Qdrant to be ready..."
        for i in {1..60}; do
            if command -v python3 &> /dev/null; then
                if python3 -c "
import sys
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(url='http://localhost:10333')
    client.get_collections()
    print('Qdrant is ready')
    sys.exit(0)
except Exception as e:
    print(f'Qdrant not ready: {e}')
    sys.exit(1)
                " 2>/dev/null; then
                    print_status "Qdrant is ready"
                    break
                else
                    print_warning "Qdrant is not yet ready"
                fi
            else
                print_warning "Python 3 is not available"
                break
            fi
            sleep 1
        done
    else
        print_warning "Docker not available - Qdrant may not be accessible"
    fi
else
    print_status "Qdrant is already running"
fi

# Check PostgreSQL (if needed)
if ! check_port 10432; then
    print_info "Starting PostgreSQL..."
    if command -v docker &> /dev/null; then
        docker run -d \
            --name postgres-standardized \
            -p 10432:5432 \
            -e POSTGRES_DB=mem0 \
            -e POSTGRES_USER=mem0 \
            -e POSTGRES_PASSWORD=mem0password \
            postgres:15-alpine || print_warning "Failed to start PostgreSQL container"
        
        sleep 3
        print_status "PostgreSQL started"
    fi
else
    print_status "PostgreSQL is already running"
fi

# Check Redis (if needed)
if ! check_port 10379; then
    print_info "Starting Redis..."
    if command -v docker &> /dev/null; then
        docker run -d \
            --name redis-standardized \
            -p 10379:6379 \
            redis:7-alpine || print_warning "Failed to start Redis container"
        
        sleep 2
        print_status "Redis started"
    fi
else
    print_status "Redis is already running"
fi

print_status "Database containers are ready"

# Set environment variables
export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:${PATH}"
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export QDRANT_URL="http://localhost:10333"
export QDRANT_COLLECTION="gabriel_memories"


# Install serve if not already installed
if ! command -v serve &> /dev/null
then
    print_info "Installing serve..."
    npm install -g serve || print_warning "Failed to install serve"
fi

# Create logs directory
mkdir -p logs
# Install missing dependencies
print_info "Installing missing dependencies..."
pip install langchain-neo4j || print_warning "Failed to install langchain-neo4j"
pip install rank-bm25 || print_warning "Failed to install rank-bm25"

# Start the unified MCP server
print_info "Starting Unified MCP Server..."
if [ -f "integrations/mcp/unified_mcp_server.py" ]; then
    (cd integrations/mcp && python3 unified_mcp_server.py > ../../logs/mcp_server.log 2>&1) &
    MCP_PID=$!
    
    # Wait a moment and check if it started
    sleep 3
    if ps -p $MCP_PID > /dev/null 2>&1; then
        print_status "Unified MCP Server started (PID: $MCP_PID)"
        echo $MCP_PID > logs/mcp_server.pid
        cd ../..
    else
        print_error "Failed to start Unified MCP Server"
        cat logs/mcp_server.log
        exit 1
    fi
else
    print_error "Unified MCP Server script not found"
    exit 1
fi

# Start Knowledge Graph UI server (disabled by request)
# print_info "Starting Knowledge Graph UI..."
# if [ -d "integrations/ui" ] && [ -f "integrations/ui/knowledge_graph_ui.html" ]; then
#     (cd integrations/ui && npx serve -p 8081 > ../../logs/ui_server.log 2>&1) &
#     UI_PID=$!
#     sleep 2
#     if ps -p $UI_PID > /dev/null 2>&1; then
#         print_status "Knowledge Graph UI started (PID: $UI_PID)"
#         echo $UI_PID > logs/ui_server.pid
#     else
#         print_error "Failed to start Knowledge Graph UI (process did not stay running)"
#         # Do not fail the whole system due to UI panel
#         print_warning "Continuing without Knowledge Graph UI"
#     fi
# else
#     # Do not fail the whole system due to UI panel
#     print_warning "Knowledge Graph UI not found at integrations/ui/knowledge_graph_ui.html - continuing without UI"
# fi

# Wait for all services to be ready
print_info "Waiting for all services to be ready..."
sleep 5

# Test MCP server connection
print_info "Testing MCP server..."
if python3 -c "
import sys
sys.path.insert(0, 'integrations/mcp')
try:
    import asyncio
    from unified_mcp_server import UnifiedMCPServer
    print('MCP server imports work')
except Exception as e:
    print(f'MCP server test failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
    print_status "MCP server is working"
else
    print_warning "MCP server test failed - check logs/mcp_server.log"
fi

# Display access information
echo ""
echo "🎉 INTEGRATED MEM0 SYSTEM IS READY!"
echo "============================================"
echo ""
print_status "Access Points:"
echo "  📊 Knowledge Graph UI:     http://localhost:8081/knowledge_graph_ui.html"
echo "  🗄️  Qdrant Dashboard:       http://localhost:10333/dashboard"
echo "  📝 MCP Server Logs:        tail -f logs/mcp_server.log"
echo "  🌐 UI Server Logs:         tail -f logs/ui_server.log"
echo ""
print_status "Database Connections:"
echo "  🔍 Qdrant Vector DB:       localhost:10333"
echo "  🐘 PostgreSQL:             localhost:10432"
echo "  📊 Redis Cache:            localhost:10379"
echo ""
print_status "Features Available:"
echo "  ✨ Persistent database connections"
echo "  🔄 Automatic reconnection handling"
echo "  📈 Interactive knowledge graph visualization"
echo "  🎯 Real-time graph statistics"
echo "  💾 Graph export functionality"
echo "  📱 Mobile-responsive UI"
echo ""
print_info "To test the system:"
echo "  1. Open http://localhost:8080/knowledge_graph_ui.html in your browser"
echo "  2. Click 'Load Graph' to see your knowledge relationships"
echo "  3. Use the MCP server tools via your preferred client"
echo ""
print_warning "To stop the system:"
echo "  Press Ctrl+C in this terminal, or run: ./stop_integrated_system.sh"
echo ""

# Monitor services
print_info "System is running... Press Ctrl+C to stop all services"

# Keep the script running and monitor services
while true; do
    sleep 30
    
    # Check if MCP server is still running
    if [ -f "logs/mcp_server.pid" ]; then
        MCP_PID=$(cat logs/mcp_server.pid)
        if ! ps -p $MCP_PID > /dev/null 2>&1; then
            print_error "MCP server has stopped unexpectedly"
            print_info "Check logs/mcp_server.log for details"
            break
        fi
    fi
    
    # (UI disabled) Skip UI server check safely
    :
done