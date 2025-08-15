#!/usr/bin/env node

/**
 * Mem0 Full-Featured MCP Server with Clean Modular Architecture
 * 
 * A comprehensive, maintainable implementation that provides:
 * - ALL original functionality (8+ tools)
 * - Clean modular file organization
 * - Apple Intelligence memory analysis
 * - Enhanced search and lifecycle management
 * - Proper separation of concerns
 * 
 * This proves you CAN have both: full functionality AND clean code.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

// Import clean, modular components
const { ConfigManager } = require('./core/config.cjs');
const { Logger } = require('./core/logger.cjs');
const { AppleIntelligenceService } = require('./core/apple-intelligence.cjs');
const { MemoryManager } = require('./core/memory-manager.cjs');

// Import tool handlers
const { MemoryTools } = require('./tools/memory-tools.cjs');
const { SystemTools } = require('./tools/system-tools.cjs');

/**
 * Full-featured, modular Mem0 MCP Server
 */
class Mem0FullServer {
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
        version: '2.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize core services
    this.appleIntelligence = new AppleIntelligenceService(this.config);
    this.memoryManager = new MemoryManager(this.config, this.appleIntelligence);
    
    // Initialize tool handlers
    this.memoryTools = new MemoryTools(this.config, this.memoryManager, this.logger);
    this.systemTools = new SystemTools(this.config, this.appleIntelligence, this.memoryManager, this.logger);
    
    // Setup tool registry
    this.setupToolHandlers();
    this.logger.info('Mem0 Full Server initialized with modular architecture');
  }

  /**
   * Setup comprehensive tool handlers with clean organization
   */
  setupToolHandlers() {
    // Combine all tool definitions
    const allTools = [
      // Basic compatibility tools
      {
        name: 'add_memory',
        description: 'Add a new memory with Apple Intelligence analysis (basic compatibility)',
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
              default: 'gabriel'
            },
            agent_id: {
              type: 'string',
              description: 'Agent identifier'
            },
            run_id: {
              type: 'string',
              description: 'Session/run identifier'
            },
            project_id: {
              type: 'string',
              description: 'Project identifier'
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
        description: 'Search stored memories (basic compatibility)',
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
              default: 'gabriel'
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
        description: 'Get service status information (basic compatibility)',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      // Enhanced memory tools
      ...this.memoryTools.getToolDefinitions(),
      // System tools
      ...this.systemTools.getToolDefinitions()
    ];

    // Register all tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: allTools
    }));

    // Handle tool calls with clean routing
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          // Basic compatibility tools
          case 'add_memory':
            return await this.handleAddMemoryBasic(args);
          case 'search_memories':
            return await this.handleSearchMemoriesBasic(args);
          case 'get_status':
            return await this.handleGetStatusBasic(args);
          
          // Enhanced memory tools
          case 'add_memory_enhanced':
            return await this.memoryTools.handleAddMemoryEnhanced(args);
          case 'search_memories_enhanced':
            return await this.memoryTools.handleSearchMemoriesEnhanced(args);
          case 'get_all_memories':
            return await this.memoryTools.handleGetAllMemories(args);
          case 'get_memory_by_id':
            return await this.memoryTools.handleGetMemoryById(args);
          
          // System tools
          case 'test_connection':
            return await this.systemTools.handleTestConnection(args);
          case 'get_system_status':
            return await this.systemTools.handleGetSystemStatus(args);
          case 'get_context_insights':
            return await this.systemTools.handleGetContextInsights(args);
          case 'get_lifecycle_statistics':
            return await this.systemTools.handleGetLifecycleStatistics(args);
          
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
   * Handle basic add memory (compatibility)
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleAddMemoryBasic(args) {
    const { content, userId = 'gabriel', agent_id, run_id, project_id, metadata = {} } = args;

    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Content must be a non-empty string');
    }

    // Convert to enhanced format with all ID fields
    const enhancedArgs = {
      messages: content,
      user_id: userId,
      agent_id,
      run_id,
      project_id,
      metadata
    };

    return await this.memoryTools.handleAddMemoryEnhanced(enhancedArgs);
  }

  /**
   * Handle basic search memories (compatibility)
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleSearchMemoriesBasic(args) {
    const { query, userId = 'gabriel', limit = 10 } = args;

    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Query must be a non-empty string');
    }

    // Convert to enhanced format
    const enhancedArgs = {
      query,
      user_id: userId,
      limit
    };

    return await this.memoryTools.handleSearchMemoriesEnhanced(enhancedArgs);
  }

  /**
   * Handle basic get status (compatibility)
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleGetStatusBasic(args) {
    return await this.systemTools.handleGetSystemStatus(args);
  }

  /**
   * Start the server
   */
  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    this.logger.info('Mem0_Local_M26 Full MCP Server started successfully', {
      appleIntelligence: this.appleIntelligence.status.connected,
      architecture: 'modular',
      toolCount: 11 // 3 basic + 4 memory + 4 system
    });
  }
}

// Start the server if run directly
if (require.main === module) {
  const server = new Mem0FullServer();
  server.start().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });
}

module.exports = { Mem0FullServer };