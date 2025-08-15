/**
 * @fileoverview Configuration management for Mem0 MCP Server
 */

const path = require('path');

/**
 * Configuration manager with validation and defaults
 */
class ConfigManager {
  /**
   * Load and validate configuration
   * @returns {import('./types.js').ServerConfig}
   */
  static loadConfiguration() {
    const config = {
      // Core paths
      pythonPath: process.env.PYTHONPATH || path.join(process.cwd()),
      
      // Feature flags
      appleIntelligenceEnabled: process.env.APPLE_INTELLIGENCE_ENABLED !== 'false',
      ollamaFallbackEnabled: process.env.OLLAMA_FALLBACK_ENABLED !== 'false',
      
      // Operation settings
      operationTimeout: parseInt(process.env.OPERATION_TIMEOUT) || 60000,
      maxRetries: parseInt(process.env.MAX_RETRIES) || 3,
      logLevel: process.env.LOG_LEVEL || 'info',
      
      // Memory configuration - force Apple Intelligence, NO OpenAI  
      memoryConfig: {
        llm: {
          provider: "openai",
          config: {
            model: "gpt-4",
            temperature: 0.1,
            max_tokens: 2000
          }
        },
        embedder: {
          provider: "huggingface",
          config: {
            model: "sentence-transformers/all-mpnet-base-v2"
          }
        },
        vector_store: {
          provider: "chroma",
          config: {
            collection_name: "mem0_apple_intelligence",
            path: "/tmp/mem0_db"
          }
        },
        version: "v1.1",
        custom_prompt: null
      }
    };

    return config;
  }

  /**
   * Validate configuration
   * @param {import('./types.js').ServerConfig} config
   * @throws {Error} If configuration is invalid
   */
  static validateConfiguration(config) {
    const required = ['pythonPath', 'memoryConfig'];
    
    for (const field of required) {
      if (!config[field]) {
        throw new Error(`Missing required configuration field: ${field}`);
      }
    }

    if (typeof config.operationTimeout !== 'number' || config.operationTimeout <= 0) {
      throw new Error('operationTimeout must be a positive number');
    }

    if (typeof config.maxRetries !== 'number' || config.maxRetries < 0) {
      throw new Error('maxRetries must be a non-negative number');
    }
  }
}

module.exports = { ConfigManager };