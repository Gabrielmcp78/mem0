#!/bin/bash

# Mem0 Clean MCP Server Startup Script
# A focused, maintainable alternative to the 2800-line monolith

echo "🚀 Starting Mem0 Full-Featured MCP Server (Clean Modular Architecture)"
echo "======================================================================="

# Set clean environment variables
export PYTHONPATH="/Volumes/Ready500/DEVELOPMENT/mem0"
export PYTHON_EXECUTABLE="python3"
export APPLE_INTELLIGENCE_ENABLED="true"
export OLLAMA_FALLBACK_ENABLED="false"
export OPERATION_TIMEOUT="30000"
export MAX_RETRIES="2"
export LOG_LEVEL="info"

echo "🔧 Environment configured:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   APPLE_INTELLIGENCE_ENABLED: $APPLE_INTELLIGENCE_ENABLED"
echo "   OLLAMA_FALLBACK_ENABLED: $OLLAMA_FALLBACK_ENABLED"

echo "🚀 Starting full-featured MCP server with modular architecture..."

# Start the full server
SERVER_PATH="integrations/mcp/mem0_full_server.cjs"

if [ ! -f "$SERVER_PATH" ]; then
    echo "❌ Server file not found: $SERVER_PATH"
    exit 1
fi

echo "   Server: $SERVER_PATH"
echo "   Press Ctrl+C to stop"
echo ""

# Run with proper error handling
node "$SERVER_PATH" || {
    echo "❌ Server failed to start"
    exit 1
}

echo "🛑 Full-Featured MCP server stopped"