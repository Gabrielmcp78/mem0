/#!/usr/bin/env python3
"""
Unified MCP Server with Persistent Database Connections
Fixes connectivity issues and provides stable knowledge graph access
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Mem0 imports
try:
    from mem0 import Memory
    from mem0.memory.graph_memory import MemoryGraph
    print("✅ Mem0 imports successful", file=sys.stderr)
except ImportError as e:
    print(f"❌ Error importing mem0: {e}", file=sys.stderr)
    sys.exit(1)

# Database connection imports (optional)
HAS_NEO4J = False
HAS_QDRANT = False

try:
    import neo4j
    HAS_NEO4J = True
except ImportError:
    print("⚠️ Neo4j not available - graph features disabled", file=sys.stderr)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    HAS_QDRANT = True
    print("✅ Qdrant client available", file=sys.stderr)
except ImportError:
    print("⚠️ Qdrant not available - using fallback vector store", file=sys.stderr)

# Import configuration
try:
    from config import system_config
    print("✅ Configuration loaded", file=sys.stderr)
except ImportError:
    print("⚠️ Configuration not found - using defaults", file=sys.stderr)
    system_config = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified-mcp-server")

class DatabaseConnectionManager:
    """Manages persistent database connections"""
    
    def __init__(self):
        self.qdrant_client = None
        self.neo4j_driver = None
        self.connection_pool = {}
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        
    async def initialize_connections(self):
        """Initialize all database connections with retries"""
        await self._init_qdrant()
        await self._init_neo4j()
        
    async def _init_qdrant(self):
        """Initialize Qdrant connection with retry logic"""
        if not HAS_QDRANT:
            logger.warning("⚠️ Qdrant client not available - skipping")
            return
            
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Try multiple Qdrant URLs
                qdrant_urls = [
                    "http://localhost:10333",
                    "http://localhost:6333", 
                    "http://qdrant-standardized:6333"
                ]
                
                for url in qdrant_urls:
                    try:
                        client = QdrantClient(url=url)
                        # Test connection
                        await asyncio.get_event_loop().run_in_executor(
                            None, client.get_collections
                        )
                        self.qdrant_client = client
                        logger.info(f"✅ Qdrant connected: {url}")
                        
                        # Ensure collection exists
                        await self._ensure_qdrant_collection()
                        return
                        
                    except Exception as e:
                        logger.debug(f"Qdrant connection failed for {url}: {e}")
                        continue
                        
                raise Exception("All Qdrant URLs failed")
                
            except Exception as e:
                logger.warning(f"Qdrant connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.warning("⚠️ Qdrant not available - using fallback storage")
                    
    async def _init_neo4j(self):
        """Initialize Neo4j connection with retry logic"""
        if not HAS_NEO4J:
            logger.warning("⚠️ Neo4j client not available - graph features disabled")
            return
            
        try:
            # Try multiple Neo4j configurations
            neo4j_configs = [
                # User-provided primary config
                {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "NowVoyager2025!"},
                # Fallbacks
                {"uri": "neo4j://localhost:7687", "user": "neo4j", "password": "NowVoyager2025!"},
                {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"},
                {"uri": "neo4j://localhost:7687", "user": "neo4j", "password": "mem0"},
                {"uri": "bolt://localhost:7688", "user": "neo4j", "password": "neo4j"}
            ]
            
            for config in neo4j_configs:
                try:
                    driver = neo4j.GraphDatabase.driver(
                        config["uri"], 
                        auth=(config["user"], config["password"])
                    )
                    # Test connection
                    await asyncio.get_event_loop().run_in_executor(
                        None, driver.verify_connectivity
                    )
                    self.neo4j_driver = driver
                    logger.info(f"✅ Neo4j connected: {config['uri']}")
                    return
                    
                except Exception as e:
                    logger.debug(f"Neo4j connection failed for {config['uri']}: {e}")
                    continue
                    
            logger.warning("⚠️ Neo4j not available - graph features limited")
            
        except Exception as e:
            logger.warning(f"⚠️ Neo4j initialization failed: {e}")
            
    async def _ensure_qdrant_collection(self):
        """Ensure Qdrant collection exists"""
        if not self.qdrant_client:
            return
            
        try:
            collection_name = "gabriel_memories"
            collections = await asyncio.get_event_loop().run_in_executor(
                None, self.qdrant_client.get_collections
            )
            
            collection_exists = any(
                collection.name == collection_name 
                for collection in collections.collections
            )
            
            if not collection_exists:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.qdrant_client.create_collection,
                    collection_name,
                    VectorParams(size=1536, distance=Distance.COSINE)
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to ensure Qdrant collection: {e}")
            
    async def health_check(self):
        """Perform health checks on all connections"""
        now = time.time()
        if now - self.last_health_check < self.health_check_interval:
            return
            
        self.last_health_check = now
        
        # Check Qdrant
        if self.qdrant_client:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.qdrant_client.get_collections
                )
                logger.debug("✅ Qdrant health check passed")
            except Exception as e:
                logger.warning(f"⚠️ Qdrant health check failed: {e}")
                await self._init_qdrant()
                
        # Check Neo4j
        if self.neo4j_driver:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.neo4j_driver.verify_connectivity
                )
                logger.debug("✅ Neo4j health check passed")
            except Exception as e:
                logger.warning(f"⚠️ Neo4j health check failed: {e}")
                await self._init_neo4j()
                
    def get_connection_status(self):
        """Get status of all database connections"""
        return {
            "qdrant": {
                "connected": self.qdrant_client is not None,
                "client_type": type(self.qdrant_client).__name__ if self.qdrant_client else None
            },
            "neo4j": {
                "connected": self.neo4j_driver is not None,
                "driver_type": type(self.neo4j_driver).__name__ if self.neo4j_driver else None
            }
        }

class UnifiedMCPServer:
    """Unified MCP Server with persistent database connections"""
    
    def __init__(self):
        self.server = Server("unified-memory-server")
        self.db_manager = DatabaseConnectionManager()
        self.memory: Optional[Memory] = None
        self.graph_memory: Optional[MemoryGraph] = None
        
    async def initialize(self):
        """Initialize server and all connections"""
        logger.info("🚀 Initializing Unified MCP Server...")
        
        # Initialize database connections
        await self.db_manager.initialize_connections()
        
        # Initialize Memory with persistent connections
        await self._setup_memory()
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        
        logger.info("✅ Unified MCP Server initialized successfully")
        
    async def _setup_memory(self):
        """Setup Memory with persistent database connections"""
        try:
            # Build configuration with available databases
            config = self._build_memory_config()
            
            # Initialize Memory
            self.memory = Memory.from_config(config)
            logger.info("✅ Memory system initialized with persistent connections")
            
            # Initialize graph memory if Neo4j available
            if self.db_manager.neo4j_driver:
                try:
                    graph_config = self._build_graph_config()
                    self.graph_memory = MemoryGraph(graph_config)
                    logger.info("✅ Graph memory initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Graph memory initialization failed: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Memory setup failed: {e}")
            # Fallback to basic memory
            self.memory = Memory()
            logger.info("⚠️ Using fallback memory configuration")
            
    def _build_memory_config(self):
        """Build memory configuration based on available databases and settings"""
        if system_config:
            config = system_config.get_memory_config()
        else:
            # Fallback configuration
            config = {
                "llm": {
                    "provider": "huggingface",
                    "config": {
                        "model": "microsoft/DialoGPT-medium",
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                },
                "embedder": {
                    "provider": "huggingface",
                    "config": {
                        "model": "sentence-transformers/all-MiniLM-L6-v2"
                    }
                }
            }
        
        # Override vector store based on available connections
        if self.db_manager.qdrant_client:
            config["vector_store"] = {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 10333,
                    "collection_name": "gabriel_memories"
                }
            }
        else:
            # Use in-memory fallback
            config["vector_store"] = {
                "provider": "chroma",
                "config": {
                    "collection_name": "gabriel_memories",
                    "path": "./chroma_db"
                }
            }
            
        return config
        
    def _build_graph_config(self):
        """Build graph configuration for Neo4j"""
        # This would need to be adapted to your specific MemoryGraph config format
        return {
            "graph_store": {
                "provider": "neo4j",
                "config": {
                    # User-provided Neo4j connection for Mem0 project
                    "url": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "NowVoyager2025!",
                    "database": "Mem0Graph"
                }
            }
        }
        
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.server.call_tool()
        async def test_connection() -> List[TextContent]:
            """Test all database connections and system status"""
            await self.db_manager.health_check()
            
            status = {
                "status": "Connected",
                "server_name": "unified-memory-server",
                "timestamp": datetime.now().isoformat(),
                "database_connections": self.db_manager.get_connection_status(),
                "memory_initialized": self.memory is not None,
                "graph_memory_available": self.graph_memory is not None,
                "features": [
                    "persistent_connections",
                    "connection_health_monitoring", 
                    "automatic_reconnection",
                    "knowledge_graph_support"
                ]
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )]
            
        @self.server.call_tool()
        async def add_memory(
            messages: str,
            user_id: str = "gabriel",
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None,
            metadata: Optional[str] = None
        ) -> List[TextContent]:
            """Add memory with automatic reconnection handling"""
            try:
                await self.db_manager.health_check()
                
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory system not initialized"
                    )]
                
                # Parse metadata
                parsed_metadata = {}
                if metadata:
                    try:
                        parsed_metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid metadata JSON: {metadata}")
                
                # Add session tracking
                if agent_id:
                    parsed_metadata["agent_id"] = agent_id
                if run_id:
                    parsed_metadata["run_id"] = run_id
                    
                parsed_metadata["timestamp"] = datetime.now().isoformat()
                parsed_metadata["server"] = "unified-memory-server"
                
                # Add memory
                result = self.memory.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=parsed_metadata
                )
                
                return [TextContent(
                    type="text", 
                    text=json.dumps(result, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error adding memory: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error adding memory: {str(e)}"
                )]
                
        @self.server.call_tool()
        async def search_memories(
            query: str,
            user_id: str = "gabriel",
            limit: int = 10
        ) -> List[TextContent]:
            """Search memories with connection health check"""
            try:
                await self.db_manager.health_check()
                
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory system not initialized"
                    )]
                
                results = self.memory.search(
                    query=query,
                    user_id=user_id,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error searching memories: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error searching memories: {str(e)}"
                )]
                
        @self.server.call_tool()
        async def get_knowledge_graph(
            user_id: str = "gabriel",
            limit: int = 50
        ) -> List[TextContent]:
            """Get knowledge graph data for visualization"""
            try:
                await self.db_manager.health_check()
                
                if not self.graph_memory:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Graph memory not available",
                            "nodes": [],
                            "edges": [],
                            "message": "Neo4j connection required for knowledge graph"
                        }, indent=2)
                    )]
                
                # Get graph data
                filters = {"user_id": user_id}
                graph_data = self.graph_memory.get_all(filters, limit)
                
                # Format for visualization
                nodes = {}
                edges = []
                
                for item in graph_data:
                    source = item.get("source", "")
                    target = item.get("target", "")
                    relationship = item.get("relationship", "")
                    
                    # Add nodes
                    if source and source not in nodes:
                        nodes[source] = {
                            "id": source,
                            "label": source.replace("_", " ").title(),
                            "type": "entity"
                        }
                    if target and target not in nodes:
                        nodes[target] = {
                            "id": target, 
                            "label": target.replace("_", " ").title(),
                            "type": "entity"
                        }
                    
                    # Add edge
                    if source and target:
                        edges.append({
                            "source": source,
                            "target": target,
                            "relationship": relationship,
                            "label": relationship.replace("_", " ").title()
                        })
                
                result = {
                    "nodes": list(nodes.values()),
                    "edges": edges,
                    "stats": {
                        "total_nodes": len(nodes),
                        "total_edges": len(edges),
                        "user_id": user_id
                    }
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Error getting knowledge graph: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "nodes": [],
                        "edges": []
                    }, indent=2)
                )]
                
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return [
                Resource(
                    uri="unified-memory://status",
                    name="System Status",
                    description="Database connections and system health",
                    mimeType="application/json"
                ),
                Resource(
                    uri="unified-memory://graph",
                    name="Knowledge Graph",
                    description="Graph visualization data",
                    mimeType="application/json"
                )
            ]
            
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            if uri == "unified-memory://status":
                await self.db_manager.health_check()
                return json.dumps(self.db_manager.get_connection_status(), indent=2)
            elif uri == "unified-memory://graph":
                # Return basic graph structure
                return json.dumps({
                    "graph_available": self.graph_memory is not None,
                    "message": "Use get_knowledge_graph tool for full data"
                }, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self):
        """Run the unified MCP server"""
        await self.initialize()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="unified-memory-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = UnifiedMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())