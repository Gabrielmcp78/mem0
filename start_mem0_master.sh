#!/bin/bash

# 🚀 MEM0 MASTER STARTUP SCRIPT 🚀
# This is THE ONLY script you need to run!

echo "🎯 Mem0 Master Startup - Apple Intelligence Edition"
echo "=================================================="

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f "openai_interceptor.py" 2>/dev/null
pkill -f "mem0.*server" 2>/dev/null
sleep 2

# Set environment - Apple Intelligence MUST work, NO fallbacks
export PYTHONPATH="/Volumes/Ready500/DEVELOPMENT/mem0"
export APPLE_INTELLIGENCE_ENABLED="true"
export OLLAMA_FALLBACK_ENABLED="false"
export LOG_LEVEL="debug"

# Set OpenAI API to use our interceptor
export OPENAI_API_KEY="fake-key-using-apple-intelligence"
export OPENAI_BASE_URL="http://localhost:8888/v1"

echo "🔧 Environment configured:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   OPENAI_BASE_URL: $OPENAI_BASE_URL (intercepted to Apple Intelligence)"

# Start OpenAI interceptor in background
echo "🌐 Starting OpenAI API Interceptor..."
python3 openai_interceptor.py &
INTERCEPTOR_PID=$!
sleep 3

# Check if interceptor started
if curl -s http://localhost:8888/v1/chat/completions > /dev/null 2>&1; then
    echo "✅ OpenAI Interceptor running on port 8888"
else
    echo "❌ Failed to start OpenAI Interceptor"
    exit 1
fi

# Start the MCP server with environment variables
echo "🚀 Starting Mem0 MCP Server with Apple Intelligence ONLY (no fallback allowed)..."
OPENAI_API_KEY="fake-key-using-apple-intelligence" OPENAI_BASE_URL="http://localhost:8888/v1" APPLE_INTELLIGENCE_ENABLED="true" OLLAMA_FALLBACK_ENABLED="false" LOG_LEVEL="debug" node integrations/mcp/mem0_full_server.cjs &
MCP_PID=$!

echo ""
echo "🎉 SUCCESS! Both services running:"
echo "   📡 OpenAI Interceptor: http://localhost:8888 (PID: $INTERCEPTOR_PID)"
echo "   🧠 MCP Server: Mem0_Local_M26 (PID: $MCP_PID)"
echo ""
echo "Now mem0 will use Apple Intelligence instead of OpenAI!"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping all services..."; kill $INTERCEPTOR_PID $MCP_PID 2>/dev/null; exit 0' INT
wait