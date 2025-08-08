#!/usr/bin/env python3
"""
Simple MCP Server Test
Test the MCP server functionality directly
"""

import asyncio
import json
import sys
from datetime import datetime

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

async def test_mcp_server():
    """Test MCP server functionality directly"""
    
    print("🧪 Testing MCP Server Multi-Agent Functionality")
    print("=" * 50)
    
    try:
        # Import the MCP server
        from integrations.mcp.server import Mem0MCPServer
        
        # Create server instance
        server = Mem0MCPServer()
        
        # Test data
        run_id = f"mcp_test_{datetime.now().strftime('%H%M%S')}"
        user_id = "gabriel"
        
        print(f"📝 Test Run ID: {run_id}")
        print()
        
        # Test 1: Test connection
        print("1. Testing connection...")
        connection_result = await server.server.call_tool("test_connection", {})
        print("✅ Connection test completed")
        print()
        
        # Test 2: Add memory with agent tracking
        print("2. Adding memory with multi-agent tracking...")
        add_result = await server.server.call_tool("add_memory", {
            "messages": "This is a test memory for multi-agent functionality.",
            "user_id": user_id,
            "agent_id": "test_claude",
            "run_id": run_id,
            "metadata": json.dumps({
                "test": True,
                "topic": "multi_agent_mcp_test"
            })
        })
        print("✅ Memory added with agent tracking")
        print()
        
        # Test 3: Add another memory from different agent
        print("3. Adding memory from different agent...")
        add_result2 = await server.server.call_tool("add_memory", {
            "messages": "This is another test memory from a different agent.",
            "user_id": user_id,
            "agent_id": "test_kiro",
            "run_id": run_id,
            "metadata": json.dumps({
                "test": True,
                "topic": "multi_agent_mcp_test"
            })
        })
        print("✅ Second memory added from different agent")
        print()
        
        # Test 4: Get agent-specific memories
        print("4. Testing agent-specific memory retrieval...")
        agent_memories = await server.server.call_tool("get_agent_memories", {
            "agent_id": "test_claude",
            "user_id": user_id,
            "run_id": run_id
        })
        print("✅ Agent-specific memories retrieved")
        print()
        
        # Test 5: Get shared context
        print("5. Testing shared context retrieval...")
        shared_context = await server.server.call_tool("get_shared_context", {
            "run_id": run_id,
            "user_id": user_id
        })
        print("✅ Shared context retrieved")
        print()
        
        # Test 6: Get collaboration summary
        print("6. Testing collaboration summary...")
        collaboration_summary = await server.server.call_tool("get_agent_collaboration_summary", {
            "run_id": run_id,
            "user_id": user_id
        })
        print("✅ Collaboration summary generated")
        print()
        
        print("🎉 MCP Server Multi-Agent Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    success = await test_mcp_server()
    if success:
        print("✅ MCP server test passed!")
        sys.exit(0)
    else:
        print("❌ MCP server test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())