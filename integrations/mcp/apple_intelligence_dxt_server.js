#!/usr/bin/env node

/**
 * Apple Intelligence DXT MCP Server - Modular Implementation
 * Clean, focused server implementation using modular components
 */

import { MCPServerBase } from './core/mcp_server_base.js';
import { PythonExecutor } from './core/python_executor.js';
import { FoundationModelsTools } from './core/foundation_models_tools.js';

class AppleIntelligenceDXTServer extends MCPServerBase {
  constructor() {
    super('apple-intelligence-dxt', '0.1.0');
    
    // Initialize components
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
  const server = new AppleIntelligenceDXTServer();
  await server.run();
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});