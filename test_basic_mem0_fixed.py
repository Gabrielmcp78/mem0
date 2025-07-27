#!/usr/bin/env python3
"""
Quick test of basic Mem0 functionality with correct API
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig

def test_basic_mem0():
    print("🧠 Testing basic Mem0 functionality...")
    
    try:
        # Create configuration
        config = MemoryConfig()
        
        # Initialize Memory with default config (should use Qdrant if available)
        memory = Memory(config)
        
        print("✅ Memory initialized successfully")
        
        # Test add memory
        result = memory.add("I love working with AI and memory systems", user_id="test_user")
        print(f"✅ Added memory: {result}")
        
        # Test search
        search_results = memory.search("AI memory", user_id="test_user")
        print(f"✅ Search found {len(search_results['results'])} results")
        for i, result in enumerate(search_results['results']):
            print(f"  {i+1}. {result['memory']}")
        
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
    success = test_basic_mem0()
    if success:
        print("\n🎉 Basic Mem0 test passed!")
    else:
        print("\n💥 Basic Mem0 test failed!")
    exit(0 if success else 1)