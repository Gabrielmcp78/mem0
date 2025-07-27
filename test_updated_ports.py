#!/usr/bin/env python3
"""
Test Updated Port Configuration
Verify all services work with new 10000+ port range
"""

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
import requests
import time

def create_memory_config():
    """Create memory config with updated ports"""
    return MemoryConfig(
        llm=LlmConfig(
            provider="ollama",
            config={
                "model": "llama3.2:3b",
                "ollama_base_url": "http://localhost:11434"  # Ollama stays on 11434
            }
        ),
        embedder=EmbedderConfig(
            provider="ollama", 
            config={
                "model": "nomic-embed-text",
                "ollama_base_url": "http://localhost:11434",
                "embedding_dims": 768
            }
        ),
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "host": "localhost",
                "port": 16333,  # Updated Qdrant port
                "collection_name": "port_test_memories",
                "embedding_model_dims": 768
            }
        )
    )

def test_memory_system():
    """Test basic memory functionality with new ports"""
    print("🧠 Testing memory system with updated ports...")
    
    try:
        config = create_memory_config()
        memory = Memory(config)
        
        print("✅ Memory system initialized successfully")
        
        # Test add memory
        result = memory.add("Testing updated port configuration", user_id="port_test_user")
        print(f"✅ Added memory: {result}")
        
        # Test search
        search_results = memory.search("port configuration", user_id="port_test_user")
        print(f"✅ Search found {len(search_results['results'])} results")
        
        # Test get all
        all_memories = memory.get_all(user_id="port_test_user")
        print(f"✅ Retrieved {len(all_memories['results'])} total memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def test_service_endpoints():
    """Test service endpoints with new ports"""
    print("\n🌐 Testing service endpoints...")
    
    services = {
        "Qdrant Health": "http://localhost:16333/health",
        "OpenMemory API": "http://localhost:18765/api/v1/config/",
        "Enhanced API": "http://localhost:18767/api/v1/health",
    }
    
    results = {}
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: OK")
                results[service_name] = True
            else:
                print(f"⚠️ {service_name}: HTTP {response.status_code}")
                results[service_name] = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {service_name}: Connection refused (service may not be running)")
            results[service_name] = False
        except Exception as e:
            print(f"❌ {service_name}: {e}")
            results[service_name] = False
    
    return results

def print_port_summary():
    """Print summary of new port assignments"""
    print("\n" + "="*60)
    print("📍 NEW PORT ASSIGNMENTS (10000+ RANGE)")
    print("="*60)
    
    services = [
        ("Enhanced UI", "13001", "Modern, accessible interface"),
        ("Original UI", "13000", "OpenMemory default interface"),
        ("Enhanced API", "18767", "Custom API with extensions"),
        ("OpenMemory API", "18765", "OpenMemory MCP REST API"),
        ("MCP Server", "18766", "WebSocket MCP protocol"),
        ("Qdrant HTTP", "16333", "Vector database HTTP API"),
        ("Qdrant gRPC", "16334", "Vector database gRPC API"),
        ("Neo4j HTTP", "17474", "Graph database web interface"),
        ("Neo4j Bolt", "17687", "Graph database Bolt protocol"),
        ("Redis", "16379", "Caching and session storage"),
        ("PostgreSQL", "15432", "Structured data storage"),
    ]
    
    for name, port, description in services:
        print(f"{name:<20} {port:<8} {description}")
    
    print("\n🚀 Quick Access URLs:")
    print(f"  Enhanced UI:     http://localhost:13001")
    print(f"  Original UI:     http://localhost:13000")
    print(f"  Qdrant Dashboard: http://localhost:16333/dashboard")
    print(f"  Neo4j Browser:   http://localhost:17474")

def main():
    """Run all tests"""
    print("🔧 Testing Updated Port Configuration")
    print("All ports moved to 10000+ range to avoid conflicts")
    
    # Test memory system
    memory_success = test_memory_system()
    
    # Test service endpoints
    service_results = test_service_endpoints()
    
    # Print summary
    print_port_summary()
    
    # Final status
    print("\n" + "="*60)
    if memory_success:
        print("🎉 MEMORY SYSTEM: ✅ Working with updated ports!")
    else:
        print("💥 MEMORY SYSTEM: ❌ Issues detected")
    
    working_services = sum(1 for result in service_results.values() if result)
    total_services = len(service_results)
    
    print(f"🌐 SERVICES: {working_services}/{total_services} responding")
    
    if not all(service_results.values()):
        print("\n⚠️ Some services not responding - they may need to be started:")
        print("   Run: ./start_enhanced_system.sh")
    
    print("\n📚 See PORT_REFERENCE.md for complete port documentation")

if __name__ == "__main__":
    main()