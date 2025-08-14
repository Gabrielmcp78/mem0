#!/usr/bin/env node

/**
 * Base MCP Server Implementation
 * Handles MCP protocol, tool registration, and server lifecycle
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

export class MCPServerBase {
  constructor(name, version, protocolVersion = '2025-03-26') {
    this.server = new Server(
      { name, version },
      {
        capabilities: { tools: {} },
        protocolVersion
      }
    );

    this.tools = new Map();
    this.setupBaseHandlers();
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupBaseHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: Array.from(this.tools.values()).map(tool => ({
          name: tool.name,
          description: tool.description,
          inputSchema: tool.inputSchema
        }))
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      const tool = this.tools.get(name);

      if (!tool) {
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
      }

      try {
        return await tool.handler(args);
      } catch (error) {
        console.error(`Tool ${name} failed:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  registerTool(name, description, inputSchema, handler) {
    this.tools.set(name, {
      name,
      description,
      inputSchema,
      handler
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error(`${this.server.name} MCP server running on stdio`);
  }
}