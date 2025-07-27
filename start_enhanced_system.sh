#!/bin/bash
set -e

echo "🚀 Starting Enhanced Memory Ecosystem..."

# Start Ollama if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Start Qdrant if not running
if ! docker ps | grep -q qdrant; then
    echo "Starting Qdrant..."
    docker run -d --name memory-qdrant -p 16333:16333 -p 16334:16334 qdrant/qdrant
fi

# Start MCP server
echo "Starting MCP server..."
python3 mcp_integration_system.py &
MCP_PID=$!

# Start enhanced API server
echo "Starting enhanced API server..."
cd custom_memory_api
python3 enhanced_api_server.py &
API_PID=$!

# Start UI development server
echo "Starting UI development server..."
cd ../custom_memory_ui
npm run dev &
UI_PID=$!

echo "✅ All services started!"
echo "📍 Access points:"
echo "  Enhanced UI:     http://localhost:13001"
echo "  Original UI:     http://localhost:13000"
echo "  Enhanced API:    http://localhost:18767"
echo "  OpenMemory API:  http://localhost:18765"
echo "  MCP Server:      ws://localhost:18766"
echo "  Qdrant:          http://localhost:16333"

# Save PIDs for cleanup
echo $MCP_PID > mcp.pid
echo $API_PID > api.pid
echo $UI_PID > ui.pid

echo "Press Ctrl+C to stop all services"
wait
