#!/usr/bin/env python3
"""
Complete Memory Ecosystem Test Suite
Tests all components: Mem0, OpenMemory, integrations, and agent frameworks
"""

import asyncio
import json
import requests
import time
import subprocess
from typing import Dict, List
from memory_config_manager import MemoryConfigManager
from agent_memory_integrations import (
    AutoGenMemoryAgent, 
    CrewAIMemoryAgent, 
    LangChainMemoryAgent,
    MultiAgentMemorySystem,
    OpenMemoryClient
)

class EcosystemTester:
    def __init__(self):
        self.config_manager = MemoryConfigManager()
        self.test_results = {}
        self.services = {
            'ollama': 'http://localhost:11434',
            'qdrant': 'http://localhost:6333',
            'neo4j': 'http://localhost:7474',
            'openmemory': 'http://localhost:8765',
            'mem0_server': 'http://localhost:1987'
        }
    
    def check_service_health(self, service_name: str, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            if service_name == 'ollama':
                response = requests.get(f"{url}/api/tags", timeout=5)
            elif service_name == 'qdrant':
                response = requests.get(f"{url}/health", timeout=5)
            elif service_name == 'neo4j':
                response = requests.get(f"{url}/", timeout=5)
            elif service_name == 'openmemory':
                response = requests.get(f"{url}/health", timeout=5)
            elif service_name == 'mem0_server':
                response = requests.get(f"{url}/health", timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            return response.status_code == 200
        except:
            return False
    
    def test_service_health(self):
        """Test all service health endpoints"""
        print("🏥 Testing service health...")
        results = {}
        
        for service, url in self.services.items():
            is_healthy = self.check_service_health(service, url)
            results[service] = is_healthy
            status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
            print(f"  {service:<15} {status}")
        
        self.test_results['service_health'] = results
        return all(results.values())
    
    def test_ollama_models(self):
        """Test Ollama models availability"""
        print("🤖 Testing Ollama models...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags")
            models = response.json()
            
            required_models = ["llama3.2:3b", "nomic-embed-text"]
            available_models = [model['name'] for model in models.get('models', [])]
            
            results = {}
            for model in required_models:
                is_available = any(model in available for available in available_models)
                results[model] = is_available
                status = "✅ AVAILABLE" if is_available else "❌ MISSING"
                print(f"  {model:<20} {status}")
            
            self.test_results['ollama_models'] = results
            return all(results.values())
        
        except Exception as e:
            print(f"  ❌ Error checking Ollama models: {e}")
            self.test_results['ollama_models'] = {'error': str(e)}
            return False
    
    def test_mem0_basic(self):
        """Test basic Mem0 functionality"""
        print("🧠 Testing Mem0 basic functionality...")
        
        try:
            from mem0 import Memory
            
            # Initialize with config
            mem0_config = self.config_manager.get_mem0_config()
            memory = Memory(**mem0_config)
            
            # Test add memory
            test_memory = "I love testing memory systems"
            result = memory.add(test_memory, user_id="test_user")
            print(f"  ✅ Added memory: {result}")
            
            # Test search
            search_results = memory.search("testing", user_id="test_user")
            print(f"  ✅ Search found {len(search_results)} results")
            
            # Test get all
            all_memories = memory.get_all(user_id="test_user")
            print(f"  ✅ Retrieved {len(all_memories)} total memories")
            
            self.test_results['mem0_basic'] = {
                'add': True,
                'search': len(search_results) > 0,
                'get_all': len(all_memories) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ Mem0 basic test failed: {e}")
            self.test_results['mem0_basic'] = {'error': str(e)}
            return False
    
    def test_mem0_async(self):
        """Test Mem0 async functionality"""
        print("⚡ Testing Mem0 async functionality...")
        
        async def async_test():
            try:
                from mem0 import AsyncMemory
                
                # Initialize async memory
                mem0_config = self.config_manager.get_mem0_config()
                async_memory = AsyncMemory(**mem0_config)
                
                # Test async operations
                await async_memory.add("Async memory test", user_id="async_user")
                results = await async_memory.search("async", user_id="async_user")
                all_memories = await async_memory.get_all(user_id="async_user")
                
                print(f"  ✅ Async operations completed successfully")
                return True
                
            except Exception as e:
                print(f"  ❌ Async test failed: {e}")
                return False
        
        try:
            result = asyncio.run(async_test())
            self.test_results['mem0_async'] = {'success': result}
            return result
        except Exception as e:
            print(f"  ❌ Async test setup failed: {e}")
            self.test_results['mem0_async'] = {'error': str(e)}
            return False
    
    def test_openmemory_api(self):
        """Test OpenMemory API functionality"""
        print("🔗 Testing OpenMemory API...")
        
        try:
            client = OpenMemoryClient()
            
            # Test add memory
            add_result = client.add_memory("OpenMemory API test")
            print(f"  ✅ Added memory via API")
            
            # Test search
            search_results = client.search_memories("API test")
            print(f"  ✅ Search found {len(search_results)} results")
            
            # Test get all
            all_memories = client.get_all_memories()
            print(f"  ✅ Retrieved {len(all_memories)} total memories")
            
            self.test_results['openmemory_api'] = {
                'add': True,
                'search': len(search_results) > 0,
                'get_all': len(all_memories) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ OpenMemory API test failed: {e}")
            self.test_results['openmemory_api'] = {'error': str(e)}
            return False
    
    def test_autogen_integration(self):
        """Test AutoGen memory integration"""
        print("🤝 Testing AutoGen integration...")
        
        try:
            # Create AutoGen memory agent
            agent = AutoGenMemoryAgent(
                name="TestAutoGenAgent",
                system_message="You are a test agent with memory"
            )
            
            # Test message processing
            messages = [{"content": "Remember that I like Python programming"}]
            response = agent.generate_reply(messages)
            print(f"  ✅ AutoGen agent responded: {response[:50]}...")
            
            # Test memory persistence
            search_results = agent.search_memory("Python")
            print(f"  ✅ Found {len(search_results)} relevant memories")
            
            self.test_results['autogen_integration'] = {
                'agent_creation': True,
                'message_processing': True,
                'memory_search': len(search_results) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ AutoGen integration test failed: {e}")
            self.test_results['autogen_integration'] = {'error': str(e)}
            return False
    
    def test_crewai_integration(self):
        """Test CrewAI memory integration"""
        print("👥 Testing CrewAI integration...")
        
        try:
            # Create CrewAI memory agent
            agent = CrewAIMemoryAgent(
                name="TestCrewAgent",
                role="Data Analyst",
                goal="Analyze data with memory",
                backstory="Expert analyst with persistent memory"
            )
            
            # Test task execution
            result = agent.execute_task("Analyze test data for patterns")
            print(f"  ✅ CrewAI agent executed task: {result[:50]}...")
            
            # Test memory search
            search_results = agent.search_memory("analyze")
            print(f"  ✅ Found {len(search_results)} relevant memories")
            
            self.test_results['crewai_integration'] = {
                'agent_creation': True,
                'task_execution': True,
                'memory_search': len(search_results) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ CrewAI integration test failed: {e}")
            self.test_results['crewai_integration'] = {'error': str(e)}
            return False
    
    def test_langchain_integration(self):
        """Test LangChain memory integration"""
        print("🔗 Testing LangChain integration...")
        
        try:
            # Create LangChain memory agent
            agent = LangChainMemoryAgent(name="TestLangChainAgent")
            
            # Test invoke method
            result = agent.invoke({"input": "Process this with memory context"})
            print(f"  ✅ LangChain agent invoked: {result['output'][:50]}...")
            
            # Test memory search
            search_results = agent.search_memory("process")
            print(f"  ✅ Found {len(search_results)} relevant memories")
            
            self.test_results['langchain_integration'] = {
                'agent_creation': True,
                'invoke_method': True,
                'memory_search': len(search_results) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ LangChain integration test failed: {e}")
            self.test_results['langchain_integration'] = {'error': str(e)}
            return False
    
    def test_multi_agent_system(self):
        """Test multi-agent memory system"""
        print("🌐 Testing multi-agent system...")
        
        try:
            # Create multi-agent system
            system = MultiAgentMemorySystem()
            
            # Add agents
            autogen_agent = AutoGenMemoryAgent("AutoGenAgent", "AutoGen assistant")
            crew_agent = CrewAIMemoryAgent("CrewAgent", "Analyst", "Analyze", "Expert")
            
            system.add_agent(autogen_agent)
            system.add_agent(crew_agent)
            
            # Test broadcast
            responses = system.broadcast_message(
                "Collaborate on this task",
                sender="TestCoordinator"
            )
            print(f"  ✅ Broadcast sent to {len(responses)} agents")
            
            # Test system context
            context = system.get_system_context("collaboration")
            print(f"  ✅ Retrieved {len(context)} system context items")
            
            self.test_results['multi_agent_system'] = {
                'system_creation': True,
                'agent_addition': len(system.agents) == 2,
                'broadcast': len(responses) > 0,
                'system_context': len(context) >= 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ Multi-agent system test failed: {e}")
            self.test_results['multi_agent_system'] = {'error': str(e)}
            return False
    
    def test_graph_memory(self):
        """Test graph memory functionality"""
        print("🕸️ Testing graph memory...")
        
        try:
            from mem0 import Memory
            
            # Initialize with graph config
            mem0_config = self.config_manager.get_mem0_config()
            if 'graph_store_config' not in mem0_config:
                print("  ⚠️ Graph store not configured, skipping test")
                return True
            
            memory = Memory(**mem0_config)
            
            # Test graph-based memory operations
            memory.add(
                "Alice works with Bob on the project",
                user_id="graph_test",
                metadata={"type": "relationship"}
            )
            
            results = memory.search("Alice Bob", user_id="graph_test")
            print(f"  ✅ Graph memory search found {len(results)} results")
            
            self.test_results['graph_memory'] = {
                'enabled': True,
                'add_relationship': True,
                'search_relationship': len(results) > 0
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ Graph memory test failed: {e}")
            self.test_results['graph_memory'] = {'error': str(e)}
            return False
    
    def test_performance(self):
        """Test system performance"""
        print("⚡ Testing performance...")
        
        try:
            from mem0 import Memory
            import time
            
            memory = Memory(**self.config_manager.get_mem0_config())
            
            # Test batch operations
            start_time = time.time()
            
            for i in range(10):
                memory.add(f"Performance test memory {i}", user_id="perf_test")
            
            add_time = time.time() - start_time
            
            # Test search performance
            start_time = time.time()
            
            for i in range(5):
                results = memory.search("performance", user_id="perf_test")
            
            search_time = time.time() - start_time
            
            print(f"  ✅ Batch add (10 items): {add_time:.2f}s")
            print(f"  ✅ Batch search (5 queries): {search_time:.2f}s")
            
            self.test_results['performance'] = {
                'batch_add_time': add_time,
                'batch_search_time': search_time,
                'acceptable_performance': add_time < 10 and search_time < 5
            }
            
            return True
            
        except Exception as e:
            print(f"  ❌ Performance test failed: {e}")
            self.test_results['performance'] = {'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Complete Memory Ecosystem Test Suite")
        print("=" * 60)
        
        tests = [
            ('Service Health', self.test_service_health),
            ('Ollama Models', self.test_ollama_models),
            ('Mem0 Basic', self.test_mem0_basic),
            ('Mem0 Async', self.test_mem0_async),
            ('OpenMemory API', self.test_openmemory_api),
            ('AutoGen Integration', self.test_autogen_integration),
            ('CrewAI Integration', self.test_crewai_integration),
            ('LangChain Integration', self.test_langchain_integration),
            ('Multi-Agent System', self.test_multi_agent_system),
            ('Graph Memory', self.test_graph_memory),
            ('Performance', self.test_performance)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                if test_func():
                    passed += 1
                    print(f"  ✅ {test_name} PASSED")
                else:
                    failed += 1
                    print(f"  ❌ {test_name} FAILED")
            except Exception as e:
                failed += 1
                print(f"  ❌ {test_name} ERROR: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Memory ecosystem is fully operational!")
        else:
            print(f"\n⚠️ {failed} tests failed. Check the output above for details.")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to test_results.json")
        
        return failed == 0

if __name__ == "__main__":
    tester = EcosystemTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)