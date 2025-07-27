#!/bin/bash

# Ensure LM Studio is running at http://localhost:1234
echo "💭 Checking if LM Studio is running..."

# Test LM Studio connection
curl -s http://localhost:1234/v1/models > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: LM Studio is not running or not accessible at http://localhost:1234"
    echo "   Please make sure LM Studio is running with:"
    echo "   - Gemma 3 model loaded"
    echo "   - API server enabled on port 1234"
    exit 1
else
    echo "✅ LM Studio is running"
fi

# Start OpenMemory MCP
echo "🚀 Starting OpenMemory MCP..."
cd /Volumes/Ready500/DEVELOPMENT/mem0/openmemory

# Build Docker images if needed
make build

# Start the services
make up

echo "🔗 OpenMemory MCP is running with LM Studio integration"
echo "   Access the UI at: http://localhost:3000"
echo "   MCP Server at: http://localhost:8765"
echo ""
echo "📋 MCP Client Configuration:"
echo "   Use the following URL in your MCP client configuration:"
echo "   http://localhost:8765/mcp/<mcp-client>/sse/<your-username>"
echo ""
echo "🛑 Press Ctrl+C to stop the services"

# Keep the script running
tail -f /dev/null
