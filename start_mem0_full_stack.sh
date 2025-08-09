#!/bin/bash

# Gabriel's Full Stack Mem0 System Startup Script
# Starts all three databases and the MCP server

set -e

echo "🚀 Starting Gabriel's Full Stack Mem0 System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Checking ${service_name} on port ${port}...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            echo -e "${GREEN}✅ ${service_name} is running on port ${port}${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Waiting for ${service_name} (attempt ${attempt}/${max_attempts})...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ ${service_name} failed to start on port ${port}${NC}"
    return 1
}

# Start Qdrant
echo -e "${BLUE}Starting Qdrant Vector Database...${NC}"
if ! pgrep -f "qdrant" > /dev/null; then
    docker run -d --name qdrant-mem0 \
        -p 6333:6333 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant:latest
    
    check_service "Qdrant" 6333
else
    echo -e "${GREEN}✅ Qdrant already running${NC}"
fi

# Start Neo4j
echo -e "${BLUE}Starting Neo4j Graph Database...${NC}"
if ! pgrep -f "neo4j" > /dev/null; then
    docker run -d --name neo4j-mem0 \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password \
        -v $(pwd)/neo4j_data:/data \
        -v $(pwd)/neo4j_logs:/logs \
        neo4j:latest
    
    check_service "Neo4j HTTP" 7474
    check_service "Neo4j Bolt" 7687
else
    echo -e "${GREEN}✅ Neo4j already running${NC}"
fi

# SQLite is file-based, no service to start
echo -e "${GREEN}✅ SQLite ready (file-based)${NC}"

# Verify Python environment
echo -e "${BLUE}Checking Python environment...${NC}"
if python3 -c "import mem0; print('mem0 version:', mem0.__version__)" 2>/dev/null; then
    echo -e "${GREEN}✅ mem0 Python package available${NC}"
else
    echo -e "${RED}❌ mem0 Python package not found${NC}"
    echo -e "${YELLOW}Installing mem0...${NC}"
    pip3 install -e .
fi

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY environment variable not set${NC}"
    echo -e "${YELLOW}Please set your OpenAI API key:${NC}"
    echo "export OPENAI_API_KEY='your-key-here'"
    exit 1
else
    echo -e "${GREEN}✅ OpenAI API key configured${NC}"
fi

# Test the full stack
echo -e "${BLUE}Testing full stack integration...${NC}"
python3 -c "
import sys
sys.path.insert(0, '.')
from mem0 import Memory
from mem0.configs.base import MemoryConfig
import json

config = {
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'collection_name': 'gabriel_apple_intelligence_memories',
            'host': 'localhost',
            'port': 6333,
            'embedding_model_dims': 1536
        }
    },
    'graph_store': {
        'provider': 'neo4j',
        'config': {
            'url': 'bolt://localhost:7687',
            'username': 'neo4j',
            'password': 'password'
        }
    },
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'gpt-4o-mini',
            'temperature': 0.1
        }
    },
    'embedder': {
        'provider': 'openai',
        'config': {
            'model': 'text-embedding-3-small',
            'embedding_dims': 1536
        }
    },
    'version': 'v1.1'
}

try:
    memory = Memory.from_config(config)
    print('✅ Full stack mem0 system initialized successfully!')
    print('📊 Architecture: Qdrant + Neo4j + SQLite')
    print('🧠 Features: Semantic search, Entity relationships, Memory deduplication')
except Exception as e:
    print(f'❌ Full stack initialization failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 Full Stack Mem0 System is ready!${NC}"
    echo -e "${BLUE}Architecture:${NC}"
    echo -e "  📊 Qdrant (Vector): localhost:6333"
    echo -e "  🕸️  Neo4j (Graph): localhost:7474 (HTTP), localhost:7687 (Bolt)"
    echo -e "  🗄️  SQLite (Metadata): ./mem0_history.db"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Update Claude Desktop config to use the full stack server"
    echo "2. Test with: node integrations/mcp/mem0_full_stack_server.js"
    echo ""
    echo -e "${GREEN}System Status: READY ✅${NC}"
else
    echo -e "${RED}❌ System startup failed${NC}"
    exit 1
fi