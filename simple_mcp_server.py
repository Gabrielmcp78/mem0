#!/usr/bin/env python3
"""
Simple MCP Server for mem0 with Apple Intelligence
Just works with what's already available
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple-mcp-server")

class SimpleMCPServer:
    """Simple MCP Server that actually works"""
    
    def __init__(self):
        self.server = Server("simple-memory-server")
        self.memory = None
        self._setup_memory()
        self._register_tools()
        
    def _setup_memory(self):
        """Setup Memory with Apple Intelligence if available"""
        try:
            from mem0 import Memory
            import os
            
            # First, check if we have a real OpenAI key in environment
            has_openai_key = bool(os.environ.get('OPENAI_API_KEY'))
            
            # Try Apple Intelligence configuration first
            try:
                config = {
                    "llm": {
                        "provider": "apple_intelligence",
                        "config": {
                            "model": "apple-intelligence-foundation",
                            "temperature": 0.3,
                            "max_tokens": 1500
                        }
                    },
                    "embedder": {
                        "provider": "apple_intelligence",
                        "config": {
                            "model": "apple-intelligence-embeddings"
                        }
                    }
                }
                
                # Only add vector store if Qdrant is actually accessible
                import requests
                try:
                    response = requests.get("http://localhost:10333/collections", timeout=2)
                    if response.status_code == 200:
                        config["vector_store"] = {
                            "provider": "qdrant",
                            "config": {
                                "host": "localhost",
                                "port": 10333,
                                "collection_name": "gabriel_memories"
                            }
                        }
                        logger.info("✅ Using Qdrant vector store")
                    else:
                        logger.info("⚠️ Qdrant not accessible, using default storage")
                except:
                    logger.info("⚠️ Qdrant not accessible, using default storage")
                
                self.memory = Memory.from_config(config)
                logger.info("✅ Memory initialized with Apple Intelligence")
                
            except Exception as e:
                logger.warning(f"Apple Intelligence setup failed: {e}")
                
                # Try different fallback strategies
                if has_openai_key:
                    # If we have a real OpenAI key, use it
                    logger.info("Falling back to OpenAI with existing API key")
                    fallback_config = {
                        "llm": {
                            "provider": "openai",
                            "config": {
                                "model": "gpt-3.5-turbo",
                                "temperature": 0.3,
                                "max_tokens": 1500
                            }
                        },
                        "embedder": {
                            "provider": "openai", 
                            "config": {
                                "model": "text-embedding-ada-002"
                            }
                        }
                    }
                else:
                    # Set a temporary dummy key to bypass initialization
                    logger.info("Setting temporary OPENAI_API_KEY for fallback")
                    os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-mem0-bypass-only'
                    
                    fallback_config = {
                        "llm": {
                            "provider": "openai",
                            "config": {
                                "model": "gpt-3.5-turbo",
                                "temperature": 0.3,
                                "max_tokens": 1500,
                                "api_key": "sk-dummy-key-for-mem0-bypass-only"
                            }
                        },
                        "embedder": {
                            "provider": "openai", 
                            "config": {
                                "model": "text-embedding-ada-002",
                                "api_key": "sk-dummy-key-for-mem0-bypass-only"
                            }
                        }
                    }
                
                # Add vector store if available
                import requests
                try:
                    response = requests.get("http://localhost:10333/collections", timeout=2)
                    if response.status_code == 200:
                        fallback_config["vector_store"] = {
                            "provider": "qdrant",
                            "config": {
                                "host": "localhost",
                                "port": 10333,
                                "collection_name": "gabriel_memories_fallback"
                            }
                        }
                except:
                    pass
                
                try:
                    self.memory = Memory.from_config(fallback_config)
                    logger.info("✅ Memory initialized with fallback configuration")
                    logger.warning("⚠️ Fallback will fail on actual LLM/embedding calls without real OpenAI key")
                except Exception as fallback_error:
                    logger.error(f"Even fallback failed: {fallback_error}")
                    self.memory = None
                
        except Exception as e:
            logger.error(f"Memory setup failed: {e}")
            self.memory = None
            
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.call_tool()
        async def test_connection() -> List[TextContent]:
            """Test connection and get status"""
            
            # Check what's actually available
            has_qdrant = False
            try:
                import requests
                response = requests.get("http://localhost:10333/collections", timeout=2)
                has_qdrant = response.status_code == 200
            except:
                pass
            
            has_apple_intelligence = False
            try:
                from mem0.utils.apple_intelligence import check_apple_intelligence_availability
                has_apple_intelligence = check_apple_intelligence_availability()
            except:
                pass
            
            status = {
                "status": "Connected",
                "server_name": "simple-memory-server",
                "timestamp": datetime.now().isoformat(),
                "memory_available": self.memory is not None,
                "apple_intelligence_available": has_apple_intelligence,
                "qdrant_available": has_qdrant,
                "features": [
                    "basic_memory_operations",
                    "apple_intelligence" if has_apple_intelligence else "fallback_models",
                    "qdrant_storage" if has_qdrant else "default_storage"
                ]
            }
            
            return [TextContent(type="text", text=json.dumps(status, indent=2))]
        
        @self.server.call_tool()
        async def add_memory(
            messages: str,
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """Add a memory"""
            try:
                if not self.memory:
                    return [TextContent(type="text", text="Error: Memory not available")]
                
                result = self.memory.add(messages=messages, user_id=user_id)
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
            except Exception as e:
                logger.error(f"Error adding memory: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def search_memories(
            query: str,
            user_id: str = "gabriel",
            limit: int = 10
        ) -> List[TextContent]:
            """Search memories"""
            try:
                if not self.memory:
                    return [TextContent(type="text", text="Error: Memory not available")]
                
                results = self.memory.search(query=query, user_id=user_id, limit=limit)
                return [TextContent(type="text", text=json.dumps(results, indent=2, default=str))]
                
            except Exception as e:
                logger.error(f"Error searching memories: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_all_memories(
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """Get all memories"""
            try:
                if not self.memory:
                    return [TextContent(type="text", text="Error: Memory not available")]
                
                results = self.memory.get_all(user_id=user_id)
                return [TextContent(type="text", text=json.dumps(results, indent=2, default=str))]
                
            except Exception as e:
                logger.error(f"Error getting memories: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_graph_data(
            user_id: str = "gabriel"
        ) -> List[TextContent]:
            """Get knowledge graph data for visualization"""
            try:
                if not self.memory:
                    return [TextContent(type="text", text=json.dumps({
                        "error": "Memory not available",
                        "nodes": [],
                        "edges": []
                    }))]
                
                # Get all memories and create a simple graph
                memories = self.memory.get_all(user_id=user_id)
                
                # Create mock graph data from memories for visualization
                nodes = []
                edges = []
                
                for i, memory in enumerate(memories[:20]):  # Limit to 20 for visualization
                    memory_text = str(memory.get('memory', ''))[:50]  # First 50 chars
                    nodes.append({
                        "id": f"memory_{i}",
                        "label": memory_text if memory_text else f"Memory {i}",
                        "type": "memory"
                    })
                    
                    # Connect to user node
                    if i == 0:
                        nodes.append({
                            "id": "user",
                            "label": user_id,
                            "type": "user"
                        })
                    
                    edges.append({
                        "source": "user",
                        "target": f"memory_{i}",
                        "label": "has_memory"
                    })
                
                return [TextContent(type="text", text=json.dumps({
                    "nodes": nodes,
                    "edges": edges,
                    "stats": {
                        "total_nodes": len(nodes),
                        "total_edges": len(edges),
                        "user_id": user_id
                    }
                }, indent=2))]
                
            except Exception as e:
                logger.error(f"Error getting graph data: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "nodes": [],
                    "edges": []
                }))]
    
    async def run(self):
        """Run the server"""
        logger.info("🚀 Starting Simple MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="simple-memory-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = SimpleMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())