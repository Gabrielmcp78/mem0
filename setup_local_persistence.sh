#!/bin/bash
# Setup Local Persistence for Mem0 Apple Intelligence Server

echo "🚀 Setting up Local Persistence for Mem0 Apple Intelligence"
echo "=========================================================="

# Copy the working server manager
cp mem0-server-simple mem0-server
chmod +x mem0-server

echo "✅ Server manager installed as 'mem0-server'"
echo ""
echo "📋 Available commands:"
echo "  ./mem0-server start    - Start the server"
echo "  ./mem0-server stop     - Stop the server"
echo "  ./mem0-server restart  - Restart the server"
echo "  ./mem0-server status   - Show server status"
echo ""
echo "🎯 To start the server now:"
echo "  ./mem0-server start"
echo ""
echo "🔄 After starting, reconnect MCP in Kiro to use the persistent server"
echo ""
echo "✅ Local persistence setup complete!"