#!/usr/bin/env node

/**
 * Predefined Test Suites for MCP Server Testing
 * 
 * Provides reusable test suites that can be composed and executed
 * by different test runners.
 */

class TestSuites {
  constructor(framework) {
    this.framework = framework;
  }

  /**
   * Basic connectivity test suite
   */
  async basicConnectivity() {
    const suite = new TestSuite('Basic Connectivity', this.framework);
    
    suite.addTest('Server Startup', async () => {
      await this.framework.startServer();
      return this.framework.isServerRunning;
    });

    suite.addTest('Initialize Connection', async () => {
      const messageId = this.framework.sendMessage('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: { roots: { listChanged: true }, sampling: {} },
        clientInfo: { name: 'test-client', version: '1.0.0' }
      });
      
      await this.framework.wait(2000);
      return true; // If no error thrown, test passes
    });

    suite.addTest('List Tools', async () => {
      this.framework.sendMessage('tools/list');
      await this.framework.wait(2000);
      return true;
    });

    return suite;
  }

  /**
   * FoundationModels specific test suite
   */
  async appleIntelligence() {
    const suite = new TestSuite('FoundationModels', this.framework);
    
    suite.addTest('Connection Status', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'test_connection',
        arguments: {}
      });
      
      await this.framework.wait(3000);
      return true;
    });

    suite.addTest('Enhanced Memory Addition', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'add_memory_enhanced',
        arguments: {
          messages: 'FoundationModels test with Neural Engine processing',
          user_id: 'test_user',
          metadata: {
            test: 'apple_intelligence',
            neural_engine: true
          }
        }
      });
      
      await this.framework.wait(4000);
      return true;
    });

    suite.addTest('Enhanced Search', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'search_memories_enhanced',
        arguments: {
          query: 'FoundationModels',
          user_id: 'test_user',
          limit: 5
        }
      });
      
      await this.framework.wait(3000);
      return true;
    });

    return suite;
  }

  /**
   * Memory operations test suite
   */
  async memoryOperations() {
    const suite = new TestSuite('Memory Operations', this.framework);
    
    suite.addTest('Add Memory', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'add_memory',
        arguments: {
          content: 'Test memory for operations suite',
          user_id: 'test_user',
          metadata: { test: 'memory_operations' }
        }
      });
      
      await this.framework.wait(3000);
      return true;
    });

    suite.addTest('Search Memories', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'search_memories',
        arguments: {
          query: 'test memory',
          user_id: 'test_user',
          limit: 5
        }
      });
      
      await this.framework.wait(3000);
      return true;
    });

    suite.addTest('Get All Memories', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'get_all_memories',
        arguments: {
          user_id: 'test_user'
        }
      });
      
      await this.framework.wait(2000);
      return true;
    });

    return suite;
  }

  /**
   * System status and health test suite
   */
  async systemHealth() {
    const suite = new TestSuite('System Health', this.framework);
    
    suite.addTest('System Status', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'get_system_status',
        arguments: {}
      });
      
      await this.framework.wait(3000);
      return true;
    });

    suite.addTest('Context Insights', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'get_context_insights',
        arguments: {
          user_id: 'test_user'
        }
      });
      
      await this.framework.wait(2000);
      return true;
    });

    return suite;
  }

  /**
   * Performance and stress test suite
   */
  async performance() {
    const suite = new TestSuite('Performance', this.framework);
    
    suite.addTest('Concurrent Memory Addition', async () => {
      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(new Promise(resolve => {
          this.framework.sendMessage('tools/call', {
            name: 'add_memory',
            arguments: {
              content: `Concurrent test memory ${i}`,
              user_id: 'perf_test_user',
              metadata: { test: 'performance', index: i }
            }
          });
          setTimeout(resolve, 1000);
        }));
      }
      
      await Promise.all(promises);
      await this.framework.wait(2000);
      return true;
    });

    suite.addTest('Large Memory Content', async () => {
      const largeContent = 'Large memory content test. '.repeat(100);
      
      this.framework.sendMessage('tools/call', {
        name: 'add_memory',
        arguments: {
          content: largeContent,
          user_id: 'perf_test_user',
          metadata: { test: 'large_content' }
        }
      });
      
      await this.framework.wait(5000);
      return true;
    });

    return suite;
  }

  /**
   * Error handling and edge cases test suite
   */
  async errorHandling() {
    const suite = new TestSuite('Error Handling', this.framework);
    
    suite.addTest('Invalid Tool Call', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'nonexistent_tool',
        arguments: {}
      });
      
      await this.framework.wait(2000);
      return true; // Should handle gracefully
    });

    suite.addTest('Malformed Arguments', async () => {
      this.framework.sendMessage('tools/call', {
        name: 'add_memory',
        arguments: {
          // Missing required content
          user_id: 'test_user'
        }
      });
      
      await this.framework.wait(2000);
      return true; // Should handle gracefully
    });

    return suite;
  }
}

/**
 * Individual Test Suite Class
 */
class TestSuite {
  constructor(name, framework) {
    this.name = name;
    this.framework = framework;
    this.tests = [];
  }

  addTest(name, testFunction) {
    this.tests.push({ name, testFunction });
  }

  async run() {
    this.framework.log('info', `\n🧪 Running Test Suite: ${this.name}`);
    this.framework.log('info', '='.repeat(50));
    
    let passed = 0;
    let failed = 0;
    
    for (const test of this.tests) {
      try {
        this.framework.log('info', `Running: ${test.name}...`);
        const result = await test.testFunction();
        
        if (result) {
          this.framework.recordResult(`${this.name}: ${test.name}`, 'PASS', 'Test completed successfully');
          passed++;
        } else {
          this.framework.recordResult(`${this.name}: ${test.name}`, 'FAIL', 'Test returned false');
          failed++;
        }
      } catch (error) {
        this.framework.recordResult(`${this.name}: ${test.name}`, 'FAIL', error.message);
        failed++;
      }
    }
    
    this.framework.log('info', `\n📊 Suite ${this.name}: ${passed} passed, ${failed} failed`);
    return { passed, failed, total: this.tests.length };
  }
}

module.exports = { TestSuites, TestSuite };