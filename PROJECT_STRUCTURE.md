# Mem0 Project Structure

This document outlines the production-ready organization of the Mem0 codebase.

## 📁 Directory Structure

```
mem0/
├── 📁 archive/                    # Archived experimental/deprecated files
│   ├── experimental/              # Development experiments
│   ├── deprecated/                # Deprecated functionality
│   └── old-docs/                  # Outdated documentation
├── 📁 mem0/                       # Core mem0 library
│   ├── __init__.py
│   ├── memory/                    # Memory management
│   ├── vector_stores/             # Vector database integrations
│   ├── llms/                      # LLM provider integrations
│   ├── embeddings/                # Embedding providers
│   ├── configs/                   # Configuration management
│   └── utils/                     # Utility functions
├── 📁 integrations/               # Clean integration examples
│   ├── agents/                    # Agent framework integrations
│   │   ├── autogen/
│   │   ├── crewai/
│   │   └── langchain/
│   ├── mcp/                       # MCP server integration
│   │   ├── server.py
│   │   └── client.py
│   └── ui/                        # UI components
│       ├── react/
│       ├── vue/
│       └── mobile/
├── 📁 deployment/                 # Production deployment configs
│   ├── docker/                    # Docker configurations
│   │   ├── Dockerfile.production
│   │   ├── docker-compose.production.yml
│   │   ├── nginx/
│   │   ├── postgres/
│   │   ├── redis/
│   │   └── qdrant/
│   ├── kubernetes/                # K8s manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   └── hpa.yaml
│   └── scripts/                   # Deployment scripts
│       ├── deploy.sh
│       ├── backup.sh
│       └── restore.sh
├── 📁 documentation/              # Consolidated documentation
│   ├── README.md                  # Documentation index
│   ├── INTEGRATIONS.md            # Integration guides
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── api/                       # API documentation
│   │   ├── core.md
│   │   ├── memory.md
│   │   ├── search.md
│   │   └── users.md
│   └── guides/                    # User guides
│       ├── installation.md
│       ├── basic-usage.md
│       ├── configuration.md
│       └── best-practices.md
├── 📁 tests/                      # Comprehensive test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── performance/               # Performance tests
│   ├── test_production_system.py  # Production validation
│   └── conftest.py                # Test configuration
├── 📁 tools/                      # Development and utility tools
│   ├── migration/                 # Database migration tools
│   ├── monitoring/                # Monitoring utilities
│   └── benchmarks/                # Performance benchmarks
├── 📁 examples/                   # Clean, working examples
│   ├── basic-chatbot/
│   ├── customer-support/
│   ├── multi-agent/
│   └── production-setup/
├── 📁 docs/                       # Static documentation assets
│   ├── images/
│   └── assets/
├── 📁 .github/                    # GitHub workflows and templates
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
└── 📄 Configuration Files
    ├── README.md                  # Main project README
    ├── pyproject.toml             # Python project configuration
    ├── poetry.lock                # Dependency lock file
    ├── .gitignore                 # Git ignore rules
    ├── .pre-commit-config.yaml    # Pre-commit hooks
    ├── Makefile                   # Build automation
    ├── CONTRIBUTING.md            # Contribution guidelines
    ├── LICENSE                    # License file
    ├── CLEANUP_PLAN.md            # Cleanup documentation
    └── PROJECT_STRUCTURE.md       # This file
```

## 🗂️ Key Directories Explained

### Core Library (`mem0/`)
The main Mem0 library containing all core functionality:
- **memory/**: Core memory management logic
- **vector_stores/**: Integrations with vector databases (Qdrant, Pinecone, Chroma)
- **llms/**: LLM provider integrations (OpenAI, Anthropic, local models)
- **embeddings/**: Embedding provider integrations
- **configs/**: Configuration management and validation

### Integrations (`integrations/`)
Clean, production-ready integration examples:
- **agents/**: Framework integrations (AutoGen, CrewAI, LangChain)
- **mcp/**: Model Context Protocol server implementation
- **ui/**: User interface components for various frameworks

### Deployment (`deployment/`)
Production deployment configurations:
- **docker/**: Complete Docker setup with multi-service orchestration
- **kubernetes/**: K8s manifests for scalable deployment
- **scripts/**: Automated deployment and maintenance scripts

### Documentation (`documentation/`)
Comprehensive, organized documentation:
- **api/**: Detailed API reference
- **guides/**: Step-by-step user guides
- **INTEGRATIONS.md**: Complete integration documentation
- **DEPLOYMENT.md**: Production deployment guide

### Tests (`tests/`)
Comprehensive test coverage:
- **unit/**: Individual component tests
- **integration/**: Cross-component integration tests
- **performance/**: Performance and load tests
- **test_production_system.py**: Production environment validation

### Archive (`archive/`)
Safely archived files that are no longer active:
- **experimental/**: Development experiments and prototypes
- **deprecated/**: Deprecated functionality kept for reference
- **old-docs/**: Outdated documentation versions

## 📋 File Organization Principles

### 1. Separation of Concerns
- Core library code is isolated from integrations
- Deployment configs are separate from application code
- Documentation is centralized and well-organized

### 2. Production Readiness
- All deployment configurations are production-tested
- Comprehensive monitoring and health checks
- Security best practices implemented

### 3. Developer Experience
- Clear directory structure with logical grouping
- Comprehensive documentation at every level
- Easy-to-find examples and integration guides

### 4. Maintainability
- Archived files are preserved but separated
- Version control friendly organization
- Clear naming conventions throughout

## 🚀 Getting Started

### For Users
1. Start with the main [README.md](README.md)
2. Follow the [installation guide](documentation/guides/installation.md)
3. Try the [basic usage examples](examples/basic-chatbot/)

### For Developers
1. Review the [contribution guidelines](CONTRIBUTING.md)
2. Set up the development environment
3. Run the test suite: `pytest tests/`

### For DevOps
1. Review the [deployment guide](documentation/DEPLOYMENT.md)
2. Use the [deployment scripts](deployment/scripts/)
3. Monitor with the provided configurations

## 🔄 Maintenance

### Regular Tasks
- Archive outdated experimental files
- Update documentation with new features
- Review and update deployment configurations
- Run comprehensive test suites

### Version Management
- Tag releases with semantic versioning
- Maintain changelog in documentation
- Archive old versions in appropriate directories

This structure ensures Mem0 remains maintainable, scalable, and production-ready while providing excellent developer and user experiences.