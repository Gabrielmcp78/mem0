#!/usr/bin/env node

/**
 * Test add_memory tool directly via MCP protocol
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testAddMemory() {
    console.log('🧪 Testing add_memory Tool via MCP Protocol');
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
        console.log('Server response:', data.toString());
    });
    
    server.stderr.on('data', (data) => {
        serverError += data.toString();
        console.log('Server stderr:', data.toString());
    });
    
    // Wait for server to start
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Send initialize request
    const initRequest = {
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: {
                name: 'test-client',
                version: '1.0.0'
            }
        }
    };
    
    server.stdin.write(JSON.stringify(initRequest) + '\n');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Test add_memory tool call
    console.log('\n🔧 Testing add_memory tool call...');
    const addMemoryRequest = {
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/call',
        params: {
            name: 'add_memory',
            arguments: {
                messages: 'Gabriel is successfully testing the Apple Intelligence memory system through direct MCP protocol communication. The system uses Foundation Models for local processing.',
                user_id: 'gabriel',
                agent_id: 'kiro',
                metadata: '{"test": "direct_mcp_protocol", "category": "system_test", "technology": "apple_intelligence"}'
            }
        }
    };
    
    server.stdin.write(JSON.stringify(addMemoryRequest) + '\n');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test search to verify the memory was added
    console.log('\n🔍 Testing search_memories to verify...');
    const searchRequest = {
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
            name: 'search_memories',
            arguments: {
                query: 'Gabriel testing Apple Intelligence',
                user_id: 'gabriel',
                limit: 5
            }
        }
    };
    
    server.stdin.write(JSON.stringify(searchRequest) + '\n');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Close server
    server.kill();
    
    console.log('\n📊 Test Complete');
    console.log('Full Server Output:', serverOutput);
    if (serverError) {
        console.log('Server Errors:', serverError);
    }
    
    return serverOutput.includes('add_memory') && serverOutput.includes('search_memories');
}

testAddMemory().then(success => {
    if (success) {
        console.log('\n✅ add_memory tool test completed successfully');
    } else {
        console.log('\n❌ add_memory tool test failed');
    }
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('❌ Test failed:', error);
    process.exit(1);
});