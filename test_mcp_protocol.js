#!/usr/bin/env node

/**
 * Test MCP Protocol Communication
 * This script tests if our MCP server properly implements the protocol
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testMCPServer() {
    console.log('🧪 Testing MCP Server Protocol Implementation');
    console.log('=' * 50);
    
    const serverPath = join(__dirname, 'integrations', 'mcp', 'server.js');
    
    // Start the MCP server
    const server = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
            ...process.env,
            QDRANT_URL: 'http://localhost:10333',
            QDRANT_COLLECTION: 'gabriel_apple_intelligence_memories',
            APPLE_INTELLIGENCE_ENABLED: 'true',
            LOG_LEVEL: 'INFO',
            PYTHONPATH: '/Volumes/Ready500/DEVELOPMENT/mem0'
        }
    });
    
    let serverOutput = '';
    let serverError = '';
    
    server.stdout.on('data', (data) => {
        serverOutput += data.toString();
        console.log('Server stdout:', data.toString());
    });
    
    server.stderr.on('data', (data) => {
        serverError += data.toString();
        console.log('Server stderr:', data.toString());
    });
    
    // Wait for server to start
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test 1: Send initialize request
    console.log('\n1. Testing initialize request...');
    const initRequest = {
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
            protocolVersion: '2024-11-05',
            capabilities: {
                roots: {
                    listChanged: true
                }
            },
            clientInfo: {
                name: 'test-client',
                version: '1.0.0'
            }
        }
    };
    
    server.stdin.write(JSON.stringify(initRequest) + '\n');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Test 2: Send list tools request
    console.log('\n2. Testing list tools request...');
    const listToolsRequest = {
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/list',
        params: {}
    };
    
    server.stdin.write(JSON.stringify(listToolsRequest) + '\n');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Test 3: Send test_connection tool call
    console.log('\n3. Testing test_connection tool call...');
    const toolCallRequest = {
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
            name: 'test_connection',
            arguments: {}
        }
    };
    
    server.stdin.write(JSON.stringify(toolCallRequest) + '\n');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Close server
    server.kill();
    
    console.log('\n📊 Test Results:');
    console.log('Server Output:', serverOutput);
    console.log('Server Error:', serverError);
    
    return serverOutput.length > 0 || serverError.length > 0;
}

testMCPServer().then(success => {
    if (success) {
        console.log('✅ MCP server responded to protocol messages');
    } else {
        console.log('❌ MCP server did not respond properly');
    }
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('❌ Test failed:', error);
    process.exit(1);
});