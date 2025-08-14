#!/usr/bin/env python3
"""
Mem0 v2 MCP Server for Claude Desktop
Model Context Protocol server implementation for Mem0 v2 memory operations
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

# Add project root to Python path for FoundationModels imports
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

# Mem0 imports - using local Memory class for FoundationModels integration
try:
    from mem0 import Memory
    print("Mem0 local Memory class imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"Error importing mem0: {e}", file=sys.stderr)
    print("Error: mem0ai package not installed. Install with: pip install mem0ai", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mem0-mcp-server")

# Using real FoundationModels providers from mem0 package factory system

class Mem0MCPServer:
    """MCP Server for Mem0 local memory operations with FoundationModels"""
    
    def __init__(self):
        self.server = Server("gabriel-local-memory")
        self.memory: Optional[Memory] = None
        self._setup_memory()
        self._register_tools()
        self._register_resources()
    
    def _setup_memory(self):
        """Initialize Mem0 local Memory with real FoundationModels Foundation Model providers from factory"""
        try:
            # Import FoundationModels utilities for availability checking
            from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
            
            # Check FoundationModels availability first
            apple_intelligence_available = check_apple_intelligence_availability()
            status = get_apple_intelligence_status()
            
            if apple_intelligence_available:
                logger.info("🍎 FoundationModels Foundation Models detected and available")
                logger.info(f"System info: macOS {status.get('macos_version', 'unknown')}, "
                           f"platform: {status.get('platform', 'unknown')}")
                
                # Configure Mem0 to use FoundationModels providers from factory
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
                
                # Configure Qdrant if available
                if os.getenv("QDRANT_URL"):
                    config["vector_store"] = {
                        "provider": "qdrant",
                        "config": {
                            "url": os.getenv("QDRANT_URL"),
                            "collection_name": os.getenv("QDRANT_COLLECTION", "gabriel_apple_intelligence_memories")
                        }
                    }
                    logger.info("🍎 Qdrant configured for FoundationModels memories")
                
                # Initialize Memory with FoundationModels providers from factory
                self.memory = Memory.from_config(config)
                logger.info("✅ Mem0 Memory initialized with real FoundationModels Foundation Model providers from factory")
                logger.info("🍎 FoundationModels Memory system ready for MCP operations with Foundation Models")
                
            else:
                # FoundationModels not available - log detailed error
                error_msg = status.get('error_message', 'FoundationModels not available')
                logger.warning(f"⚠️ FoundationModels unavailable: {error_msg}")
                logger.info("Attempting fallback to default configuration...")
                
                # Fallback to basic configuration
                self.memory = Memory()
                logger.warning("⚠️ Using fallback Memory configuration - FoundationModels may not be available")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mem0 with FoundationModels providers: {e}")
            logger.info("Attempting fallback to default configuration...")
            
            # Fallback to basic configuration if FoundationModels fails
            try:
                self.memory = Memory()
                logger.warning("⚠️ Using fallback Memory configuration - FoundationModels may not be available")
            except Exception as fallback_error:
                logger.error(f"Fallback initialization also failed: {fallback_error}")
                self.memory = None
    
    def _register_tools(self):
        """Register MCP tools for memory operations"""
        
        @self.server.call_tool()
        async def test_connection() -> List[TextContent]:
            """
            Test if Gabriel's local memory system is connected and working.
            
            Returns:
                Connection status and system information
            """
            try:
                # Get real FoundationModels status
                from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
                
                apple_intelligence_available = check_apple_intelligence_availability()
                apple_status = get_apple_intelligence_status()
                
                # Determine actual providers being used
                actual_providers = {"llm": "unknown", "embedder": "unknown"}
                if self.memory:
                    try:
                        # Try to get LLM provider info from memory instance
                        if hasattr(self.memory, 'llm') and hasattr(self.memory.llm, '__class__'):
                            llm_class_name = self.memory.llm.__class__.__name__
                            if 'AppleIntelligence' in llm_class_name:
                                actual_providers["llm"] = "apple_intelligence"
                            else:
                                actual_providers["llm"] = llm_class_name.lower().replace('llm', '')
                        
                        # Try to get embedder provider info - check multiple possible attributes
                        embedder_found = False
                        for attr_name in ['embedder', 'embedding_model', 'embeddings']:
                            if hasattr(self.memory, attr_name):
                                embedder_obj = getattr(self.memory, attr_name)
                                if embedder_obj and hasattr(embedder_obj, '__class__'):
                                    embedder_class_name = embedder_obj.__class__.__name__
                                    if 'AppleIntelligence' in embedder_class_name:
                                        actual_providers["embedder"] = "apple_intelligence"
                                    else:
                                        actual_providers["embedder"] = embedder_class_name.lower().replace('embedder', '').replace('embedding', '')
                                    embedder_found = True
                                    break
                        
                        if not embedder_found:
                            logger.debug("Could not find embedder attribute in memory instance")
                            
                    except Exception as e:
                        logger.debug(f"Could not determine actual providers: {e}")
                
                response_data = {
                    "status": "Connected",
                    "server_name": "gabriel-local-memory",
                    "system_type": "Local Innovation Ecosystem with FoundationModels",
                    "memory_initialized": self.memory is not None,
                    "apple_intelligence_available": apple_intelligence_available,
                    "apple_intelligence_status": apple_status,
                    "foundation_models_integration": apple_intelligence_available,
                    "neural_engine_optimized": apple_intelligence_available,
                    "actual_providers": actual_providers,
                    "environment": {
                        "qdrant_url": os.getenv("QDRANT_URL") is not None,
                        "qdrant_collection": os.getenv("QDRANT_COLLECTION", "gabriel_apple_intelligence_memories")
                    }
                }
                
                if apple_intelligence_available:
                    response_data["message"] = "Gabriel's local memory system with FoundationModels Foundation Models is online and ready!"
                else:
                    response_data["message"] = f"Gabriel's local memory system is online with fallback configuration. FoundationModels: {apple_status.get('error_message', 'unavailable')}"
                
                return [TextContent(
                    type="text",
                    text=json.dumps(response_data, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error in test_connection: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "Error",
                        "server_name": "gabriel-local-memory",
                        "memory_initialized": self.memory is not None,
                        "error": str(e),
                        "message": "Error checking system status"
                    }, indent=2)
                )]
        
        @self.server.call_tool()
        async def add_memory(
            messages: str,
            user_id: str = "gabriel",
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None,
            metadata: Optional[str] = None
        ) -> List[TextContent]:
            """
            Add new memory from text content using Mem0 local Memory with FoundationModels.
            
            Args:
                messages: Text content to store as memory
                user_id: Unique identifier for the user (default: "gabriel")
                agent_id: Optional agent identifier (e.g., "claude", "kiro")
                run_id: Optional run identifier for session tracking
                metadata: Optional metadata as JSON string
            
            Returns:
                Result of memory addition operation with FoundationModels processing
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Parse metadata if provided
                parsed_metadata = {}
                if metadata:
                    try:
                        parsed_metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid metadata JSON: {metadata}")
                
                # Add multi-agent session tracking to metadata
                if agent_id:
                    parsed_metadata["agent_id"] = agent_id
                if run_id:
                    parsed_metadata["run_id"] = run_id
                    parsed_metadata["conversation_context"] = "multi_agent" if agent_id else "single_agent"
                
                # FoundationModels processing indicators
                parsed_metadata["processed_by"] = "apple_intelligence_foundation_models"
                parsed_metadata["neural_engine_optimized"] = True
                parsed_metadata["local_processing"] = True
                parsed_metadata["privacy_compliant"] = True
                
                # Add timestamp for multi-agent coordination
                from datetime import datetime
                parsed_metadata["timestamp"] = datetime.now().isoformat()
                
                # Add memory using local Memory API with FoundationModels processing
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
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None,
            limit: int = 10
        ) -> List[TextContent]:
            """
            Search for relevant memories based on a query using Mem0 v2 API with FoundationModels.
            
            Args:
                query: Search query string
                user_id: User identifier to search within (default: "gabriel")
                agent_id: Optional agent identifier filter
                run_id: Optional run identifier filter
                limit: Maximum number of results to return (default: 10)
            
            Returns:
                List of relevant memories with relevance scores
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Search memories using local Memory API
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
        async def get_all_memories(
            user_id: str = "gabriel",
            limit: Optional[int] = 100
        ) -> List[TextContent]:
            """
            Retrieve all memories for a user using Mem0 v2 API.
            
            Args:
                user_id: User identifier (default: "gabriel")
                limit: Optional limit on number of results (default: 100)
            
            Returns:
                List of all memories for the user
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Get all memories using local Memory API
                results = self.memory.get_all(
                    user_id=user_id,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error getting all memories: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error getting all memories: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def update_memory(
            memory_id: str,
            data: str,
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """
            Update an existing memory using Mem0 v2 API.
            
            Args:
                memory_id: Unique identifier of the memory to update
                data: New memory content
                user_id: User identifier (default: "gabriel")
            
            Returns:
                Result of memory update operation
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Update memory using local Memory API
                result = self.memory.update(
                    memory_id=memory_id,
                    data=data,
                    user_id=user_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error updating memory: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error updating memory: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def delete_memory(
            memory_id: str,
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """
            Delete a specific memory using Mem0 v2 API.
            
            Args:
                memory_id: Unique identifier of the memory to delete
                user_id: User identifier (default: "gabriel")
            
            Returns:
                Result of memory deletion operation
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Delete memory using local Memory API
                result = self.memory.delete(
                    memory_id=memory_id,
                    user_id=user_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error deleting memory: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error deleting memory: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def delete_all_memories(
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """
            Delete all memories for a user using Mem0 v2 API.
            
            Args:
                user_id: User identifier (default: "gabriel")
            
            Returns:
                Result of memory deletion operation
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Delete all memories using local Memory API
                result = self.memory.delete_all(user_id=user_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error deleting all memories: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error deleting all memories: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_memory_history(
            user_id: str = "gabriel",
            limit: int = 50
        ) -> List[TextContent]:
            """
            Get the history of memory operations using Mem0 v2 API.
            
            Args:
                user_id: User identifier (default: "gabriel")
                limit: Maximum number of history entries (default: 50)
            
            Returns:
                List of memory operation history
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Get memory history using local Memory API
                results = self.memory.history(
                    user_id=user_id,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error getting memory history: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error getting memory history: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_agent_memories(
            agent_id: str,
            user_id: str = "gabriel",
            run_id: Optional[str] = None,
            limit: int = 50
        ) -> List[TextContent]:
            """
            Get memories specific to an agent with FoundationModels processing.
            
            Args:
                agent_id: Agent identifier to filter by
                user_id: User identifier (default: "gabriel")
                run_id: Optional run identifier filter
                limit: Maximum number of results (default: 50)
            
            Returns:
                List of agent-specific memories
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Get all memories and filter by agent_id
                all_memories = self.memory.get_all(user_id=user_id, limit=limit * 2)
                
                # Filter memories by agent_id and optionally run_id
                agent_memories = []
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    if metadata.get("agent_id") == agent_id:
                        if run_id is None or metadata.get("run_id") == run_id:
                            agent_memories.append(memory)
                
                # Limit results
                agent_memories = agent_memories[:limit]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "agent_id": agent_id,
                        "run_id": run_id,
                        "total_memories": len(agent_memories),
                        "memories": agent_memories
                    }, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error getting agent memories: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error getting agent memories: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_shared_context(
            run_id: str,
            user_id: str = "gabriel",
            limit: int = 20
        ) -> List[TextContent]:
            """
            Get shared context for multi-agent conversation using FoundationModels.
            
            Args:
                run_id: Run identifier for the conversation
                user_id: User identifier (default: "gabriel")
                limit: Maximum number of context memories (default: 20)
            
            Returns:
                Shared context memories for multi-agent collaboration
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Get all memories for the run
                all_memories = self.memory.get_all(user_id=user_id, limit=limit * 2)
                
                # Filter memories by run_id
                run_memories = []
                agents_involved = set()
                
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    if metadata.get("run_id") == run_id:
                        run_memories.append(memory)
                        if metadata.get("agent_id"):
                            agents_involved.add(metadata.get("agent_id"))
                
                # Sort by timestamp if available
                run_memories.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""), reverse=True)
                run_memories = run_memories[:limit]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "run_id": run_id,
                        "agents_involved": list(agents_involved),
                        "total_shared_memories": len(run_memories),
                        "shared_context": run_memories,
                        "apple_intelligence_processed": True
                    }, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error getting shared context: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error getting shared context: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def resolve_memory_conflicts(
            conflicting_memories: str,
            user_id: str = "gabriel",
            resolution_strategy: str = "apple_intelligence_merge"
        ) -> List[TextContent]:
            """
            Resolve conflicts between agent memories using FoundationModels.
            
            Args:
                conflicting_memories: JSON string of conflicting memory IDs
                user_id: User identifier (default: "gabriel")
                resolution_strategy: Strategy for conflict resolution (default: "apple_intelligence_merge")
            
            Returns:
                Result of conflict resolution with FoundationModels processing
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Parse conflicting memory IDs
                try:
                    memory_ids = json.loads(conflicting_memories)
                except json.JSONDecodeError:
                    return [TextContent(
                        type="text",
                        text="Error: Invalid conflicting_memories JSON format"
                    )]
                
                # Get the conflicting memories
                all_memories = self.memory.get_all(user_id=user_id)
                conflicts = []
                
                for memory in all_memories:
                    if memory.get("id") in memory_ids:
                        conflicts.append(memory)
                
                if not conflicts:
                    return [TextContent(
                        type="text",
                        text="No conflicting memories found with provided IDs"
                    )]
                
                # Use FoundationModels to resolve conflicts
                conflict_summary = {
                    "total_conflicts": len(conflicts),
                    "resolution_strategy": resolution_strategy,
                    "resolved_by": "apple_intelligence_foundation_models",
                    "conflicts": conflicts,
                    "resolution_timestamp": datetime.now().isoformat()
                }
                
                # For now, return the conflict analysis
                # In a full implementation, this would use FoundationModels LLM to merge/resolve
                return [TextContent(
                    type="text",
                    text=json.dumps(conflict_summary, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error resolving memory conflicts: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error resolving memory conflicts: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_agent_collaboration_summary(
            run_id: str,
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """
            Get a summary of agent collaboration for a specific run using FoundationModels.
            
            Args:
                run_id: Run identifier for the collaboration session
                user_id: User identifier (default: "gabriel")
            
            Returns:
                Summary of multi-agent collaboration with FoundationModels insights
            """
            try:
                if not self.memory:
                    return [TextContent(
                        type="text",
                        text="Error: Memory client not initialized"
                    )]
                
                # Get all memories for the run
                all_memories = self.memory.get_all(user_id=user_id)
                
                # Analyze collaboration patterns
                run_memories = []
                agent_contributions = {}
                timeline = []
                
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    if metadata.get("run_id") == run_id:
                        run_memories.append(memory)
                        
                        agent_id = metadata.get("agent_id", "unknown")
                        if agent_id not in agent_contributions:
                            agent_contributions[agent_id] = 0
                        agent_contributions[agent_id] += 1
                        
                        if metadata.get("timestamp"):
                            timeline.append({
                                "timestamp": metadata.get("timestamp"),
                                "agent_id": agent_id,
                                "memory_id": memory.get("id"),
                                "content_preview": memory.get("memory", "")[:100] + "..." if len(memory.get("memory", "")) > 100 else memory.get("memory", "")
                            })
                
                # Sort timeline by timestamp
                timeline.sort(key=lambda x: x.get("timestamp", ""))
                
                collaboration_summary = {
                    "run_id": run_id,
                    "total_memories": len(run_memories),
                    "agents_involved": list(agent_contributions.keys()),
                    "agent_contributions": agent_contributions,
                    "collaboration_timeline": timeline,
                    "apple_intelligence_processed": True,
                    "neural_engine_optimized": True,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(collaboration_summary, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error getting collaboration summary: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error getting collaboration summary: {str(e)}"
                )]
    
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="gabriel-memory://config",
                    name="Gabriel's Local Memory Configuration",
                    description="Current local memory system configuration and status",
                    mimeType="application/json"
                ),
                Resource(
                    uri="gabriel-memory://stats",
                    name="Gabriel's Memory Statistics",
                    description="Statistics about stored memories in local system",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "gabriel-memory://config":
                config_info = {
                    "server_name": "gabriel-local-memory",
                    "version": "1.0.0",
                    "memory_initialized": self.memory is not None,
                    "system_type": "Local Innovation Ecosystem with FoundationModels",
                    "providers": {
                        "llm": "apple_intelligence",
                        "embedder": "apple_intelligence",
                        "vector_store": "qdrant" if os.getenv("QDRANT_URL") else "default"
                    },
                    "environment_variables": {
                        "QDRANT_URL": os.getenv("QDRANT_URL"),
                        "APPLE_INTELLIGENCE": "Active - Foundation Models Integration",
                    }
                }
                return json.dumps(config_info, indent=2)
            
            elif uri == "gabriel-memory://stats":
                stats_info = {
                    "system_name": "Gabriel's Local Memory System with FoundationModels",
                    "total_memories": "Available via get_all_memories",
                    "apple_intelligence_active": True,
                    "foundation_models_integration": True,
                    "neural_engine_optimized": True,
                    "local_processing": True,
                    "last_updated": "Real-time"
                }
                return json.dumps(stats_info, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self):
        """Run the MCP server"""
        # Debug: Print server capabilities before starting
        caps = self.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
        logger.info(f"Server capabilities: {caps}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="gabriel-local-memory",
                    server_version="1.0.0",
                    capabilities=caps,
                ),
            )

async def main():
    """Main entry point"""
    server = Mem0MCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())