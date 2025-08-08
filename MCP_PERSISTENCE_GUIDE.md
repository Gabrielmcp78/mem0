# MCP Server Persistence and Auto-Restart Guide

This guide explains how to configure the Apple Intelligence MCP server for maximum reliability with automatic startup, persistence, and auto-restart capabilities.

## 🔄 Persistence Features

### Automatic Startup
The MCP server is configured to start automatically when Claude Desktop launches, ensuring your Apple Intelligence memory system is always available.

### Auto-Restart on Failure
If the MCP server crashes or fails, Claude Desktop will automatically restart it, maintaining continuous service.

### Health Monitoring
Regular health checks ensure the server is responsive and restart it if it becomes unresponsive.

## ⚙️ Configuration Options

### Core Persistence Settings

```json
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "persistent": true,           // Keep server running persistently
      "autoRestart": true,          // Auto-restart on failure
      "maxRestarts": 5,             // Max restart attempts
      "restartDelay": 2000,         // Delay between restarts (ms)
      "initTimeout": 10000,         // Server initialization timeout (ms)
      "timeout": 30000              // Request timeout (ms)
    }
  }
}
```

### Health Check Configuration

```json
{
  "healthCheck": {
    "enabled": true,                // Enable health monitoring
    "interval": 30000,              // Check every 30 seconds
    "timeout": 5000                 // Health check timeout (ms)
  }
}
```

## 📋 Complete Configuration Example

### Development Configuration
```json
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "command": "python",
      "args": ["/path/to/mem0/integrations/mcp/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "gabriel_apple_intelligence_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/path/to/mem0"
      },
      "disabled": false,
      "persistent": true,
      "autoRestart": true,
      "maxRestarts": 5,
      "restartDelay": 2000,
      "alwaysAllow": [
        "test_connection",
        "add_memory",
        "search_memories",
        "get_all_memories",
        "update_memory",
        "delete_memory",
        "get_memory_history"
      ],
      "timeout": 30000,
      "initTimeout": 10000,
      "healthCheck": {
        "enabled": true,
        "interval": 30000,
        "timeout": 5000
      }
    }
  }
}
```

### Production Configuration
```json
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "command": "python",
      "args": ["/path/to/mem0/integrations/mcp/server.py"],
      "env": {
        "QDRANT_URL": "https://your-qdrant-cluster.qdrant.io",
        "QDRANT_API_KEY": "your-qdrant-api-key",
        "QDRANT_COLLECTION": "production_apple_intelligence_memories",
        "APPLE_INTELLIGENCE_ENABLED": "auto",
        "LOG_LEVEL": "INFO",
        "OPENAI_API_KEY": "sk-fallback-key-here"
      },
      "disabled": false,
      "persistent": true,
      "autoRestart": true,
      "maxRestarts": 3,
      "restartDelay": 3000,
      "alwaysAllow": [
        "test_connection",
        "add_memory",
        "search_memories",
        "get_all_memories",
        "update_memory",
        "delete_memory",
        "get_memory_history"
      ],
      "timeout": 30000,
      "initTimeout": 15000,
      "healthCheck": {
        "enabled": true,
        "interval": 60000,
        "timeout": 10000
      }
    }
  }
}
```

## 🔧 Configuration Parameters Explained

### Persistence Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `persistent` | boolean | `true` | Keep the MCP server running persistently |
| `autoRestart` | boolean | `true` | Automatically restart the server if it fails |
| `maxRestarts` | integer | `5` | Maximum number of restart attempts |
| `restartDelay` | integer | `2000` | Delay between restart attempts (milliseconds) |
| `initTimeout` | integer | `10000` | Timeout for server initialization (milliseconds) |

### Health Check Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `healthCheck.enabled` | boolean | `true` | Enable health monitoring |
| `healthCheck.interval` | integer | `30000` | Health check interval (milliseconds) |
| `healthCheck.timeout` | integer | `5000` | Health check timeout (milliseconds) |

### Timeout Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | integer | `30000` | Request timeout (milliseconds) |
| `initTimeout` | integer | `10000` | Server initialization timeout (milliseconds) |

## 🚀 Automatic Setup

### Using Quick Start Script

The `quick_start.sh` script automatically configures persistence:

```bash
./quick_start.sh
```

This script:
1. Creates and activates Python virtual environment
2. Installs dependencies
3. Tests Apple Intelligence
4. Starts Qdrant if needed
5. Configures Claude Desktop with persistence settings
6. Tests the MCP server

### Using Full Startup Script

The `start_apple_intelligence_system.sh` script provides comprehensive setup:

```bash
./start_apple_intelligence_system.sh
```

This script includes all quick start features plus:
1. System requirements checking
2. Comprehensive testing
3. Status monitoring
4. Detailed logging

## 📊 Monitoring and Troubleshooting

### Checking Server Status

1. **Claude Desktop Logs**: Check Claude Desktop logs for MCP server status
2. **Health Check Status**: Monitor health check results in logs
3. **Restart Count**: Track restart attempts and failures

### Common Issues and Solutions

#### Server Won't Start
- Check Python path and virtual environment
- Verify dependencies are installed
- Check file permissions
- Review initialization timeout settings

#### Frequent Restarts
- Check Apple Intelligence availability
- Verify Qdrant connection
- Review server logs for errors
- Increase `initTimeout` if needed

#### Health Check Failures
- Verify server responsiveness
- Check network connectivity
- Adjust health check timeout
- Review server resource usage

### Log Analysis

Look for these log messages:

```
✅ Apple Intelligence Foundation Models detected and available
✅ Memory initialized with real Apple Intelligence Foundation Model providers
🍎 Apple Intelligence Memory system ready for MCP operations
```

## 🔄 Restart Behavior

### Automatic Restart Triggers
- Server process crashes
- Health check failures
- Initialization timeouts
- Unhandled exceptions

### Restart Process
1. Server failure detected
2. Wait for `restartDelay` milliseconds
3. Attempt restart (up to `maxRestarts` times)
4. If all restarts fail, mark server as failed
5. Log restart attempts and outcomes

### Restart Limits
- Development: 5 restarts with 2-second delay
- Production: 3 restarts with 3-second delay
- After max restarts: Server marked as failed

## 🛡️ Best Practices

### Development Environment
- Use higher `maxRestarts` (5) for development
- Shorter `restartDelay` (2000ms) for faster iteration
- More frequent health checks (30s) for quick feedback

### Production Environment
- Use conservative `maxRestarts` (3) to avoid resource waste
- Longer `restartDelay` (3000ms) to allow system recovery
- Less frequent health checks (60s) to reduce overhead

### Monitoring
- Enable health checks in all environments
- Monitor restart frequency and patterns
- Set up alerts for repeated failures
- Review logs regularly for issues

## 📞 Support

If you experience persistent issues:

1. Check the [troubleshooting guide](integrations/mcp/README.md#troubleshooting)
2. Review server logs and restart patterns
3. Test Apple Intelligence availability
4. Verify system requirements
5. Contact support with log details

The persistence configuration ensures your Apple Intelligence memory system remains available and reliable for continuous use with Claude Desktop.