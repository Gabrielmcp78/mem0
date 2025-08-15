#!/usr/bin/env node

/**
 * Mem0 Clean MCP Server with Apple Intelligence Integration
 * 
 * A focused, maintainable implementation that provides:
 * - Apple Intelligence memory analysis
 * - Simple memory operations (add, search)
 * - Clean separation of concerns
 * - Proper error handling
 * 
 * Refactored from 2800-line monolith into modular, testable components.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

// Import our clean, modular components
const { ConfigManager } = require('./core/config.cjs');
const { Logger } = require('./core/logger.cjs');
const { AppleIntelligenceService } = require('./core/apple-intelligence.cjs');
const { MemoryManager } = require('./core/memory-manager.cjs');

/**
 * Clean, focused Mem0 MCP Server
 */
class Mem0CleanServer {
  constructor() {
    // Load and validate configuration
    this.config = ConfigManager.loadConfiguration();
    ConfigManager.validateConfiguration(this.config);
    
    // Initialize logger
    this.logger = new Logger(this.config.logLevel);
    
    // Initialize MCP server
    this.server = new Server(
      {
        name: 'Mem0_Local_M26',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize services
    this.appleIntelligence = new AppleIntelligenceService(this.config);
    this.memoryManager = new MemoryManager(this.config, this.appleIntelligence);
    
    this.setupToolHandlers();
    this.logger.info('Mem0 Clean Server initialized');
  }

  /**
   * Setup MCP tool handlers with clean separation
   */
  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'add_memory',
          description: 'Add a new memory with Apple Intelligence analysis',
          inputSchema: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'Content to store as memory'
              },
              userId: {
                type: 'string',
                description: 'User identifier',
                default: 'default'
              },
              metadata: {
                type: 'object',
                description: 'Additional metadata (optional)',
                default: {}
              }
            },
            required: ['content']
          }
        },
        {
          name: 'search_memories',
          description: 'Search stored memories',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query'
              },
              userId: {
                type: 'string',
                description: 'User identifier',
                default: 'default'
              },
              limit: {
                type: 'number',
                description: 'Maximum number of results',
                default: 10
              }
            },
            required: ['query']
          }
        },
        {
          name: 'get_status',
          description: 'Get service status information',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        }
      ]
    }));

    // Handle tool calls with proper error handling
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'add_memory':
            return await this.handleAddMemory(args);
          
          case 'search_memories':
            return await this.handleSearchMemories(args);
          
          case 'get_status':
            return await this.handleGetStatus(args);
          
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }
      } catch (error) {
        this.logger.error(`Tool ${name} failed`, { error: error.message });
        
        if (error instanceof McpError) {
          throw error;
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  /**
   * Handle add memory requests
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleAddMemory(args) {
    const { content, userId = 'default', metadata = {} } = args;

    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Content must be a non-empty string');
    }

    const result = await this.memoryManager.addMemory(content, userId, metadata);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }

  /**
   * Handle search memories requests
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleSearchMemories(args) {
    const { query, userId = 'default', limit = 10 } = args;

    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Query must be a non-empty string');
    }

    const results = await this.memoryManager.searchMemories(query, { userId, limit });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            query,
            results,
            total_results: results.length,
            timestamp: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  /**
   * Handle get status requests
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleGetStatus(args) {
    const status = {
      server: {
        name: 'Mem0_Local_M26',
        version: '1.0.0',
        status: 'running'
      },
      apple_intelligence: this.appleIntelligence.getStatus(),
      configuration: {
        apple_intelligence_enabled: this.config.appleIntelligenceEnabled,
        ollama_fallback_enabled: this.config.ollamaFallbackEnabled,
        operation_timeout: this.config.operationTimeout,
        log_level: this.config.logLevel
      },
      timestamp: new Date().toISOString()
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(status, null, 2)
        }
      ]
    };
  }

  /**
   * Start the server
   */
  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    this.logger.info('Mem0_Local_M26 MCP Server started successfully', {
      appleIntelligence: this.appleIntelligence.status.connected
    });
  }
}

// Start the server if run directly
if (require.main === module) {
  const server = new Mem0CleanServer();
  server.start().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });
}

module.exports = { Mem0CleanServer };