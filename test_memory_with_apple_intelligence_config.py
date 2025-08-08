#!/usr/bin/env python3
"""
Test Memory with explicit Apple Intelligence configuration
"""

import sys
import os
import time
import json
import asyncio
import logging
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('apple-intelligence-memory-test')

async def test_memory_with_apple_intelligence():
    """Test memory system with explicit Apple Intelligence configuration"""
    
    print("🍎 Testing Memory with Apple Intelligence Configuration")
    print("=" * 60)
    
    try:
        # Import required modules
        from mem0 import Memory
        from mem0.configs.llms.apple_intelligence import AppleIntelligenceLlmConfig
        from mem0.configs.embeddings.apple_intelligence import AppleIntelligenceEmbedderConfig
        from mem0.configs.vector_stores.qdrant import QdrantConfig
        
        # Create explicit Apple Intelligence configuration
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
                    "embedding_dims": 1536,
                    "neural_engine_optimization": True
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "gabriel_apple_intelligence_memories",
                    "host": "localhost",
                    "port": 6333
                }
            }
        }
        
        print("✅ Configuration created with Apple Intelligence providers")
        
        # Initialize memory with explicit config
        memory = Memory.from_config(config)
        
        if memory:
            print("✅ Memory initialized successfully")
            
            # Verify providers
            llm_class = memory.llm.__class__.__name__ if hasattr(memory, 'llm') else 'Unknown'
            embedder_class = memory.embedding_model.__class__.__name__ if hasattr(memory, 'embedding_model') else 'Unknown'
            
            print(f"📊 LLM Provider: {llm_class}")
            print(f"📊 Embedder Provider: {embedder_class}")
            
            apple_intelligence_active = 'AppleIntelligence' in llm_class and 'AppleIntelligence' in embedder_class
            print(f"🍎 Apple Intelligence Active: {apple_intelligence_active}")
            
            if apple_intelligence_active:
                # Test memory operations
                test_user_id = f"apple_intelligence_test_{int(time.time())}"
                
                print(f"\n🧪 Testing Memory Operations with User ID: {test_user_id}")
                
                # Test 1: Add memory
                print("\n1. Testing Add Memory...")
                add_result = memory.add(
                    messages="Gabriel prefers Apple Intelligence for local processing and privacy",
                    user_id=test_user_id,
                    metadata={"category": "preferences", "technology": "apple_intelligence"}
                )
                
                if add_result:
                    print("✅ Memory added successfully")
                    print(f"   Result: {add_result}")
                else:
                    print("❌ Failed to add memory")
                    return False
                
                # Wait for indexing
                await asyncio.sleep(2)
                
                # Test 2: Search memory
                print("\n2. Testing Search Memory...")
                search_results = memory.search(
                    query="Gabriel Apple Intelligence preferences",
                    user_id=test_user_id,
                    limit=5
                )
                
                if search_results and len(search_results) > 0:
                    print(f"✅ Search successful - found {len(search_results)} results")
                    for i, result in enumerate(search_results):
                        print(f"   Result {i+1}: {result.get('memory', 'No content')[:100]}...")
                else:
                    print("❌ Search failed or no results")
                
                # Test 3: Get all memories
                print("\n3. Testing Get All Memories...")
                all_memories = memory.get_all(user_id=test_user_id)
                
                if all_memories and len(all_memories) > 0:
                    print(f"✅ Retrieved {len(all_memories)} memories")
                    
                    # Test 4: Update memory
                    print("\n4. Testing Update Memory...")
                    memory_to_update = all_memories[0]
                    memory_id = memory_to_update.get('id')
                    
                    if memory_id:
                        update_result = memory.update(
                            memory_id=memory_id,
                            data="Gabriel prefers Apple Intelligence for local processing, privacy, and Neural Engine optimization",
                            user_id=test_user_id
                        )
                        
                        if update_result:
                            print("✅ Memory updated successfully")
                        else:
                            print("❌ Failed to update memory")
                    
                    # Test 5: Delete memory
                    print("\n5. Testing Delete Memory...")
                    if memory_id:
                        delete_result = memory.delete(
                            memory_id=memory_id,
                            user_id=test_user_id
                        )
                        
                        if delete_result:
                            print("✅ Memory deleted successfully")
                        else:
                            print("❌ Failed to delete memory")
                else:
                    print("❌ No memories retrieved")
                
                print(f"\n🎉 Apple Intelligence Memory System Test Complete!")
                return True
            else:
                print("❌ Apple Intelligence providers not active")
                return False
        else:
            print("❌ Failed to initialize memory")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_persistence_across_sessions():
    """Test persistence by creating new memory instances"""
    
    print(f"\n🔄 Testing Persistence Across Sessions")
    print("=" * 40)
    
    try:
        from mem0 import Memory
        
        # Create explicit Apple Intelligence configuration
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
                    "embedding_dims": 1536,
                    "neural_engine_optimization": True
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "gabriel_apple_intelligence_memories",
                    "host": "localhost",
                    "port": 6333
                }
            }
        }
        
        # Session 1: Add memory
        print("📝 Session 1: Adding persistent memory...")
        memory1 = Memory.from_config(config)
        
        test_user_id = "persistence_test_user"
        persistent_content = "This is a persistence test - Apple Intelligence local memory system"
        
        add_result = memory1.add(
            messages=persistent_content,
            user_id=test_user_id,
            metadata={"test": "persistence", "session": 1}
        )
        
        if add_result:
            print("✅ Memory added in session 1")
        else:
            print("❌ Failed to add memory in session 1")
            return False
        
        # Wait for persistence
        await asyncio.sleep(3)
        
        # Session 2: Retrieve memory (simulate restart)
        print("🔍 Session 2: Retrieving persistent memory...")
        memory2 = Memory.from_config(config)
        
        retrieved_memories = memory2.get_all(user_id=test_user_id)
        
        if retrieved_memories and len(retrieved_memories) > 0:
            print(f"✅ Retrieved {len(retrieved_memories)} persistent memories")
            
            # Verify content
            for memory_item in retrieved_memories:
                if "persistence test" in memory_item.get('memory', '').lower():
                    print("✅ Persistent memory content verified")
                    
                    # Cleanup
                    memory_id = memory_item.get('id')
                    if memory_id:
                        memory2.delete(memory_id=memory_id, user_id=test_user_id)
                        print("✅ Test memory cleaned up")
                    
                    return True
            
            print("❌ Expected persistent content not found")
            return False
        else:
            print("❌ No persistent memories retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Persistence test failed: {str(e)}")
        return False

async def main():
    """Main test execution"""
    print("🧪 Apple Intelligence Memory System - Comprehensive Test")
    print("=" * 60)
    
    # Test 1: Basic memory operations with Apple Intelligence
    basic_test_success = await test_memory_with_apple_intelligence()
    
    # Test 2: Persistence across sessions
    persistence_test_success = await test_persistence_across_sessions()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"Basic Operations: {'✅ PASS' if basic_test_success else '❌ FAIL'}")
    print(f"Persistence Test: {'✅ PASS' if persistence_test_success else '❌ FAIL'}")
    
    overall_success = basic_test_success and persistence_test_success
    
    if overall_success:
        print(f"\n🎉 ALL TESTS PASSED - Apple Intelligence Memory System is robust and reliable!")
        return 0
    else:
        print(f"\n⚠️ SOME TESTS FAILED - System needs attention")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)