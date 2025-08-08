#!/bin/bash

echo "🛑 Stopping Integrated Mem0 System"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Stop MCP server
if [ -f "logs/mcp_server.pid" ]; then
    MCP_PID=$(cat logs/mcp_server.pid)
    if ps -p $MCP_PID > /dev/null 2>&1; then
        kill $MCP_PID 2>/dev/null
        print_status "MCP server stopped"
    fi
    rm -f logs/mcp_server.pid
fi

# Stop UI server
if [ -f "logs/ui_server.pid" ]; then
    UI_PID=$(cat logs/ui_server.pid)
    if ps -p $UI_PID > /dev/null 2>&1; then
        kill $UI_PID 2>/dev/null
        print_status "UI server stopped"
    fi
    rm -f logs/ui_server.pid
fi

# Kill any remaining processes
pkill -f "unified_mcp_server.py" 2>/dev/null || true
pkill -f "python -m http.server 8080" 2>/dev/null || true

# Optionally stop Docker containers (uncomment if desired)
# print_info "Stopping database containers..."
# docker stop qdrant-standardized postgres-standardized redis-standardized 2>/dev/null || true

print_status "All services stopped"
print_info "Log files are preserved in the logs/ directory"