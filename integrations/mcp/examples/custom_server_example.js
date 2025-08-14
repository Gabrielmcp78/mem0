#!/usr/bin/env node

/**
 * Example: Custom MCP Server using modular components
 * Demonstrates how to create a custom server with additional tools
 */

import { MCPServerBase } from '../core/mcp_server_base.js';
import { PythonExecutor } from '../core/python_executor.js';
import { FoundationModelsTools } from '../core/foundation_models_tools.js';

class CustomMCPServer extends MCPServerBase {
  constructor() {
    super('custom-mcp-server', '1.0.0');
    
    // Initialize components
    this.pythonExecutor = new PythonExecutor();
    this.foundationModelsTools = new FoundationModelsTools(this.pythonExecutor);
    
    // Register all tools
    this.registerFoundationModelsTools();
    this.registerCustomTools();
  }

  registerFoundationModelsTools() {
    // Register standard Foundation Models tools
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

  registerCustomTools() {
    // Add custom tools
    this.registerTool(
      'system_info',
      'Get system information',
      {
        type: 'object',
        properties: {
          detailed: {
            type: 'boolean',
            description: 'Include detailed system information',
            default: false
          }
        }
      },
      this.getSystemInfo.bind(this)
    );

    this.registerTool(
      'echo',
      'Echo back the input message',
      {
        type: 'object',
        properties: {
          message: {
            type: 'string',
            description: 'Message to echo back'
          }
        },
        required: ['message']
      },
      this.echo.bind(this)
    );
  }

  async getSystemInfo(args) {
    const { detailed = false } = args;
    
    try {
      const script = `
import sys
import json
import platform
from datetime import datetime

info = {
    "platform": platform.system(),
    "platform_version": platform.version(),
    "python_version": sys.version,
    "architecture": platform.machine(),
    "timestamp": datetime.now().isoformat()
}

${detailed ? `
info.update({
    "processor": platform.processor(),
    "node": platform.node(),
    "release": platform.release(),
    "python_implementation": platform.python_implementation(),
    "python_compiler": platform.python_compiler()
})
` : ''}

print(json.dumps(info, indent=2))
`;

      const result = await this.pythonExecutor.executeScript(
        script,
        'System Info',
        5000
      );

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `System info failed: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }

  async echo(args) {
    const { message } = args;
    
    return {
      content: [
        {
          type: 'text',
          text: `Echo: ${message}`
        }
      ]
    };
  }
}

async function main() {
  console.error('Starting Custom MCP Server with Foundation Models + Custom Tools...');
  
  const server = new CustomMCPServer();
  await server.run();
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});