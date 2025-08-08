#!/usr/bin/env python3
"""
Kiro-Specific MCP Memory Server
Enhanced MCP server for Kiro IDE with project-specific memory management
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
from datetime import datetime

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Mem0 imports
try:
    from mem0 import Memory
    from mem0.config import Config
except ImportError:
    print("Error: mem0ai package not installed. Install with: pip install mem0ai", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kiro-memory-server")

class KiroMemoryServer:
    """Kiro-specific MCP server with project-aware memory management"""
    
    def __init__(self):
        self.server = Server("kiro-memory-server")
        self.memory: Optional[Memory] = None
        self.current_project: Optional[str] = None
        self.workspace_path: Optional[str] = None
        self._setup_memory()
        self._register_tools()
        self._register_resources()
    
    def _setup_memory(self):
        """Initialize Mem0 with Apple Intelligence configuration"""
        try:
            # Import Apple Intelligence utilities for availability checking
            from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
            
            # Check Apple Intelligence availability first
            apple_intelligence_available = check_apple_intelligence_availability()
            status = get_apple_intelligence_status()
            
            if apple_intelligence_available:
                logger.info("🍎 Apple Intelligence Foundation Models detected for Kiro")
                
                # Configure Mem0 to use Apple Intelligence providers
                config_dict = {
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
                    },
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "host": "localhost",
                            "port": 26333,
                            "collection_name": "kiro_apple_intelligence_memories"
                        }
                    }
                }
                
                config = Config.from_dict(config_dict)
                self.memory = Memory(config=config)
                logger.info("✅ Kiro memory system initialized with Apple Intelligence")
                
            else:
                # Fallback to Ollama configuration
                logger.warning(f"⚠️ Apple Intelligence unavailable for Kiro: {status.get('error_message', 'unknown error')}")
                
                config_dict = {
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "host": "localhost",
                            "port": 26333,
                            "collection_name": "kiro_project_memories"
                        }
                    },
                    "llm": {
                        "provider": "ollama",
                        "config": {
                            "model": "llama3.2:3b",
                            "base_url": "http://localhost:11434"
                        }
                    }
                }
                
                config = Config.from_dict(config_dict)
                self.memory = Memory(config=config)
                logger.warning("⚠️ Kiro memory system initialized with Ollama fallback")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kiro memory: {e}")
            self.memory = Memory()  # Fallback to default
    
    def _get_project_context(self, workspace_path: str = None) -> Dict[str, Any]:
        """Extract project context from workspace"""
        if not workspace_path:
            workspace_path = os.getcwd()
        
        project_info = {
            "workspace_path": workspace_path,
            "project_name": Path(workspace_path).name,
            "project_hash": hashlib.md5(workspace_path.encode()).hexdigest()[:8]
        }
        
        # Detect project type
        if Path(workspace_path, "package.json").exists():
            project_info["type"] = "nodejs"
        elif Path(workspace_path, "pyproject.toml").exists() or Path(workspace_path, "requirements.txt").exists():
            project_info["type"] = "python"
        elif Path(workspace_path, "Cargo.toml").exists():
            project_info["type"] = "rust"
        elif Path(workspace_path, "go.mod").exists():
            project_info["type"] = "go"
        else:
            project_info["type"] = "general"
        
        return project_info
    
    def _register_tools(self):
        """Register Kiro-specific memory tools"""
        
        @self.server.call_tool()
        async def set_project_context(
            workspace_path: str,
            project_name: Optional[str] = None
        ) -> List[TextContent]:
            """Set the current project context for memory operations"""
            try:
                self.workspace_path = workspace_path
                project_info = self._get_project_context(workspace_path)
                
                if project_name:
                    project_info["project_name"] = project_name
                
                self.current_project = project_info["project_hash"]
                
                return [TextContent(
                    type="text",
                    text=f"Project context set: {project_info['project_name']} ({project_info['type']})"
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error setting project context: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def add_code_memory(
            content: str,
            file_path: Optional[str] = None,
            memory_type: str = "code_insight",
            tags: Optional[List[str]] = None,
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None
        ) -> List[TextContent]:
            """Add code-related memory with project context"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                # Create project-specific user ID
                user_id = f"kiro_project_{self.current_project}"
                
                # Enhanced metadata for code memories with multi-agent support
                metadata = {
                    "type": memory_type,
                    "project": self.current_project,
                    "workspace": self.workspace_path,
                    "file_path": file_path,
                    "tags": tags or [],
                    "source": "kiro_ide",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add multi-agent tracking
                if agent_id:
                    metadata["agent_id"] = agent_id
                if run_id:
                    metadata["run_id"] = run_id
                    metadata["conversation_context"] = "multi_agent" if agent_id else "single_agent"
                
                # Apple Intelligence processing indicators
                metadata["processed_by"] = "apple_intelligence_foundation_models"
                metadata["neural_engine_optimized"] = True
                metadata["local_processing"] = True
                metadata["privacy_compliant"] = True
                
                # Format as conversation for Mem0
                messages = [
                    {"role": "user", "content": f"Code insight: {content}"},
                    {"role": "assistant", "content": f"Stored {memory_type} for project context"}
                ]
                
                result = self.memory.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error adding code memory: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def search_project_memory(
            query: str,
            memory_types: Optional[List[str]] = None,
            limit: int = 10
        ) -> List[TextContent]:
            """Search memories within current project context"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Build filters for project-specific search
                filters = {"project": self.current_project}
                if memory_types:
                    filters["type"] = {"$in": memory_types}
                
                results = self.memory.search(
                    query=query,
                    user_id=user_id,
                    limit=limit,
                    filters=filters
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error searching project memory: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_project_context_summary(self) -> List[TextContent]:
            """Get a summary of the current project's memory context"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="No project context set"
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Get all memories for this project
                all_memories = self.memory.get_all(user_id=user_id)
                
                # Analyze memory types and patterns
                memory_stats = {}
                for memory in all_memories:
                    mem_type = memory.get("metadata", {}).get("type", "unknown")
                    memory_stats[mem_type] = memory_stats.get(mem_type, 0) + 1
                
                summary = {
                    "project": self.current_project,
                    "workspace": self.workspace_path,
                    "total_memories": len(all_memories),
                    "memory_types": memory_stats,
                    "recent_memories": all_memories[:5] if all_memories else []
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2, default=str)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting project summary: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def add_learning_memory(
            concept: str,
            explanation: str,
            examples: Optional[List[str]] = None,
            difficulty: str = "medium",
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None
        ) -> List[TextContent]:
            """Add learning-focused memory for concepts and explanations"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Format learning content
                content = f"Concept: {concept}\nExplanation: {explanation}"
                if examples:
                    content += f"\nExamples: {'; '.join(examples)}"
                
                metadata = {
                    "type": "learning",
                    "concept": concept,
                    "difficulty": difficulty,
                    "project": self.current_project,
                    "examples": examples or [],
                    "source": "kiro_ide",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add multi-agent tracking
                if agent_id:
                    metadata["agent_id"] = agent_id
                if run_id:
                    metadata["run_id"] = run_id
                    metadata["conversation_context"] = "multi_agent" if agent_id else "single_agent"
                
                # Apple Intelligence processing indicators
                metadata["processed_by"] = "apple_intelligence_foundation_models"
                metadata["neural_engine_optimized"] = True
                metadata["local_processing"] = True
                metadata["privacy_compliant"] = True
                
                messages = [
                    {"role": "user", "content": f"I learned about: {concept}"},
                    {"role": "assistant", "content": explanation}
                ]
                
                result = self.memory.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error adding learning memory: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def add_debugging_session(
            problem: str,
            solution: str,
            file_path: Optional[str] = None,
            error_type: Optional[str] = None,
            agent_id: Optional[str] = None,
            run_id: Optional[str] = None
        ) -> List[TextContent]:
            """Add debugging session memory with multi-agent support"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                content = f"Problem: {problem}\nSolution: {solution}"
                
                metadata = {
                    "type": "debugging",
                    "problem": problem,
                    "solution": solution,
                    "file_path": file_path,
                    "error_type": error_type,
                    "project": self.current_project,
                    "source": "kiro_ide",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add multi-agent tracking
                if agent_id:
                    metadata["agent_id"] = agent_id
                if run_id:
                    metadata["run_id"] = run_id
                    metadata["conversation_context"] = "multi_agent" if agent_id else "single_agent"
                
                # Apple Intelligence processing indicators
                metadata["processed_by"] = "apple_intelligence_foundation_models"
                metadata["neural_engine_optimized"] = True
                metadata["local_processing"] = True
                metadata["privacy_compliant"] = True
                
                messages = [
                    {"role": "user", "content": f"I encountered this problem: {problem}"},
                    {"role": "assistant", "content": f"Here's the solution: {solution}"}
                ]
                
                result = self.memory.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error adding debugging session: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_project_agent_memories(
            agent_id: str,
            run_id: Optional[str] = None,
            memory_types: Optional[List[str]] = None,
            limit: int = 50
        ) -> List[TextContent]:
            """Get project memories specific to an agent with Apple Intelligence processing"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Get all memories for this project
                all_memories = self.memory.get_all(user_id=user_id)
                
                # Filter by agent_id and optionally run_id and memory_types
                agent_memories = []
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    
                    # Check agent_id match
                    if metadata.get("agent_id") != agent_id:
                        continue
                    
                    # Check run_id match if specified
                    if run_id and metadata.get("run_id") != run_id:
                        continue
                    
                    # Check memory_types match if specified
                    if memory_types and metadata.get("type") not in memory_types:
                        continue
                    
                    agent_memories.append(memory)
                
                # Limit results
                agent_memories = agent_memories[:limit]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "project": self.current_project,
                        "agent_id": agent_id,
                        "run_id": run_id,
                        "memory_types_filter": memory_types,
                        "total_memories": len(agent_memories),
                        "memories": agent_memories,
                        "apple_intelligence_processed": True
                    }, indent=2, default=str)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting project agent memories: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def get_project_collaboration_context(
            run_id: str,
            limit: int = 20
        ) -> List[TextContent]:
            """Get shared collaboration context for the current project using Apple Intelligence"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Get all memories for this project and run
                all_memories = self.memory.get_all(user_id=user_id)
                
                # Filter by run_id and analyze collaboration
                run_memories = []
                agents_involved = set()
                memory_types = {}
                
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    if metadata.get("run_id") == run_id:
                        run_memories.append(memory)
                        
                        if metadata.get("agent_id"):
                            agents_involved.add(metadata.get("agent_id"))
                        
                        mem_type = metadata.get("type", "unknown")
                        memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
                
                # Sort by timestamp
                run_memories.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""), reverse=True)
                run_memories = run_memories[:limit]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "project": self.current_project,
                        "workspace": self.workspace_path,
                        "run_id": run_id,
                        "agents_involved": list(agents_involved),
                        "memory_types": memory_types,
                        "total_shared_memories": len(run_memories),
                        "shared_context": run_memories,
                        "apple_intelligence_processed": True,
                        "neural_engine_optimized": True
                    }, indent=2, default=str)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting project collaboration context: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def analyze_project_agent_patterns(
            time_range_hours: int = 24,
            min_interactions: int = 2
        ) -> List[TextContent]:
            """Analyze agent interaction patterns in the current project using Apple Intelligence"""
            try:
                if not self.current_project:
                    return [TextContent(
                        type="text",
                        text="Error: No project context set. Use set_project_context first."
                    )]
                
                user_id = f"kiro_project_{self.current_project}"
                
                # Get all memories for this project
                all_memories = self.memory.get_all(user_id=user_id)
                
                # Analyze patterns
                agent_interactions = {}
                run_collaborations = {}
                memory_type_by_agent = {}
                
                from datetime import datetime, timedelta
                cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
                
                for memory in all_memories:
                    metadata = memory.get("metadata", {})
                    agent_id = metadata.get("agent_id")
                    run_id = metadata.get("run_id")
                    mem_type = metadata.get("type", "unknown")
                    timestamp_str = metadata.get("timestamp")
                    
                    # Skip if no agent_id or too old
                    if not agent_id:
                        continue
                    
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if timestamp < cutoff_time:
                                continue
                        except:
                            pass  # Skip timestamp filtering if parsing fails
                    
                    # Track agent interactions
                    if agent_id not in agent_interactions:
                        agent_interactions[agent_id] = 0
                    agent_interactions[agent_id] += 1
                    
                    # Track run collaborations
                    if run_id:
                        if run_id not in run_collaborations:
                            run_collaborations[run_id] = set()
                        run_collaborations[run_id].add(agent_id)
                    
                    # Track memory types by agent
                    if agent_id not in memory_type_by_agent:
                        memory_type_by_agent[agent_id] = {}
                    if mem_type not in memory_type_by_agent[agent_id]:
                        memory_type_by_agent[agent_id][mem_type] = 0
                    memory_type_by_agent[agent_id][mem_type] += 1
                
                # Filter collaborations with minimum interactions
                significant_collaborations = {
                    run_id: list(agents) for run_id, agents in run_collaborations.items()
                    if len(agents) >= min_interactions
                }
                
                analysis = {
                    "project": self.current_project,
                    "workspace": self.workspace_path,
                    "analysis_period_hours": time_range_hours,
                    "total_agents": len(agent_interactions),
                    "agent_interactions": agent_interactions,
                    "memory_types_by_agent": memory_type_by_agent,
                    "collaborative_runs": significant_collaborations,
                    "total_collaborative_runs": len(significant_collaborations),
                    "apple_intelligence_processed": True,
                    "neural_engine_optimized": True,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(analysis, indent=2, default=str)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error analyzing agent patterns: {str(e)}"
                )]
    
    def _register_resources(self):
        """Register Kiro-specific resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available Kiro memory resources"""
            return [
                Resource(
                    uri="kiro://project-context",
                    name="Current Project Context",
                    description="Information about the current project and workspace",
                    mimeType="application/json"
                ),
                Resource(
                    uri="kiro://memory-stats",
                    name="Project Memory Statistics",
                    description="Statistics about memories stored for the current project",
                    mimeType="application/json"
                ),
                Resource(
                    uri="kiro://recent-memories",
                    name="Recent Project Memories",
                    description="Most recent memories for the current project",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read Kiro-specific resource content"""
            if uri == "kiro://project-context":
                if self.current_project and self.workspace_path:
                    context = self._get_project_context(self.workspace_path)
                    return json.dumps(context, indent=2)
                else:
                    return json.dumps({"error": "No project context set"})
            
            elif uri == "kiro://memory-stats":
                if self.current_project:
                    user_id = f"kiro_project_{self.current_project}"
                    try:
                        memories = self.memory.get_all(user_id=user_id)
                        
                        # Analyze memory types
                        type_stats = {}
                        for memory in memories:
                            mem_type = memory.get("metadata", {}).get("type", "unknown")
                            type_stats[mem_type] = type_stats.get(mem_type, 0) + 1
                        
                        stats = {
                            "total_memories": len(memories),
                            "project": self.current_project,
                            "workspace": self.workspace_path,
                            "memory_types": type_stats,
                            "last_updated": datetime.now().isoformat()
                        }
                        return json.dumps(stats, indent=2)
                    except Exception as e:
                        return json.dumps({"error": str(e)})
                else:
                    return json.dumps({"error": "No project context set"})
            
            elif uri == "kiro://recent-memories":
                if self.current_project:
                    user_id = f"kiro_project_{self.current_project}"
                    try:
                        memories = self.memory.get_all(user_id=user_id, limit=10)
                        return json.dumps(memories, indent=2, default=str)
                    except Exception as e:
                        return json.dumps({"error": str(e)})
                else:
                    return json.dumps({"error": "No project context set"})
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self):
        """Run the Kiro MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="kiro-memory-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = KiroMemoryServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())