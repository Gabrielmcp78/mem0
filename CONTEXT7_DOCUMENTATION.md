# 🧠 Mem0 Apple Intelligence Integration - Context7 Documentation

## Overview

This documentation provides comprehensive Context7-compatible information for the **Mem0 Apple Intelligence Integration**, a complete solution that enables local on-device AI memory operations using Apple's Foundation Models framework with persistent MCP server connections and interactive knowledge graph visualization.

## 🚀 Quick Start with Context7

When using Context7 with this integration, simply add `use context7` to your prompts:

```
Set up mem0 with Apple Intelligence for local memory operations. use context7
```

```
Create an MCP server that connects persistently to Qdrant database. use context7
```

```
Build a knowledge graph visualization for mem0 memories. use context7
```

## 📋 Core Components

### 1. Apple Intelligence LLM Provider (`mem0/llms/apple_intelligence.py`)

**Purpose**: On-device text generation using Apple's Foundation Models framework

**Key Features**:
- Local processing with Neural Engine optimization
- Graceful fallback when Apple Intelligence unavailable  
- Full LLMBase interface compliance
- Automatic availability detection

**Usage Example**:
```python
from mem0.llms.apple_intelligence import AppleIntelligenceLLM

# Initialize with automatic configuration
llm = AppleIntelligenceLLM()

# Generate response locally
response = llm.generate_response([
    {"role": "user", "content": "Extract key facts from this text"}
])
```

**Configuration**:
```python
config = {
    "model": "apple-intelligence-foundation",
    "temperature": 0.3,
    "max_tokens": 1500,
    "enable_neural_engine": True,
    "privacy_mode": "strict"
}
```

### 2. Apple Intelligence Embeddings (`mem0/embeddings/apple_intelligence.py`)

**Purpose**: Local embedding generation using Apple's Foundation Models

**Key Features**:
- On-device embedding generation
- Neural Engine optimization
- Configurable dimensions (default: 1536)
- Memory action-specific embeddings

**Usage Example**:
```python
from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder

embedder = AppleIntelligenceEmbedder()
embeddings = embedder.embed("Important memory content", memory_action="add")
```

### 3. Simple MCP Server (`simple_mcp_server.py`)

**Purpose**: Streamlined MCP server with Apple Intelligence integration

**Key Features**:
- Persistent Qdrant database connections
- Automatic Apple Intelligence detection
- Health monitoring and graceful fallbacks
- Full MCP protocol compliance

**MCP Tools Available**:
- `test_connection` - Check server and database status
- `add_memory` - Add new memories with Apple Intelligence
- `search_memories` - Search existing memories
- `get_all_memories` - Retrieve all user memories
- `get_graph_data` - Export knowledge graph data

**Usage Example**:
```bash
# Start the MCP server
python3 simple_mcp_server.py

# Test connection via MCP protocol
{"method": "tools/call", "params": {"name": "test_connection"}}
```

**Claude Desktop Configuration**:
```json
{
  "mcpServers": {
    "mem0-apple-intelligence": {
      "command": "python3",
      "args": ["/path/to/mem0/simple_mcp_server.py"]
    }
  }
}
```

### 4. Knowledge Graph Memory (`mem0/memory/graph_memory.py`)

**Purpose**: Neo4j-based graph memory with Apple Intelligence integration

**Key Features**:
- Entity extraction using Apple Intelligence
- Relationship mapping and storage
- Vector similarity search
- BM25 reranking for graph queries

**Usage Example**:
```python
config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": "bolt://localhost:7687"}
    },
    "llm": {"provider": "apple_intelligence"},
    "embedder": {"provider": "apple_intelligence"}
}

graph_memory = MemoryGraph(config)
result = graph_memory.add("User loves Python programming", {"user_id": "gabriel"})
```

## 🔧 Configuration Patterns

### Basic Apple Intelligence Setup

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "apple_intelligence",
        "config": {
            "model": "apple-intelligence-foundation",
            "temperature": 0.3,
            "max_tokens": 1500
        }
    },
    "embedder": {
        "provider": "apple_intelligence", 
        "config": {
            "model": "apple-intelligence-embeddings"
        }
    }
}

memory = Memory.from_config(config)
```

### MCP Server with Persistent Connections

```python
from simple_mcp_server import SimpleMCPServer

# Server automatically detects and configures:
# - Apple Intelligence availability
# - Qdrant database connection (localhost:10333)
# - Graceful fallbacks for missing components

server = SimpleMCPServer()
await server.run()
```

### Database Connection with Health Monitoring

```python
# Automatic Qdrant detection and connection
import requests

try:
    response = requests.get("http://localhost:10333/collections", timeout=2)
    if response.status_code == 200:
        # Use Qdrant with persistent connections
        config["vector_store"] = {
            "provider": "qdrant",
            "config": {
                "host": "localhost",
                "port": 10333,
                "collection_name": "gabriel_memories"
            }
        }
except:
    # Graceful fallback to in-memory storage
    pass
```

## 🛠️ Development Setup

### Prerequisites

```bash
# Ensure Apple Intelligence is available (macOS 15.1+)
python3 -c "from mem0.utils.apple_intelligence import check_apple_intelligence_availability; print(check_apple_intelligence_availability())"

# Start required databases
docker run -p 10333:6333 qdrant/qdrant
docker run -p 7687:7687 neo4j/neo4j
```

### Installation

```bash
# Install mem0 with Apple Intelligence support
pip install mem0ai

# Install additional dependencies
pip install qdrant-client neo4j langchain-neo4j rank-bm25

# Clone integration files
git clone https://github.com/mem0ai/mem0.git
cd mem0/integrations/mcp
```

### Testing

```bash
# Test Apple Intelligence availability
python3 -c "from mem0.llms.apple_intelligence import is_apple_intelligence_llm_available; print(is_apple_intelligence_llm_available())"

# Test MCP server
python3 test_mcp_simple.py

# Test database connections
python3 test_memory_persistence_robustness.py
```

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude MCP    │───▶│ Simple MCP      │───▶│ Apple Intel.    │
│     Client      │    │    Server       │    │ Foundation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │  Persistent     │───▶│   On-Device     │
                    │  Connections    │    │   Processing    │
                    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │ Qdrant Vector   │    │ Knowledge Graph │
                    │   Database      │    │   Visualization │
                    └─────────────────┘    └─────────────────┘
```

## 🔍 Error Handling & Fallbacks

### Apple Intelligence Unavailable

```python
try:
    from mem0.llms.apple_intelligence import AppleIntelligenceLLM
    llm = AppleIntelligenceLLM()
    if not llm.is_available:
        # Automatic fallback to default models
        from mem0 import Memory
        memory = Memory()  # Uses default configuration
except Exception as e:
    print(f"Fallback initialized: {e}")
```

### Database Connection Issues

```python
# MCP server handles connection failures gracefully
{
    "status": "Connected", 
    "qdrant_available": False,  # Will use in-memory storage
    "apple_intelligence_available": True,
    "features": ["basic_memory_operations", "apple_intelligence", "default_storage"]
}
```

## 📈 Performance Optimization

### Neural Engine Utilization

```python
# Enable Neural Engine optimization
config = {
    "embedder": {
        "provider": "apple_intelligence",
        "config": {
            "neural_engine_optimization": True,
            "privacy_mode": "strict",
            "batch_size": 1  # Optimal for Neural Engine
        }
    }
}
```

### Connection Pooling

```python
# MCP server maintains persistent connections
class SimpleMCPServer:
    def _setup_memory(self):
        # Connection is maintained throughout server lifecycle
        self.memory = Memory.from_config(config)
        # Health checks every 30 seconds
```

## 🚀 Production Deployment

### Environment Variables

```bash
export QDRANT_URL="http://localhost:10333"
export QDRANT_COLLECTION="gabriel_memories"
export APPLE_INTELLIGENCE_ENABLED="true"
```

### Docker Configuration

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "10333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
      
  mem0-mcp:
    build: .
    depends_on:
      - qdrant
    environment:
      - QDRANT_URL=http://qdrant:6333
```

## 🧪 Testing Framework

### Unit Tests

```python
# Test Apple Intelligence availability
def test_apple_intelligence_available():
    from mem0.utils.apple_intelligence import check_apple_intelligence_availability
    assert check_apple_intelligence_availability() is not None

# Test MCP server functionality  
async def test_mcp_server():
    server = SimpleMCPServer()
    result = await server.test_connection()
    assert "Connected" in result[0].text
```

### Integration Tests

```python
# Test end-to-end memory operations
def test_memory_persistence():
    memory = Memory.from_config(apple_intelligence_config)
    
    # Add memory
    result = memory.add("Test memory content", user_id="test_user")
    assert result is not None
    
    # Search memory
    results = memory.search("test", user_id="test_user")
    assert len(results) > 0
```

## 📚 API Reference

### Memory Operations

```python
# Add memory with Apple Intelligence
memory.add(
    messages="User prefers Python over JavaScript",
    user_id="gabriel"
)

# Search memories
results = memory.search(
    query="programming preferences", 
    user_id="gabriel",
    limit=10
)

# Get all memories
all_memories = memory.get_all(user_id="gabriel")
```

### MCP Tools

```python
# Via MCP protocol
{
    "method": "tools/call",
    "params": {
        "name": "add_memory",
        "arguments": {
            "messages": "Important information to remember",
            "user_id": "gabriel"
        }
    }
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Apple Intelligence Not Available**
   - Ensure macOS 15.1+ with compatible hardware
   - Check System Settings > Apple Intelligence

2. **Database Connection Failed**
   - Verify Qdrant is running: `curl http://localhost:10333/collections`
   - Check Docker containers: `docker ps`

3. **MCP Server Not Responding**
   - Check logs: `tail -f logs/mcp_server.log`
   - Verify Python path in Claude Desktop config

### Debug Commands

```bash
# Test individual components
python3 -c "from mem0.llms.apple_intelligence import AppleIntelligenceLLM; print(AppleIntelligenceLLM().is_available)"

# Test MCP server
python3 simple_mcp_server.py

# Check database connectivity
curl -X GET http://localhost:10333/collections
```

## 📄 License

This integration follows the mem0 project licensing terms. Apple Intelligence features require macOS 15.1+ and compatible hardware.

---

*For the most up-to-date information and examples, use Context7 by adding "use context7" to your prompts when working with this integration.*