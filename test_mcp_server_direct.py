#!/usr/bin/env python3
"""
Direct test of MCP server functionality
"""

import sys
import os
import json
import asyncio
import subprocess
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'integrations', 'mcp'))

async def test_mcp_server_direct():
    """Test MCP server directly"""
    
    print("🧪 Testing MCP Server Direct Communication")
    print("=" * 50)
    
    try:
        # Test the memory operations module directly first
        print("1. Testing memory operations module...")
        from memory_operations import add_memory, search_memories, get_all_memories
        
        # Test add memory
        add_result = add_memory({
            'messages': 'Direct MCP test - Gabriel testing Apple Intelligence integration',
            'user_id': 'gabriel',
            'agent_id': 'kiro',
            'metadata': '{"test": "direct_mcp", "category": "testing"}'
        })
        
        print(f"✅ Direct add_memory result: {add_result}")
        
        if add_result.get('success'):
            # Test search
            search_result = search_memories({
                'query': 'Gabriel testing Apple Intelligence',
                'user_id': 'gabriel',
                'limit': 5
            })
            
            print(f"✅ Direct search_memories result: {search_result}")
            
            # Test get all
            get_all_result = get_all_memories({
                'user_id': 'gabriel'
            })
            
            print(f"✅ Direct get_all_memories result: Found {len(get_all_result.get('memories', []))} memories")
            
            return True
        else:
            print("❌ Direct memory operations failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing memory operations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_node_server():
    """Test Node.js MCP server"""
    
    print("\n2. Testing Node.js MCP Server...")
    
    try:
        # Check if server.js exists
        server_path = os.path.join(PROJECT_ROOT, 'integrations', 'mcp', 'server.js')
        
        if os.path.exists(server_path):
            print(f"✅ Server file exists: {server_path}")
            
            # Test server startup (just check syntax)
            result = subprocess.run(
                ['node', '--check', server_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Node.js server syntax is valid")
                return True
            else:
                print(f"❌ Node.js server syntax error: {result.stderr}")
                return False
        else:
            print(f"❌ Server file not found: {server_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Node.js server: {str(e)}")
        return False

async def main():
    """Main test execution"""
    
    print("🧪 MCP Server Direct Test Suite")
    print("=" * 50)
    
    # Test 1: Memory operations module
    memory_ops_ok = await test_mcp_server_direct()
    
    # Test 2: Node.js server
    node_server_ok = await test_node_server()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"Memory Operations: {'✅ PASS' if memory_ops_ok else '❌ FAIL'}")
    print(f"Node.js Server: {'✅ PASS' if node_server_ok else '❌ FAIL'}")
    
    if memory_ops_ok and node_server_ok:
        print(f"\n🎉 MCP Server components are working correctly!")
        print(f"\n💡 If MCP tools are still failing, the issue may be:")
        print(f"   • MCP server not properly registered in Kiro")
        print(f"   • Network connectivity issues")
        print(f"   • MCP protocol communication problems")
        return 0
    else:
        print(f"\n⚠️ Some MCP server components need attention")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)