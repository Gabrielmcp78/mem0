#!/usr/bin/env python3
"""
Configuration for the integrated mem0 system
Handles local and cloud model configurations
"""

import os
from typing import Dict, Any, Optional

class SystemConfig:
    """Configuration manager for the integrated system"""
    
    def __init__(self):
        self.config = self._load_default_config()
        self._apply_environment_overrides()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration with local model fallbacks"""
        return {
            # LLM Configuration - prefer local models
            "llm": {
                "provider": "ollama",  # Default to local Ollama
                "config": {
                    "model": "llama2",
                    "temperature": 0.3,
                    "max_tokens": 1500,
                    "base_url": "http://localhost:11434"
                }
            },
            
            # Embeddings Configuration - prefer local
            "embedder": {
                "provider": "huggingface",  # Use local HuggingFace models
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "embedding_dims": 384
                }
            },
            
            # Vector Store Configuration
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost", 
                    "port": 10333,
                    "collection_name": "gabriel_memories",
                    "vector_size": 384
                }
            },
            
            # Graph Store Configuration (optional)
            "graph_store": {
                "provider": "neo4j",
                "config": {
                    "url": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "password",
                    "database": "neo4j"
                }
            },
            
            # System Configuration
            "system": {
                "enable_graph": False,  # Disabled by default unless Neo4j available
                "enable_persistence": True,
                "health_check_interval": 30,
                "auto_reconnect": True,
                "log_level": "INFO"
            }
        }
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        
        # OpenAI configuration (if API key is available)
        if os.getenv("OPENAI_API_KEY"):
            self.config["llm"] = {
                "provider": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            }
            self.config["embedder"] = {
                "provider": "openai", 
                "config": {
                    "model": "text-embedding-ada-002"
                }
            }
            self.config["vector_store"]["config"]["vector_size"] = 1536
        
        # Qdrant URL override
        if os.getenv("QDRANT_URL"):
            url_parts = os.getenv("QDRANT_URL").replace("http://", "").replace("https://", "").split(":")
            self.config["vector_store"]["config"]["host"] = url_parts[0]
            if len(url_parts) > 1:
                self.config["vector_store"]["config"]["port"] = int(url_parts[1])
        
        # Collection name override
        if os.getenv("QDRANT_COLLECTION"):
            self.config["vector_store"]["config"]["collection_name"] = os.getenv("QDRANT_COLLECTION")
        
        # Neo4j configuration
        if os.getenv("NEO4J_URL"):
            self.config["graph_store"]["config"]["url"] = os.getenv("NEO4J_URL")
            self.config["system"]["enable_graph"] = True
        
        if os.getenv("NEO4J_USER"):
            self.config["graph_store"]["config"]["username"] = os.getenv("NEO4J_USER")
        
        if os.getenv("NEO4J_PASSWORD"):
            self.config["graph_store"]["config"]["password"] = os.getenv("NEO4J_PASSWORD")
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get configuration for Memory initialization"""
        return {
            "llm": self.config["llm"],
            "embedder": self.config["embedder"],
            "vector_store": self.config["vector_store"]
        }
    
    def get_graph_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration for graph memory (if enabled)"""
        if self.config["system"]["enable_graph"]:
            return self.config["graph_store"]
        return None
    
    def is_graph_enabled(self) -> bool:
        """Check if graph functionality is enabled"""
        return self.config["system"]["enable_graph"]
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.config["system"]
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about configured providers"""
        return {
            "llm_provider": self.config["llm"]["provider"],
            "embedder_provider": self.config["embedder"]["provider"], 
            "vector_store_provider": self.config["vector_store"]["provider"],
            "graph_enabled": str(self.config["system"]["enable_graph"])
        }

# Global configuration instance
system_config = SystemConfig()