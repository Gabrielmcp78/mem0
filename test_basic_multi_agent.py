#!/usr/bin/env python3
"""
Basic Multi-Agent Memory Test
Simple test to verify multi-agent memory functionality
"""

import json
import sys
from datetime import datetime

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

def test_basic_multi_agent():
    """Test basic multi-agent memory functionality"""
    
    print("🧪 Basic Multi-Agent Memory Test")
    print("=" * 40)
    
    try:
        from integrations.mcp.memory_operations import add_memory, get_all_memories
        
        # Test data
        run_id = f"basic_test_{datetime.now().strftime('%H%M%S')}"
        user_id = "gabriel"
        
        print(f"📝 Test Run ID: {run_id}")
        print()
        
        # Add a memory with agent tracking
        print("1. Adding memory with agent tracking...")
        memory_params = {
            "messages": "This is a test memory with multi-agent tracking.",
            "user_id": user_id,
            "agent_id": "test_agent",
            "run_id": run_id,
            "metadata": json.dumps({
                "test": True,
                "topic": "multi_agent_test"
            })
        }
        
        result = add_memory(memory_params)
        print(f"✅ Memory added: {result.get('success', False)}")
        if not result.get('success'):
            print(f"❌ Error: {result.get('error')}")
            return False
        
        # Get all memories to see what was stored
        print("\n2. Retrieving all memories...")
        all_memories_result = get_all_memories({
            "user_id": user_id,
            "limit": 10
        })
        
        if all_memories_result.get('success'):
            memories = all_memories_result.get('results', [])
            print(f"✅ Retrieved {len(memories)} memories")
            print(f"   Type of memories: {type(memories)}")
            print(f"   Memories: {memories}")
            
            # Check if our test memory is there
            found_test_memory = False
            for memory in memories:
                if isinstance(memory, str):
                    try:
                        memory = json.loads(memory)
                    except:
                        continue
                
                metadata = memory.get('metadata', {})
                if metadata.get('run_id') == run_id:
                    found_test_memory = True
                    print(f"✅ Found test memory with agent_id: {metadata.get('agent_id')}")
                    print(f"   - Run ID: {metadata.get('run_id')}")
                    print(f"   - Processed by: {metadata.get('processed_by')}")
                    print(f"   - Neural Engine optimized: {metadata.get('neural_engine_optimized')}")
                    break
            
            if not found_test_memory:
                print("⚠️ Test memory not found in results")
                print("Available memories:")
                print(f"   Type of memories: {type(memories)}")
                print(f"   Memories content: {memories}")
                
                # Handle different data types
                if isinstance(memories, list) and len(memories) > 0:
                    for i, memory in enumerate(memories[:3]):  # Show first 3
                        print(f"   Memory {i+1} type: {type(memory)}")
                        if isinstance(memory, str):
                            try:
                                memory = json.loads(memory)
                            except:
                                print(f"   Memory {i+1} (raw): {memory[:100]}...")
                                continue
                        print(f"   Memory {i+1}: {memory.get('memory', 'No content')[:50]}...")
                        print(f"   Metadata: {memory.get('metadata', {})}")
                elif isinstance(memories, dict):
                    print(f"   Memories is a dict: {memories}")
                else:
                    print(f"   Unexpected memories type: {type(memories)}")
        else:
            print(f"❌ Failed to get memories: {all_memories_result.get('error')}")
            return False
        
        print("\n🎉 Basic Multi-Agent Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_multi_agent()
    if success:
        print("✅ Basic test passed!")
        sys.exit(0)
    else:
        print("❌ Basic test failed!")
        sys.exit(1)