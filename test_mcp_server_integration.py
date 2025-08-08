#!/usr/bin/env python3
"""
Test MCP Server Integration

This script tests the MCP server directly to ensure it works with Apple Intelligence.
"""

import sys
import os
import json
import asyncio
import logging

# Add project path
sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0')

from mem0.client.main import MemoryClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-test")

async def test_mcp_server():
    """Test the MCP server initialization and basic functionality"""
    print("🚀 Testing MCP Server with Apple Intelligence...")
    
    try:
        # Import the MCP server
        sys.path.append('/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp')
        from server import Mem0MCPServer
        
        # Create server instance
        server = Mem0MCPServer()
        
        print(f"Server created: {server is not None}")
        print(f"Memory initialized: {server.memory is not None}")
        
        if server.memory:
            # Check actual providers
            llm_class = server.memory.llm.__class__.__name__ if hasattr(server.memory, 'llm') else 'Unknown'
            # Try different ways to get embedder class name
            embedder_class = 'Unknown'
            if hasattr(server.memory, 'embedder'):
                embedder_class = server.memory.embedder.__class__.__name__
            elif hasattr(server.memory, 'embedding_model'):
                embedder_class = server.memory.embedding_model.__class__.__name__
            print(f"Actual LLM provider: {llm_class}")
            print(f"Actual Embedder provider: {embedder_class}")
            
            # Test if Apple Intelligence providers are being used
            apple_intelligence_llm = 'AppleIntelligence' in llm_class
            apple_intelligence_embedder = 'AppleIntelligence' in embedder_class
            
            print(f"Using Apple Intelligence LLM: {apple_intelligence_llm}")
            print(f"Using Apple Intelligence Embedder: {apple_intelligence_embedder}")
            
            return apple_intelligence_llm and apple_intelligence_embedder
        
        return False
        
    except Exception as e:
        print(f"Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    async def test_add_memory():
        """Test the add method of MemoryClient"""
        print("\n🧪 Testing add() method...")
        try:
            # Create a MemoryClient instance
            client = MemoryClient(api_key="test_api_key")  # Replace with a valid API key if needed
    
            # Define a user request and messages
            user_request = "This is a test request."
            messages = [{"role": "user", "content": "Hello"}]
    
            # Call the add method
            response = await client.add(messages, user_request=user_request)
    
            # Verify the response (example: check if the response is not None)
            print(f"Add method response: {response}")
            return response is not None
    
        except Exception as e:
            print(f"Error testing add() method: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_claude_desktop_config():
        """Test Claude Desktop configuration"""
    print("\n📋 Testing Claude Desktop configuration...")
    
    try:
        # Check if the config file exists
        config_path = "/Volumes/Ready500/DEVELOPMENT/mem0/claude-desktop-config-ready.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("Claude Desktop config found:")
            print(json.dumps(config, indent=2))
            
            # Check if MCP server is configured
            mcp_servers = config.get("mcpServers", {})
            gabriel_memory = mcp_servers.get("gabriel-local-memory", {}) or mcp_servers.get("gabriel-apple-intelligence-memory", {})
            
            if gabriel_memory:
                print("Gabriel local memory MCP server is configured")
                command = gabriel_memory.get("command")
                args = gabriel_memory.get("args", [])
                print(f"Command: {command}")
                print(f"Args: {args}")
                
                # Check if the server script exists
                if args and len(args) > 0:
                    server_script = args[0]
                    if os.path.exists(server_script):
                        print(f"Server script exists: {server_script}")
                        return True
                    else:
                        print(f"Server script not found: {server_script}")
                        return False
            else:
                print("Gabriel local memory MCP server not configured")
                return False
        else:
            print(f"Claude Desktop config not found: {config_path}")
            return False
            
    except Exception as e:
        print(f"Error checking Claude Desktop config: {e}")
        return False

    def test_claude_desktop_config():
        """Test Claude Desktop configuration"""
    print("\n📋 Testing Claude Desktop configuration...")
    
    try:
        # Check if the config file exists
        config_path = "/Volumes/Ready500/DEVELOPMENT/mem0/claude-desktop-config-ready.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("Claude Desktop config found:")
            print(json.dumps(config, indent=2))
            
            # Check if MCP server is configured
            mcp_servers = config.get("mcpServers", {})
            gabriel_memory = mcp_servers.get("gabriel-local-memory", {}) or mcp_servers.get("gabriel-apple-intelligence-memory", {})
            
            if gabriel_memory:
                print("Gabriel local memory MCP server is configured")
                command = gabriel_memory.get("command")
                args = gabriel_memory.get("args", [])
                print(f"Command: {command}")
                print(f"Args: {args}")
                
                # Check if the server script exists
                if args and len(args) > 0:
                    server_script = args[0]
                    if os.path.exists(server_script):
                        print(f"Server script exists: {server_script}")
                        return True
                    else:
                        print(f"Server script not found: {server_script}")
                        return False
            else:
                print("Gabriel local memory MCP server not configured")
                return False
        else:
            print(f"Claude Desktop config not found: {config_path}")
            return False
            
    except Exception as e:
        print(f"Error checking Claude Desktop config: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting MCP Server Integration Tests\n")
    
    # Test 1: MCP Server initialization
    server_ok = asyncio.run(test_mcp_server())
    
    # Test 2: Claude Desktop configuration
    config_ok = test_claude_desktop_config()
    add_memory_ok = asyncio.run(test_add_memory())
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"MCP Server with Apple Intelligence: {'✅' if server_ok else '❌'}")
    print(f"Claude Desktop Configuration: {'✅' if config_ok else '❌'}")
    
    all_tests_passed = all([server_ok, config_ok])
    print(f"\nOverall Status: {'✅ All tests passed!' if all_tests_passed else '❌ Some tests failed'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)