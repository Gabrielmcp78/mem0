# Port Reference - Updated to 10000+ Range

## New Port Assignments

| Service | Old Port | New Port | Purpose |
|---------|----------|----------|---------|
| OpenMemory UI | 3000 | 13000 | Original OpenMemory interface |
| Enhanced UI | 3001 | 13001 | Modern, accessible interface |
| Qdrant HTTP | 6333 | 16333 | Vector database HTTP API |
| Qdrant gRPC | 6334 | 16334 | Vector database gRPC API |
| Neo4j HTTP | 7474 | 17474 | Graph database web interface |
| Neo4j Bolt | 7687 | 17687 | Graph database Bolt protocol |
| OpenMemory API | 8765 | 18765 | OpenMemory MCP REST API |
| Custom MCP Server | 8766 | 18766 | WebSocket MCP protocol |
| Enhanced API | 8767 | 18767 | Custom API with extensions |
| Redis | 6379 | 16379 | Caching and session storage |
| PostgreSQL | 5432 | 15432 | Structured data storage |

## Updated Access Points

- **Enhanced UI**: http://localhost:13001
- **Original UI**: http://localhost:13000
- **Enhanced API**: http://localhost:18767
- **OpenMemory API**: http://localhost:18765
- **MCP WebSocket**: ws://localhost:18766
- **Qdrant Dashboard**: http://localhost:16333/dashboard
- **Neo4j Browser**: http://localhost:17474

## Configuration Updates

All configuration files have been updated to use the new port ranges:
- Docker Compose files
- Memory configuration
- UI package.json
- API server configurations
- MCP server settings
- Test and demo scripts
- Documentation files

## Why 10000+ Range?

- Avoids conflicts with common development ports (3000-9999)
- Follows enterprise port allocation practices
- Reduces chance of port conflicts with other services
- Maintains logical grouping (13xxx for UI, 16xxx for databases, 18xxx for APIs)
