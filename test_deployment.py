#!/usr/bin/env python3
"""
Test script to verify Mem0 deployment and infrastructure services
"""

import os
import sys
import requests
import psycopg2
import redis
from typing import Dict, Any

def test_infrastructure_services() -> Dict[str, Any]:
    """Test all infrastructure services"""
    results = {
        "postgresql": False,
        "redis": False,
        "qdrant": False,
        "ollama": False
    }
    
    # Test PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=25432,
            database="mem0",
            user="mem0",
            password="mem0_secure_password_2024"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        if version:
            results["postgresql"] = True
            print("✅ PostgreSQL: Connected successfully")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL: Connection failed - {e}")
    
    # Test Redis
    try:
        r = redis.Redis(host="localhost", port=26379, decode_responses=True)
        r.ping()
        r.set("test_key", "test_value")
        if r.get("test_key") == "test_value":
            results["redis"] = True
            print("✅ Redis: Connected successfully")
        r.delete("test_key")
    except Exception as e:
        print(f"❌ Redis: Connection failed - {e}")
    
    # Test Qdrant
    try:
        response = requests.get("http://localhost:26333/", timeout=5)
        if response.status_code == 200 and "qdrant" in response.text.lower():
            results["qdrant"] = True
            print("✅ Qdrant: API accessible")
        else:
            print(f"❌ Qdrant: API check failed - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Qdrant: Connection failed - {e}")
    
    # Test Ollama
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            results["ollama"] = True
            print("✅ Ollama: API accessible")
        else:
            print(f"❌ Ollama: API failed - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama: Connection failed - {e}")
    
    return results

def test_mem0_basic_functionality():
    """Test basic Mem0 functionality"""
    try:
        # Set environment variables for Mem0 to use our infrastructure
        os.environ["QDRANT_URL"] = "http://localhost:26333"
        os.environ["REDIS_URL"] = "redis://localhost:26379"
        
        # Try to import and initialize Mem0
        from mem0 import Memory
        
        # Create memory instance with custom config
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "url": "http://localhost:26333",
                    "collection_name": "test_memories"
                }
            },
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.2:3b",
                    "base_url": "http://localhost:11434"
                }
            }
        }
        
        memory = Memory.from_config(config)
        
        # Test basic operations
        print("\n🧪 Testing Mem0 basic operations...")
        
        # Add a test memory
        test_user = "test_deployment_user"
        messages = [
            {"role": "user", "content": "I love testing deployment systems"},
            {"role": "assistant", "content": "Great! I'll remember that you enjoy testing deployments."}
        ]
        
        result = memory.add(messages, user_id=test_user)
        print("✅ Memory added successfully")
        
        # Search for the memory
        search_results = memory.search("testing", user_id=test_user)
        if search_results:
            print("✅ Memory search successful")
        else:
            print("⚠️  Memory search returned no results")
        
        # Get all memories
        all_memories = memory.get_all(user_id=test_user)
        if all_memories:
            print("✅ Memory retrieval successful")
        else:
            print("⚠️  Memory retrieval returned no results")
        
        # Clean up
        memory.delete_all(user_id=test_user)
        print("✅ Memory cleanup successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Mem0 import failed: {e}")
        print("💡 Install Mem0 with: pip install mem0ai")
        return False
    except Exception as e:
        print(f"❌ Mem0 functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Mem0 Deployment Infrastructure\n")
    
    # Test infrastructure services
    print("📊 Testing Infrastructure Services:")
    results = test_infrastructure_services()
    
    # Summary
    total_services = len(results)
    working_services = sum(results.values())
    
    print(f"\n📈 Infrastructure Status: {working_services}/{total_services} services working")
    
    if working_services == total_services:
        print("🎉 All infrastructure services are working!")
        
        # Test Mem0 functionality
        print("\n" + "="*50)
        if test_mem0_basic_functionality():
            print("\n🎉 Mem0 deployment test completed successfully!")
            print("\n💡 Your Mem0 infrastructure is ready for production use!")
            print("\n📚 Next steps:")
            print("   1. Configure your application to use these services")
            print("   2. Set up monitoring and alerting")
            print("   3. Configure backup procedures")
            print("   4. Review security settings")
        else:
            print("\n⚠️  Mem0 functionality test failed")
            print("💡 Check the error messages above and ensure Mem0 is installed")
    else:
        print("❌ Some infrastructure services are not working")
        print("💡 Check the error messages above and ensure Docker containers are running")
        sys.exit(1)

if __name__ == "__main__":
    main()