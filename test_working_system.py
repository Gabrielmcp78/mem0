#!/usr/bin/env python3
"""
Test script to verify the working mem0 Apple Intelligence system
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

def test_apple_intelligence():
    """Test Apple Intelligence availability"""
    print("🧠 Testing Apple Intelligence...")
    try:
        from mem0.utils.apple_intelligence import check_apple_intelligence_availability
        available = check_apple_intelligence_availability()
        if available:
            print("   ✅ Apple Intelligence is available")
            return True
        else:
            print("   ❌ Apple Intelligence is not available")
            return False
    except Exception as e:
        print(f"   ❌ Apple Intelligence test failed: {e}")
        return False

def test_qdrant_connection():
    """Test Qdrant database connection"""
    print("🗄️  Testing Qdrant connection...")
    try:
        import requests
        response = requests.get("http://localhost:10333/collections", timeout=5)
        if response.status_code == 200:
            collections = response.json()
            print(f"   ✅ Qdrant connected - {len(collections['result']['collections'])} collections")
            return True
        else:
            print(f"   ❌ Qdrant connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Qdrant connection failed: {e}")
        return False

def test_memory_operations():
    """Test basic memory operations"""
    print("💾 Testing memory operations...")
    try:
        from simple_mcp_server import SimpleMCPServer
        
        # Initialize server
        server = SimpleMCPServer()
        if not server.memory:
            print("   ❌ Memory not initialized")
            return False
        
        # Test adding memory
        test_message = f"Test memory added at {datetime.now().isoformat()}"
        result = server.memory.add(test_message, user_id="test_user")
        if result:
            print("   ✅ Memory add successful")
        else:
            print("   ❌ Memory add failed")
            return False
        
        # Test searching memory
        results = server.memory.search("test memory", user_id="test_user", limit=5)
        if results and len(results) > 0:
            print(f"   ✅ Memory search successful - {len(results)} results")
        else:
            print("   ❌ Memory search failed or no results")
            return False
        
        # Test getting all memories
        all_memories = server.memory.get_all(user_id="test_user")
        print(f"   ✅ Get all memories successful - {len(all_memories)} total")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Memory operations failed: {e}")
        return False

def test_claude_config():
    """Test Claude Desktop configuration"""
    print("🤖 Testing Claude Desktop configuration...")
    try:
        with open('claude-desktop-config.json', 'r') as f:
            config = json.load(f)
        
        # Check if our MCP server is configured
        mcp_servers = config.get('mcpServers', {})
        if 'Mem0 Simple Apple Intelligence' in mcp_servers:
            server_config = mcp_servers['Mem0 Simple Apple Intelligence']
            if not server_config.get('disabled', False):
                print("   ✅ Simple MCP server configured and enabled")
                return True
            else:
                print("   ⚠️  Simple MCP server configured but disabled")
                return False
        else:
            print("   ❌ Simple MCP server not found in configuration")
            return False
            
    except Exception as e:
        print(f"   ❌ Claude config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Mem0 Apple Intelligence System")
    print("=" * 50)
    
    results = []
    results.append(("Apple Intelligence", test_apple_intelligence()))
    results.append(("Qdrant Database", test_qdrant_connection()))
    results.append(("Memory Operations", test_memory_operations()))
    results.append(("Claude Config", test_claude_config()))
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Restart Claude Desktop to load the new MCP server")
        print("2. You should see 'Mem0 Simple Apple Intelligence' in your MCP tools")
        print("3. Test with: test_connection, add_memory, search_memories")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)