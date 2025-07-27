#!/usr/bin/env python3
"""
Test Mem0 with correct Ollama configuration and embedding dimensions
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig

def test_mem0_with_ollama():
    print("🧠 Testing Mem0 with Ollama (final config)...")
    
    try:
        # Create configuration for Ollama with correct dimensions
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
                    "embedding_dims": 768  # nomic-embed-text produces 768-dimensional embeddings
                }
            ),
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "host": "localhost",
                    "port": 6333,
                    "collection_name": "mem0_ollama_test",
                    "embedding_model_dims": 768  # Match the embedding dimensions
                }
            )
        )
        
        # Initialize Memory
        memory = Memory(config)
        print("✅ Memory initialized successfully with Ollama")
        
        # Test add memory
        result = memory.add("I love working with AI and memory systems", user_id="test_user")
        print(f"✅ Added memory: {result}")
        
        # Test another memory
        result2 = memory.add("Python is my favorite programming language", user_id="test_user")
        print(f"✅ Added second memory: {result2}")
        
        # Test search
        search_results = memory.search("AI memory", user_id="test_user")
        print(f"✅ Search found {len(search_results['results'])} results")
        for i, result in enumerate(search_results['results']):
            print(f"  {i+1}. {result['memory']} (score: {result.get('score', 'N/A'):.3f})")
        
        # Test search for programming
        search_results2 = memory.search("programming", user_id="test_user")
        print(f"✅ Programming search found {len(search_results2['results'])} results")
        for i, result in enumerate(search_results2['results']):
            print(f"  {i+1}. {result['memory']} (score: {result.get('score', 'N/A'):.3f})")
        
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
        print("\n🎉 Mem0 with Ollama test passed! Local memory system is working!")
    else:
        print("\n💥 Mem0 with Ollama test failed!")
    exit(0 if success else 1)