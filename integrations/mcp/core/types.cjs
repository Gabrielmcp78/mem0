/**
 * @fileoverview Type definitions for Mem0 MCP Server
 */

/**
 * @typedef {Object} ServerConfig
 * @property {string} pythonPath - Path to Python executable
 * @property {boolean} appleIntelligenceEnabled - Whether Apple Intelligence is enabled
 * @property {number} operationTimeout - Timeout for operations in ms
 * @property {number} maxRetries - Maximum retry attempts
 * @property {string} logLevel - Logging level
 * @property {boolean} ollamaFallbackEnabled - Whether Ollama fallback is enabled
 * @property {MemoryConfig} memoryConfig - Memory configuration
 */

/**
 * @typedef {Object} MemoryConfig
 * @property {LLMConfig} llm - LLM configuration
 * @property {EmbedderConfig} embedder - Embedder configuration
 * @property {string} version - Configuration version
 */

/**
 * @typedef {Object} LLMConfig
 * @property {string} provider - LLM provider (e.g., 'apple_intelligence')
 * @property {Object} config - Provider-specific configuration
 */

/**
 * @typedef {Object} EmbedderConfig
 * @property {string} provider - Embedder provider
 * @property {Object} config - Provider-specific configuration
 */

/**
 * @typedef {Object} MemoryResult
 * @property {boolean} success - Operation success status
 * @property {string} memory_id - Generated memory ID
 * @property {number} processing_time_ms - Processing time in milliseconds
 * @property {Object} analysis - Analysis results
 * @property {boolean} apple_intelligence_used - Whether Apple Intelligence was used
 */

/**
 * @typedef {Object} SearchResult
 * @property {string} memory_id - Memory identifier
 * @property {string} content - Memory content
 * @property {number} relevance_score - Relevance score (0-1)
 * @property {Object} metadata - Additional metadata
 */

module.exports = {
  // Export types for JSDoc validation
};