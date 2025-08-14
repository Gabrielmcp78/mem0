#!/usr/bin/env node

/**
 * FoundationModels Specific Test Runner
 * 
 * Focused test runner for FoundationModels features using the modular framework
 */

const MCPTestFramework = require('../framework/MCPTestFramework');
const { TestSuites } = require('../framework/TestSuites');

class AppleIntelligenceTestRunner {
  constructor(config = {}) {
    this.config = {
      serverPath: 'integrations/mcp/mem0_enhanced_server.cjs',
      logResponses: false,
      logServerOutput: false,
      logServerErrors: true,
      logMessages: false,
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
    
    this.framework = new MCPTestFramework(this.config);
    this.testSuites = new TestSuites(this.framework);
  }

  async runAppleIntelligenceTests() {
    this.framework.log('info', '🍎 FoundationModels Test Runner');
    this.framework.log('info', '================================');
    
    try {
      // Start server
      await this.framework.startServer();
      
      // Set up FoundationModels specific event handlers
      this.setupAppleIntelligenceHandlers();
      
      // Run test suites in sequence
      const suites = [
        await this.testSuites.basicConnectivity(),
        await this.testSuites.appleIntelligence(),
        await this.testSuites.memoryOperations(),
        await this.testSuites.systemHealth()
      ];
      
      let totalPassed = 0;
      let totalFailed = 0;
      
      for (const suite of suites) {
        const result = await suite.run();
        totalPassed += result.passed;
        totalFailed += result.failed;
      }
      
      // Print final results
      this.framework.log('info', '\n🎯 FoundationModels TEST SUMMARY');
      this.framework.log('info', '===================================');
      this.framework.log('info', `Total Tests: ${totalPassed + totalFailed}`);
      this.framework.log('info', `Passed: ${totalPassed}`);
      this.framework.log('info', `Failed: ${totalFailed}`);
      
      if (totalFailed === 0) {
        this.framework.log('info', '🎉 All FoundationModels tests PASSED!');
        this.framework.log('info', '✅ FoundationModels integration is working correctly');
      } else {
        this.framework.log('error', '⚠️ Some FoundationModels tests failed');
      }
      
      return totalFailed === 0;
      
    } catch (error) {
      this.framework.log('error', `Test runner error: ${error.message}`);
      return false;
    } finally {
      await this.framework.cleanup();
    }
  }

  setupAppleIntelligenceHandlers() {
    // Listen for FoundationModels specific responses
    this.framework.on('serverResponse', (response) => {
      if (response.result && response.result.content) {
        try {
          const content = JSON.parse(response.result.content[0].text);
          if (content.apple_intelligence_status) {
            this.framework.log('info', '🍎 FoundationModels Status Detected:');
            this.framework.log('info', `  Connected: ${content.apple_intelligence_status.apple_intelligence}`);
            this.framework.log('info', `  Foundation Models: ${content.apple_intelligence_status.foundation_models}`);
            this.framework.log('info', `  Status: ${content.apple_intelligence_status.status}`);
            if (content.apple_intelligence_status.neural_engine) {
              this.framework.log('info', '  🧠 Neural Engine: Active');
            }
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    });

    this.framework.on('serverError', (message) => {
      if (message.includes('FoundationModels Status: connected')) {
        this.framework.log('info', '✅ FoundationModels Connected Successfully!');
      }
      if (message.includes('Neural Engine')) {
        this.framework.log('info', '✅ Neural Engine Processing Confirmed!');
      }
    });
  }
}

// Run if called directly
if (require.main === module) {
  const runner = new AppleIntelligenceTestRunner();
  runner.runAppleIntelligenceTests()
    .then(success => process.exit(success ? 0 : 1))
    .catch(error => {
      console.error('Test runner failed:', error);
      process.exit(1);
    });
}

module.exports = AppleIntelligenceTestRunner;