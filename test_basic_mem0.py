#!/usr/bin/env python3
"""
Quick test of basic Mem0 functionality
"""

from mem0 import Memory

def test_basic_mem0():
    print("🧠 Testing basic Mem0 functionality...")
    
    try:
        # Initialize Memory with Ollama
        memory = Memory(
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
        
        print("✅ Memory initialized successfully")
        
        # Test add memory
        result = memory.add("I love working with AI and memory systems", user_id="test_user")
        print(f"✅ Added memory: {result}")
        
        # Test search
        search_results = memory.search("AI memory", user_id="test_user")
        print(f"✅ Search found {len(search_results)} results")
        for i, result in enumerate(search_results):
            print(f"  {i+1}. {result.text}")
        
        # Test get all
        all_memories = memory.get_all(user_id="test_user")
        print(f"✅ Retrieved {len(all_memories)} total memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_mem0()
    if success:
        print("\n🎉 Basic Mem0 test passed!")
    else:
        print("\n💥 Basic Mem0 test failed!")
    exit(0 if success else 1)