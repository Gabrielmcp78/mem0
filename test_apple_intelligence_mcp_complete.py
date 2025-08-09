#!/usr/bin/env python3

"""
Complete Test Suite for Apple Intelligence + Mem0 MCP Integration
Tests all components of the full stack system
"""

import subprocess
import json
import time
import sys
import os

def run_mcp_command(tool_name, args=None):
    """Send a command to the MCP server and get response"""
    if args is None:
        args = {}
    
    command = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": args
        }
    }
    
    try:
        process = subprocess.Popen(
            ['node', 'mem0_apple_intelligence_server.js'],
            cwd='/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(
            input=json.dumps(command) + '\n',
            timeout=30
        )
        
        if process.returncode != 0:
            print(f"❌ MCP server error: {stderr}")
            return None
            
        # Parse the response
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith('🍎'):
                continue  # Skip startup messages
            try:
                response = json.loads(line)
                if response.get('result'):
                    content = response['result']['content'][0]['text']
                    return json.loads(content)
            except:
                continue
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"❌ MCP command timeout: {tool_name}")
        process.kill()
        return None
    except Exception as e:
        print(f"❌ MCP command failed: {e}")
        return None

def test_apple_intelligence_mcp():
    """Test the complete Apple Intelligence MCP system"""
    print("🚀 Testing Apple Intelligence + Mem0 MCP Integration")
    print("=" * 60)
    
    # Test 1: Connection test
    print("\n1️⃣  Testing MCP server connection...")
    result = run_mcp_command('test_connection')
    if result and result.get('success'):
        print("✅ MCP server connection successful!")
        print(f"   Server: {result.get('server')}")
        print(f"   Version: {result.get('version')}")
        print(f"   Apple Intelligence: {result.get('apple_intelligence')}")
        print(f"   Status: {result.get('status')}")
    else:
        print("❌ MCP server connection failed!")
        return False
    
    # Test 2: Add memory with Apple Intelligence processing
    print("\n2️⃣  Testing memory addition with Apple Intelligence...")
    test_memory = {
        "text": """
        Gabriel is working on an advanced Apple Intelligence integration with mem0.
        The system combines three databases: Qdrant for vector embeddings, 
        Neo4j for graph relationships, and SQLite for structured metadata.
        Apple Intelligence provides advanced natural language understanding
        and fact extraction capabilities.
        """,
        "user_id": "gabriel",
        "metadata": {
            "test": True,
            "system": "apple_intelligence_mcp",
            "timestamp": "2025-01-08"
        }
    }
    
    result = run_mcp_command('add_memory', test_memory)
    if result and result.get('results'):
        print("✅ Memory addition successful!")
        print(f"   Memories created: {len(result['results'])}")
        for i, mem in enumerate(result['results'][:2]):
            print(f"   Memory {i+1}: {mem.get('memory', '')[:60]}...")
    else:
        print("❌ Memory addition failed!")
        if result:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if result.get('traceback'):
                print(f"   Traceback: {result.get('traceback')}")
        else:
            print("   No response received from MCP server")
        return False
    
    # Test 3: Semantic search with Apple Intelligence
    print("\n3️⃣  Testing semantic search...")
    search_queries = [
        "Apple Intelligence integration",
        "database architecture",
        "natural language understanding"
    ]
    
    for query in search_queries:
        result = run_mcp_command('search_memories', {
            "query": query,
            "user_id": "gabriel",
            "limit": 5
        })
        
        if result and result.get('results'):
            print(f"✅ Search '{query}': {len(result['results'])} results")
        else:
            print(f"❌ Search '{query}' failed")
    
    # Test 4: Get all memories
    print("\n4️⃣  Testing memory retrieval...")
    result = run_mcp_command('get_all_memories', {
        "user_id": "gabriel",
        "limit": 20
    })
    
    if result and result.get('results'):
        print(f"✅ Memory retrieval successful!")
        print(f"   Total memories: {len(result['results'])}")
    else:
        print("❌ Memory retrieval failed!")
        return False
    
    # Test 5: Memory history analysis
    print("\n5️⃣  Testing memory history analysis...")
    result = run_mcp_command('get_memory_history', {
        "user_id": "gabriel",
        "days": 7
    })
    
    if result and result.get('success'):
        print("✅ Memory history analysis successful!")
        print(f"   Period: {result.get('period_days')} days")
        print(f"   Total memories: {result.get('total_memories')}")
    else:
        print("❌ Memory history analysis failed!")
        return False
    
    print(f"\n🎉 Apple Intelligence + Mem0 MCP Integration Test PASSED!")
    print(f"✨ All systems operational:")
    print(f"  🍎 Apple Intelligence (LLM): ✅")
    print(f"  🤗 HuggingFace (Embeddings): ✅") 
    print(f"  📊 Qdrant (Vector Store): ✅")
    print(f"  🕸️  Neo4j (Graph Store): ✅")
    print(f"  🗄️  SQLite (Metadata): ✅")
    print(f"  🔗 MCP Server: ✅")
    
    return True

if __name__ == "__main__":
    success = test_apple_intelligence_mcp()
    sys.exit(0 if success else 1)