#!/usr/bin/env python3
"""
Test script for the integrated mem0 system
Tests MCP server connectivity and database persistence
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_database_connections():
    """Test database connectivity"""
    print("🔍 Testing database connections...")
    
    # Test Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:10333")
        collections = client.get_collections()
        print(f"✅ Qdrant connected - Collections: {len(collections.collections)}")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
    
    # Test Redis if available
    try:
        import redis
        r = redis.Redis(host='localhost', port=10379, decode_responses=True)
        r.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
    
    # Test PostgreSQL if available
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=10432,
            database="mem0",
            user="mem0",
            password="mem0password"
        )
        conn.close()
        print("✅ PostgreSQL connected")
    except Exception as e:
        print(f"⚠️ PostgreSQL connection failed: {e}")

async def test_memory_system():
    """Test mem0 memory system"""
    print("\n🧠 Testing memory system...")
    
    try:
        from mem0 import Memory
        
        # Test basic memory operations
        memory = Memory()
        
        # Add a test memory
        result = memory.add(
            messages="This is a test memory for system validation",
            user_id="test_user"
        )
        print(f"✅ Memory added: {result}")
        
        # Search memories
        search_results = memory.search(
            query="test memory",
            user_id="test_user"
        )
        print(f"✅ Memory search: Found {len(search_results)} results")
        
        # Get all memories
        all_memories = memory.get_all(user_id="test_user")
        print(f"✅ Memory retrieval: Found {len(all_memories)} total memories")
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")

async def test_mcp_server():
    """Test MCP server functionality"""
    print("\n🔌 Testing MCP server...")
    
    try:
        # Import the server class
        sys.path.insert(0, str(project_root / "integrations" / "mcp"))
        from unified_mcp_server import UnifiedMCPServer, DatabaseConnectionManager
        
        # Test database connection manager
        db_manager = DatabaseConnectionManager()
        await db_manager.initialize_connections()
        
        status = db_manager.get_connection_status()
        print(f"✅ Database connections: {json.dumps(status, indent=2)}")
        
        print("✅ MCP server components loaded successfully")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")

async def test_graph_functionality():
    """Test graph memory functionality if available"""
    print("\n📊 Testing graph functionality...")
    
    try:
        # Try to test graph memory
        from mem0.memory.graph_memory import MemoryGraph
        print("✅ Graph memory module available")
        
        # Note: Full graph testing would require Neo4j configuration
        print("ℹ️ Graph memory requires Neo4j for full functionality")
        
    except ImportError as e:
        print(f"⚠️ Graph memory not available: {e}")
    except Exception as e:
        print(f"❌ Graph functionality test failed: {e}")

def test_ui_availability():
    """Test if UI files are available"""
    print("\n🎨 Testing UI availability...")
    
    ui_file = project_root / "integrations" / "ui" / "knowledge_graph_ui.html"
    if ui_file.exists():
        print("✅ Knowledge Graph UI file exists")
        
        # Check if it's being served
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:8080/knowledge_graph_ui.html")
            if response.status == 200:
                print("✅ Knowledge Graph UI is accessible")
            else:
                print(f"⚠️ UI server returned status: {response.status}")
        except Exception as e:
            print(f"⚠️ UI server not accessible: {e}")
    else:
        print("❌ Knowledge Graph UI file not found")

def display_system_info():
    """Display system information"""
    print("\n📋 System Information:")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check for key files
    key_files = [
        "integrations/mcp/unified_mcp_server.py",
        "integrations/ui/knowledge_graph_ui.html",
        "start_integrated_system.sh",
        "stop_integrated_system.sh"
    ]
    
    print("\n📁 Key files:")
    for file_path in key_files:
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {status} {file_path}")

async def main():
    """Run all tests"""
    print("🚀 Testing Integrated Mem0 System")
    print("=" * 50)
    
    # Display system info
    display_system_info()
    
    # Run tests
    await test_database_connections()
    await test_memory_system()
    await test_mcp_server()
    await test_graph_functionality()
    test_ui_availability()
    
    print("\n" + "=" * 50)
    print("🎉 System test completed!")
    print("\nNext steps:")
    print("1. Run: ./start_integrated_system.sh")
    print("2. Open: http://localhost:8080/knowledge_graph_ui.html")
    print("3. Test the knowledge graph visualization")

if __name__ == "__main__":
    asyncio.run(main())