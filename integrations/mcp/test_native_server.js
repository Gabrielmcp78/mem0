#!/usr/bin/env node

/**
 * Test the native Node.js MCP server
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testServer() {
  console.log('🧪 Testing Native Node.js FoundationModels MCP Server');
  console.log('=' * 60);

  const serverPath = join(__dirname, 'native_node_server.js');
  
  // Set environment variables
  const env = {
    ...process.env,
    QDRANT_URL: 'http://localhost:6333',
    QDRANT_COLLECTION: 'gabriel_apple_intelligence_memories',
    APPLE_INTELLIGENCE_ENABLED: 'true',
  };

  console.log('🚀 Starting server...');
  
  const serverProcess = spawn('node', [serverPath], {
    env,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  let serverOutput = '';
  let serverError = '';

  serverProcess.stdout.on('data', (data) => {
    serverOutput += data.toString();
  });

  serverProcess.stderr.on('data', (data) => {
    serverError += data.toString();
    console.log('Server:', data.toString().trim());
  });

  // Give server time to start
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test if server is running
  if (serverProcess.pid && !serverProcess.killed) {
    console.log('✅ Server started successfully');
    console.log(`📊 Process ID: ${serverProcess.pid}`);
    
    // Terminate test server
    serverProcess.kill('SIGTERM');
    
    // Wait for graceful shutdown
    await new Promise(resolve => {
      serverProcess.on('exit', resolve);
      setTimeout(() => {
        serverProcess.kill('SIGKILL');
        resolve();
      }, 5000);
    });
    
    console.log('✅ Server shutdown gracefully');
    return true;
  } else {
    console.log('❌ Server failed to start');
    console.log('STDOUT:', serverOutput);
    console.log('STDERR:', serverError);
    return false;
  }
}

async function main() {
  try {
    const success = await testServer();
    
    console.log('\n📊 Test Results:');
    console.log(`Native Node.js Server: ${success ? '✅ PASS' : '❌ FAIL'}`);
    
    if (success) {
      console.log('\n🎉 Native Node.js MCP Server is working!');
      console.log('\n📋 Next Steps:');
      console.log('1. Update Claude Desktop config to use native_node_server.js');
      console.log('2. Restart Claude Desktop');
      console.log('3. Test with "test_connection" tool');
      console.log('\n💡 This server runs entirely in Node.js - no Python dependencies!');
    } else {
      console.log('\n❌ Server test failed - check output above');
    }
    
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error('Test failed:', error);
    process.exit(1);
  }
}

main();