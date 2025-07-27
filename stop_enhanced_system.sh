#!/bin/bash
echo "🛑 Stopping Enhanced Memory Ecosystem..."

# Kill processes
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

# Stop Docker containers
docker stop memory-qdrant 2>/dev/null || true
docker rm memory-qdrant 2>/dev/null || true

echo "✅ All services stopped"
