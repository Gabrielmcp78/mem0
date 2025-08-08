# Mem0 MCP Server with Apple Intelligence

🍎 **Apple Intelligence Integration Complete!** Model Context Protocol (MCP) server for Mem0 memory operations with native Apple Intelligence Foundation Models support, providing seamless integration with Claude Desktop and Kiro IDE.

## ✅ What's New - Apple Intelligence Integration

- **🍎 Native Apple Intelligence**: Complete on-device processing with Foundation Models
- **🧠 Neural Engine Optimization**: Leverages Apple's Neural Engine for optimal performance  
- **🔒 Privacy First**: Zero external API calls - everything processed locally on-device
- **⚡ Automatic Detection**: Seamlessly detects and uses Apple Intelligence when available
- **🔄 Graceful Fallback**: Falls back to default providers if Apple Intelligence unavailable

## 🚀 Quick Start

### 1. System Requirements

**For Apple Intelligence (Recommended)**:
- macOS 15.1 or later
- Apple Silicon (M1, M2, M3, M4)
- PyObjC for Foundation Models access

**Alternative**: Works on any system with fallback providers

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install mem0ai mcp pyobjc

# Install Node.js dependencies (for Node.js server)
npm install
```

### 3. Verify Apple Intelligence

```bash
# Test Apple Intelligence availability
python -c "from mem0.utils.apple_intelligence import check_apple_intelligence_availability; print(f'🍎 Apple Intelligence Available: {check_apple_intelligence_availability()}')"
```

### 4. Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "Mem0 Local -M26": {
      "command": "node",
      "args": ["/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp/server.js"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "gabriel_apple_intelligence_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/Volumes/Ready500/DEVELOPMENT/mem0"
      },
      "disabled": false,
      "alwaysAllow": [
        "test_connection",
        "add_memory",
        "search_memories",
        "get_all_memories",
        "update_memory",
        "delete_memory",
        "get_memory_history"
      ],
      "timeout": 30000
    }
  }
}
```

### 5. Start the System

```bash
# Start Qdrant (if using vector storage)
docker run -p 6333:6333 qdrant/qdrant

# Start Python MCP server (recommended)
python integrations/mcp/server.py

# Or use Node.js server (calls Python backend)
node integrations/mcp/server.js
```

## 🍎 Apple Intelligence Features

### Automatic Configuration

When Apple Intelligence is available, the server automatically configures:

```python
config = {
    "llm": {
        "provider": "apple_intelligence",
        "config": {
            "model": "apple-intelligence-foundation",
            "max_tokens": 500,
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 50
        }
    },
    "embedder": {
        "provider": "apple_intelligence",
        "config": {
            "model": "apple-intelligence-embeddings",
            "embedding_dims": 1536
        }
    }
}
```

### Status Verification

Use the `test_connection` tool to verify Apple Intelligence status:

```json
{
  "status": "Connected",
  "apple_intelligence_available": true,
  "foundation_models_integration": true,
  "neural_engine_optimized": true,
  "actual_providers": {
    "llm": "apple_intelligence",
    "embedder": "apple_intelligence"
  },
  "message": "Gabriel's local memory system with Apple Intelligence Foundation Models is online and ready!"
}
```

## 🛠 Available Tools

### Core Memory Operations

All tools now use Apple Intelligence for processing:

- **`test_connection`**: Test server connectivity and Apple Intelligence status
- **`add_memory`**: Store new memories with Apple Intelligence processing
- **`search_memories`**: Search memories using Apple Intelligence embeddings  
- **`get_all_memories`**: Retrieve all memories for a user
- **`update_memory`**: Update existing memories with Apple Intelligence
- **`delete_memory`**: Delete specific memories
- **`delete_all_memories`**: Clear all memories for a user
- **`get_memory_history`**: View memory operation history

### Multi-Agent Support

All tools support multi-agent scenarios:
- **`user_id`**: Unique user identifier (default: "gabriel")
- **`agent_id`**: Agent identifier for multi-agent scenarios
- **`run_id`**: Session/run identifier for context tracking
- **`metadata`**: Custom metadata as JSON string

Apple Intelligence processing metadata is automatically added:
```json
{
  "processed_by": "apple_intelligence_foundation_models",
  "neural_engine_optimized": true
}
```

## 🖥 Server Options

### Python Server

- **File**: `server.py`
- **Features**: Full Apple Intelligence integration, direct mem0 API access
- **Best for**: Kiro IDE, direct MCP clients, development testing
- **Apple Intelligence**: ✅ Native support

### Node.js Server (Recommended for Claude Desktop) ⭐

- **File**: `server.js`  
- **Features**: MCP protocol wrapper that calls Python memory operations with Apple Intelligence backend
- **Best for**: Claude Desktop integration, web applications, Node.js environments
- **Apple Intelligence**: ✅ Via Python backend
- **Compatibility**: ✅ Optimized for Claude Desktop MCP protocol

### Kiro Server

- **File**: `kiro_server.py`
- **Features**: Project-aware memory management with Apple Intelligence
- **Best for**: Kiro IDE integration
- **Apple Intelligence**: ✅ Native support

## ⚙️ Configuration

### Environment Variables

- **`QDRANT_URL`**: Qdrant vector database URL (optional)
- **`QDRANT_COLLECTION`**: Collection name for memories (default: "gabriel_apple_intelligence_memories")
- **`APPLE_INTELLIGENCE_ENABLED`**: Enable/disable Apple Intelligence (default: auto-detect)
- **`LOG_LEVEL`**: Logging level (DEBUG, INFO, WARNING, ERROR)

### Apple Intelligence Settings

The system automatically optimizes for Apple Intelligence:
- **Neural Engine**: Enabled by default for optimal performance
- **Privacy Mode**: Strict mode ensures no external API calls
- **Local Processing**: All operations occur on-device
- **Fallback**: Automatic fallback to default providers if unavailable

## 🧪 Testing & Verification

### Comprehensive Test Suite

```bash
# Test Apple Intelligence integration
python test_apple_intelligence_mcp_integration.py

# Test MCP server functionality  
python test_mcp_server_integration.py

# Complete system integration test
python test_complete_integration.py

# Test Python MCP server specifically
python test_python_mcp_server.py
```

### Expected Test Results

```
🍎 Apple Intelligence Available: True
✅ LLM Provider: AppleIntelligenceLLM (Available: True)
✅ Embedder Provider: AppleIntelligenceEmbedder (Available: True)
✅ Memory initialized with Apple Intelligence: True
✅ Python MCP Server with Apple Intelligence: True
✅ All tests passed!
```

## 🔧 Troubleshooting

### Apple Intelligence Issues

1. **Check System Requirements**:
```bash
# Check macOS version (requires 15.1+)
sw_vers

# Check architecture (requires Apple Silicon)
uname -m  # Should show: arm64
```

2. **Verify Dependencies**:
```bash
# Test PyObjC installation
python -c "import objc; print('✅ PyObjC available')"

# Test Apple Intelligence availability
python -c "from mem0.utils.apple_intelligence import check_apple_intelligence_availability; print(f'🍎 Available: {check_apple_intelligence_availability()}')"
```

3. **Check Server Logs**:
```bash
# Look for Apple Intelligence status messages
python server.py 2>&1 | grep -E "(Apple Intelligence|Foundation Models)"
```

### Common Solutions

| Issue | Solution |
|-------|----------|
| "Apple Intelligence not available" | Ensure macOS 15.1+ and Apple Silicon |
| "PyObjC not found" | Install with `pip install pyobjc` |
| Memory operations fail | Check Qdrant connection and configuration |
| Claude Desktop connection issues | Verify MCP configuration and file paths |
| Fallback providers used | Check Apple Intelligence availability and logs |

## 📊 Performance & Privacy

### Apple Intelligence Benefits

- **🚀 Performance**: Neural Engine optimization for faster processing
- **🔒 Privacy**: Complete on-device processing, no external API calls
- **💰 Cost**: No API costs for LLM or embedding operations
- **⚡ Speed**: Local processing eliminates network latency
- **🔋 Efficiency**: Optimized for Apple Silicon power efficiency

### Monitoring

The system provides detailed logging:
```
🍎 Apple Intelligence Foundation Models detected and available
✅ Memory initialized with real Apple Intelligence Foundation Model providers
🍎 Apple Intelligence Memory system ready for MCP operations with Foundation Models
```

## 🚀 Production Deployment

### Claude Desktop Production Config

```json
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "command": "python",
      "args": ["/path/to/mem0/integrations/mcp/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "production_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "timeout": 30000
    }
  }
}
```

### Kiro IDE Integration

For Kiro IDE, use the Python server directly:
```python
# Kiro will automatically detect and use the MCP server
# No additional configuration needed
```

## 📚 Documentation & Support

- **🍎 Apple Intelligence Guide**: [Apple Intelligence Integration](APPLE_INTELLIGENCE_INTEGRATION.md)
- **📖 Full Documentation**: [docs.mem0.ai/integrations/mcp](https://docs.mem0.ai/integrations/mcp)
- **🐛 Issues**: [GitHub Issues](https://github.com/mem0ai/mem0/issues)
- **💬 Community**: [Discord](https://mem0.dev/DiG)
- **📧 Contact**: founders@mem0.ai

## 🎉 What's Next

The Apple Intelligence integration is complete and ready for production use! Future enhancements are tracked in [FUTURE_FEATURES.md](../../FUTURE_FEATURES.md) and include:

- Enhanced unit testing
- Performance optimizations
- Additional privacy features
- Chrome extension integration

**Start using Apple Intelligence with Mem0 today!** 🚀