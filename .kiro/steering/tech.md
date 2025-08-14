# Technology Stack

## Core Technologies

### Python (Primary)

- **Version**: Python 3.9+ (specified in pyproject.toml)
- **Package Manager**: Hatch (primary), Poetry (legacy support)
- **Core Library**: `mem0ai` package with modular architecture

### Node.js/TypeScript (Secondary)

- **Package**: `mem0ai` npm package for JavaScript/TypeScript integration
- **Version**: Node.js 18+ required
- **Build Tool**: tsup for TypeScript compilation
- **Package Manager**: pnpm preferred

## Infrastructure Components

### Vector Databases

- **Qdrant** (primary): Vector storage and semantic search
- **Alternatives**: Pinecone, Chroma, Weaviate, FAISS, Upstash Vector

### Graph Databases

- **Neo4j**: Entity relationships and graph-based memory
- **Alternative**: Memgraph

### Metadata Storage

- **SQLite**: Default for development and small deployments
- **PostgreSQL**: Production deployments
- **Redis**: Caching layer

### LLM Providers

- **FoundationModels**: Native on-device processing for macOS
- **Alternatives**: Anthropic, Groq, Together, Ollama, Google Vertex AI

### Embedding Providers

- **OpenAI**: text-embedding-3-small (default)
- **FoundationModels**: On-device embeddings
- **Alternatives**: Sentence Transformers, local models

## Development Tools

### Code Quality

- **Linting**: Ruff (replaces flake8, black, isort)
- **Formatting**: Ruff format
- **Import Sorting**: Ruff/isort with black profile
- **Pre-commit**: Automated code quality checks

### Testing

- **Framework**: pytest
- **Coverage**: Built-in pytest coverage
- **Types**: pytest-asyncio for async testing

### Build System

- **Python**: Hatch for build, dependency management, and environments
- **Node.js**: tsup for TypeScript compilation and bundling

## Common Commands

### Python Development

```bash
# Install development environment
make install

# Install all optional dependencies
make install_all

# Code formatting and linting
make format    # Format code with ruff
make sort      # Sort imports
make lint      # Lint code

# Testing
make test                # Run all tests
make test-py-3.9        # Test on Python 3.9
make test-py-3.10       # Test on Python 3.10
make test-py-3.11       # Test on Python 3.11

# Build and publish
make build     # Build package
make publish   # Publish to PyPI
make clean     # Clean build artifacts
```

### Node.js Development

```bash
# Install dependencies
pnpm install

# Development
pnpm run dev      # Development mode
pnpm run build    # Build TypeScript
pnpm run test     # Run tests

# Formatting
pnpm run format        # Format code
pnpm run format:check  # Check formatting
```

### Production Deployment

```bash
# Start full production stack
./deployment/scripts/start-production.sh

# Start development services
./start_mem0_full_stack.sh

# Service management (macOS)
bash scripts/install_launch_agents.sh  # Install auto-startup
bash scripts/test_launch_agents.sh     # Test services
```

## Configuration Management

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (required for default setup)
- `QDRANT_URL`: Qdrant connection URL
- `POSTGRES_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection URL
- `APPLE_INTELLIGENCE_ENABLED`: Enable FoundationModels (auto-detected)

### Config Files

- `pyproject.toml`: Python project configuration
- `package.json`: Node.js project configuration (in mem0-ts/)
- `docker-compose.production.yml`: Production deployment
- `claude_desktop_config.json`: MCP server configuration

## FoundationModels Integration

### Requirements

- macOS 15.1+
- Apple Silicon (M1/M2/M3/M4)
- PyObjC for Foundation Models access

### Features

- On-device LLM processing
- Local embedding generation
- Neural Engine optimization
- Zero external API calls for privacy

## MCP (Model Context Protocol)

### Server Options

- **Python Server**: Direct mem0 integration with FoundationModels
- **Node.js Server**: MCP protocol wrapper (recommended for Claude Desktop)
- **Kiro Server**: Project-aware memory management

### Integration Points

- Claude Desktop
- Kiro IDE
- Custom MCP clients
