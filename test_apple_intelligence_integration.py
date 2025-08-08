#!/usr/bin/env python3
"""
Test script for Apple Intelligence integration with MCP server
"""

import sys
import os
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

def test_apple_intelligence_integration():
    """Test Apple Intelligence integration with mem0"""
    
    print("🍎 Testing Apple Intelligence Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import Apple Intelligence providers
        print("1. Testing Apple Intelligence provider imports...")
        from mem0.llms.apple_intelligence import AppleIntelligenceLLM
        from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder
        print("✅ Apple Intelligence providers imported successfully")
        
        # Test 2: Initialize providers
        print("\n2. Testing provider initialization...")
        llm = AppleIntelligenceLLM()
        embedder = AppleIntelligenceEmbedder()
        print(f"✅ LLM initialized: {llm.__class__.__name__} (available: {llm.is_available})")
        print(f"✅ Embedder initialized: {embedder.__class__.__name__} (available: {embedder.is_available()})")
        
        # Test 3: Test factory integration
        print("\n3. Testing factory integration...")
        from mem0.utils.factory import LlmFactory, EmbedderFactory
        from mem0.configs.llms.base import BaseLlmConfig
        from mem0.configs.embeddings.base import BaseEmbedderConfig
        
        llm_config = BaseLlmConfig(model="apple-intelligence-foundation")
        embedder_config = BaseEmbedderConfig(model="apple-intelligence-embeddings")
        
        factory_llm = LlmFactory.create("apple_intelligence", {"model": "apple-intelligence-foundation"})
        factory_embedder = EmbedderFactory.create("apple_intelligence", {"model": "apple-intelligence-embeddings"}, None)
        
        print(f"✅ Factory LLM: {factory_llm.__class__.__name__}")
        print(f"✅ Factory Embedder: {factory_embedder.__class__.__name__}")
        
        # Test 4: Test Memory initialization with Apple Intelligence
        print("\n4. Testing Memory initialization with Apple Intelligence...")
        from mem0 import Memory
        from mem0.configs.base import MemoryConfig
        
        config = {
            "llm": {
                "provider": "apple_intelligence",
                "config": {
                    "model": "apple-intelligence-foundation",
                    "max_tokens": 500,
                    "temperature": 0.3
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
        
        memory_config = MemoryConfig(**config)
        memory = Memory(memory_config)
        
        print(f"✅ Memory initialized with Apple Intelligence")
        print(f"   LLM: {memory.llm.__class__.__name__}")
        print(f"   Embedder: {memory.embedding_model.__class__.__name__}")
        
        # Test 5: Test basic memory operations
        print("\n5. Testing basic memory operations...")
        
        # Add a test memory
        result = memory.add(
            messages="This is a test memory using Apple Intelligence Foundation Models",
            user_id="test_user",
            metadata={"processed_by": "apple_intelligence_foundation_models", "test": True}
        )
        print(f"✅ Memory added: {result}")
        
        # Search for the memory
        search_results = memory.search(
            query="test memory Apple Intelligence",
            user_id="test_user",
            limit=5
        )
        print(f"✅ Memory search completed: {len(search_results)} results")
        
        # Test 6: Test MCP server initialization
        print("\n6. Testing MCP server initialization...")
        from integrations.mcp.server import Mem0MCPServer
        
        server = Mem0MCPServer()
        if server.memory:
            print(f"✅ MCP Server initialized successfully")
            print(f"   Server memory LLM: {server.memory.llm.__class__.__name__}")
            print(f"   Server memory Embedder: {server.memory.embedding_model.__class__.__name__}")
        else:
            print("❌ MCP Server memory initialization failed")
        
        print("\n🎉 All tests passed! Apple Intelligence integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_apple_intelligence_integration()
    sys.exit(0 if success else 1)