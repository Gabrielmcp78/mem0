# Mem0 Documentation

Welcome to the comprehensive documentation for Mem0 - The Memory Layer for Personalized AI.

## 📚 Documentation Structure

### Quick Start
- [Installation Guide](guides/installation.md)
- [Basic Usage](guides/basic-usage.md)
- [Configuration](guides/configuration.md)

### API Reference
- [Core API](api/core.md)
- [Memory Operations](api/memory.md)
- [Search & Retrieval](api/search.md)
- [User Management](api/users.md)

### Integration Guides
- [Agent Frameworks](INTEGRATIONS.md#agent-frameworks)
- [MCP Server](INTEGRATIONS.md#mcp-server)
- [UI Components](INTEGRATIONS.md#ui-components)
- [Custom Implementations](INTEGRATIONS.md#custom)

### Deployment
- [Production Setup](DEPLOYMENT.md#production)
- [Docker Deployment](DEPLOYMENT.md#docker)
- [Kubernetes](DEPLOYMENT.md#kubernetes)
- [Scaling Considerations](DEPLOYMENT.md#scaling)

### Examples
- [Basic Chat Bot](../examples/basic-chatbot/)
- [Customer Support](../examples/customer-support/)
- [Multi-Agent Systems](../examples/multi-agent/)

## 🚀 Getting Started

```python
from mem0 import Memory

# Initialize memory
memory = Memory()

# Add memories
memory.add("User prefers dark mode", user_id="user123")

# Search memories
results = memory.search("preferences", user_id="user123")
```

## 🔗 Quick Links

- [GitHub Repository](https://github.com/mem0ai/mem0)
- [Discord Community](https://mem0.dev/DiG)
- [Live Demo](https://mem0.dev/demo)
- [API Documentation](https://docs.mem0.ai)

## 📖 Additional Resources

- [Research Paper](https://mem0.ai/research)
- [Blog Posts](https://mem0.ai/blog)
- [Video Tutorials](https://mem0.ai/tutorials)