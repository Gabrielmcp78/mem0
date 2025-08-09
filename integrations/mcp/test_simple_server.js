#!/usr/bin/env node

/**
 * Simple test MCP server to verify Claude Desktop connection
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

class SimpleTestServer {
  constructor() {
    this.server = new Server(
      {
        name: 'gabriel-simple-test',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'test_simple',
            description: 'Simple test to verify MCP connection',
            inputSchema: {
              type: 'object',
              properties: {
                message: {
                  type: 'string',
                  description: 'Test message',
                  default: 'Hello from Gabriel!'
                }
              }
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      if (name === 'test_simple') {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: args.message || 'Hello from Gabriel!',
              timestamp: new Date().toISOString(),
              server: 'gabriel-simple-test',
              status: 'MCP connection working!'
            }, null, 2)
          }]
        };
      }

      throw new Error(`Unknown tool: ${name}`);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('🚀 Gabriel\'s Simple Test Server running!');
  }
}

const server = new SimpleTestServer();
server.run().catch(console.error);