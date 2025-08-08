# 🍎 Gabriel's Apple Intelligence Memory System

A complete local AI memory ecosystem that integrates Apple Intelligence with Claude Desktop, Kiro IDE, and Chrome Extension. Everything runs privately on your Mac.

## 🚀 Quick Start

**Ready to use in 3 steps:**

1. **Copy Claude Desktop configuration:**
   ```bash
   cp claude-desktop-config-ready.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Restart Claude Desktop**

3. **Test in Claude:**
   ```
   Please test the Apple Intelligence memory connection
   ```

## 📖 Complete Documentation

**👉 See [SETUP_GUIDE.md](SETUP_GUIDE.md) for the complete setup and usage guide.**

## 🏗️ What You Get

- **🍎 Apple Intelligence Integration** - Uses your Mac's Neural Engine
- **🧠 Persistent Memory** - Remembers across all conversations  
- **🔒 100% Private** - No external API calls, all local processing
- **⚡ Multi-Platform** - Works with Claude Desktop, Kiro IDE, and Chrome
- **🗄️ Local Infrastructure** - PostgreSQL, Redis, Qdrant, Ollama

## 🎯 Key Features

- **Intelligent Memory Storage** - Apple Intelligence processes and stores meaningful context
- **Semantic Search** - Find memories by meaning, not just keywords
- **Session Tracking** - Remembers which AI agent created each memory
- **Project Context** - Kiro IDE integration for development workflows
- **Web Memory** - Chrome extension for browsing context

## 📁 Architecture

```
🍎 Apple Intelligence (Neural Engine)
    ↕️ MCP Protocol  
🔧 Kiro IDE ←→ 🤖 Claude Desktop ←→ 🌐 Chrome Extension
    ↕️ Node.js MCP Server
    ↕️ Python Memory Backend
🗄️ Local Infrastructure
```

## 🛠️ Status

- ✅ **Infrastructure**: Deployed and tested
- ✅ **Apple Intelligence**: Integrated and working
- ✅ **Claude Desktop**: MCP server ready
- ✅ **Kiro IDE**: Specialized integration available
- ✅ **Chrome Extension**: Local migration guide provided

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and usage (START HERE)
- **[KIRO_MEMORY_INTEGRATION_PLAN.md](KIRO_MEMORY_INTEGRATION_PLAN.md)** - Kiro IDE integration details
- **[integrations/chrome-extension/LOCAL_MIGRATION_GUIDE.md](integrations/chrome-extension/LOCAL_MIGRATION_GUIDE.md)** - Chrome extension setup

## 🧪 Testing

Test your deployment:
```bash
python3 test_deployment.py
```

## 🎉 Ready to Use

Your Apple Intelligence memory system is production-ready and waiting for you to explore the future of private, intelligent AI memory! 🚀