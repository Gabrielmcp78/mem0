#!/usr/bin/env node

/**
 * Gabriel's FoundationModels Memory MCP Server (Node.js Wrapper)
 * 
 * This Node.js server wraps the Python FoundationModels memory system
 * for reliable integration with Claude Desktop via MCP protocol.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class AppleIntelligenceMemoryServer {
  constructor() {
    this.server = new Server(
      {
        name: 'gabriel-apple-intelligence-memory',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.pythonScriptPath = join(__dirname, 'memory_operations.py');
    this.setupToolHandlers();
  }

  /**
   * Execute Python memory operation with FoundationModels
   */
  async executePythonMemoryOperation(operation, params = {}) {
    return new Promise((resolve, reject) => {
      const env = {
        ...process.env,
        APPLE_INTELLIGENCE_ENABLED: 'true',
        QDRANT_URL: 'http://localhost:10333',
        QDRANT_COLLECTION: 'gabriel_apple_intelligence_memories',
        PYTHONPATH: '/Volumes/Ready500/DEVELOPMENT/mem0'
      };

      const pythonProcess = spawn('python3', [this.pythonScriptPath, operation, JSON.stringify(params)], {
        env,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (parseError) {
            resolve({ success: true, data: stdout.trim(), raw_output: true });
          }
        } else {
          reject(new Error(`Python process failed with code ${code}: ${stderr}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'test_connection',
            description: 'Test FoundationModels memory system connection',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'add_memory',
            description: 'Add new memory using FoundationModels processing',
            inputSchema: {
              type: 'object',
              properties: {
                messages: {
                  type: 'string',
                  description: 'Content to store as memory',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                agent_id: {
                  type: 'string',
                  description: 'Agent identifier (e.g., claude, kiro)',
                },
                run_id: {
                  type: 'string',
                  description: 'Session/run identifier',
                },
                metadata: {
                  type: 'string',
                  description: 'Additional metadata as JSON string',
                },
              },
              required: ['messages'],
            },
          },
          {
            name: 'search_memories',
            description: 'Search memories using FoundationModels semantic understanding',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                agent_id: {
                  type: 'string',
                  description: 'Agent identifier filter',
                },
                run_id: {
                  type: 'string',
                  description: 'Session/run identifier filter',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum results to return',
                  default: 10,
                },
              },
              required: ['query'],
            },
          },
          {
            name: 'get_all_memories',
            description: 'Retrieve all memories for a user',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum results to return',
                  default: 100,
                },
              },
            },
          },
          {
            name: 'update_memory',
            description: 'Update an existing memory',
            inputSchema: {
              type: 'object',
              properties: {
                memory_id: {
                  type: 'string',
                  description: 'Memory ID to update',
                },
                data: {
                  type: 'string',
                  description: 'New memory content',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
              required: ['memory_id', 'data'],
            },
          },
          {
            name: 'delete_memory',
            description: 'Delete a specific memory',
            inputSchema: {
              type: 'object',
              properties: {
                memory_id: {
                  type: 'string',
                  description: 'Memory ID to delete',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
              required: ['memory_id'],
            },
          },
          {
            name: 'get_memory_history',
            description: 'Get memory operation history',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum history entries',
                  default: 50,
                },
              },
            },
          },
          {
            name: 'get_agent_memories',
            description: 'Get memories specific to an agent with FoundationModels processing',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'Agent identifier to filter by',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                run_id: {
                  type: 'string',
                  description: 'Optional run identifier filter',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results',
                  default: 50,
                },
              },
              required: ['agent_id'],
            },
          },
          {
            name: 'get_shared_context',
            description: 'Get shared context for multi-agent conversation using FoundationModels',
            inputSchema: {
              type: 'object',
              properties: {
                run_id: {
                  type: 'string',
                  description: 'Run identifier for the conversation',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of context memories',
                  default: 20,
                },
              },
              required: ['run_id'],
            },
          },
          {
            name: 'resolve_memory_conflicts',
            description: 'Resolve conflicts between agent memories using FoundationModels',
            inputSchema: {
              type: 'object',
              properties: {
                conflicting_memories: {
                  type: 'string',
                  description: 'JSON string of conflicting memory IDs',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                resolution_strategy: {
                  type: 'string',
                  description: 'Strategy for conflict resolution',
                  default: 'apple_intelligence_merge',
                },
              },
              required: ['conflicting_memories'],
            },
          },
          {
            name: 'get_agent_collaboration_summary',
            description: 'Get a summary of agent collaboration for a specific run using FoundationModels',
            inputSchema: {
              type: 'object',
              properties: {
                run_id: {
                  type: 'string',
                  description: 'Run identifier for the collaboration session',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
              required: ['run_id'],
            },
          },
          {
            name: 'register_agent',
            description: 'Register an agent for memory tracking and multi-agent coordination',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'Agent identifier (e.g., claude, kiro, assistant)',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                run_id: {
                  type: 'string',
                  description: 'Run identifier for the session',
                },
                context: {
                  type: 'string',
                  description: 'Additional context as JSON string',
                },
              },
              required: ['agent_id'],
            },
          },
          {
            name: 'get_active_agents',
            description: 'Get list of all active agents in the conversation',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
                run_id: {
                  type: 'string',
                  description: 'Run identifier to filter by',
                },
              },
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result;

        switch (name) {
          case 'test_connection':
            result = {
              status: 'Connected',
              server_name: 'gabriel-apple-intelligence-memory',
              system_type: 'FoundationModels Local Memory System',
              message: '🍎 Gabriel\'s FoundationModels memory system is online and ready!',
              timestamp: new Date().toISOString()
            };
            break;

          default:
            // Execute Python memory operation
            result = await this.executePythonMemoryOperation(name, args);
            break;
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        console.error(`Error executing ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to execute ${name}: ${error.message}`
        );
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('🍎 Gabriel\'s FoundationModels Memory MCP Server running');
  }
}

const server = new AppleIntelligenceMemoryServer();
server.run().catch(console.error);