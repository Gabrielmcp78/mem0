#!/usr/bin/env python3
"""
MCP Integration System for Memory Ecosystem
Provides comprehensive MCP server integration and plugin architecture
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPMessage:
    """Standard MCP message format"""
    id: str
    method: str
    params: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class MCPResponse:
    """Standard MCP response format"""
    id: str
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class MCPPlugin(ABC):
    """Base class for MCP plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """Handle incoming MCP message"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities"""
        pass
    
    def enable(self):
        """Enable the plugin"""
        self.enabled = True
        logger.info(f"Plugin {self.name} enabled")
    
    def disable(self):
        """Disable the plugin"""
        self.enabled = False
        logger.info(f"Plugin {self.name} disabled")

class MemoryMCPPlugin(MCPPlugin):
    """Memory management MCP plugin"""
    
    def __init__(self, memory_system):
        super().__init__("memory", "1.0.0")
        self.memory = memory_system
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """Handle memory-related MCP messages"""
        try:
            method = message.method
            params = message.params
            
            if method == "memory.add":
                result = await self._add_memory(params)
            elif method == "memory.search":
                result = await self._search_memory(params)
            elif method == "memory.get":
                result = await self._get_memory(params)
            elif method == "memory.update":
                result = await self._update_memory(params)
            elif method == "memory.delete":
                result = await self._delete_memory(params)
            elif method == "memory.list":
                result = await self._list_memories(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return MCPResponse(id=message.id, result=result)
            
        except Exception as e:
            logger.error(f"Error handling message {message.id}: {e}")
            return MCPResponse(
                id=message.id,
                error={"code": -1, "message": str(e)}
            )
    
    async def _add_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new memory"""
        text = params.get("text")
        user_id = params.get("user_id", "default")
        metadata = params.get("metadata", {})
        
        if not text:
            raise ValueError("Text is required")
        
        result = self.memory.add(text, user_id=user_id, metadata=metadata)
        return {"success": True, "memory_id": result.get("id"), "result": result}
    
    async def _search_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories"""
        query = params.get("query")
        user_id = params.get("user_id", "default")
        limit = params.get("limit", 10)
        
        if not query:
            raise ValueError("Query is required")
        
        results = self.memory.search(query, user_id=user_id, limit=limit)
        return {"results": results.get("results", [])}
    
    async def _get_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific memory"""
        memory_id = params.get("memory_id")
        
        if not memory_id:
            raise ValueError("Memory ID is required")
        
        result = self.memory.get(memory_id)
        return {"memory": result}
    
    async def _update_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a memory"""
        memory_id = params.get("memory_id")
        text = params.get("text")
        
        if not memory_id or not text:
            raise ValueError("Memory ID and text are required")
        
        result = self.memory.update(memory_id, text)
        return {"success": True, "result": result}
    
    async def _delete_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a memory"""
        memory_id = params.get("memory_id")
        
        if not memory_id:
            raise ValueError("Memory ID is required")
        
        result = self.memory.delete(memory_id)
        return {"success": True, "result": result}
    
    async def _list_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List memories"""
        user_id = params.get("user_id", "default")
        limit = params.get("limit", 100)
        
        results = self.memory.get_all(user_id=user_id, limit=limit)
        return {"memories": results.get("results", [])}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return memory plugin capabilities"""
        return {
            "methods": [
                "memory.add",
                "memory.search", 
                "memory.get",
                "memory.update",
                "memory.delete",
                "memory.list"
            ],
            "description": "Memory management operations",
            "version": self.version
        }

class AgentMCPPlugin(MCPPlugin):
    """Agent management MCP plugin"""
    
    def __init__(self, agent_registry):
        super().__init__("agent", "1.0.0")
        self.agents = agent_registry
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """Handle agent-related MCP messages"""
        try:
            method = message.method
            params = message.params
            
            if method == "agent.register":
                result = await self._register_agent(params)
            elif method == "agent.list":
                result = await self._list_agents(params)
            elif method == "agent.message":
                result = await self._send_message(params)
            elif method == "agent.status":
                result = await self._get_status(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return MCPResponse(id=message.id, result=result)
            
        except Exception as e:
            logger.error(f"Error handling agent message {message.id}: {e}")
            return MCPResponse(
                id=message.id,
                error={"code": -1, "message": str(e)}
            )
    
    async def _register_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent"""
        agent_id = params.get("agent_id")
        agent_type = params.get("type", "generic")
        capabilities = params.get("capabilities", [])
        
        if not agent_id:
            raise ValueError("Agent ID is required")
        
        self.agents[agent_id] = {
            "id": agent_id,
            "type": agent_type,
            "capabilities": capabilities,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        
        return {"success": True, "agent_id": agent_id}
    
    async def _list_agents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List registered agents"""
        return {"agents": list(self.agents.values())}
    
    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to agent"""
        agent_id = params.get("agent_id")
        message = params.get("message")
        
        if not agent_id or not message:
            raise ValueError("Agent ID and message are required")
        
        # In a real implementation, this would route to the actual agent
        return {"success": True, "message_id": str(uuid.uuid4())}
    
    async def _get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status"""
        agent_id = params.get("agent_id")
        
        if not agent_id:
            raise ValueError("Agent ID is required")
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        return {"agent": agent}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent plugin capabilities"""
        return {
            "methods": [
                "agent.register",
                "agent.list",
                "agent.message",
                "agent.status"
            ],
            "description": "Agent management operations",
            "version": self.version
        }

class MCPServer:
    """MCP Server with plugin system"""
    
    def __init__(self, host: str = "localhost", port: int = 8766):
        self.host = host
        self.port = port
        self.plugins: Dict[str, MCPPlugin] = {}
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
    def register_plugin(self, plugin: MCPPlugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
        try:
            async for message in websocket:
                await self.handle_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def handle_message(self, client_id: str, raw_message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(raw_message)
            message = MCPMessage(**data)
            
            # Route message to appropriate plugin
            plugin_name = message.method.split('.')[0]
            
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                if plugin.enabled:
                    response = await plugin.handle_message(message)
                else:
                    response = MCPResponse(
                        id=message.id,
                        error={"code": -2, "message": f"Plugin {plugin_name} is disabled"}
                    )
            else:
                response = MCPResponse(
                    id=message.id,
                    error={"code": -3, "message": f"Unknown plugin: {plugin_name}"}
                )
            
            # Send response back to client
            await self.send_response(client_id, response)
            
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            error_response = MCPResponse(
                id="unknown",
                error={"code": -4, "message": str(e)}
            )
            await self.send_response(client_id, error_response)
    
    async def send_response(self, client_id: str, response: MCPResponse):
        """Send response to client"""
        if client_id in self.clients:
            websocket = self.clients[client_id]
            try:
                await websocket.send(json.dumps(asdict(response)))
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Failed to send response to {client_id}: connection closed")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[ws.send(json.dumps(message)) for ws in self.clients.values()],
                return_exceptions=True
            )
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "host": self.host,
            "port": self.port,
            "plugins": {
                name: plugin.get_capabilities()
                for name, plugin in self.plugins.items()
            },
            "connected_clients": len(self.clients),
            "status": "running"
        }
    
    async def start(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"MCP server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

class MCPClient:
    """MCP Client for connecting to MCP servers"""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.connected = False
        self.message_queue = asyncio.Queue()
        self.responses = {}
    
    async def connect(self):
        """Connect to MCP server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            logger.info(f"Connected to MCP server at {self.uri}")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.uri}: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from MCP server")
    
    async def _handle_messages(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                response = MCPResponse(**data)
                
                # Store response for waiting requests
                self.responses[response.id] = response
                
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            logger.info("Connection to MCP server closed")
    
    async def send_message(self, method: str, params: Dict[str, Any]) -> MCPResponse:
        """Send message to MCP server and wait for response"""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        message_id = str(uuid.uuid4())
        message = MCPMessage(id=message_id, method=method, params=params)
        
        # Send message
        await self.websocket.send(json.dumps(asdict(message)))
        
        # Wait for response
        timeout = 30  # 30 second timeout
        for _ in range(timeout * 10):  # Check every 100ms
            if message_id in self.responses:
                response = self.responses.pop(message_id)
                return response
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"No response received for message {message_id}")

# Example usage and testing
async def main():
    """Example usage of MCP system"""
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig
    from mem0.llms.configs import LlmConfig
    from mem0.embeddings.configs import EmbedderConfig
    from mem0.vector_stores.configs import VectorStoreConfig
    
    # Create memory system
    config = MemoryConfig(
        llm=LlmConfig(
            provider="ollama",
            config={
                "model": "llama3.2:3b",
                "ollama_base_url": "http://localhost:11434"
            }
        ),
        embedder=EmbedderConfig(
            provider="ollama", 
            config={
                "model": "nomic-embed-text",
                "ollama_base_url": "http://localhost:11434",
                "embedding_dims": 768
            }
        ),
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "host": "localhost",
                "port": 6333,
                "collection_name": "mcp_memories",
                "embedding_model_dims": 768
            }
        )
    )
    
    memory = Memory(config)
    
    # Create MCP server
    server = MCPServer(host="localhost", port=18766)
    
    # Register plugins
    memory_plugin = MemoryMCPPlugin(memory)
    agent_plugin = AgentMCPPlugin({})
    
    server.register_plugin(memory_plugin)
    server.register_plugin(agent_plugin)
    
    print("🚀 MCP Server starting...")
    print(f"Server info: {json.dumps(server.get_server_info(), indent=2)}")
    print("Connect to: ws://localhost:18766")
    print("Available methods:")
    for plugin_name, plugin in server.plugins.items():
        capabilities = plugin.get_capabilities()
        print(f"  {plugin_name}: {capabilities['methods']}")
    
    # Start server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())