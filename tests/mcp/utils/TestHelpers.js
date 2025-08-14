/**
 * Test Helper Utilities
 * 
 * Common utilities and helpers for MCP testing
 */

class TestHelpers {
  /**
   * Generate test user ID with timestamp
   */
  static generateTestUserId(prefix = 'test_user') {
    return `${prefix}_${Date.now()}`;
  }

  /**
   * Generate test memory content
   */
  static generateTestMemory(index = 0, category = 'general') {
    const memories = {
      general: [
        'This is a test memory for validation purposes',
        'Testing memory storage and retrieval functionality',
        'Validating semantic search capabilities',
        'Checking memory deduplication features',
        'Testing context understanding and analysis'
      ],
      apple_intelligence: [
        'FoundationModels provides on-device AI processing',
        'Neural Engine optimizes machine learning workloads',
        'Foundation Models enable natural language understanding',
        'Privacy-first AI with local processing capabilities',
        'Semantic analysis using FoundationModels frameworks'
      ],
      technical: [
        'Vector embeddings enable semantic similarity search',
        'Graph databases store entity relationships',
        'SQLite provides metadata and history tracking',
        'Qdrant offers high-performance vector operations',
        'Neo4j enables complex relationship queries'
      ]
    };
    
    const categoryMemories = memories[category] || memories.general;
    const baseMemory = categoryMemories[index % categoryMemories.length];
    
    return `${baseMemory} (Test #${index + 1})`;
  }

  /**
   * Generate test metadata
   */
  static generateTestMetadata(testName, additionalData = {}) {
    return {
      test: testName,
      timestamp: new Date().toISOString(),
      test_run_id: `run_${Date.now()}`,
      framework: 'mcp_test_framework',
      ...additionalData
    };
  }

  /**
   * Wait for a specific condition with timeout
   */
  static async waitForCondition(conditionFn, timeout = 5000, interval = 100) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      if (await conditionFn()) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    throw new Error(`Condition not met within ${timeout}ms`);
  }

  /**
   * Validate MCP response structure
   */
  static validateMCPResponse(response) {
    if (!response) {
      throw new Error('Response is null or undefined');
    }
    
    if (!response.jsonrpc || response.jsonrpc !== '2.0') {
      throw new Error('Invalid JSON-RPC version');
    }
    
    if (response.error) {
      throw new Error(`MCP Error: ${response.error.message || 'Unknown error'}`);
    }
    
    return true;
  }

  /**
   * Extract memory content from MCP response
   */
  static extractMemoryContent(response) {
    try {
      if (response.result && response.result.content) {
        const content = JSON.parse(response.result.content[0].text);
        return content;
      }
      return null;
    } catch (error) {
      throw new Error(`Failed to extract memory content: ${error.message}`);
    }
  }

  /**
   * Create test configuration for different scenarios
   */
  static createTestConfig(scenario = 'default') {
    const baseConfig = {
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
      }
    };

    const scenarios = {
      default: baseConfig,
      
      debug: {
        ...baseConfig,
        logResponses: true,
        logServerOutput: true,
        logServerErrors: true,
        logMessages: true,
        env: {
          ...baseConfig.env,
          LOG_LEVEL: 'debug'
        }
      },
      
      performance: {
        ...baseConfig,
        startupTimeout: 10000,
        responseTimeout: 10000,
        env: {
          ...baseConfig.env,
          OPERATION_TIMEOUT: '60000'
        }
      },
      
      minimal: {
        ...baseConfig,
        logResponses: false,
        logServerOutput: false,
        logServerErrors: false,
        logMessages: false,
        env: {
          ...baseConfig.env,
          LOG_LEVEL: 'error'
        }
      }
    };

    return scenarios[scenario] || baseConfig;
  }

  /**
   * Performance measurement utilities
   */
  static createPerformanceTracker() {
    const tracker = {
      startTime: null,
      measurements: [],
      
      start() {
        this.startTime = Date.now();
      },
      
      measure(label) {
        if (!this.startTime) {
          throw new Error('Performance tracker not started');
        }
        
        const duration = Date.now() - this.startTime;
        this.measurements.push({ label, duration, timestamp: new Date().toISOString() });
        return duration;
      },
      
      getResults() {
        return {
          measurements: this.measurements,
          totalDuration: this.measurements.length > 0 
            ? this.measurements[this.measurements.length - 1].duration 
            : 0
        };
      },
      
      reset() {
        this.startTime = null;
        this.measurements = [];
      }
    };
    
    return tracker;
  }

  /**
   * Memory cleanup utilities
   */
  static async cleanupTestMemories(framework, userId) {
    try {
      framework.sendMessage('tools/call', {
        name: 'clear_memories',
        arguments: { user_id: userId }
      });
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      return true;
    } catch (error) {
      console.warn(`Failed to cleanup test memories: ${error.message}`);
      return false;
    }
  }

  /**
   * Assertion utilities for test validation
   */
  static assert = {
    isTrue(condition, message = 'Assertion failed') {
      if (!condition) {
        throw new Error(message);
      }
    },
    
    isFalse(condition, message = 'Assertion failed') {
      if (condition) {
        throw new Error(message);
      }
    },
    
    equals(actual, expected, message = 'Values are not equal') {
      if (actual !== expected) {
        throw new Error(`${message}. Expected: ${expected}, Actual: ${actual}`);
      }
    },
    
    contains(array, item, message = 'Array does not contain item') {
      if (!Array.isArray(array) || !array.includes(item)) {
        throw new Error(message);
      }
    },
    
    hasProperty(object, property, message = 'Object does not have property') {
      if (!object || !object.hasOwnProperty(property)) {
        throw new Error(`${message}: ${property}`);
      }
    },
    
    isType(value, type, message = 'Type mismatch') {
      if (typeof value !== type) {
        throw new Error(`${message}. Expected: ${type}, Actual: ${typeof value}`);
      }
    }
  };
}

module.exports = TestHelpers;