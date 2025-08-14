#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Mem0 FoundationModels Setup Verification"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success_count=0
total_checks=0

check() {
    local name="$1"
    local command="$2"
    total_checks=$((total_checks + 1))
    
    echo -n "Checking $name... "
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        success_count=$((success_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
}

echo ""
echo "📋 System Requirements"
echo "----------------------"

check "macOS version" "sw_vers -productVersion | grep -E '^1[5-9]\.|^[2-9][0-9]\.' >/dev/null"
check "Apple Silicon" "uname -m | grep -E '^arm64' >/dev/null"
check "Docker" "docker --version"
check "Node.js" "node --version"
check "Python 3" "python3 --version"

echo ""
echo "📦 Dependencies"
echo "---------------"

check "mem0ai package" "python3 -c 'import mem0'"
check "mcp package" "python3 -c 'import mcp'"
check "PyObjC" "python3 -c 'import objc'"
check "Node MCP SDK" "node -e 'require(\"@modelcontextprotocol/sdk\")'"

echo ""
echo "🍎 FoundationModels"
echo "---------------------"

if python3 -c "
try:
    import Foundation
    import FoundationModels
    print('FoundationModels: Available')
except ImportError as e:
    print(f'FoundationModels: Not Available ({e})')
    exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✅ FoundationModels Available${NC}"
    success_count=$((success_count + 1))
else
    echo -e "${YELLOW}⚠️  FoundationModels Not Available (will use fallback)${NC}"
fi
total_checks=$((total_checks + 1))

echo ""
echo "🐳 Services"
echo "-----------"

check "Docker running" "docker info"
check "Qdrant container" "docker ps | grep qdrant"
check "Neo4j container" "docker ps | grep neo4j"

echo ""
echo "🔌 Service Health"
echo "-----------------"

check "Qdrant health (6333)" "curl -sf http://localhost:6333/health"
check "Qdrant health (10333)" "curl -sf http://localhost:10333/health"
check "Neo4j web (7474)" "curl -sf http://localhost:7474"

echo ""
echo "🚀 Launch Agents"
echo "----------------"

check "Services agent installed" "test -f ~/Library/LaunchAgents/com.gabriel.mem0-services.plist"
check "FoundationModels agent installed" "test -f ~/Library/LaunchAgents/com.gabriel.mem0-apple-intelligence.plist"
check "Services agent loaded" "launchctl list | grep mem0-services"
check "FoundationModels agent loaded" "launchctl list | grep mem0-apple-intelligence"

echo ""
echo "📁 Files"
echo "--------"

REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
check "start_mem0_services.sh" "test -x '$REPO_PATH/start_mem0_services.sh'"
check "MCP server" "test -f '$REPO_PATH/integrations/mcp/mem0_native_node_server.js'"
check "Foundation Models integration" "test -f '$REPO_PATH/integrations/mcp/core/foundation_models_integration.py'"

echo ""
echo "📊 Summary"
echo "----------"

if [ $success_count -eq $total_checks ]; then
    echo -e "${GREEN}🎉 All checks passed! ($success_count/$total_checks)${NC}"
    echo -e "${GREEN}Your Mem0 FoundationModels setup is ready!${NC}"
    exit 0
elif [ $success_count -gt $((total_checks * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠️  Most checks passed ($success_count/$total_checks)${NC}"
    echo -e "${YELLOW}Setup is mostly working but may have some issues.${NC}"
    exit 1
else
    echo -e "${RED}❌ Many checks failed ($success_count/$total_checks)${NC}"
    echo -e "${RED}Setup needs attention before it will work properly.${NC}"
    exit 2
fi