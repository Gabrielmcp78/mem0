"""
Memory Configuration Manager
Centralized configuration for all memory components
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryProvider(Enum):
    MEM0 = "mem0"
    OPENMEMORY = "openmemory"
    BOTH = "both"

class VectorStore(Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"
    PINECONE = "pinecone"

class GraphStore(Enum):
    NEO4J = "neo4j"
    MEMGRAPH = "memgraph"

class LLMProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000

@dataclass
class EmbeddingConfig:
    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    dimensions: Optional[int] = None

@dataclass
class VectorStoreConfig:
    provider: VectorStore
    host: str = "localhost"
    port: int = 6333
    api_key: Optional[str] = None
    collection_name: str = "mem0_collection"
    
@dataclass
class GraphStoreConfig:
    provider: GraphStore
    uri: str = "bolt://localhost:17687"
    username: str = "neo4j"
    password: str = "mem0production"
    database: str = "neo4j"

@dataclass
class MemorySystemConfig:
    memory_provider: MemoryProvider
    llm_config: LLMConfig
    embedding_config: EmbeddingConfig
    vector_store_config: VectorStoreConfig
    graph_store_config: Optional[GraphStoreConfig] = None
    enable_graph: bool = True
    enable_async: bool = True
    cache_enabled: bool = True
    redis_url: str = "redis://:mem0redis@localhost:16379"

class MemoryConfigManager:
    """Centralized configuration management for memory systems"""
    
    def __init__(self, config_path: str = "memory_config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[MemorySystemConfig] = None
        self.load_config()
    
    def create_default_config(self) -> MemorySystemConfig:
        """Create default configuration for local setup"""
        return MemorySystemConfig(
            memory_provider=MemoryProvider.BOTH,
            llm_config=LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:3b",
                api_key="ollama",
                base_url="http://localhost:11434/v1"
            ),
            embedding_config=EmbeddingConfig(
                provider=LLMProvider.OLLAMA,
                model="nomic-embed-text",
                api_key="ollama",
                base_url="http://localhost:11434/v1"
            ),
            vector_store_config=VectorStoreConfig(
                provider=VectorStore.QDRANT,
                host="localhost",
                port=16333
            ),
            graph_store_config=GraphStoreConfig(
                provider=GraphStore.NEO4J,
                uri="bolt://localhost:17687",
                username="neo4j",
                password="mem0production"
            )
        )
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                self.config = self._dict_to_config(config_dict)
        else:
            self.config = self.create_default_config()
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_dict = self._config_to_dict(self.config)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def _config_to_dict(self, config: MemorySystemConfig) -> Dict:
        """Convert config object to dictionary"""
        def enum_serializer(obj):
            if isinstance(obj, Enum):
                return obj.value
            return obj
        
        config_dict = asdict(config)
        
        # Convert enums to strings
        def convert_enums(d):
            if isinstance(d, dict):
                return {k: convert_enums(v) for k, v in d.items()}
            elif isinstance(d, Enum):
                return d.value
            else:
                return d
        
        return convert_enums(config_dict)
    
    def _dict_to_config(self, config_dict: Dict) -> MemorySystemConfig:
        """Convert dictionary to config object"""
        # Convert string enums back to enum objects
        config_dict['memory_provider'] = MemoryProvider(config_dict['memory_provider'])
        config_dict['llm_config']['provider'] = LLMProvider(config_dict['llm_config']['provider'])
        config_dict['embedding_config']['provider'] = LLMProvider(config_dict['embedding_config']['provider'])
        config_dict['vector_store_config']['provider'] = VectorStore(config_dict['vector_store_config']['provider'])
        
        if config_dict.get('graph_store_config'):
            config_dict['graph_store_config']['provider'] = GraphStore(config_dict['graph_store_config']['provider'])
            config_dict['graph_store_config'] = GraphStoreConfig(**config_dict['graph_store_config'])
        
        # Create config objects
        config_dict['llm_config'] = LLMConfig(**config_dict['llm_config'])
        config_dict['embedding_config'] = EmbeddingConfig(**config_dict['embedding_config'])
        config_dict['vector_store_config'] = VectorStoreConfig(**config_dict['vector_store_config'])
        
        return MemorySystemConfig(**config_dict)
    
    def get_mem0_config(self) -> Dict:
        """Get configuration for Mem0 client"""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        config = {
            "llm_config": {
                "model": f"{self.config.llm_config.provider.value}/{self.config.llm_config.model}",
                "api_key": self.config.llm_config.api_key,
                "base_url": self.config.llm_config.base_url
            },
            "embedder_config": {
                "model": f"{self.config.embedding_config.provider.value}/{self.config.embedding_config.model}",
                "api_key": self.config.embedding_config.api_key,
                "base_url": self.config.embedding_config.base_url
            },
            "vector_store_config": {
                "provider": self.config.vector_store_config.provider.value,
                "host": self.config.vector_store_config.host,
                "port": self.config.vector_store_config.port
            }
        }
        
        if self.config.enable_graph and self.config.graph_store_config:
            config["graph_store_config"] = {
                "provider": self.config.graph_store_config.provider.value,
                "uri": self.config.graph_store_config.uri,
                "username": self.config.graph_store_config.username,
                "password": self.config.graph_store_config.password
            }
        
        return config
    
    def get_openmemory_env(self) -> Dict[str, str]:
        """Get environment variables for OpenMemory"""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        env = {
            "OPENAI_API_KEY": self.config.llm_config.api_key,
            "OPENAI_BASE_URL": self.config.llm_config.base_url or "",
            "QDRANT_URL": f"http://{self.config.vector_store_config.host}:{self.config.vector_store_config.port}",
            "USER": os.getenv("USER", "mem0user")
        }
        
        if self.config.graph_store_config:
            env.update({
                "NEO4J_URI": self.config.graph_store_config.uri,
                "NEO4J_USERNAME": self.config.graph_store_config.username,
                "NEO4J_PASSWORD": self.config.graph_store_config.password
            })
        
        if self.config.cache_enabled:
            env["REDIS_URL"] = self.config.redis_url
        
        return env
    
    def update_llm_config(self, provider: LLMProvider, model: str, api_key: str, base_url: str = None):
        """Update LLM configuration"""
        self.config.llm_config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url
        )
        self.save_config()
    
    def update_vector_store(self, provider: VectorStore, host: str = "localhost", port: int = 6333):
        """Update vector store configuration"""
        self.config.vector_store_config = VectorStoreConfig(
            provider=provider,
            host=host,
            port=port
        )
        self.save_config()
    
    def enable_graph_memory(self, provider: GraphStore, uri: str, username: str, password: str):
        """Enable and configure graph memory"""
        self.config.enable_graph = True
        self.config.graph_store_config = GraphStoreConfig(
            provider=provider,
            uri=uri,
            username=username,
            password=password
        )
        self.save_config()
    
    def disable_graph_memory(self):
        """Disable graph memory"""
        self.config.enable_graph = False
        self.config.graph_store_config = None
        self.save_config()
    
    def get_docker_compose_env(self) -> Dict[str, str]:
        """Get environment variables for docker-compose"""
        env = self.get_openmemory_env()
        env.update({
            "COMPOSE_PROJECT_NAME": "mem0-ecosystem",
            "POSTGRES_DB": "mem0db",
            "POSTGRES_USER": "mem0user",
            "POSTGRES_PASSWORD": "mem0postgres",
            "REDIS_PASSWORD": "mem0redis"
        })
        return env
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        if not self.config:
            return False
        
        # Check required fields
        required_fields = [
            self.config.llm_config.model,
            self.config.embedding_config.model,
            self.config.vector_store_config.host
        ]
        
        return all(field for field in required_fields)
    
    def print_config_summary(self):
        """Print configuration summary"""
        if not self.config:
            print("❌ No configuration loaded")
            return
        
        print("🔧 Memory System Configuration")
        print("=" * 40)
        print(f"Memory Provider: {self.config.memory_provider.value}")
        print(f"LLM: {self.config.llm_config.provider.value}/{self.config.llm_config.model}")
        print(f"Embeddings: {self.config.embedding_config.provider.value}/{self.config.embedding_config.model}")
        print(f"Vector Store: {self.config.vector_store_config.provider.value} @ {self.config.vector_store_config.host}:{self.config.vector_store_config.port}")
        
        if self.config.enable_graph and self.config.graph_store_config:
            print(f"Graph Store: {self.config.graph_store_config.provider.value} @ {self.config.graph_store_config.uri}")
        else:
            print("Graph Store: Disabled")
        
        print(f"Async Support: {'Enabled' if self.config.enable_async else 'Disabled'}")
        print(f"Caching: {'Enabled' if self.config.cache_enabled else 'Disabled'}")

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Configuration Manager")
    parser.add_argument("--config", default="memory_config.yaml", help="Configuration file path")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--create-default", action="store_true", help="Create default configuration")
    
    args = parser.parse_args()
    
    manager = MemoryConfigManager(args.config)
    
    if args.show:
        manager.print_config_summary()
    
    if args.validate:
        if manager.validate_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration is invalid")
    
    if args.create_default:
        manager.config = manager.create_default_config()
        manager.save_config()
        print(f"✅ Default configuration created at {args.config}")
        manager.print_config_summary()