#!/usr/bin/env python3

"""
Debug Apple Intelligence + Mem0 Integration
"""

import sys
import os
sys.path.insert(0, '/Volumes/Ready500/DEVELOPMENT/mem0')

try:
    print("🔄 Testing local Apple Intelligence configuration...")
    from mem0 import Memory
    
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "gabriel_local_apple_intelligence_384",
                "host": "localhost",
                "port": 6333,
                "embedding_model_dims": 384
            }
        },
        "llm": {
            "provider": "apple_intelligence",
            "config": {
                "model": "foundation_models",
                "temperature": 0.1
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
    
    print("✅ Config created")
    
    print("🔄 Initializing memory system...")
    memory = Memory.from_config(config)
    print("✅ Memory system initialized!")
    
    print("🔄 Testing simple memory add...")
    result = memory.add(
        messages="Gabriel is testing the local Apple Intelligence memory system.",
        user_id="gabriel"
    )
    
    print("✅ Memory add successful!")
    print(f"Result: {result}")
    
    print("🔄 Testing search...")
    search_result = memory.search(
        query="Apple Intelligence",
        user_id="gabriel",
        limit=5
    )
    
    print("✅ Search successful!")
    print(f"Found {len(search_result.get('results', []))} memories")
    
    print("🎉 Local Apple Intelligence system is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()