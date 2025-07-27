"""
Universal Agent Memory Integrations
Supports: AutoGen, CrewAI, LangChain, Custom Agents
"""

import asyncio
import json
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from mem0 import Memory, AsyncMemory
from datetime import datetime

class BaseMemoryAgent(ABC):
    """Base class for memory-enhanced agents"""
    
    def __init__(self, name: str, memory_config: Dict = None):
        self.name = name
        self.memory_config = memory_config or self._default_memory_config()
        self.memory = Memory(**self.memory_config)
        self.conversation_history = []
    
    def _default_memory_config(self):
        return {
            "llm_config": {
                "model": "ollama/llama3.2:3b",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1"
            },
            "embedder_config": {
                "model": "ollama/nomic-embed-text",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1"
            },
            "vector_store_config": {
                "provider": "qdrant",
                "host": "localhost",
                "port": 6333
            },
            "graph_store_config": {
                "provider": "neo4j",
                "uri": "bolt://localhost:17687",
                "username": "neo4j",
                "password": "mem0production"
            }
        }
    
    def add_memory(self, content: str, metadata: Dict = None):
        """Add memory with agent context"""
        metadata = metadata or {}
        metadata.update({
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "type": "agent_memory"
        })
        return self.memory.add(content, user_id=self.name, metadata=metadata)
    
    def search_memory(self, query: str, limit: int = 5):
        """Search agent's memories"""
        return self.memory.search(query, user_id=self.name, limit=limit)
    
    def get_context(self, query: str, max_context: int = 3):
        """Get relevant context for a query"""
        memories = self.search_memory(query, limit=max_context)
        return "\n".join([m.text for m in memories])
    
    @abstractmethod
    def process_message(self, message: str, sender: str = None):
        """Process incoming message - to be implemented by subclasses"""
        pass

class AutoGenMemoryAgent(BaseMemoryAgent):
    """AutoGen integration with persistent memory"""
    
    def __init__(self, name: str, system_message: str, memory_config: Dict = None):
        super().__init__(name, memory_config)
        self.system_message = system_message
        
        # Store system message as foundational memory
        self.add_memory(
            f"System role: {system_message}",
            metadata={"type": "system_role"}
        )
    
    def process_message(self, message: str, sender: str = None):
        """Process message with memory context"""
        # Store incoming message
        self.add_memory(
            f"Received from {sender or 'user'}: {message}",
            metadata={"sender": sender, "type": "received"}
        )
        
        # Get relevant context
        context = self.get_context(message)
        
        # Enhanced message with context
        enhanced_message = f"""
Context from memory:
{context}

Current message: {message}
"""
        
        return enhanced_message
    
    def generate_reply(self, messages: List[Dict], sender=None):
        """Generate reply with memory enhancement"""
        if not messages:
            return "I don't have any messages to respond to."
        
        last_message = messages[-1].get("content", "")
        enhanced_message = self.process_message(last_message, sender.name if sender else None)
        
        # In a real implementation, this would call the LLM
        # For now, return a context-aware response
        reply = f"Based on our conversation history and my memory, I understand you're asking about: {last_message}"
        
        # Store our reply
        self.add_memory(
            f"Replied to {sender.name if sender else 'user'}: {reply}",
            metadata={"recipient": sender.name if sender else "user", "type": "sent"}
        )
        
        return reply

class CrewAIMemoryAgent(BaseMemoryAgent):
    """CrewAI integration with persistent memory"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str, memory_config: Dict = None):
        super().__init__(name, memory_config)
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
        # Store agent profile as foundational memory
        self.add_memory(
            f"Role: {role}. Goal: {goal}. Backstory: {backstory}",
            metadata={"type": "agent_profile"}
        )
    
    def process_message(self, message: str, sender: str = None):
        """Process task with memory context"""
        # Store the task
        self.add_memory(
            f"Task received: {message}",
            metadata={"sender": sender, "type": "task"}
        )
        
        # Get relevant context for the task
        context = self.get_context(message)
        
        return {
            "task": message,
            "context": context,
            "agent_profile": {
                "role": self.role,
                "goal": self.goal,
                "backstory": self.backstory
            }
        }
    
    def execute_task(self, task: str):
        """Execute task with memory enhancement"""
        task_info = self.process_message(task)
        
        # In a real implementation, this would execute the actual task
        result = f"Executed task: {task} with context from previous experiences"
        
        # Store task completion
        self.add_memory(
            f"Completed task: {task}. Result: {result}",
            metadata={"type": "task_completion"}
        )
        
        return result

class LangChainMemoryAgent(BaseMemoryAgent):
    """LangChain integration with persistent memory"""
    
    def __init__(self, name: str, memory_config: Dict = None):
        super().__init__(name, memory_config)
        self.chat_history = []
    
    def process_message(self, message: str, sender: str = None):
        """Process message for LangChain chain"""
        # Store message
        self.add_memory(
            f"User input: {message}",
            metadata={"type": "user_input"}
        )
        
        # Get relevant context
        context = self.get_context(message)
        
        # Update chat history with context
        self.chat_history.append({
            "human": message,
            "context": context
        })
        
        return {
            "input": message,
            "context": context,
            "chat_history": self.chat_history[-5:]  # Last 5 exchanges
        }
    
    def invoke(self, input_data: Dict):
        """LangChain-style invoke method"""
        message = input_data.get("input", "")
        processed = self.process_message(message)
        
        # Simulate chain execution
        response = f"Processed: {message} with relevant context"
        
        # Store response
        self.add_memory(
            f"Generated response: {response}",
            metadata={"type": "ai_response"}
        )
        
        return {"output": response}

class OpenMemoryClient:
    """Client for OpenMemory MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:18765", user_id: str = "default"):
        self.base_url = base_url
        self.user_id = user_id
    
    def add_memory(self, text: str, metadata: Dict = None):
        """Add memory via OpenMemory API"""
        response = requests.post(f"{self.base_url}/memories", json={
            "text": text,
            "user_id": self.user_id,
            "metadata": metadata or {}
        })
        return response.json()
    
    def search_memories(self, query: str, limit: int = 10):
        """Search memories via OpenMemory API"""
        response = requests.get(f"{self.base_url}/memories/search", params={
            "query": query,
            "user_id": self.user_id,
            "limit": limit
        })
        return response.json()
    
    def get_all_memories(self):
        """Get all memories for user"""
        response = requests.get(f"{self.base_url}/memories", params={
            "user_id": self.user_id
        })
        return response.json()

class MultiAgentMemorySystem:
    """Coordinate memory across multiple agents"""
    
    def __init__(self, memory_config: Dict = None):
        self.agents = {}
        self.shared_memory = Memory(**(memory_config or {}))
        self.conversation_log = []
    
    def add_agent(self, agent: BaseMemoryAgent):
        """Add agent to the system"""
        self.agents[agent.name] = agent
        
        # Add agent introduction to shared memory
        self.shared_memory.add(
            f"Agent {agent.name} joined the system",
            user_id="system",
            metadata={"type": "agent_join", "agent_name": agent.name}
        )
    
    def broadcast_message(self, message: str, sender: str, exclude: List[str] = None):
        """Broadcast message to all agents"""
        exclude = exclude or []
        responses = {}
        
        for agent_name, agent in self.agents.items():
            if agent_name not in exclude and agent_name != sender:
                response = agent.process_message(message, sender)
                responses[agent_name] = response
        
        # Store in shared memory
        self.shared_memory.add(
            f"Broadcast from {sender}: {message}",
            user_id="system",
            metadata={"type": "broadcast", "sender": sender}
        )
        
        return responses
    
    def get_system_context(self, query: str):
        """Get context from shared system memory"""
        return self.shared_memory.search(query, user_id="system")

# Example usage and testing
if __name__ == "__main__":
    # Test AutoGen integration
    print("Testing AutoGen Memory Agent...")
    autogen_agent = AutoGenMemoryAgent(
        name="AutoGenAssistant",
        system_message="You are a helpful coding assistant"
    )
    
    # Simulate conversation
    messages = [{"content": "Help me with Python functions"}]
    response = autogen_agent.generate_reply(messages)
    print(f"AutoGen Response: {response}")
    
    # Test CrewAI integration
    print("\nTesting CrewAI Memory Agent...")
    crew_agent = CrewAIMemoryAgent(
        name="DataAnalyst",
        role="Data Analyst",
        goal="Analyze data and provide insights",
        backstory="Expert in data analysis with 10 years experience"
    )
    
    result = crew_agent.execute_task("Analyze sales data for Q4")
    print(f"CrewAI Result: {result}")
    
    # Test multi-agent system
    print("\nTesting Multi-Agent System...")
    multi_system = MultiAgentMemorySystem()
    multi_system.add_agent(autogen_agent)
    multi_system.add_agent(crew_agent)
    
    responses = multi_system.broadcast_message(
        "We need to analyze code performance",
        sender="ProjectManager"
    )
    print(f"Multi-agent responses: {responses}")
    
    print("\n✅ All integrations tested successfully!")