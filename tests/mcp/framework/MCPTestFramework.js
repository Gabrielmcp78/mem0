#!/usr/bin/env node

/**
 * Modular MCP Test Framework
 * 
 * Provides a reusable framework for testing MCP servers with:
 * - Server lifecycle management
 * - Message handling
 * - Test result tracking
 * - Cleanup utilities
 */

const { spawn } = require('child_process');
const readline = require('readline');
const { EventEmitter } = require('events');

class MCPTestFramework extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      serverPath: 'integrations/mcp/mem0_enhanced_server.cjs',
      startupTimeout: 5000,
      responseTimeout: 3000,
      env: {
        PYTHONPATH: '/Volumes/Ready500/DEVELOPMENT/mem0',
        PYTHON_EXECUTABLE: 'python3',
        APPLE_INTELLIGENCE_ENABLED: 'true',
        NEO4J_PASSWORD: 'password',
        OPERATION_TIMEOUT: '30000',
        MAX_RETRIES: '2',
        LOG_LEVEL: 'info'
      },
      ...config
    };
    
    this.serverProcess = null;
    this.messageId = 1;
    this.testResults = [];
    this.isServerRunning = false;
  }

  /**
   * Start the MCP server
   */
  async startServer() {
    if (this.isServerRunning) {
      throw new Error('Server is already running');
    }

    this.log('info', '🚀 Starting MCP Server...');
    
    return new Promise((resolve, reject) => {
      this.serverProcess = spawn('node', [this.config.serverPath], {
        env: { ...process.env, ...this.config.env },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Set up output handling
      this.setupOutputHandling();

      // Handle process errors
      this.serverProcess.on('error', (error) => {
        this.log('error', `Server process error: ${error.message}`);
        reject(error);
      });

      // Wait for server to start
      setTimeout(() => {
        if (this.serverProcess && !this.serverProcess.killed) {
          this.isServerRunning = true;
          this.log('info', '✅ Server started successfully');
          this.emit('serverStarted');
          resolve();
        } else {
          reject(new Error('Server failed to start'));
        }
      }, this.config.startupTimeout);
    });
  }

  /**
   * Set up output handling for server process
   */
  setupOutputHandling() {
    const rl = readline.createInterface({
      input: this.serverProcess.stdout,
      crlfDelay: Infinity
    });

    rl.on('line', (line) => {
      try {
        const response = JSON.parse(line);
        this.emit('serverResponse', response);
        if (this.config.logResponses) {
          this.log('response', JSON.stringify(response, null, 2));
        }
      } catch (e) {
        this.emit('serverLog', line);
        if (this.config.logServerOutput) {
          this.log('server', line);
        }
      }
    });

    this.serverProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      this.emit('serverError', message);
      if (this.config.logServerErrors) {
        this.log('debug', message);
      }
    });
  }

  /**
   * Send a message to the server
   */
  sendMessage(method, params = {}) {
    if (!this.isServerRunning) {
      throw new Error('Server is not running');
    }

    const message = {
      jsonrpc: '2.0',
      id: this.messageId++,
      method: method,
      params: params
    };

    if (this.config.logMessages) {
      this.log('send', JSON.stringify(message, null, 2));
    }

    this.serverProcess.stdin.write(JSON.stringify(message) + '\n');
    this.emit('messageSent', message);
    
    return message.id;
  }

  /**
   * Wait for a specific amount of time
   */
  async wait(ms = this.config.responseTimeout) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Stop the server
   */
  async stopServer() {
    if (!this.isServerRunning) {
      return;
    }

    this.log('info', '🛑 Stopping server...');
    
    if (this.serverProcess && !this.serverProcess.killed) {
      this.serverProcess.kill('SIGTERM');
      
      // Wait for graceful shutdown
      await this.wait(2000);
      
      if (!this.serverProcess.killed) {
        this.serverProcess.kill('SIGKILL');
      }
    }
    
    this.isServerRunning = false;
    this.log('info', '✅ Server stopped');
    this.emit('serverStopped');
  }

  /**
   * Record a test result
   */
  recordResult(testName, status, message = '', details = {}) {
    const result = {
      test: testName,
      status: status, // 'PASS', 'FAIL', 'SKIP'
      message: message,
      timestamp: new Date().toISOString(),
      ...details
    };
    
    this.testResults.push(result);
    this.emit('testResult', result);
    
    const emoji = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏭️';
    this.log('result', `${emoji} ${testName}: ${message}`);
    
    return result;
  }

  /**
   * Get test results summary
   */
  getResultsSummary() {
    const passed = this.testResults.filter(r => r.status === 'PASS').length;
    const failed = this.testResults.filter(r => r.status === 'FAIL').length;
    const skipped = this.testResults.filter(r => r.status === 'SKIP').length;
    
    return {
      total: this.testResults.length,
      passed,
      failed,
      skipped,
      results: this.testResults
    };
  }

  /**
   * Print test results
   */
  printResults() {
    const summary = this.getResultsSummary();
    
    this.log('info', '\n📊 TEST RESULTS SUMMARY');
    this.log('info', '========================');
    
    summary.results.forEach(result => {
      const emoji = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⏭️';
      this.log('info', `${emoji} ${result.test}: ${result.message}`);
    });
    
    this.log('info', `\n📈 SUMMARY: ${summary.passed} passed, ${summary.failed} failed, ${summary.skipped} skipped`);
    
    if (summary.failed === 0) {
      this.log('info', '🎉 ALL TESTS PASSED!');
    } else {
      this.log('error', '⚠️ Some tests failed. Please review and fix issues.');
    }
    
    return summary;
  }

  /**
   * Clean up resources
   */
  async cleanup() {
    this.log('info', '🧹 Cleaning up...');
    await this.stopServer();
    this.removeAllListeners();
    this.log('info', '✅ Cleanup completed');
  }

  /**
   * Logging utility
   */
  log(level, message) {
    const timestamp = new Date().toISOString();
    const levelEmoji = {
      info: 'ℹ️',
      error: '❌',
      warn: '⚠️',
      debug: '🔍',
      send: '📤',
      response: '📨',
      server: '📝',
      result: '📊'
    };
    
    console.log(`[${timestamp}] ${levelEmoji[level] || '📝'} ${message}`);
  }
}

module.exports = MCPTestFramework;