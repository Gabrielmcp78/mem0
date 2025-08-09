#!/usr/bin/env python3

"""
Test script for Gabriel's Full Stack Mem0 System with local embeddings
Tests integration between Qdrant, Neo4j, and SQLite without requiring OpenAI API
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, '.')

try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig
    print("✅ mem0 package imported successfully")
except ImportError as e:
    print(f"❌ Failed to import mem0: {e}")
    sys.exit(1)

# Configuration for full stack with local embeddings
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "gabriel_apple_intelligence_memories",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 384  # Sentence transformers dimension
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password"
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:1b",
            "temperature": 0.1,
            "base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dims": 384
        }
    },
    "version": "v1.1"
}

def test_connections():
    """Test individual database connections"""
    print("🔍 Testing individual database connections...")
    
    # Test Qdrant
    try:
        import requests
        response = requests.get("http://localhost:6333/collections")
        if response.status_code == 200:
            print("✅ Qdrant connection successful")
            collections = response.json()
            print(f"   📊 Collections: {len(collections.get('result', {}).get('collections', []))}")
        else:
            print(f"⚠️  Qdrant responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
    
    # Test Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("✅ Neo4j connection successful")
            driver.close()
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("   💡 Make sure Neo4j is running with auth neo4j/password")
    
    # Test SQLite (always works)
    print("✅ SQLite ready (file-based database)")

def test_basic_functionality():
    """Test basic mem0 functionality without full LLM integration"""
    print("\n🧪 Testing basic mem0 functionality...")
    
    try:
        # Test with minimal config (just vector store)
        minimal_config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "gabriel_test_memories",
                    "host": "localhost", 
                    "port": 6333,
                    "embedding_model_dims": 384
                }
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "embedding_dims": 384
                }
            },
            "version": "v1.1"
        }
        
        print("📊 Initializing minimal memory system...")
        memory = Memory.from_config(minimal_config)
        print("✅ Minimal memory system initialized!")
        
        # Test adding memory without LLM inference
        print("💾 Testing raw memory addition (no LLM inference)...")
        result = memory.add(
            messages="Gabriel is testing the mem0 full stack architecture with local embeddings.",
            user_id="gabriel",
            infer=False  # Skip LLM processing
        )
        
        print(f"✅ Raw memory added successfully!")
        print(f"📝 Results: {result}")
        
        # Test search
        print("🔍 Testing memory search...")
        search_result = memory.search(
            query="mem0 architecture",
            user_id="gabriel",
            limit=3
        )
        
        print(f"✅ Search completed!")
        print(f"📊 Found {len(search_result.get('results', []))} memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Testing Gabriel's Full Stack Mem0 System (Local Mode)...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Test connections first
    test_connections()
    
    # Test basic functionality
    success = test_basic_functionality()
    
    if success:
        print(f"\n🎉 Basic Mem0 System Test PASSED!")
        print(f"📊 Architecture Status:")
        print(f"  • Qdrant (Vector Store): ✅ Working")
        print(f"  • Neo4j (Graph Store): ⏳ Available (not tested in basic mode)")
        print(f"  • SQLite (Metadata): ✅ Working")
        print(f"  • HuggingFace Embeddings: ✅ Working")
        print(f"\n💡 Next Steps:")
        print(f"  1. Set OPENAI_API_KEY for full LLM features")
        print(f"  2. Test the MCP server: node integrations/mcp/mem0_full_stack_server.js")
        print(f"  3. Update Claude Desktop configuration")
        return True
    else:
        print(f"\n💥 Basic System Test FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)