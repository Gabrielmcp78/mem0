/**
 * @fileoverview Memory management operations
 */

const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const { Logger } = require('./logger.cjs');

/**
 * Memory manager for handling mem0 operations
 */
class MemoryManager {
  constructor(config, appleIntelligenceService) {
    this.config = config;
    this.appleIntelligence = appleIntelligenceService;
    this.logger = new Logger(config.logLevel);
  }

  /**
   * Add a memory with Apple Intelligence analysis
   * @param {string} content - Memory content
   * @param {string} userId - User identifier
   * @param {Object} [metadata] - Additional metadata
   * @returns {Promise<import('./types.js').MemoryResult>}
   */
  async addMemory(content, userId, metadata = {}) {
    const startTime = Date.now();
    const operationId = uuidv4();

    this.logger.info('Starting memory addition', { operationId, userId });

    try {
      // Analyze content with Apple Intelligence
      let analysis = null;
      let appleIntelligenceUsed = false;

      if (this.config.appleIntelligenceEnabled && this.appleIntelligence.status.connected) {
        try {
          analysis = await this.appleIntelligence.analyzeMemoryContent(content, userId);
          appleIntelligenceUsed = true;
          this.logger.info('Apple Intelligence analysis completed', { operationId });
        } catch (error) {
          this.logger.warn('Apple Intelligence analysis failed, using fallback', { 
            operationId, 
            error: error.message 
          });
          
          if (!this.config.ollamaFallbackEnabled) {
            throw new Error(`Apple Intelligence failed and fallback disabled: ${error.message}`);
          }
        }
      }

      // Store memory using mem0
      const memoryResult = await this.storeMemory(content, userId, analysis, metadata);

      const processingTime = Date.now() - startTime;

      const result = {
        success: true,
        operation_id: operationId,
        memory_id: memoryResult.memory_id,
        processing_time_ms: processingTime,
        analysis: analysis,
        apple_intelligence_used: appleIntelligenceUsed,
        processed_by: 'mem0_enhanced_orchestrator',
        architecture: {
          orchestrator: 'apple_intelligence_enhanced',
          storage: 'mem0_default',
          context_understanding: 'active'
        }
      };

      this.logger.info('Memory addition completed', { 
        operationId, 
        memoryId: result.memory_id,
        processingTime 
      });

      return result;

    } catch (error) {
      this.logger.error('Memory addition failed', { operationId, error: error.message });
      throw error;
    }
  }

  /**
   * Search memories
   * @param {string} query - Search query
   * @param {Object} [options] - Search options
   * @returns {Promise<import('./types.js').SearchResult[]>}
   */
  async searchMemories(query, options = {}) {
    const {
      userId = 'default',
      limit = 10,
      filters = {}
    } = options;

    this.logger.info('Starting memory search', { query, userId, limit });

    const pythonScript = `
import sys
import json
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    
    # Use the full mem0 system with Apple Intelligence LLM
    config = ${JSON.stringify(this.config.memoryConfig).replace(/true/g, 'True').replace(/false/g, 'False').replace(/null/g, 'None')}
    memory = Memory.from_config(config)
    
    # Search using mem0's full vector search capabilities
    results = memory.search(
        query="${query.replace(/"/g, '\\"')}",
        user_id="${userId}",
        limit=${limit}
    )
    
    # Format results - handle both string and dict results
    formatted_results = []
    for i, result in enumerate(results):
        # Handle case where result might be a string or dict
        if isinstance(result, str):
            formatted_results.append({
                "memory_id": f"result_{i}",
                "content": result,
                "relevance_score": 0.5,
                "metadata": {},
                "created_at": "",
                "updated_at": ""
            })
        elif isinstance(result, dict):
            formatted_results.append({
                "memory_id": result.get("id", f"result_{i}"),
                "content": result.get("memory", result.get("text", result.get("content", ""))),
                "relevance_score": result.get("score", 0.5),
                "metadata": result.get("metadata", {}),
                "created_at": result.get("created_at", ""),
                "updated_at": result.get("updated_at", "")
            })
        else:
            # Handle other types by converting to string
            formatted_results.append({
                "memory_id": f"result_{i}",
                "content": str(result),
                "relevance_score": 0.5,
                "metadata": {},
                "created_at": "",
                "updated_at": ""
            })
    
    print(json.dumps({
        "success": True,
        "results": formatted_results,
        "query": "${query}",
        "user_id": "${userId}",
        "search_method": "mem0_full_vector_search",
        "timestamp": "${new Date().toISOString()}"
    }))
    
except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e),
        "query": "${query}",
        "user_id": "${userId}",
        "search_method": "mem0_full_vector_search",
        "timestamp": "${new Date().toISOString()}"
    }))
`;

    return new Promise((resolve, reject) => {
      const process = spawn('python3', ['-c', pythonScript], {
        timeout: this.config.operationTimeout,
        env: {
          ...require('process').env,
          OPENAI_API_KEY: "fake-key-using-apple-intelligence",
          OPENAI_BASE_URL: "http://localhost:8888/v1",
          PYTHONPATH: this.config.pythonPath
        }
      });

      let output = '';
      let errorOutput = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      process.on('close', (code) => {
        try {
          if (code === 0 && output.trim()) {
            const result = JSON.parse(output.trim());
            if (result.success) {
              this.logger.info('Memory search completed', { 
                query, 
                resultCount: result.results.length 
              });
              resolve(result.results);
            } else {
              reject(new Error(result.error));
            }
          } else {
            reject(new Error(errorOutput || 'Search failed'));
          }
        } catch (error) {
          reject(new Error('Invalid JSON response from memory search'));
        }
      });

      process.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Store memory using mem0 with Apple Intelligence LLM
   * @param {string} content 
   * @param {string} userId 
   * @param {Object} analysis 
   * @param {Object} metadata 
   * @returns {Promise<Object>}
   */
  async storeMemory(content, userId, analysis, metadata) {
    const pythonScript = `
import sys
import json
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    
    # Use the full mem0 system with Apple Intelligence LLM
    config = ${JSON.stringify(this.config.memoryConfig).replace(/true/g, 'True').replace(/false/g, 'False').replace(/null/g, 'None')}
    memory = Memory.from_config(config)
    
    # Add memory using the full mem0 infrastructure (vectors, graphs, etc.)
    result = memory.add(
        messages="${content.replace(/"/g, '\\"')}",
        user_id="${userId}"
    )
    
    print(json.dumps({
        "success": True,
        "memory_id": result.get("id", "generated_id"),
        "message": result.get("message", "Memory stored successfully"),
        "storage_method": "mem0_full_system"
    }))
    
except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e),
        "storage_method": "mem0_full_system"
    }))
`;

    return new Promise((resolve, reject) => {
      const process = spawn('python3', ['-c', pythonScript], {
        timeout: this.config.operationTimeout,
        env: {
          ...require('process').env,
          OPENAI_API_KEY: "fake-key-using-apple-intelligence",
          OPENAI_BASE_URL: "http://localhost:8888/v1",
          PYTHONPATH: this.config.pythonPath
        }
      });

      let output = '';
      let errorOutput = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      process.on('close', (code) => {
        try {
          if (code === 0 && output.trim()) {
            const result = JSON.parse(output.trim());
            if (result.success) {
              resolve(result);
            } else {
              reject(new Error(result.error));
            }
          } else {
            reject(new Error(errorOutput || 'Storage failed'));
          }
        } catch (error) {
          reject(new Error('Invalid JSON response from memory storage'));
        }
      });

      process.on('error', (error) => {
        reject(error);
      });
    });
  }
}

module.exports = { MemoryManager };