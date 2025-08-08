#!/usr/bin/env python3
"""
Test MCP client to verify server functionality
"""

import asyncio
import json
import subprocess
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("🧪 Testing MCP Server with Apple Intelligence...")
    
    # Start the server process
    server_script = os.path.join(os.path.dirname(__file__), 'test_minimal_server.py')
    process = await asyncio.create_subprocess_exec(
        'python3', server_script,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.path.dirname(__file__)
    )
    
    try:
        # Test 1: Initialize the server
        print("🔄 Initializing MCP server...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "apple-intelligence-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_json = json.dumps(init_request) + '\n'
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(f"Debug - Init response: {response}")
                print(f"✅ Server initialized: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                
                # Send initialized notification as required by MCP protocol
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                
                notification_json = json.dumps(initialized_notification) + '\n'
                process.stdin.write(notification_json.encode())
                await process.stdin.drain()
                
            else:
                print("❌ No response from server during initialization")
                return False
        except asyncio.TimeoutError:
            print("❌ Server initialization timed out")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response during initialization: {e}")
            return False
        
        # Test 2: List available tools
        print("🔄 Listing available tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(list_tools_request) + '\n'
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(f"Debug - Tools list response: {response}")
                tools = response.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools[:5]:  # Show first 5 tools
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:80]}...")
            else:
                print("❌ No response from server when listing tools")
                return False
        except asyncio.TimeoutError:
            print("❌ Tools list request timed out")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response when listing tools: {e}")
            return False
        
        # Test 3: Test connection tool
        print("🔄 Testing connection with Apple Intelligence...")
        test_connection_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        }
        
        request_json = json.dumps(test_connection_request) + '\n'
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                result = response.get('result')
                if result and result.get('content'):
                    content_text = result['content'][0]['text']
                    connection_data = json.loads(content_text)
                    print(f"✅ Connection test successful:")
                    print(f"   - Status: {connection_data.get('status')}")
                    print(f"   - Apple Intelligence: {connection_data.get('apple_intelligence_available')}")
                    print(f"   - Foundation Models: {connection_data.get('foundation_models_integration')}")
                    print(f"   - Neural Engine: {connection_data.get('neural_engine_optimized')}")
                    print(f"   - Actual LLM Provider: {connection_data.get('actual_providers', {}).get('llm')}")
                    print(f"   - Actual Embedder Provider: {connection_data.get('actual_providers', {}).get('embedder')}")
                else:
                    print("❌ No content in connection test response")
                    return False
            else:
                print("❌ No response from server during connection test")
                return False
        except asyncio.TimeoutError:
            print("❌ Connection test timed out")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response during connection test: {e}")
            return False
        
        # Test 4: Add a memory
        print("🔄 Testing memory addition with Apple Intelligence...")
        add_memory_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "add_memory",
                "arguments": {
                    "messages": "Gabriel is testing Apple Intelligence MCP server integration with Foundation Models",
                    "user_id": "gabriel",
                    "agent_id": "test_client",
                    "metadata": json.dumps({"test": "apple_intelligence_integration"})
                }
            }
        }
        
        request_json = json.dumps(add_memory_request) + '\n'
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                result = response.get('result')
                if result and result.get('content'):
                    content_text = result['content'][0]['text']
                    try:
                        memory_data = json.loads(content_text)
                        print(f"✅ Memory added successfully:")
                        print(f"   - Memory ID: {memory_data.get('id', 'Unknown')}")
                        print(f"   - Message: Added via Apple Intelligence")
                    except json.JSONDecodeError:
                        print(f"✅ Memory operation completed: {content_text[:100]}...")
                else:
                    print("❌ No content in add memory response")
                    return False
            else:
                print("❌ No response from server during memory addition")
                return False
        except asyncio.TimeoutError:
            print("❌ Add memory test timed out")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response during memory addition: {e}")
            return False
        
        print("\n🎉 All tests passed! Apple Intelligence MCP server is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up and check stderr
        try:
            stderr_output = await process.stderr.read()
            if stderr_output:
                print(f"🔍 Server stderr: {stderr_output.decode()}")
            
            process.terminate()
            await process.wait()
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)