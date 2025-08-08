#!/bin/bash

# Test MCP server via STDIO transport
cd /Volumes/Ready500/DEVELOPMENT/mem0

# Set environment variables
export QDRANT_URL="http://localhost:6333"
export QDRANT_COLLECTION="gabriel_apple_intelligence_memories"
export APPLE_INTELLIGENCE_ENABLED="true"
export LOG_LEVEL="INFO"
export PYTHONPATH="/Volumes/Ready500/DEVELOPMENT/mem0"

echo "🧪 Testing MCP Server via STDIO Transport"
echo "=========================================="

# Create a temporary file with MCP messages
cat > /tmp/mcp_test_messages.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_memory","arguments":{"messages":"Gabriel is testing the Apple Intelligence memory system via STDIO transport. This should work for both Claude Desktop and Kiro.","user_id":"gabriel","agent_id":"kiro","metadata":"{\"test\":\"stdio_transport\",\"category\":\"integration_test\"}"}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"search_memories","arguments":{"query":"Gabriel testing STDIO transport","user_id":"gabriel","limit":3}}}
EOF

echo "📤 Sending MCP messages to server..."
cat /tmp/mcp_test_messages.json | node integrations/mcp/server.js

echo ""
echo "✅ STDIO transport test completed"

# Cleanup
rm -f /tmp/mcp_test_messages.json