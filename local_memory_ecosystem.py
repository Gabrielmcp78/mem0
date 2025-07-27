#!/usr/bin/env python3
"""
Local Memory Ecosystem Setup
Complete local memory system for any agent framework
Integrates Mem0 + OpenMemory + Neo4j + Qdrant + Ollama
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

class LocalMemoryEcosystem:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.services = {
            'ollama': {'port': 11434, 'status': False},
            'qdrant': {'port': 6333, 'status': False},
            'neo4j': {'port': 7474, 'bolt_port': 7687, 'status': False},
            'openmemory_mcp': {'port': 8765, 'status': False},
            'openmemory_ui': {'port': 3000, 'status': False},
            'mem0_server': {'port': 1987, 'status': False}
        }
    
    def check_service_status(self, port):
        """Check if a service is running on given port"""
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def start_ollama(self):
        """Start Ollama service and pull required models"""
        print("🚀 Starting Ollama service...")
        
        # Start Ollama if not running
        if not self.check_service_status(11434):
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL)
            time.sleep(3)
        
        # Pull required models
        models_to_pull = [
            'llama3.2:3b',  # Fast local LLM
            'nomic-embed-text',  # Embedding model
            'phi4:latest'  # Already have this
        ]
        
        for model in models_to_pull:
            if model != 'phi4:latest':  # Skip if already exists
                print(f"📥 Pulling {model}...")
                subprocess.run(['ollama', 'pull', model])
        
        self.services['ollama']['status'] = True
        print("✅ Ollama ready")
    
    def start_databases(self):
        """Start Qdrant and Neo4j databases"""
        print("🗄️ Starting databases...")
        
        # Start Qdrant if not running
        if not self.check_service_status(6333):
            print("Starting Qdrant...")
            subprocess.Popen([
                'docker', 'run', '-d',
                '--name', 'mem0-qdrant',
                '-p', '6333:6333',
                '-p', '6334:6334',
                '-v', f'{self.base_dir}/qdrant_data:/qdrant/storage',
                'qdrant/qdrant'
            ])
            time.sleep(5)
        
        # Start Neo4j if not running
        if not self.check_service_status(7474):
            print("Starting Neo4j...")
            subprocess.Popen([
                'docker', 'run', '-d',
                '--name', 'mem0-neo4j',
                '-p', '7474:7474',
                '-p', '7687:7687',
                '-e', 'NEO4J_AUTH=neo4j/mem0password',
                '-v', f'{self.base_dir}/neo4j_data:/data',
                'neo4j:latest'
            ])
            time.sleep(10)
        
        self.services['qdrant']['status'] = True
        self.services['neo4j']['status'] = True
        print("✅ Databases ready")
    
    def setup_environment(self):
        """Setup environment files and configurations"""
        print("⚙️ Setting up environment...")
        
        # Create OpenMemory .env file
        openmemory_env = self.base_dir / 'openmemory' / 'api' / '.env'
        if not openmemory_env.exists():
            env_content = f"""
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0password
USER={os.getenv('USER', 'mem0user')}
NEXT_PUBLIC_API_URL=http://localhost:8765
NEXT_PUBLIC_USER_ID={os.getenv('USER', 'mem0user')}
"""
            openmemory_env.write_text(env_content.strip())
        
        print("✅ Environment configured")
    
    def start_openmemory(self):
        """Start OpenMemory services"""
        print("🧠 Starting OpenMemory...")
        
        os.chdir(self.base_dir / 'openmemory')
        
        # Build and start OpenMemory
        subprocess.run(['make', 'build'])
        subprocess.Popen(['make', 'up'])
        
        time.sleep(10)
        self.services['openmemory_mcp']['status'] = True
        self.services['openmemory_ui']['status'] = True
        
        os.chdir(self.base_dir)
        print("✅ OpenMemory ready")
    
    def start_mem0_server(self):
        """Start Mem0 API server"""
        print("🔧 Starting Mem0 server...")
        
        # Install mem0 in development mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'])
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.[graph]'])
        
        # Start Mem0 server
        subprocess.Popen([
            sys.executable, '-m', 'mem0.server'
        ])
        
        time.sleep(5)
        self.services['mem0_server']['status'] = True
        print("✅ Mem0 server ready")
    
    def create_test_clients(self):
        """Create test client files for different agent frameworks"""
        print("📝 Creating test clients...")
        
        # Mem0 client
        mem0_client = """
from mem0 import Memory
import asyncio

# Synchronous Mem0 client
def create_mem0_client():
    return Memory(
        llm_config={
            "model": "ollama/llama3.2:3b",
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1"
        },
        embedder_config={
            "model": "ollama/nomic-embed-text",
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1"
        },
        vector_store_config={
            "provider": "qdrant",
            "host": "localhost",
            "port": 6333
        },
        graph_store_config={
            "provider": "neo4j",
            "uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "mem0password"
        }
    )

# Test the client
if __name__ == "__main__":
    mem = create_mem0_client()
    
    # Add some memories
    mem.add("I love Python programming", user_id="test_user")
    mem.add("My favorite color is blue", user_id="test_user")
    
    # Search memories
    results = mem.search("What do I love?", user_id="test_user")
    print("Search results:", results)
    
    # Get all memories
    all_memories = mem.get_all(user_id="test_user")
    print("All memories:", len(all_memories))
"""
        
        # OpenMemory MCP client
        openmemory_client = """
import requests
import json

class OpenMemoryClient:
    def __init__(self, base_url="http://localhost:8765"):
        self.base_url = base_url
        self.user_id = "test_user"
    
    def add_memory(self, text, metadata=None):
        response = requests.post(f"{self.base_url}/memories", json={
            "text": text,
            "user_id": self.user_id,
            "metadata": metadata or {}
        })
        return response.json()
    
    def search_memories(self, query, limit=10):
        response = requests.get(f"{self.base_url}/memories/search", params={
            "query": query,
            "user_id": self.user_id,
            "limit": limit
        })
        return response.json()
    
    def get_all_memories(self):
        response = requests.get(f"{self.base_url}/memories", params={
            "user_id": self.user_id
        })
        return response.json()

# Test the client
if __name__ == "__main__":
    client = OpenMemoryClient()
    
    # Add memories
    client.add_memory("I work as a software engineer")
    client.add_memory("I prefer working with TypeScript")
    
    # Search
    results = client.search_memories("What is my job?")
    print("Search results:", results)
"""
        
        # AutoGen integration
        autogen_integration = """
import autogen
from mem0 import Memory
import os

class MemoryEnhancedAgent(autogen.Agent):
    def __init__(self, name, system_message, memory_config=None):
        super().__init__(name, system_message=system_message)
        self.memory = Memory(
            llm_config={
                "model": "ollama/llama3.2:3b",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1"
            },
            embedder_config={
                "model": "ollama/nomic-embed-text",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1"
            },
            vector_store_config={
                "provider": "qdrant",
                "host": "localhost",
                "port": 6333
            }
        )
    
    def receive(self, message, sender, config):
        # Store conversation in memory
        self.memory.add(
            f"Received from {sender.name}: {message}",
            user_id=self.name,
            metadata={"sender": sender.name, "type": "received"}
        )
        super().receive(message, sender, config)
    
    def generate_reply(self, messages, sender, config):
        # Get relevant context from memory
        if messages:
            last_message = messages[-1]["content"]
            context = self.memory.search(last_message, user_id=self.name)
            
            # Add context to system message
            context_str = "\\n".join([m.text for m in context[:3]])
            enhanced_messages = messages + [{
                "role": "system",
                "content": f"Relevant context from memory: {context_str}"
            }]
            
            reply = super().generate_reply(enhanced_messages, sender, config)
            
            # Store our reply in memory
            self.memory.add(
                f"Replied to {sender.name}: {reply}",
                user_id=self.name,
                metadata={"recipient": sender.name, "type": "sent"}
            )
            
            return reply
        
        return super().generate_reply(messages, sender, config)

# Example usage
if __name__ == "__main__":
    config_list = [{
        "model": "llama3.2:3b",
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1"
    }]
    
    assistant = MemoryEnhancedAgent(
        name="MemoryAssistant",
        system_message="You are a helpful assistant with persistent memory."
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3
    )
    
    user_proxy.initiate_chat(
        assistant,
        message="Hello! Remember that I like Python programming."
    )
"""
        
        # Write test files
        (self.base_dir / 'test_mem0_client.py').write_text(mem0_client)
        (self.base_dir / 'test_openmemory_client.py').write_text(openmemory_client)
        (self.base_dir / 'test_autogen_integration.py').write_text(autogen_integration)
        
        print("✅ Test clients created")
    
    def print_status(self):
        """Print status of all services"""
        print("\n" + "="*50)
        print("🧠 LOCAL MEMORY ECOSYSTEM STATUS")
        print("="*50)
        
        for service, config in self.services.items():
            status = "✅ RUNNING" if config['status'] else "❌ STOPPED"
            port_info = f":{config['port']}" if 'port' in config else ""
            print(f"{service.upper():<20} {status} {port_info}")
        
        print("\n📍 ACCESS POINTS:")
        print(f"OpenMemory UI:      http://localhost:3000")
        print(f"OpenMemory API:     http://localhost:8765")
        print(f"Mem0 Server:        http://localhost:1987")
        print(f"Qdrant Dashboard:   http://localhost:6333/dashboard")
        print(f"Neo4j Browser:      http://localhost:7474")
        print(f"Ollama API:         http://localhost:11434")
        
        print("\n🧪 TEST FILES CREATED:")
        print("- test_mem0_client.py")
        print("- test_openmemory_client.py") 
        print("- test_autogen_integration.py")
        
        print("\n🚀 READY FOR ANY AGENT FRAMEWORK!")
    
    async def start_all(self):
        """Start the complete ecosystem"""
        print("🌟 Starting Local Memory Ecosystem...")
        
        self.start_ollama()
        self.start_databases()
        self.setup_environment()
        self.start_openmemory()
        self.start_mem0_server()
        self.create_test_clients()
        
        # Update service statuses
        for service, config in self.services.items():
            if 'port' in config:
                config['status'] = self.check_service_status(config['port'])
        
        self.print_status()

if __name__ == "__main__":
    ecosystem = LocalMemoryEcosystem()
    asyncio.run(ecosystem.start_all())