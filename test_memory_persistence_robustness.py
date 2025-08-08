#!/usr/bin/env python3
"""
Comprehensive Memory Storage and Persistence Test
Tests the robustness and reliability of the Apple Intelligence memory system
"""

import sys
import os
import time
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'integrations', 'mcp'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('memory-persistence-test')

class MemoryPersistenceTest:
    """Comprehensive test suite for memory persistence and robustness"""
    
    def __init__(self):
        self.test_results = []
        self.test_user_id = f"persistence_test_{int(time.time())}"
        self.test_memories = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
    def print_header(self, title: str):
        """Print formatted test section header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
        
    async def test_apple_intelligence_foundation(self):
        """Test 1: Apple Intelligence Foundation Models availability"""
        self.print_header("Apple Intelligence Foundation Models Test")
        
        try:
            from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
            
            available = check_apple_intelligence_availability()
            status = get_apple_intelligence_status()
            
            if available:
                self.log_test_result(
                    "Apple Intelligence Foundation", 
                    True, 
                    f"Available on macOS {status.get('macos_version')}, {status.get('machine')}"
                )
                
                # Test providers
                from mem0.llms.apple_intelligence import AppleIntelligenceLLM
                from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder
                from mem0.configs.llms.apple_intelligence import AppleIntelligenceLlmConfig
                from mem0.configs.embeddings.base import BaseEmbedderConfig
                
                llm = AppleIntelligenceLLM(AppleIntelligenceLlmConfig())
                embedder = AppleIntelligenceEmbedder(BaseEmbedderConfig())
                
                llm_available = llm.is_available
                embedder_available = embedder.is_available()
                
                self.log_test_result(
                    "Apple Intelligence LLM Provider", 
                    llm_available, 
                    f"LLM Available: {llm_available}"
                )
                
                self.log_test_result(
                    "Apple Intelligence Embedder Provider", 
                    embedder_available, 
                    f"Embedder Available: {embedder_available}"
                )
                
                return llm_available and embedder_available
            else:
                self.log_test_result(
                    "Apple Intelligence Foundation", 
                    False, 
                    f"Not available: {status.get('error_message', 'Unknown')}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Apple Intelligence Foundation", False, f"Error: {str(e)}")
            return False
    
    async def test_memory_initialization(self):
        """Test 2: Memory system initialization"""
        self.print_header("Memory System Initialization Test")
        
        try:
            from mem0 import Memory
            
            memory = Memory()
            
            if memory:
                llm_class = memory.llm.__class__.__name__ if hasattr(memory, 'llm') else 'Unknown'
                embedder_class = memory.embedding_model.__class__.__name__ if hasattr(memory, 'embedding_model') else 'Unknown'
                
                apple_intelligence_active = 'AppleIntelligence' in llm_class and 'AppleIntelligence' in embedder_class
                
                self.log_test_result(
                    "Memory Initialization", 
                    True, 
                    f"LLM: {llm_class}, Embedder: {embedder_class}, Apple Intelligence: {apple_intelligence_active}"
                )
                
                return memory, apple_intelligence_active
            else:
                self.log_test_result("Memory Initialization", False, "Memory object is None")
                return None, False
                
        except Exception as e:
            self.log_test_result("Memory Initialization", False, f"Error: {str(e)}")
            return None, False
    
    async def test_basic_memory_operations(self, memory):
        """Test 3: Basic memory operations (add, search, get)"""
        self.print_header("Basic Memory Operations Test")
        
        try:
            # Test data
            test_memories = [
                {
                    'content': 'Gabriel prefers detailed technical explanations with code examples',
                    'metadata': {'category': 'preferences', 'priority': 'high'}
                },
                {
                    'content': 'Apple Intelligence integration project uses Foundation Models for local processing',
                    'metadata': {'category': 'project', 'technology': 'apple_intelligence'}
                },
                {
                    'content': 'Memory system uses Qdrant for vector storage and persistence',
                    'metadata': {'category': 'architecture', 'component': 'storage'}
                }
            ]
            
            added_memories = []
            
            # Test adding memories
            for i, test_memory in enumerate(test_memories):
                try:
                    result = memory.add(
                        messages=test_memory['content'],
                        user_id=self.test_user_id,
                        metadata=test_memory['metadata']
                    )
                    
                    if result:
                        added_memories.append(result)
                        self.log_test_result(
                            f"Add Memory {i+1}", 
                            True, 
                            f"Added: {test_memory['content'][:50]}..."
                        )
                    else:
                        self.log_test_result(f"Add Memory {i+1}", False, "No result returned")
                        
                except Exception as e:
                    self.log_test_result(f"Add Memory {i+1}", False, f"Error: {str(e)}")
            
            # Wait a moment for indexing
            await asyncio.sleep(2)
            
            # Test searching memories
            search_queries = [
                "Gabriel preferences",
                "Apple Intelligence",
                "vector storage"
            ]
            
            for i, query in enumerate(search_queries):
                try:
                    results = memory.search(
                        query=query,
                        user_id=self.test_user_id,
                        limit=5
                    )
                    
                    if results and len(results) > 0:
                        self.log_test_result(
                            f"Search Memory {i+1}", 
                            True, 
                            f"Query: '{query}' returned {len(results)} results"
                        )
                    else:
                        self.log_test_result(f"Search Memory {i+1}", False, f"No results for query: '{query}'")
                        
                except Exception as e:
                    self.log_test_result(f"Search Memory {i+1}", False, f"Error: {str(e)}")
            
            # Test getting all memories
            try:
                all_memories = memory.get_all(user_id=self.test_user_id)
                
                if all_memories and len(all_memories) >= len(test_memories):
                    self.log_test_result(
                        "Get All Memories", 
                        True, 
                        f"Retrieved {len(all_memories)} memories"
                    )
                    self.test_memories = all_memories
                else:
                    self.log_test_result(
                        "Get All Memories", 
                        False, 
                        f"Expected at least {len(test_memories)}, got {len(all_memories) if all_memories else 0}"
                    )
                    
            except Exception as e:
                self.log_test_result("Get All Memories", False, f"Error: {str(e)}")
            
            return len(added_memories) > 0
            
        except Exception as e:
            self.log_test_result("Basic Memory Operations", False, f"Error: {str(e)}")
            return False
    
    async def test_memory_persistence(self, memory):
        """Test 4: Memory persistence across sessions"""
        self.print_header("Memory Persistence Test")
        
        try:
            # Create a new memory instance to simulate session restart
            from mem0 import Memory
            new_memory = Memory()
            
            # Try to retrieve previously stored memories
            retrieved_memories = new_memory.get_all(user_id=self.test_user_id)
            
            if retrieved_memories and len(retrieved_memories) > 0:
                self.log_test_result(
                    "Memory Persistence", 
                    True, 
                    f"Successfully retrieved {len(retrieved_memories)} persisted memories"
                )
                
                # Verify content matches
                for memory_item in retrieved_memories:
                    if 'Gabriel prefers detailed' in memory_item.get('memory', ''):
                        self.log_test_result(
                            "Persistence Content Verification", 
                            True, 
                            "Content integrity verified"
                        )
                        break
                else:
                    self.log_test_result(
                        "Persistence Content Verification", 
                        False, 
                        "Expected content not found"
                    )
                
                return True
            else:
                self.log_test_result(
                    "Memory Persistence", 
                    False, 
                    "No persisted memories found"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Memory Persistence", False, f"Error: {str(e)}")
            return False
    
    async def test_memory_update_operations(self, memory):
        """Test 5: Memory update and delete operations"""
        self.print_header("Memory Update Operations Test")
        
        try:
            if not self.test_memories:
                self.log_test_result("Memory Update Operations", False, "No test memories available")
                return False
            
            # Test updating a memory
            memory_to_update = self.test_memories[0]
            memory_id = memory_to_update.get('id')
            
            if memory_id:
                try:
                    updated_content = "Gabriel prefers detailed technical explanations with code examples and Apple Intelligence integration"
                    
                    update_result = memory.update(
                        memory_id=memory_id,
                        data=updated_content,
                        user_id=self.test_user_id
                    )
                    
                    if update_result:
                        self.log_test_result(
                            "Update Memory", 
                            True, 
                            f"Successfully updated memory {memory_id}"
                        )
                        
                        # Verify update
                        updated_memories = memory.get_all(user_id=self.test_user_id)
                        for mem in updated_memories:
                            if mem.get('id') == memory_id and 'Apple Intelligence integration' in mem.get('memory', ''):
                                self.log_test_result(
                                    "Update Verification", 
                                    True, 
                                    "Update content verified"
                                )
                                break
                        else:
                            self.log_test_result("Update Verification", False, "Updated content not found")
                    else:
                        self.log_test_result("Update Memory", False, "Update operation failed")
                        
                except Exception as e:
                    self.log_test_result("Update Memory", False, f"Error: {str(e)}")
            
            # Test deleting a memory
            if len(self.test_memories) > 1:
                memory_to_delete = self.test_memories[-1]
                delete_id = memory_to_delete.get('id')
                
                if delete_id:
                    try:
                        delete_result = memory.delete(
                            memory_id=delete_id,
                            user_id=self.test_user_id
                        )
                        
                        if delete_result:
                            self.log_test_result(
                                "Delete Memory", 
                                True, 
                                f"Successfully deleted memory {delete_id}"
                            )
                            
                            # Verify deletion
                            remaining_memories = memory.get_all(user_id=self.test_user_id)
                            for mem in remaining_memories:
                                if mem.get('id') == delete_id:
                                    self.log_test_result("Delete Verification", False, "Deleted memory still exists")
                                    break
                            else:
                                self.log_test_result("Delete Verification", True, "Memory successfully deleted")
                        else:
                            self.log_test_result("Delete Memory", False, "Delete operation failed")
                            
                    except Exception as e:
                        self.log_test_result("Delete Memory", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test_result("Memory Update Operations", False, f"Error: {str(e)}")
            return False
    
    async def test_mcp_server_integration(self):
        """Test 6: MCP Server integration"""
        self.print_header("MCP Server Integration Test")
        
        try:
            from memory_operations import initialize_memory, add_memory, search_memories, get_all_memories
            
            # Test memory operations module
            memory = initialize_memory()
            
            if memory:
                self.log_test_result(
                    "MCP Memory Operations Init", 
                    True, 
                    "Memory operations module initialized"
                )
                
                # Test add memory via MCP operations
                add_params = {
                    'messages': 'MCP integration test - robustness verification',
                    'user_id': self.test_user_id,
                    'metadata': '{"test": "mcp_integration", "robustness": true}'
                }
                
                add_result = add_memory(add_params)
                add_success = add_result.get('success', False)
                
                self.log_test_result(
                    "MCP Add Memory", 
                    add_success, 
                    f"Add result: {add_result.get('message', 'No message')}"
                )
                
                if add_success:
                    # Test search via MCP operations
                    search_params = {
                        'query': 'MCP integration test',
                        'user_id': self.test_user_id,
                        'limit': 5
                    }
                    
                    search_result = search_memories(search_params)
                    search_success = search_result.get('success', False)
                    
                    self.log_test_result(
                        "MCP Search Memory", 
                        search_success, 
                        f"Search found {len(search_result.get('memories', []))} results"
                    )
                    
                    # Test get all via MCP operations
                    get_all_params = {
                        'user_id': self.test_user_id
                    }
                    
                    get_all_result = get_all_memories(get_all_params)
                    get_all_success = get_all_result.get('success', False)
                    
                    self.log_test_result(
                        "MCP Get All Memories", 
                        get_all_success, 
                        f"Retrieved {len(get_all_result.get('memories', []))} memories"
                    )
                    
                    return add_success and search_success and get_all_success
                
                return False
            else:
                self.log_test_result("MCP Memory Operations Init", False, "Failed to initialize")
                return False
                
        except Exception as e:
            self.log_test_result("MCP Server Integration", False, f"Error: {str(e)}")
            return False
    
    async def test_qdrant_persistence(self):
        """Test 7: Qdrant vector database persistence"""
        self.print_header("Qdrant Vector Database Persistence Test")
        
        try:
            import requests
            
            # Test Qdrant connection
            response = requests.get('http://localhost:6333/', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Qdrant Connection", 
                    True, 
                    f"Qdrant {data.get('version', 'unknown')} running"
                )
                
                # Test collections
                collections_response = requests.get('http://localhost:6333/collections', timeout=5)
                
                if collections_response.status_code == 200:
                    collections_data = collections_response.json()
                    collections = collections_data.get('result', {}).get('collections', [])
                    
                    # Look for our collection
                    collection_names = [col.get('name') for col in collections]
                    
                    if any('gabriel' in name.lower() or 'mem0' in name.lower() for name in collection_names):
                        self.log_test_result(
                            "Qdrant Collections", 
                            True, 
                            f"Found collections: {collection_names}"
                        )
                        
                        # Test collection info
                        for collection_name in collection_names:
                            if 'gabriel' in collection_name.lower() or 'mem0' in collection_name.lower():
                                info_response = requests.get(
                                    f'http://localhost:6333/collections/{collection_name}', 
                                    timeout=5
                                )
                                
                                if info_response.status_code == 200:
                                    info_data = info_response.json()
                                    vectors_count = info_data.get('result', {}).get('vectors_count', 0)
                                    
                                    self.log_test_result(
                                        f"Collection {collection_name}", 
                                        True, 
                                        f"Contains {vectors_count} vectors"
                                    )
                                break
                        
                        return True
                    else:
                        self.log_test_result(
                            "Qdrant Collections", 
                            False, 
                            f"Memory collections not found in: {collection_names}"
                        )
                        return False
                else:
                    self.log_test_result("Qdrant Collections", False, f"HTTP {collections_response.status_code}")
                    return False
            else:
                self.log_test_result("Qdrant Connection", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Qdrant Vector Database Persistence", False, f"Error: {str(e)}")
            return False
    
    async def test_stress_operations(self, memory):
        """Test 8: Stress test with multiple operations"""
        self.print_header("Stress Test - Multiple Operations")
        
        try:
            stress_memories = []
            
            # Add multiple memories rapidly
            for i in range(10):
                try:
                    content = f"Stress test memory {i+1} - testing system robustness and performance under load"
                    result = memory.add(
                        messages=content,
                        user_id=f"{self.test_user_id}_stress",
                        metadata={'stress_test': True, 'batch': i}
                    )
                    
                    if result:
                        stress_memories.append(result)
                        
                except Exception as e:
                    logger.warning(f"Stress test add {i+1} failed: {str(e)}")
            
            self.log_test_result(
                "Stress Test - Rapid Adds", 
                len(stress_memories) >= 8, 
                f"Successfully added {len(stress_memories)}/10 memories"
            )
            
            # Wait for indexing
            await asyncio.sleep(3)
            
            # Perform multiple searches
            search_success_count = 0
            for i in range(5):
                try:
                    results = memory.search(
                        query=f"stress test memory {i*2+1}",
                        user_id=f"{self.test_user_id}_stress",
                        limit=3
                    )
                    
                    if results and len(results) > 0:
                        search_success_count += 1
                        
                except Exception as e:
                    logger.warning(f"Stress test search {i+1} failed: {str(e)}")
            
            self.log_test_result(
                "Stress Test - Multiple Searches", 
                search_success_count >= 3, 
                f"Successful searches: {search_success_count}/5"
            )
            
            return len(stress_memories) >= 8 and search_success_count >= 3
            
        except Exception as e:
            self.log_test_result("Stress Test", False, f"Error: {str(e)}")
            return False
    
    async def cleanup_test_data(self, memory):
        """Cleanup test data"""
        self.print_header("Cleanup Test Data")
        
        try:
            # Delete test memories
            test_users = [self.test_user_id, f"{self.test_user_id}_stress"]
            
            for user_id in test_users:
                try:
                    memories = memory.get_all(user_id=user_id)
                    
                    if memories:
                        for mem in memories:
                            memory_id = mem.get('id')
                            if memory_id:
                                memory.delete(memory_id=memory_id, user_id=user_id)
                        
                        self.log_test_result(
                            f"Cleanup {user_id}", 
                            True, 
                            f"Deleted {len(memories)} test memories"
                        )
                    
                except Exception as e:
                    self.log_test_result(f"Cleanup {user_id}", False, f"Error: {str(e)}")
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_header("Test Report Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        print(f"\n🎯 Overall System Status:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - System is highly robust and reliable")
        elif success_rate >= 75:
            print("   🟡 GOOD - System is mostly reliable with minor issues")
        elif success_rate >= 50:
            print("   🟠 FAIR - System has significant issues that need attention")
        else:
            print("   🔴 POOR - System has critical issues requiring immediate attention")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate
            },
            'detailed_results': self.test_results
        }
        
        with open('memory_persistence_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: memory_persistence_test_report.json")
        
        return success_rate >= 75

async def main():
    """Main test execution"""
    print("🧪 Memory Storage and Persistence Robustness Test")
    print("=" * 60)
    print("Testing Apple Intelligence Local Memory System")
    print("=" * 60)
    
    test_suite = MemoryPersistenceTest()
    
    try:
        # Run all tests
        apple_intelligence_ok = await test_suite.test_apple_intelligence_foundation()
        
        memory, ai_active = await test_suite.test_memory_initialization()
        
        if memory:
            basic_ops_ok = await test_suite.test_basic_memory_operations(memory)
            persistence_ok = await test_suite.test_memory_persistence(memory)
            update_ops_ok = await test_suite.test_memory_update_operations(memory)
            stress_ok = await test_suite.test_stress_operations(memory)
            
            # Cleanup
            await test_suite.cleanup_test_data(memory)
        else:
            basic_ops_ok = persistence_ok = update_ops_ok = stress_ok = False
        
        mcp_ok = await test_suite.test_mcp_server_integration()
        qdrant_ok = await test_suite.test_qdrant_persistence()
        
        # Generate final report
        system_robust = test_suite.generate_report()
        
        if system_robust:
            print(f"\n🎉 SYSTEM VERIFICATION COMPLETE: Memory system is robust and reliable!")
            return 0
        else:
            print(f"\n⚠️ SYSTEM NEEDS ATTENTION: Some components require fixes")
            return 1
            
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)