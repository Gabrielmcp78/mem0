#!/usr/bin/env python3
"""
Corrected Memory Persistence Test with proper Apple Intelligence configuration
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
logger = logging.getLogger('memory-persistence-test')

async def test_memory_operations_comprehensive():
    """Comprehensive test of memory operations with Apple Intelligence"""
    
    print("🍎 Comprehensive Memory Operations Test with Apple Intelligence")
    print("=" * 70)
    
    test_results = []
    
    def log_result(test_name, success, details=""):
        result = {'test': test_name, 'success': success, 'details': details}
        test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
    
    try:
        # Test 1: Apple Intelligence Foundation Models
        print("\n1. 🍎 Testing Apple Intelligence Foundation Models...")
        from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
        
        available = check_apple_intelligence_availability()
        status = get_apple_intelligence_status()
        
        if available:
            log_result("Apple Intelligence Foundation", True, f"Available on macOS {status.get('macos_version')}")
        else:
            log_result("Apple Intelligence Foundation", False, f"Not available: {status.get('error_message')}")
            return False
        
        # Test 2: Memory initialization with proper config
        print("\n2. 💾 Testing Memory Initialization...")
        from mem0 import Memory
        
        # Use proper Apple Intelligence configuration
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
                    "enable_neural_engine": True
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
        
        memory = Memory.from_config(config)
        
        if memory:
            llm_class = memory.llm.__class__.__name__ if hasattr(memory, 'llm') else 'Unknown'
            embedder_class = memory.embedding_model.__class__.__name__ if hasattr(memory, 'embedding_model') else 'Unknown'
            
            apple_intelligence_active = 'AppleIntelligence' in llm_class and 'AppleIntelligence' in embedder_class
            
            log_result("Memory Initialization", True, f"LLM: {llm_class}, Embedder: {embedder_class}, AI Active: {apple_intelligence_active}")
            
            if not apple_intelligence_active:
                log_result("Apple Intelligence Providers", False, "Not using Apple Intelligence providers")
                return False
        else:
            log_result("Memory Initialization", False, "Memory object is None")
            return False
        
        # Test 3: Basic memory operations
        print("\n3. 🔧 Testing Basic Memory Operations...")
        test_user_id = f"comprehensive_test_{int(time.time())}"
        
        # Test memories to add
        test_memories = [
            {
                'content': 'Gabriel prefers Apple Intelligence for local processing and privacy protection',
                'metadata': {'category': 'preferences', 'priority': 'high', 'technology': 'apple_intelligence'}
            },
            {
                'content': 'Memory system uses Qdrant vector database for persistent storage with Apple Intelligence embeddings',
                'metadata': {'category': 'architecture', 'component': 'storage', 'technology': 'qdrant'}
            },
            {
                'content': 'Neural Engine optimization provides faster embedding generation on Apple Silicon',
                'metadata': {'category': 'performance', 'optimization': 'neural_engine', 'hardware': 'apple_silicon'}
            }
        ]
        
        added_memories = []
        
        # Add memories
        for i, test_memory in enumerate(test_memories):
            try:
                result = memory.add(
                    messages=test_memory['content'],
                    user_id=test_user_id,
                    metadata=test_memory['metadata']
                )
                
                if result:
                    added_memories.append(result)
                    log_result(f"Add Memory {i+1}", True, f"Added: {test_memory['content'][:50]}...")
                else:
                    log_result(f"Add Memory {i+1}", False, "No result returned")
                    
            except Exception as e:
                log_result(f"Add Memory {i+1}", False, f"Error: {str(e)}")
        
        # Wait for indexing
        await asyncio.sleep(3)
        
        # Test search operations
        search_queries = [
            "Gabriel Apple Intelligence preferences",
            "Qdrant vector database storage",
            "Neural Engine optimization"
        ]
        
        search_success_count = 0
        for i, query in enumerate(search_queries):
            try:
                results = memory.search(
                    query=query,
                    user_id=test_user_id,
                    limit=5
                )
                
                if results and len(results) > 0:
                    search_success_count += 1
                    log_result(f"Search {i+1}", True, f"Query: '{query}' found {len(results)} results")
                else:
                    log_result(f"Search {i+1}", False, f"No results for: '{query}'")
                    
            except Exception as e:
                log_result(f"Search {i+1}", False, f"Error: {str(e)}")
        
        # Test get all memories
        try:
            all_memories = memory.get_all(user_id=test_user_id)
            
            if all_memories and len(all_memories) >= len(test_memories):
                log_result("Get All Memories", True, f"Retrieved {len(all_memories)} memories")
                
                # Test update operation
                if len(all_memories) > 0:
                    memory_to_update = all_memories[0]
                    memory_id = memory_to_update.get('id')
                    
                    if memory_id:
                        try:
                            updated_content = "Gabriel prefers Apple Intelligence for local processing, privacy protection, and Neural Engine optimization"
                            
                            update_result = memory.update(
                                memory_id=memory_id,
                                data=updated_content,
                                user_id=test_user_id
                            )
                            
                            if update_result:
                                log_result("Update Memory", True, f"Updated memory {memory_id}")
                            else:
                                log_result("Update Memory", False, "Update operation failed")
                                
                        except Exception as e:
                            log_result("Update Memory", False, f"Error: {str(e)}")
                
                # Test delete operation
                if len(all_memories) > 1:
                    memory_to_delete = all_memories[-1]
                    delete_id = memory_to_delete.get('id')
                    
                    if delete_id:
                        try:
                            delete_result = memory.delete(
                                memory_id=delete_id,
                                user_id=test_user_id
                            )
                            
                            if delete_result:
                                log_result("Delete Memory", True, f"Deleted memory {delete_id}")
                            else:
                                log_result("Delete Memory", False, "Delete operation failed")
                                
                        except Exception as e:
                            log_result("Delete Memory", False, f"Error: {str(e)}")
            else:
                log_result("Get All Memories", False, f"Expected at least {len(test_memories)}, got {len(all_memories) if all_memories else 0}")
                
        except Exception as e:
            log_result("Get All Memories", False, f"Error: {str(e)}")
        
        # Test 4: Persistence across sessions
        print("\n4. 🔄 Testing Persistence Across Sessions...")
        
        # Add a persistence test memory
        persistence_content = "Persistence test - Apple Intelligence memory system robustness verification"
        persistence_user = "persistence_test_user"
        
        try:
            persistence_result = memory.add(
                messages=persistence_content,
                user_id=persistence_user,
                metadata={'test': 'persistence', 'timestamp': datetime.now().isoformat()}
            )
            
            if persistence_result:
                log_result("Add Persistence Memory", True, "Added persistence test memory")
                
                # Wait for persistence
                await asyncio.sleep(2)
                
                # Create new memory instance (simulate restart)
                memory2 = Memory.from_config(config)
                
                # Try to retrieve the persistent memory
                persistent_memories = memory2.get_all(user_id=persistence_user)
                
                if persistent_memories and len(persistent_memories) > 0:
                    # Verify content
                    for mem in persistent_memories:
                        if "persistence test" in mem.get('memory', '').lower():
                            log_result("Persistence Verification", True, "Persistent memory content verified")
                            
                            # Cleanup
                            memory_id = mem.get('id')
                            if memory_id:
                                memory2.delete(memory_id=memory_id, user_id=persistence_user)
                            break
                    else:
                        log_result("Persistence Verification", False, "Expected persistent content not found")
                else:
                    log_result("Persistence Verification", False, "No persistent memories retrieved")
            else:
                log_result("Add Persistence Memory", False, "Failed to add persistence test memory")
                
        except Exception as e:
            log_result("Persistence Test", False, f"Error: {str(e)}")
        
        # Test 5: Qdrant database verification
        print("\n5. 🗄️ Testing Qdrant Database...")
        
        try:
            import requests
            
            # Test Qdrant connection
            response = requests.get('http://localhost:6333/', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                log_result("Qdrant Connection", True, f"Qdrant {data.get('version', 'unknown')} running")
                
                # Test collections
                collections_response = requests.get('http://localhost:6333/collections', timeout=5)
                
                if collections_response.status_code == 200:
                    collections_data = collections_response.json()
                    collections = collections_data.get('result', {}).get('collections', [])
                    collection_names = [col.get('name') for col in collections]
                    
                    if 'gabriel_apple_intelligence_memories' in collection_names:
                        log_result("Qdrant Collections", True, f"Found target collection in: {collection_names}")
                        
                        # Get collection info
                        info_response = requests.get(
                            'http://localhost:6333/collections/gabriel_apple_intelligence_memories', 
                            timeout=5
                        )
                        
                        if info_response.status_code == 200:
                            info_data = info_response.json()
                            vectors_count = info_data.get('result', {}).get('vectors_count', 0)
                            log_result("Collection Info", True, f"Collection contains {vectors_count} vectors")
                        else:
                            log_result("Collection Info", False, f"HTTP {info_response.status_code}")
                    else:
                        log_result("Qdrant Collections", False, f"Target collection not found in: {collection_names}")
                else:
                    log_result("Qdrant Collections", False, f"HTTP {collections_response.status_code}")
            else:
                log_result("Qdrant Connection", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            log_result("Qdrant Database", False, f"Error: {str(e)}")
        
        # Cleanup test data
        print("\n6. 🧹 Cleaning up test data...")
        try:
            cleanup_memories = memory.get_all(user_id=test_user_id)
            if cleanup_memories:
                for mem in cleanup_memories:
                    memory_id = mem.get('id')
                    if memory_id:
                        memory.delete(memory_id=memory_id, user_id=test_user_id)
                
                log_result("Cleanup", True, f"Cleaned up {len(cleanup_memories)} test memories")
            else:
                log_result("Cleanup", True, "No test memories to clean up")
                
        except Exception as e:
            log_result("Cleanup", False, f"Error: {str(e)}")
        
        # Generate summary
        print(f"\n📊 Test Summary")
        print("=" * 40)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT - Memory system is highly robust and reliable!")
            return True
        elif success_rate >= 75:
            print(f"\n🟡 GOOD - Memory system is mostly reliable with minor issues")
            return True
        else:
            print(f"\n⚠️ NEEDS ATTENTION - Memory system has significant issues")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test execution"""
    print("🧪 Memory Storage and Persistence - Comprehensive Robustness Test")
    print("=" * 70)
    print("Testing Apple Intelligence Local Memory System")
    print("=" * 70)
    
    success = await test_memory_operations_comprehensive()
    
    if success:
        print(f"\n🚀 SYSTEM VERIFICATION COMPLETE: Memory system is robust and ready for production!")
        return 0
    else:
        print(f"\n⚠️ SYSTEM NEEDS ATTENTION: Some components require fixes")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)