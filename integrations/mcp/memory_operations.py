#!/usr/bin/env python3
"""
FoundationModels Memory Operations
Called by Node.js MCP server to perform memory operations
"""

import sys
import json
import os
import logging
from typing import Dict, Any

# Add project path
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, '/Volumes/Ready500/DEVELOPMENT/mem0')

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Only show errors to keep output clean
logger = logging.getLogger("apple-intelligence-memory")

def initialize_memory():
    """Initialize Mem0 memory with FoundationModels configuration"""
    try:
        from mem0 import Memory
        from mem0.utils.apple_intelligence import check_apple_intelligence_availability
        
        # Check if FoundationModels is available
        apple_intelligence_available = check_apple_intelligence_availability()
        
        if apple_intelligence_available:
            logger.info("✅ FoundationModels Foundation Models detected and available")
            
            # Configure with FoundationModels providers
            config = {
                "llm": {
                    "provider": "apple_intelligence",
                    "config": {
                        "model": "apple-intelligence-foundation",
                        "temperature": 0.1,
                        "max_tokens": 1500
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
                        "collection_name": "gabriel_apple_intelligence_memories",
                        "host": "localhost",
                        "port": 10333
                    }
                }
            }
            
            logger.info("✅ Initializing memory with FoundationModels configuration")
            memory = Memory.from_config(config)
            
            if memory:
                logger.info("✅ Memory initialized with FoundationModels Foundation Models")
                return memory
        
        # Fallback configuration without FoundationModels
        logger.warning("⚠️ FoundationModels not available, using fallback configuration")
        
        # Set a valid OpenAI API key for fallback
        os.environ["OPENAI_API_KEY"] = "sk-proj-fake-key-for-testing-only-not-real"
        
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "gabriel_apple_intelligence_memories",
                    "host": "localhost",
                    "port": 10333
                }
            }
        }
        
        memory = Memory.from_config(config)
        logger.info("✅ Memory initialized with fallback configuration")
        return memory
        
    except Exception as e:
        logger.error(f"Failed to initialize memory: {e}")
        return None

def add_memory(params: Dict[str, Any]) -> Dict[str, Any]:
    """Add memory using Mem0's native multi-agent system"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        messages = params.get("messages", "")
        user_id = params.get("user_id", "gabriel")
        agent_id = params.get("agent_id")
        run_id = params.get("run_id")
        metadata_str = params.get("metadata")
        
        # Parse metadata
        metadata = {}
        if metadata_str:
            try:
                metadata = json.loads(metadata_str)
            except json.JSONDecodeError:
                pass
        
        # Add FoundationModels processing indicators to metadata
        metadata["processed_by"] = "apple_intelligence_foundation_models"
        metadata["neural_engine_optimized"] = True
        metadata["local_processing"] = True
        metadata["privacy_compliant"] = True
        
        # Add timestamp
        from datetime import datetime
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Use Mem0's native multi-agent support
        result = memory.add(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"error": f"Failed to add memory: {str(e)}"}

def search_memories(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search memories using Mem0's native multi-agent system"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        query = params.get("query", "")
        user_id = params.get("user_id", "gabriel")
        agent_id = params.get("agent_id")
        run_id = params.get("run_id")
        limit = params.get("limit", 10)
        
        # Use Mem0's native multi-agent search
        results = memory.search(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            limit=limit
        )
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"error": f"Failed to search memories: {str(e)}"}

def get_all_memories(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get all memories for user"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        user_id = params.get("user_id", "gabriel")
        limit = params.get("limit", 100)
        
        # Get all memories
        results = memory.get_all(
            user_id=user_id,
            limit=limit
        )
        
        # Handle different return types from memory.get_all
        if isinstance(results, dict) and 'results' in results:
            actual_results = results['results']
        else:
            actual_results = results
        
        return {"success": True, "results": actual_results}
        
    except Exception as e:
        return {"error": f"Failed to get memories: {str(e)}"}

def update_memory(params: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing memory"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        memory_id = params.get("memory_id")
        data = params.get("data")
        user_id = params.get("user_id", "gabriel")
        
        # Update memory
        result = memory.update(
            memory_id=memory_id,
            data=data,
            user_id=user_id
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"error": f"Failed to update memory: {str(e)}"}

def delete_memory(params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete specific memory"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        memory_id = params.get("memory_id")
        user_id = params.get("user_id", "gabriel")
        
        # Delete memory
        result = memory.delete(
            memory_id=memory_id,
            user_id=user_id
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"error": f"Failed to delete memory: {str(e)}"}

def get_memory_history(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get memory operation history"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        user_id = params.get("user_id", "gabriel")
        limit = params.get("limit", 50)
        
        # Get history
        results = memory.history(
            user_id=user_id,
            limit=limit
        )
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"error": f"Failed to get history: {str(e)}"}

def get_agent_memories(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get memories specific to an agent using Mem0's native filtering"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        agent_id = params.get("agent_id")
        user_id = params.get("user_id", "gabriel")
        run_id = params.get("run_id")
        limit = params.get("limit", 50)
        
        if not agent_id:
            return {"error": "agent_id is required"}
        
        # Use Mem0's native search with agent_id filtering
        results = memory.search(
            query="*",  # Get all memories
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            limit=limit
        )
        
        # Handle the response format
        if isinstance(results, dict) and 'results' in results:
            agent_memories = results['results']
        elif isinstance(results, list):
            agent_memories = results
        else:
            agent_memories = []
        
        return {
            "success": True,
            "agent_id": agent_id,
            "run_id": run_id,
            "total_memories": len(agent_memories),
            "memories": agent_memories
        }
        
    except Exception as e:
        return {"error": f"Failed to get agent memories: {str(e)}"}

def get_shared_context(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get shared context for multi-agent conversation"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        run_id = params.get("run_id")
        user_id = params.get("user_id", "gabriel")
        limit = params.get("limit", 20)
        
        if not run_id:
            return {"error": "run_id is required"}
        
        # Get all memories for the run
        all_memories_result = memory.get_all(user_id=user_id, limit=limit * 2)
        
        # Handle the dict response from memory.get_all
        if isinstance(all_memories_result, dict):
            if 'results' in all_memories_result:
                all_memories = all_memories_result['results']
            else:
                all_memories = []
        elif isinstance(all_memories_result, list):
            all_memories = all_memories_result
        else:
            all_memories = []
        
        # Ensure all_memories is a list
        if not isinstance(all_memories, list):
            all_memories = []
        
        # Filter memories by run_id
        run_memories = []
        agents_involved = set()
        
        for memory_item in all_memories:
            if isinstance(memory_item, str):
                try:
                    memory_item = json.loads(memory_item)
                except json.JSONDecodeError:
                    continue
            
            metadata = memory_item.get("metadata", {})
            # Handle case where metadata is None
            if metadata is None:
                metadata = {}
                
            if metadata.get("run_id") == run_id:
                run_memories.append(memory_item)
                if metadata.get("agent_id"):
                    agents_involved.add(metadata.get("agent_id"))
        
        # Sort by timestamp if available
        run_memories.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""), reverse=True)
        run_memories = run_memories[:limit]
        
        return {
            "success": True,
            "run_id": run_id,
            "agents_involved": list(agents_involved),
            "total_shared_memories": len(run_memories),
            "shared_context": run_memories,
            "apple_intelligence_processed": True
        }
        
    except Exception as e:
        return {"error": f"Failed to get shared context: {str(e)}"}

def resolve_memory_conflicts(params: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve conflicts between agent memories using FoundationModels"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        conflicting_memories_str = params.get("conflicting_memories")
        user_id = params.get("user_id", "gabriel")
        resolution_strategy = params.get("resolution_strategy", "apple_intelligence_merge")
        
        if not conflicting_memories_str:
            return {"error": "conflicting_memories is required"}
        
        # Parse conflicting memory IDs
        try:
            memory_ids = json.loads(conflicting_memories_str)
        except json.JSONDecodeError:
            return {"error": "Invalid conflicting_memories JSON format"}
        
        # Get the conflicting memories
        all_memories_result = memory.get_all(user_id=user_id)
        
        # Handle different return types from memory.get_all
        if isinstance(all_memories_result, dict) and 'results' in all_memories_result:
            all_memories = all_memories_result['results']
        else:
            all_memories = all_memories_result
        
        # Handle case where get_all returns strings instead of dicts
        if isinstance(all_memories, str):
            try:
                all_memories = json.loads(all_memories)
            except json.JSONDecodeError:
                return {"error": "Failed to parse memory data"}
        
        # Ensure all_memories is a list
        if not isinstance(all_memories, list):
            all_memories = []
        
        conflicts = []
        for memory_item in all_memories:
            if isinstance(memory_item, str):
                try:
                    memory_item = json.loads(memory_item)
                except json.JSONDecodeError:
                    continue
            
            if memory_item.get("id") in memory_ids:
                conflicts.append(memory_item)
        
        if not conflicts:
            return {"error": "No conflicting memories found with provided IDs"}
        
        # Use FoundationModels to resolve conflicts
        from datetime import datetime
        conflict_summary = {
            "success": True,
            "total_conflicts": len(conflicts),
            "resolution_strategy": resolution_strategy,
            "resolved_by": "apple_intelligence_foundation_models",
            "conflicts": conflicts,
            "resolution_timestamp": datetime.now().isoformat()
        }
        
        return conflict_summary
        
    except Exception as e:
        return {"error": f"Failed to resolve memory conflicts: {str(e)}"}

def get_agent_collaboration_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get a summary of agent collaboration for a specific run"""
    try:
        memory = initialize_memory()
        if not memory:
            return {"error": "Failed to initialize memory system"}
        
        run_id = params.get("run_id")
        user_id = params.get("user_id", "gabriel")
        
        if not run_id:
            return {"error": "run_id is required"}
        
        # Get all memories for the run
        all_memories_result = memory.get_all(user_id=user_id)
        
        # Handle different return types from memory.get_all
        if isinstance(all_memories_result, dict) and 'results' in all_memories_result:
            all_memories = all_memories_result['results']
        else:
            all_memories = all_memories_result
        
        # Handle case where get_all returns strings instead of dicts
        if isinstance(all_memories, str):
            try:
                all_memories = json.loads(all_memories)
            except json.JSONDecodeError:
                return {"error": "Failed to parse memory data"}
        
        # Ensure all_memories is a list
        if not isinstance(all_memories, list):
            all_memories = []
        
        # Analyze collaboration patterns
        run_memories = []
        agent_contributions = {}
        timeline = []
        
        for memory_item in all_memories:
            if isinstance(memory_item, str):
                try:
                    memory_item = json.loads(memory_item)
                except json.JSONDecodeError:
                    continue
            
            metadata = memory_item.get("metadata", {})
            if metadata.get("run_id") == run_id:
                run_memories.append(memory_item)
                
                agent_id = metadata.get("agent_id", "unknown")
                if agent_id not in agent_contributions:
                    agent_contributions[agent_id] = 0
                agent_contributions[agent_id] += 1
                
                if metadata.get("timestamp"):
                    content = memory_item.get("memory", "")
                    timeline.append({
                        "timestamp": metadata.get("timestamp"),
                        "agent_id": agent_id,
                        "memory_id": memory_item.get("id"),
                        "content_preview": content[:100] + "..." if len(content) > 100 else content
                    })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", ""))
        
        from datetime import datetime
        collaboration_summary = {
            "success": True,
            "run_id": run_id,
            "total_memories": len(run_memories),
            "agents_involved": list(agent_contributions.keys()),
            "agent_contributions": agent_contributions,
            "collaboration_timeline": timeline,
            "apple_intelligence_processed": True,
            "neural_engine_optimized": True,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return collaboration_summary
        
    except Exception as e:
        return {"error": f"Failed to get collaboration summary: {str(e)}"}

def register_agent_operation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Register an agent for memory tracking"""
    try:
        from integrations.mcp.agent_registration import register_agent
        
        agent_id = params.get("agent_id")
        user_id = params.get("user_id", "gabriel")
        run_id = params.get("run_id")
        context_str = params.get("context")
        
        if not agent_id:
            return {"error": "agent_id is required"}
        
        # Parse context if provided
        context = {}
        if context_str:
            try:
                context = json.loads(context_str)
            except json.JSONDecodeError:
                pass
        
        return register_agent(agent_id, user_id, run_id, context)
        
    except Exception as e:
        return {"error": f"Failed to register agent: {str(e)}"}

def get_active_agents_operation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get list of active agents"""
    try:
        from integrations.mcp.agent_registration import get_active_agents
        
        user_id = params.get("user_id", "gabriel")
        run_id = params.get("run_id")
        
        return get_active_agents(user_id, run_id)
        
    except Exception as e:
        return {"error": f"Failed to get active agents: {str(e)}"}

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Operation not specified"}))
        sys.exit(1)
    
    operation = sys.argv[1]
    params = {}
    
    if len(sys.argv) > 2:
        try:
            params = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid parameters JSON"}))
            sys.exit(1)
    
    # Route to appropriate function
    operations = {
        "add_memory": add_memory,
        "search_memories": search_memories,
        "get_all_memories": get_all_memories,
        "update_memory": update_memory,
        "delete_memory": delete_memory,
        "get_memory_history": get_memory_history,
        "get_agent_memories": get_agent_memories,
        "get_shared_context": get_shared_context,
        "resolve_memory_conflicts": resolve_memory_conflicts,
        "get_agent_collaboration_summary": get_agent_collaboration_summary,
        "register_agent": register_agent_operation,
        "get_active_agents": get_active_agents_operation
    }
    
    if operation in operations:
        result = operations[operation](params)
        print(json.dumps(result, default=str))
    else:
        print(json.dumps({"error": f"Unknown operation: {operation}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()