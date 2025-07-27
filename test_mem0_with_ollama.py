#!/usr/bin/env python3
"""
Test Mem0 with Ollama configuration
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig

def test_mem0_with_ollama():
    print("🧠 Testing Mem0 with Ollama...")
    
    try:
        # Create configuration for Ollama
        config = MemoryConfig(
            llm=LlmConfig(
                provider="ollama",
                config={
                    "model": "llama3.2:3b",
                    "base_url": "http://localhost:11434",
                    "ollama_additional_kwargs": {}
                }
            ),
            embedder=EmbedderConfig(
                provider="ollama", 
                config={
                    "model": "nomic-embed-text",
                    "base_url": "http://localhost:11434",
                    "ollama_additional_kwargs": {}
                }
            ),
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "host": "localhost",
                    "port": 6333,
                    "collection_name": "mem0_test"
                }
            )
        )
        
        # Initialize Memory
        memory = Memory(config)
        print("✅ Memory initialized successfully with Ollama")
        
        # Test add memory
        result = memory.add("I love working with AI and memory systems", user_id="test_user")
        print(f"✅ Added memory: {result}")
        
        # Test search
        search_results = memory.search("AI memory", user_id="test_user")
        print(f"✅ Search found {len(search_results['results'])} results")
        for i, result in enumerate(search_results['results']):
            print(f"  {i+1}. {result['memory']} (score: {result.get('score', 'N/A')})")
        
        # Test get all
        all_memories = memory.get_all(user_id="test_user")
        print(f"✅ Retrieved {len(all_memories['results'])} total memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mem0_with_ollama()
    if success:
        print("\n🎉 Mem0 with Ollama test passed!")
    else:
        print("\n💥 Mem0 with Ollama test failed!")
    exit(0 if success else 1)