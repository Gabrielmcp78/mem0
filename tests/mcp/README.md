# MCP Server Testing Framework

A comprehensive, modular testing framework for MCP (Model Context Protocol) servers with specific support for FoundationModels integration.

## Architecture

The testing framework is organized into several modular components:

```
tests/mcp/
├── framework/
│   ├── MCPTestFramework.js    # Core testing framework
│   └── TestSuites.js          # Reusable test suites
├── runners/
│   ├── AppleIntelligenceTestRunner.js    # FoundationModels specific tests
│   └── ComprehensiveTestRunner.js        # All test suites
├── utils/
│   └── TestHelpers.js         # Utility functions and helpers
└── README.md                  # This file
```

## Quick Start

### Run All Tests
```bash
node run_tests.js
```

### Run Quick Tests
```bash
node run_tests.js quick
```

### Run FoundationModels Tests Only
```bash
node run_tests.js apple-intelligence
```

### Debug Mode
```bash
node run_tests.js all --debug
```

## Framework Components

### MCPTestFramework

The core framework provides:
- Server lifecycle management (start/stop)
- Message handling and protocol communication
- Event-driven architecture with listeners
- Test result tracking and reporting
- Automatic cleanup and resource management

```javascript
const MCPTestFramework = require('./framework/MCPTestFramework');

const framework = new MCPTestFramework({
  serverPath: 'path/to/server.js',
  logResponses: true
});

await framework.startServer();
framework.sendMessage('tools/list');
await framework.stopServer();
```

### TestSuites

Predefined test suites for common scenarios:
- **Basic Connectivity**: Server startup, initialization, tool listing
- **FoundationModels**: AI-specific features and capabilities
- **Memory Operations**: Add, search, retrieve memory operations
- **System Health**: Status checks and health monitoring
- **Performance**: Load testing and response time validation
- **Error Handling**: Edge cases and error scenarios

```javascript
const { TestSuites } = require('./framework/TestSuites');

const testSuites = new TestSuites(framework);
const suite = await testSuites.appleIntelligence();
const results = await suite.run();
```

### Test Runners

Specialized runners for different testing scenarios:

#### AppleIntelligenceTestRunner
Focused on FoundationModels features:
- Foundation Models integration
- Neural Engine processing
- On-device AI capabilities
- Semantic analysis validation

#### ComprehensiveTestRunner
Runs all test suites for complete validation:
- Full system integration testing
- Performance benchmarking
- Error handling validation
- Comprehensive reporting

### TestHelpers

Utility functions for common testing tasks:
- Test data generation
- Performance measurement
- Memory cleanup
- Assertion utilities
- Configuration management

```javascript
const TestHelpers = require('./utils/TestHelpers');

const userId = TestHelpers.generateTestUserId();
const memory = TestHelpers.generateTestMemory(0, 'apple_intelligence');
const metadata = TestHelpers.generateTestMetadata('test_name');
```

## Test Suites

### Basic Connectivity
- Server startup validation
- MCP protocol initialization
- Tool listing and availability

### FoundationModels
- Connection status verification
- Enhanced memory operations
- Semantic analysis capabilities
- Neural Engine processing

### Memory Operations
- Memory addition and storage
- Semantic search functionality
- Memory retrieval and listing
- Metadata handling

### System Health
- System status monitoring
- Context insights generation
- Health check validation

### Performance
- Concurrent operation handling
- Large content processing
- Response time measurement
- Resource usage monitoring

### Error Handling
- Invalid tool calls
- Malformed arguments
- Network error scenarios
- Graceful degradation

## Configuration

### Environment Variables
```bash
PYTHONPATH=/path/to/mem0
PYTHON_EXECUTABLE=python3
APPLE_INTELLIGENCE_ENABLED=true
NEO4J_PASSWORD=password
OPERATION_TIMEOUT=30000
MAX_RETRIES=2
LOG_LEVEL=info
```

### Test Configuration
```javascript
const config = {
  serverPath: 'integrations/mcp/mem0_enhanced_server.cjs',
  startupTimeout: 5000,
  responseTimeout: 3000,
  logResponses: false,
  logServerOutput: false,
  logServerErrors: true,
  env: { /* environment variables */ }
};
```

## Usage Examples

### Custom Test Suite
```javascript
const MCPTestFramework = require('./framework/MCPTestFramework');
const { TestSuite } = require('./framework/TestSuites');

const framework = new MCPTestFramework();
const suite = new TestSuite('Custom Tests', framework);

suite.addTest('Custom Test', async () => {
  framework.sendMessage('tools/call', {
    name: 'custom_tool',
    arguments: { test: true }
  });
  
  await framework.wait(2000);
  return true;
});

await framework.startServer();
const results = await suite.run();
await framework.cleanup();
```

### Performance Testing
```javascript
const TestHelpers = require('./utils/TestHelpers');

const tracker = TestHelpers.createPerformanceTracker();
tracker.start();

// Perform operations
tracker.measure('Operation 1');
tracker.measure('Operation 2');

const results = tracker.getResults();
console.log('Performance results:', results);
```

## Best Practices

1. **Use Modular Components**: Leverage existing test suites and helpers
2. **Clean Up Resources**: Always call cleanup methods
3. **Handle Errors Gracefully**: Use try-catch blocks and proper error handling
4. **Use Appropriate Timeouts**: Configure timeouts based on operation complexity
5. **Log Appropriately**: Use debug mode for development, minimal for CI/CD
6. **Test Isolation**: Each test should be independent and not rely on others
7. **Performance Awareness**: Monitor test execution times and resource usage

## Extending the Framework

### Adding New Test Suites
```javascript
// In TestSuites.js
async customTestSuite() {
  const suite = new TestSuite('Custom Suite', this.framework);
  
  suite.addTest('Test Name', async () => {
    // Test implementation
    return true;
  });
  
  return suite;
}
```

### Creating Custom Runners
```javascript
class CustomTestRunner {
  constructor(config) {
    this.framework = new MCPTestFramework(config);
    this.testSuites = new TestSuites(this.framework);
  }
  
  async runCustomTests() {
    await this.framework.startServer();
    // Run custom test logic
    await this.framework.cleanup();
  }
}
```

## Troubleshooting

### Common Issues

1. **Server Won't Start**: Check environment variables and server path
2. **Tests Timeout**: Increase timeout values or check server performance
3. **Connection Errors**: Verify database services are running
4. **FoundationModels Not Available**: Ensure macOS 15.1+ and Apple Silicon

### Debug Mode
Enable debug mode for detailed logging:
```bash
node run_tests.js all --debug
```

### Manual Testing
For manual testing and debugging:
```javascript
const framework = new MCPTestFramework({ logResponses: true });
await framework.startServer();

// Manual message sending
framework.sendMessage('tools/list');
await framework.wait(2000);

await framework.cleanup();
```

## Contributing

When adding new tests or features:
1. Follow the modular architecture
2. Add appropriate error handling
3. Include documentation and examples
4. Test with both debug and minimal modes
5. Ensure cleanup is properly handled