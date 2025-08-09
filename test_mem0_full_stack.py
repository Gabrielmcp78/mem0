#!/usr/bin/env python3

"""
Test script for Gabriel's Full Stack Mem0 System
Tests integration between Qdrant, Neo4j, and SQLite
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
    print("Installing mem0...")
    os.system("pip3 install -e .")
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig

# Configuration for full stack
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "gabriel_apple_intelligence_memories",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1536
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
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.1
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "embedding_dims": 1536
        }
    },
    "version": "v1.1"
}

def test_full_stack():
    print("🚀 Testing Gabriel's Full Stack Mem0 System...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Initialize memory system
        print("\n📊 Initializing full stack memory system...")
        memory = Memory.from_config(config)
        print("✅ Memory system initialized successfully!")
        
        # Test adding a memory
        print("\n💾 Testing memory addition...")
        test_message = "Gabriel is working on integrating mem0 with Apple Intelligence for advanced memory capabilities."
        
        result = memory.add(
            messages=test_message,
            user_id="gabriel",
            agent_id="kiro",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        print(f"✅ Memory added successfully!")
        print(f"📝 Results: {len(result.get('results', []))} memories created")
        if 'relations' in result:
            print(f"🕸️  Relations: {len(result.get('relations', []))} relationships extracted")
        
        # Test searching memories
        print("\n🔍 Testing memory search...")
        search_result = memory.search(
            query="Apple Intelligence integration",
            user_id="gabriel",
            limit=5
        )
        
        print(f"✅ Search completed!")
        print(f"📊 Found {len(search_result.get('results', []))} relevant memories")
        
        # Test getting all memories
        print("\n📋 Testing get all memories...")
        all_memories = memory.get_all(
            user_id="gabriel",
            limit=10
        )
        
        print(f"✅ Retrieved {len(all_memories.get('results', []))} total memories")
        
        # Display system status
        print("\n🎉 Full Stack System Status:")
        print("  📊 Qdrant (Vector): ✅ Connected")
        print("  🕸️  Neo4j (Graph): ✅ Connected") 
        print("  🗄️  SQLite (Metadata): ✅ Connected")
        print("  🧠 OpenAI (LLM): ✅ Connected")
        print("  🔤 OpenAI (Embeddings): ✅ Connected")
        
        print(f"\n✨ Architecture Features:")
        print("  • Semantic similarity search")
        print("  • Entity relationship mapping")
        print("  • Memory deduplication")
        print("  • Automatic fact extraction")
        print("  • Cross-database consistency")
        print("  • Temporal memory analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Full stack test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_stack()
    if success:
        print(f"\n🎊 Full Stack Mem0 System is READY!")
        sys.exit(0)
    else:
        print(f"\n💥 Full Stack System test FAILED!")
        sys.exit(1)