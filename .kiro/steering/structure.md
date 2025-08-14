# Project Structure

## Root Directory Organization

### Core Library (`mem0/`)

The main Mem0 Python library with modular architecture:

- `memory/`: Core memory management logic and operations
- `vector_stores/`: Vector database integrations (Qdrant, Pinecone, Chroma, etc.)
- `llms/`: LLM provider integrations (OpenAI, FoundationModels, Anthropic, etc.)
- `embeddings/`: Embedding provider integrations
- `graphs/`: Graph database integrations (Neo4j, Memgraph)
- `configs/`: Configuration management and validation
- `utils/`: Utility functions and helpers

### TypeScript Package (`mem0-ts/`)

JavaScript/TypeScript SDK with dual export support:

- `src/`: TypeScript source code
- `dist/`: Compiled JavaScript output (CJS + ESM)
- Supports both hosted platform and open-source usage

### Integrations (`integrations/`)

Production-ready integration examples:

- `agents/`: Framework integrations (AutoGen, CrewAI, LangChain)
- `mcp/`: Model Context Protocol server implementations
- `ui/`: User interface components (React, Vue, mobile)
- `server/`: API server implementations
- `chrome-extension/`: Browser extension for memory capture

### Deployment (`deployment/`)

Production deployment configurations:

- `docker/`: Complete Docker setup with multi-service orchestration
- `scripts/`: Automated deployment and maintenance scripts
- Includes monitoring (Prometheus, Grafana) and reverse proxy (Nginx)

### Documentation (`docs/`, `documentation/`)

- `docs/`: Static documentation site (Mintlify-based)
- `documentation/`: Consolidated technical documentation
- `examples/`: Clean, working code examples
- API reference, guides, and integration documentation

## Key Directories

### Archive (`archive/`)

Safely archived files no longer in active development:

- `experimental/`: Development experiments and prototypes
- `deprecated/`: Deprecated functionality kept for reference
- `old-docs/`: Outdated documentation versions

### Testing (`tests/`)

Comprehensive test coverage:

- `unit/`: Individual component tests
- `integration/`: Cross-component integration tests
- `performance/`: Performance and load tests
- Multiple Python version testing (3.9, 3.10, 3.11)

### Scripts (`scripts/`)

System management and automation:

- `install_launch_agents.sh`: macOS service auto-startup
- `verify_setup.sh`: System verification
- `create_local_launchers.sh`: Local development setup

### Launch Agents (`launch_agents/`)

macOS-specific service management:

- `com.gabriel.mem0-services.plist`: Docker services (Qdrant, Neo4j)
- `com.gabriel.mem0-apple-intelligence.plist`: MCP server with FoundationModels

## File Naming Conventions

### Python Files

- Snake_case for modules: `memory_manager.py`
- Classes in PascalCase: `MemoryManager`
- Functions in snake_case: `add_memory()`

### Configuration Files

- `pyproject.toml`: Python project configuration
- `docker-compose.production.yml`: Production deployment
- `claude_desktop_config.json`: MCP client configuration
- Environment-specific configs: `.env.production`

### Test Files

- Prefix with `test_`: `test_memory_operations.py`
- Integration tests: `test_*_integration.py`
- System tests: `test_complete_integration.py`

## Import Patterns

### Core Library Usage

```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.memory.main import MemoryMain
```

### Integration Usage

```python
# MCP server
from integrations.mcp.server import MCPServer

# Agent frameworks
from integrations.agents.autogen import AutoGenMemory
```

## Configuration Hierarchy

### Development

1. Local environment variables
2. `.env` files
3. Default configurations in code

### Production

1. Environment variables (Docker/K8s)
2. Configuration files mounted as volumes
3. Secrets management for sensitive data

## Multi-Language Support

### Python (Primary)

- Core library implementation
- Direct database integrations
- FoundationModels native support

### Node.js/TypeScript

- SDK wrapper around Python core
- MCP protocol implementation
- Web application integrations

### Integration Points

- MCP servers bridge Python core with various clients
- REST API for language-agnostic access
- Docker containers for deployment consistency

## Development Workflow

### Local Development

1. Install dependencies: `make install`
2. Start services: `./start_mem0_full_stack.sh`
3. Run tests: `make test`
4. Code formatting: `make format lint`

### Production Deployment

1. Build containers: `docker-compose build`
2. Deploy stack: `./deployment/scripts/start-production.sh`
3. Monitor services: Grafana dashboard on port 10300

## Special Directories

### `.bmad-core/`

Business analysis and development framework:

- Agent definitions and team configurations
- Task templates and workflow management
- Checklists and validation frameworks

### `openmemory/`

Open-source memory platform UI:

- React-based web interface
- API server for memory operations
- Docker-based deployment

### `embedchain/`

Legacy embedding chain functionality (deprecated):

- Maintained for backward compatibility
- New development should use core `mem0/` library
