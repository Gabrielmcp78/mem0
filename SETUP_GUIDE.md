# 🍎 Gabriel's Apple Intelligence Memory System - Complete Setup Guide

## Overview

This is your complete local Apple Intelligence memory system that integrates with Claude Desktop and Kiro IDE. Everything runs locally on your Mac with full privacy.

## 🏗️ Architecture

```
🍎 Apple Intelligence (Neural Engine)
    ↕️ MCP Protocol
🔧 Kiro IDE ←→ 🤖 Claude Desktop ←→ 🌐 Chrome Extension
    ↕️ Node.js MCP Server (server.js)
    ↕️ Python Memory Backend (memory_operations.py)
🗄️ Local Infrastructure: PostgreSQL + Redis + Qdrant + Ollama
```

## 🚀 Quick Start

### 1. Infrastructure Status
Your infrastructure is already deployed and working:
- ✅ PostgreSQL: localhost:25432
- ✅ Redis: localhost:26379  
- ✅ Qdrant: localhost:26333
- ✅ Ollama: localhost:11434

### 2. Configure Claude Desktop

Copy the configuration to Claude Desktop:

```bash
cp claude-desktop-config-ready.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Configuration Details:**
```json
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "command": "node",
      "args": ["/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp/server.js"],
      "env": {
        "QDRANT_URL": "http://localhost:26333",
        "QDRANT_COLLECTION": "gabriel_apple_intelligence_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true",
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

### 3. Restart Claude Desktop

### 4. Test the System

In Claude Desktop, say:
```
Please test the Apple Intelligence memory connection
```

You should see a successful connection message.

## 🛠️ System Components

### Node.js MCP Server (`integrations/mcp/server.js`)
- **Purpose**: Reliable MCP protocol interface for Claude Desktop
- **Technology**: Node.js with @modelcontextprotocol/sdk
- **Function**: Handles MCP communication and calls Python backend

### Python Memory Backend (`integrations/mcp/memory_operations.py`)
- **Purpose**: Apple Intelligence memory processing
- **Technology**: Python with Mem0 library
- **Function**: Actual memory operations with Apple Intelligence integration

### Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `test_connection` | Verify system status | Test if everything is working |
| `add_memory` | Store new memories | "Remember that I prefer TypeScript" |
| `search_memories` | Find relevant memories | "What do you remember about my preferences?" |
| `get_all_memories` | List all stored memories | "Show me everything you remember" |
| `update_memory` | Modify existing memory | Update specific memory by ID |
| `delete_memory` | Remove specific memory | Delete memory by ID |
| `get_memory_history` | View operation history | See memory operation timeline |

## 🔧 Advanced Configuration

### Kiro IDE Integration
For Kiro IDE integration, use the specialized server:
```json
{
  "mcpServers": {
    "kiro-memory": {
      "command": "python3",
      "args": ["/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp/kiro_server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:26333",
        "QDRANT_COLLECTION": "kiro_project_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true"
      },
      "alwaysAllow": [
        "set_project_context",
        "add_code_memory", 
        "search_project_memory",
        "add_learning_memory",
        "get_project_context_summary"
      ]
    }
  }
}
```

### Chrome Extension Integration
The Chrome extension connects to your local API at `http://localhost:8000`. See `integrations/chrome-extension/LOCAL_MIGRATION_GUIDE.md` for setup details.

## 🧪 Testing & Verification

### Test MCP Server Directly
```bash
cd /Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node server.js
```

### Test Python Backend
```bash
cd /Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp
python3 memory_operations.py get_all_memories '{"user_id": "gabriel", "limit": 5}'
```

### Test Infrastructure
```bash
cd /Volumes/Ready500/DEVELOPMENT/mem0
python3 test_deployment.py
```

## 🔒 Privacy & Security

- **100% Local Processing**: No external API calls
- **Apple Intelligence**: Uses your Mac's Neural Engine
- **Private Storage**: All data stored locally in Qdrant
- **No Cloud Dependencies**: Completely self-contained system

## 📁 File Structure

```
/Volumes/Ready500/DEVELOPMENT/mem0/
├── integrations/mcp/
│   ├── server.js                 # Node.js MCP server (main)
│   ├── memory_operations.py      # Python memory backend
│   ├── kiro_server.py            # Kiro IDE specialized server
│   └── package.json              # Node.js dependencies
├── claude-desktop-config-ready.json  # Claude Desktop configuration
├── test_deployment.py            # Infrastructure test script
└── SETUP_GUIDE.md               # This file (single source of truth)
```

## 🚨 Troubleshooting

### Claude Desktop Not Showing Tools
1. Check configuration file location: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Restart Claude Desktop completely
3. Check Node.js is installed: `node --version`

### Memory Operations Failing
1. Verify infrastructure: `python3 test_deployment.py`
2. Check Python dependencies: `pip3 show mem0ai`
3. Test Python backend directly (see Testing section above)

### Connection Issues
1. Ensure all services are running (PostgreSQL, Redis, Qdrant, Ollama)
2. Check ports are not blocked by firewall
3. Verify file paths in configuration are correct

## 🎯 Usage Examples

### Basic Memory Operations
```
# Add a memory
"Remember that I'm working on a local AI memory system with Apple Intelligence"

# Search memories  
"What do you remember about my AI projects?"

# Get all memories
"Show me everything you remember about me"
```

### Development Context
```
# With Kiro IDE integration
"Remember this code pattern for future TypeScript projects"
"What debugging approaches have worked for me before?"
```

## 🔄 Migration from Managed Service

If you have existing memories in the managed Mem0 service, use:
```bash
python3 tools/migrate_from_managed.py --api-key your-key --user-id your-id
```

## 🎉 You're Ready!

Your Apple Intelligence memory system is now fully configured and ready to provide persistent, intelligent memory across all your AI interactions. Enjoy your private, local AI ecosystem! 🍎🧠✨