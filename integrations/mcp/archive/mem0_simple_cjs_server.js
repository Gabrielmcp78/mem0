#!/usr/bin/env node

/**
 * Gabriel's Simple CommonJS MCP Server
 * Using require() instead of import for better compatibility
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

class SimpleMemoryServer {
  constructor() {
    this.server = new Server(
      {
        name: 'gabriel-simple-memory',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.memories = new Map(); // Simple in-memory storage
    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'test_connection',
            description: 'Test simple memory server connection',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'add_simple_memory',
            description: 'Add a simple memory',
            inputSchema: {
              type: 'object',
              properties: {
                text: {
                  type: 'string',
                  description: 'Memory content'
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel'
                }
              },
              required: ['text']
            }
          },
          {
            name: 'get_simple_memories',
            description: 'Get all simple memories',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel'
                }
              }
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result;
        
        switch (name) {
          case 'test_connection':
            result = {
              success: true,
              server: 'gabriel-simple-memory',
              version: '1.0.0',
              timestamp: new Date().toISOString(),
              status: 'Simple memory server is working!',
              memory_count: this.memories.size
            };
            break;

          case 'add_simple_memory':
            const memoryId = Date.now().toString();
            const memory = {
              id: memoryId,
              text: args.text,
              user_id: args.user_id || 'gabriel',
              created_at: new Date().toISOString()
            };
            
            this.memories.set(memoryId, memory);
            
            result = {
              success: true,
              memory_id: memoryId,
              memory: memory,
              message: 'Memory added successfully!'
            };
            break;

          case 'get_simple_memories':
            const userMemories = Array.from(this.memories.values())
              .filter(m => m.user_id === (args.user_id || 'gabriel'));
            
            result = {
              success: true,
              memories: userMemories,
              count: userMemories.length,
              user_id: args.user_id || 'gabriel'
            };
            break;

          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              error: error.message,
              tool: name,
              timestamp: new Date().toISOString()
            }, null, 2)
          }],
          isError: true
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('🚀 Gabriel\'s Simple Memory Server running!');
    console.error('📝 In-memory storage ready');
  }
}

const server = new SimpleMemoryServer();
server.run().catch(console.error);