#!/usr/bin/env node

/**
 * Comprehensive Test Runner
 * 
 * Runs all test suites for complete system validation
 */

const MCPTestFramework = require('../framework/MCPTestFramework');
const { TestSuites } = require('../framework/TestSuites');

class ComprehensiveTestRunner {
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

  async runAllTests() {
    this.framework.log('info', '🚀 Comprehensive MCP Server Test Suite');
    this.framework.log('info', '======================================');
    
    try {
      // Start server
      await this.framework.startServer();
      
      // Run all test suites
      const suites = [
        { name: 'Basic Connectivity', suite: await this.testSuites.basicConnectivity() },
        { name: 'FoundationModels', suite: await this.testSuites.appleIntelligence() },
        { name: 'Memory Operations', suite: await this.testSuites.memoryOperations() },
        { name: 'System Health', suite: await this.testSuites.systemHealth() },
        { name: 'Performance', suite: await this.testSuites.performance() },
        { name: 'Error Handling', suite: await this.testSuites.errorHandling() }
      ];
      
      const results = [];
      let totalPassed = 0;
      let totalFailed = 0;
      
      for (const { name, suite } of suites) {
        this.framework.log('info', `\n🔄 Starting ${name} Test Suite...`);
        const result = await suite.run();
        results.push({ name, ...result });
        totalPassed += result.passed;
        totalFailed += result.failed;
      }
      
      // Print comprehensive summary
      this.printComprehensiveSummary(results, totalPassed, totalFailed);
      
      return totalFailed === 0;
      
    } catch (error) {
      this.framework.log('error', `Comprehensive test runner error: ${error.message}`);
      return false;
    } finally {
      await this.framework.cleanup();
    }
  }

  printComprehensiveSummary(results, totalPassed, totalFailed) {
    this.framework.log('info', '\n📊 COMPREHENSIVE TEST RESULTS');
    this.framework.log('info', '==============================');
    
    // Suite-by-suite breakdown
    results.forEach(result => {
      const status = result.failed === 0 ? '✅' : '❌';
      this.framework.log('info', `${status} ${result.name}: ${result.passed}/${result.total} passed`);
    });
    
    this.framework.log('info', '\n📈 OVERALL SUMMARY');
    this.framework.log('info', `Total Tests: ${totalPassed + totalFailed}`);
    this.framework.log('info', `Passed: ${totalPassed}`);
    this.framework.log('info', `Failed: ${totalFailed}`);
    this.framework.log('info', `Success Rate: ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`);
    
    if (totalFailed === 0) {
      this.framework.log('info', '\n🎉 ALL TESTS PASSED!');
      this.framework.log('info', '✅ Enhanced MCP Server is production ready');
      this.framework.log('info', '🍎 FoundationModels integration confirmed');
      this.framework.log('info', '🧠 Memory operations working correctly');
      this.framework.log('info', '⚡ Performance within acceptable limits');
      this.framework.log('info', '🛡️ Error handling robust');
    } else {
      this.framework.log('error', '\n⚠️ SOME TESTS FAILED');
      this.framework.log('error', 'Please review failed tests and fix issues before deployment');
      
      // Show which suites failed
      const failedSuites = results.filter(r => r.failed > 0);
      if (failedSuites.length > 0) {
        this.framework.log('error', '\nFailed Test Suites:');
        failedSuites.forEach(suite => {
          this.framework.log('error', `  ❌ ${suite.name}: ${suite.failed} failures`);
        });
      }
    }
  }

  async runQuickTest() {
    this.framework.log('info', '⚡ Quick Test Suite');
    this.framework.log('info', '==================');
    
    try {
      await this.framework.startServer();
      
      // Run only essential tests
      const suites = [
        await this.testSuites.basicConnectivity(),
        await this.testSuites.appleIntelligence()
      ];
      
      let totalPassed = 0;
      let totalFailed = 0;
      
      for (const suite of suites) {
        const result = await suite.run();
        totalPassed += result.passed;
        totalFailed += result.failed;
      }
      
      this.framework.log('info', `\n⚡ Quick Test Results: ${totalPassed}/${totalPassed + totalFailed} passed`);
      return totalFailed === 0;
      
    } catch (error) {
      this.framework.log('error', `Quick test error: ${error.message}`);
      return false;
    } finally {
      await this.framework.cleanup();
    }
  }
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const runner = new ComprehensiveTestRunner();
  
  if (args.includes('--quick')) {
    runner.runQuickTest()
      .then(success => process.exit(success ? 0 : 1))
      .catch(error => {
        console.error('Quick test failed:', error);
        process.exit(1);
      });
  } else {
    runner.runAllTests()
      .then(success => process.exit(success ? 0 : 1))
      .catch(error => {
        console.error('Comprehensive test failed:', error);
        process.exit(1);
      });
  }
}

module.exports = ComprehensiveTestRunner;