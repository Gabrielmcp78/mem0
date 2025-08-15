/**
 * @fileoverview Memory operation tools
 */

const { McpError, ErrorCode } = require('@modelcontextprotocol/sdk/types.js');

/**
 * Memory operation tools handler
 */
class MemoryTools {
  constructor(config, memoryManager, logger) {
    this.config = config;
    this.memoryManager = memoryManager;
    this.logger = logger;
  }

  /**
   * Get tool definitions for memory operations
   * @returns {Array} Tool definitions
   */
  getToolDefinitions() {
    return [
      {
        name: 'add_memory_enhanced',
        description: 'Add memory with full Apple Intelligence orchestration, context understanding, and lifecycle management',
        inputSchema: {
          type: 'object',
          properties: {
            messages: {
              type: 'string',
              description: 'Content to store as memory',
            },
            text: {
              type: 'string',
              description: 'Content to store as memory (alternative to messages)',
            },
            user_id: {
              type: 'string',
              description: 'User identifier',
              default: 'gabriel',
            },
            agent_id: {
              type: 'string',
              description: 'Agent identifier',
            },
            run_id: {
              type: 'string',
              description: 'Session/run identifier',
            },
            project_id: {
              type: 'string',
              description: 'Project identifier for organizing memories by project context',
            },
            metadata: {
              type: 'object',
              description: 'Additional metadata',
            },
          },
        },
      },
      {
        name: 'search_memories_enhanced',
        description: 'Search memories with Apple Intelligence ranking, context understanding, and intent analysis',
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
            project_id: {
              type: 'string',
              description: 'Project identifier filter',
            },
            limit: {
              type: 'number',
              description: 'Maximum results to return',
              default: 10,
            },
            filters: {
              type: 'object',
              description: 'Additional filters',
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'get_all_memories',
        description: 'Get all memories with enhanced metadata and lifecycle information',
        inputSchema: {
          type: 'object',
          properties: {
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
            project_id: {
              type: 'string',
              description: 'Project identifier filter',
            },
            limit: {
              type: 'number',
              description: 'Maximum results to return',
              default: 100,
            },
            filters: {
              type: 'object',
              description: 'Additional filters',
            },
          },
        },
      },
      {
        name: 'get_memory_by_id',
        description: 'Get specific memory by ID with full context and lifecycle information',
        inputSchema: {
          type: 'object',
          properties: {
            memory_id: {
              type: 'string',
              description: 'Memory ID to retrieve',
            },
          },
          required: ['memory_id'],
        },
      },
    ];
  }

  /**
   * Handle add memory enhanced
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleAddMemoryEnhanced(args) {
    const { messages, text, user_id = 'gabriel', agent_id, run_id, project_id, metadata = {} } = args;
    
    // Get content from either messages or text
    const content = messages || text;
    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Content (messages or text) must be a non-empty string');
    }

    // Add agent_id, run_id, and project_id to metadata if provided
    const enhancedMetadata = { ...metadata };
    if (agent_id) enhancedMetadata.agent_id = agent_id;
    if (run_id) enhancedMetadata.run_id = run_id;
    if (project_id) enhancedMetadata.project_id = project_id;

    const result = await this.memoryManager.addMemory(content, user_id, enhancedMetadata);

    // Add agent_id, run_id, and project_id to top-level response
    const enhancedResult = {
      ...result,
      agent_id: agent_id || null,
      run_id: run_id || null,
      project_id: project_id || null,
      user_id: user_id
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(enhancedResult, null, 2)
        }
      ]
    };
  }

  /**
   * Handle search memories enhanced
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleSearchMemoriesEnhanced(args) {
    const { query, user_id = 'gabriel', agent_id, run_id, project_id, limit = 10, filters = {} } = args;

    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      throw new McpError(ErrorCode.InvalidParams, 'Query must be a non-empty string');
    }

    // Add agent_id, run_id, and project_id to filters
    const enhancedFilters = { ...filters };
    if (agent_id) enhancedFilters.agent_id = agent_id;
    if (run_id) enhancedFilters.run_id = run_id;
    if (project_id) enhancedFilters.project_id = project_id;

    const results = await this.memoryManager.searchMemories(query, { 
      userId: user_id, 
      limit, 
      filters: enhancedFilters 
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            query,
            results,
            total_results: results.length,
            filters: enhancedFilters,
            timestamp: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  /**
   * Handle get all memories
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleGetAllMemories(args) {
    const { user_id = 'gabriel', agent_id, run_id, project_id, limit = 100, filters = {} } = args;

    // For now, implement as a search with empty query
    const enhancedFilters = { ...filters };
    if (agent_id) enhancedFilters.agent_id = agent_id;
    if (run_id) enhancedFilters.run_id = run_id;
    if (project_id) enhancedFilters.project_id = project_id;

    // Use a broad search to get all memories
    const results = await this.memoryManager.searchMemories('', { 
      userId: user_id, 
      limit, 
      filters: enhancedFilters 
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            user_id,
            total_memories: results.length,
            memories: results,
            filters: enhancedFilters,
            timestamp: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  /**
   * Handle get memory by ID
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result object
   */
  async handleGetMemoryById(args) {
    const { memory_id } = args;

    if (!memory_id || typeof memory_id !== 'string') {
      throw new McpError(ErrorCode.InvalidParams, 'Memory ID must be a non-empty string');
    }

    // This would need to be implemented in the memory manager
    // For now, return a placeholder
    const result = {
      memory_id,
      status: 'not_implemented',
      message: 'get_memory_by_id functionality needs to be implemented in memory manager',
      timestamp: new Date().toISOString()
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
}

module.exports = { MemoryTools };