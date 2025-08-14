#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Testing Launch Agents Setup"
echo "================================"

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# Check if launch agent files exist
echo "📁 Checking launch agent files..."
for agent in com.gabriel.mem0-services.plist com.gabriel.mem0-apple-intelligence.plist; do
    if [[ -f "$LAUNCH_AGENTS_DIR/$agent" ]]; then
        echo "✅ $agent exists"
    else
        echo "❌ $agent missing"
    fi
done

echo ""
echo "🔍 Checking if agents are loaded..."
launchctl list | grep mem0 || echo "❌ No mem0 agents loaded"

echo ""
echo "📋 Recent log entries:"
echo "Services log:"
tail -n 5 /tmp/mem0-services.log 2>/dev/null || echo "No services log yet"

echo ""
echo "FoundationModels log:"
tail -n 5 /tmp/mem0-apple-intelligence.log 2>/dev/null || echo "No FoundationModels log yet"

echo ""
echo "🐳 Docker containers:"
docker ps --filter "name=mem0" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "Docker not available"

echo ""
echo "🔌 Port checks:"
echo "Qdrant (6333):"
curl -s http://localhost:6333/health 2>/dev/null && echo "✅ Qdrant healthy on 6333" || echo "❌ Qdrant not responding on 6333"

echo "Qdrant (10333):"
curl -s http://localhost:10333/health 2>/dev/null && echo "✅ Qdrant healthy on 10333" || echo "❌ Qdrant not responding on 10333"

echo "Neo4j (7474):"
curl -s http://localhost:7474 2>/dev/null >/dev/null && echo "✅ Neo4j responding on 7474" || echo "❌ Neo4j not responding on 7474"

echo ""
echo "✨ Test complete!"