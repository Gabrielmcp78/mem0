#!/bin/bash

# Mem0 Enhanced Server Startup Script
# Starts the enhanced MCP server with FoundationModels integration

set -e

echo "🚀 Starting Mem0 Enhanced MCP Server with FoundationModels"
echo "============================================================"

# Configuration
PYTHON_PATH="/Volumes/Ready500/DEVELOPMENT/mem0"
SERVER_PATH="integrations/mcp/mem0_enhanced_server.cjs"
CONFIG_PATH="claude_desktop_config_enhanced.json"

# Validate prerequisites
echo "📋 Validating prerequisites..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if server file exists
if [ ! -f "$SERVER_PATH" ]; then
    echo "❌ Enhanced server file not found: $SERVER_PATH"
    exit 1
fi

# Check if Python path exists
if [ ! -d "$PYTHON_PATH" ]; then
    echo "❌ Python path does not exist: $PYTHON_PATH"
    exit 1
fi

# Check if mem0 is installed
if [ ! -d "$PYTHON_PATH/mem0" ]; then
    echo "❌ mem0 library not found at: $PYTHON_PATH/mem0"
    exit 1
fi

echo "✅ All prerequisites validated"

# Check if services are running
echo "🔍 Checking required services..."

# Check Qdrant
if ! curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo "⚠️  Qdrant is not running on localhost:6333"
    echo "   Please start Qdrant: docker run -p 6333:6333 qdrant/qdrant"
fi

# Check Neo4j
if ! curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo "⚠️  Neo4j is not running on localhost:7474"
    echo "   Please start Neo4j: docker run -p 7474:7474 -p 7687:7687 neo4j"
fi

# Check LM Studio (optional)
if ! curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo "⚠️  LM Studio is not running on localhost:1234"
    echo "   This is optional but recommended for enhanced AI capabilities"
fi

echo "✅ Service check completed"

# Set environment variables
export PYTHONPATH="$PYTHON_PATH"
export PYTHON_EXECUTABLE="python3"
export APPLE_INTELLIGENCE_ENABLED="true"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"
export OPERATION_TIMEOUT="60000"
export MAX_RETRIES="3"
export LOG_LEVEL="info"

echo "🔧 Environment configured:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   PYTHON_EXECUTABLE: $PYTHON_EXECUTABLE"
echo "   APPLE_INTELLIGENCE_ENABLED: $APPLE_INTELLIGENCE_ENABLED"

# Start the enhanced server
echo "🚀 Starting enhanced MCP server..."
echo "   Server: $SERVER_PATH"
echo "   Press Ctrl+C to stop"
echo ""

# Run the server with proper error handling
node "$SERVER_PATH" 2>&1 | while IFS= read -r line; do
    # Add timestamp to log lines
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"
done

echo "🛑 Enhanced MCP server stopped"