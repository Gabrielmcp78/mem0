#!/usr/bin/env python3
"""
Test Apple Intelligence MCP Integration

This script tests the integration of Apple Intelligence providers with the MCP server.
"""

import sys
import os
import json
import logging

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apple-intelligence-mcp-test")

def test_apple_intelligence_availability():
    """Test Apple Intelligence availability"""
    print("🍎 Testing Apple Intelligence availability...")
    
    try:
        from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
        
        available = check_apple_intelligence_availability()
        status = get_apple_intelligence_status()
        
        print(f"Available: {available}")
        print(f"Status: {json.dumps(status, indent=2, default=str)}")
        
        return available
        
    except Exception as e:
        print(f"Error checking Apple Intelligence: {e}")
        return False

def test_apple_intelligence_providers():
    """Test Apple Intelligence LLM and Embedder providers"""
    print("\n🧠 Testing Apple Intelligence providers...")
    
    try:
        # Test LLM provider
        from mem0.llms.apple_intelligence import AppleIntelligenceLLM
        from mem0.configs.llms.apple_intelligence import AppleIntelligenceLlmConfig
        
        llm_config = AppleIntelligenceLlmConfig()
        llm = AppleIntelligenceLLM(llm_config)
        
        print(f"LLM Provider: {llm.__class__.__name__}")
        print(f"LLM Available: {llm.is_available}")
        print(f"LLM Model Info: {json.dumps(llm.get_model_info(), indent=2, default=str)}")
        
        # Test Embedder provider
        from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder
        from mem0.configs.embeddings.base import BaseEmbedderConfig
        
        embedder_config = BaseEmbedderConfig()
        embedder = AppleIntelligenceEmbedder(embedder_config)
        
        print(f"Embedder Provider: {embedder.__class__.__name__}")
        print(f"Embedder Available: {embedder.is_available()}")
        print(f"Embedder Status: {json.dumps(embedder.get_status(), indent=2, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"Error testing providers: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_initialization():
    """Test Memory initialization with Apple Intelligence"""
    print("\n💾 Testing Memory initialization...")
    
    try:
        from mem0 import Memory
        from mem0.utils.apple_intelligence import check_apple_intelligence_availability
        
        apple_intelligence_available = check_apple_intelligence_availability()
        
        if apple_intelligence_available:
            # Test with Apple Intelligence configuration
            config = {
                "llm": {
                    "provider": "apple_intelligence",
                    "config": {
                        "model": "apple-intelligence-foundation",
                        "max_tokens": 500,
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "top_k": 50
                    }
                },
                "embedder": {
                    "provider": "apple_intelligence", 
                    "config": {
                        "model": "apple-intelligence-embeddings",
                        "embedding_dims": 1536
                    }
                }
            }
            
            memory = Memory.from_config(config)
            print(f"Memory initialized with Apple Intelligence: {memory is not None}")
            
            # Check actual providers
            if memory:
                llm_class = memory.llm.__class__.__name__ if hasattr(memory, 'llm') else 'Unknown'
                embedder_class = memory.embedder.__class__.__name__ if hasattr(memory, 'embedder') else 'Unknown'
                print(f"Actual LLM provider: {llm_class}")
                print(f"Actual Embedder provider: {embedder_class}")
            
        else:
            # Test with fallback configuration
            memory = Memory()
            print(f"Memory initialized with fallback: {memory is not None}")
        
        return memory is not None
        
    except Exception as e:
        print(f"Error initializing memory: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_memory_operations():
    """Test memory operations from MCP server"""
    print("\n🔧 Testing MCP memory operations...")
    
    try:
        # Import the memory operations module
        sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp')
        from memory_operations import initialize_memory, add_memory, search_memories
        
        # Initialize memory
        memory = initialize_memory()
        if not memory:
            print("Failed to initialize memory")
            return False
        
        print("Memory initialized successfully")
        
        # Test add memory
        add_params = {
            "messages": "This is a test memory for Apple Intelligence integration",
            "user_id": "test_user",
            "agent_id": "test_agent",
            "metadata": json.dumps({"test": True, "integration": "apple_intelligence"})
        }
        
        add_result = add_memory(add_params)
        print(f"Add memory result: {json.dumps(add_result, indent=2, default=str)}")
        
        if add_result.get("success"):
            # Test search memories
            search_params = {
                "query": "test memory Apple Intelligence",
                "user_id": "test_user",
                "limit": 5
            }
            
            search_result = search_memories(search_params)
            print(f"Search memory result: {json.dumps(search_result, indent=2, default=str)}")
            
            return search_result.get("success", False)
        
        return False
        
    except Exception as e:
        print(f"Error testing MCP operations: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Apple Intelligence MCP Integration Tests\n")
    
    # Test 1: Apple Intelligence availability
    availability_ok = test_apple_intelligence_availability()
    
    # Test 2: Apple Intelligence providers
    providers_ok = test_apple_intelligence_providers()
    
    # Test 3: Memory initialization
    memory_ok = test_memory_initialization()
    
    # Test 4: MCP memory operations
    mcp_ok = test_mcp_memory_operations()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"Apple Intelligence Availability: {'✅' if availability_ok else '❌'}")
    print(f"Apple Intelligence Providers: {'✅' if providers_ok else '❌'}")
    print(f"Memory Initialization: {'✅' if memory_ok else '❌'}")
    print(f"MCP Memory Operations: {'✅' if mcp_ok else '❌'}")
    
    all_tests_passed = all([availability_ok, providers_ok, memory_ok, mcp_ok])
    print(f"\nOverall Status: {'✅ All tests passed!' if all_tests_passed else '❌ Some tests failed'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)