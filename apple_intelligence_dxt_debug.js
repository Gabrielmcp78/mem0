#!/usr/bin/env node

/**
 * Debug version of apple-intelligence-dxt MCP server
 * REFACTORED: This file has been refactored into a modular architecture
 * 
 * The functionality has been moved to:
 * - integrations/mcp/core/mcp_server_base.js - Base MCP server functionality
 * - integrations/mcp/core/python_executor.js - Python script execution
 * - integrations/mcp/core/foundation_models_tools.js - Tool implementations
 * - integrations/mcp/apple_intelligence_dxt_server.js - Clean server implementation
 * 
 * For new development, use the modular components.
 * This file is maintained for backward compatibility only.
 */

// Import the refactored modular server
import { MCPServerBase } from './integrations/mcp/core/mcp_server_base.js';
import { PythonExecutor } from './integrations/mcp/core/python_executor.js';
import { FoundationModelsTools } from './integrations/mcp/core/foundation_models_tools.js';

class AppleIntelligenceDXTServer extends MCPServerBase {
  constructor() {
    console.error('⚠️  Using deprecated debug server - consider upgrading to modular implementation');
    console.error('   New server: integrations/mcp/apple_intelligence_dxt_server.js\n');
    
    super('apple-intelligence-dxt-debug', '0.1.0');
    
    // Initialize components using modular architecture
    this.pythonExecutor = new PythonExecutor();
    this.foundationModelsTools = new FoundationModelsTools(this.pythonExecutor);
    
    // Register tools
    this.registerFoundationModelsTools();
  }

  registerFoundationModelsTools() {
    const tools = this.foundationModelsTools.getToolDefinitions();
    
    for (const tool of tools) {
      this.registerTool(
        tool.name,
        tool.description,
        tool.inputSchema,
        tool.handler
      );
    }
  }
}

async function main() {
  console.error("=" * 60);
  console.error("DEPRECATION NOTICE");
  console.error("=" * 60);
  console.error("This debug server has been refactored into a modular architecture.");
  console.error("Please use the new modular server:");
  console.error("  integrations/mcp/apple_intelligence_dxt_server.js");
  console.error("");
  console.error("Running with deprecated interface...");
  console.error("=" * 60);
  console.error("");
  
  const server = new AppleIntelligenceDXTServer();
  await server.run();
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});