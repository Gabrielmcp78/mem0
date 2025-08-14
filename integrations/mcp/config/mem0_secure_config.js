/**
 * Secure Configuration Manager for Mem0 Full Stack
 * Handles environment variables and secure credential management
 */

export class SecureConfig {
  constructor() {
    this.validateEnvironment();
  }

  validateEnvironment() {
    const required = ['MEM0_PROJECT_PATH'];
    const missing = required.filter(env => !process.env[env]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  getMemoryConfig() {
    return {
      "vector_store": {
        "provider": "qdrant",
        "config": {
          "collection_name": process.env.QDRANT_COLLECTION || "gabriel_memories",
          "host": process.env.QDRANT_HOST || "localhost",
          "port": parseInt(process.env.QDRANT_PORT || "6333"),
          "embedding_model_dims": 384
        }
      },
      "graph_store": {
        "provider": "neo4j",
        "config": {
          "url": process.env.NEO4J_URL || "bolt://localhost:7687",
          "username": process.env.NEO4J_USERNAME || "neo4j",
          "password": process.env.NEO4J_PASSWORD || "password"
        }
      },
      "llm": {
        "provider": "apple_intelligence",
        "config": {
          "model": "apple_intelligence",
          "temperature": 0.1,
          "max_tokens": 2000,
          "system_prompt": this.getSystemPrompt(),
          "use_foundation_models": true
        }
      },
      "embedder": {
        "provider": "apple_intelligence", 
        "config": {
          "model": "apple_intelligence",
          "embedding_dims": 384,
          "use_foundation_models": true
        }
      },
      "version": "v1.1"
    };
  }

  getSystemPrompt() {
    return `You are an intelligent memory orchestrator using FoundationModels.
Your role is to:
1. Extract meaningful entities and relationships from memories
2. Understand context and temporal patterns
3. Identify semantic connections between memories
4. Manage memory deduplication intelligently
5. Provide contextual memory retrieval

Focus on understanding the deeper meaning and connections in memories, not just storing text.`;
  }

  sanitizePath(path) {
    // Basic path sanitization to prevent injection
    return path.replace(/['"\\]/g, '');
  }

  getEnvironmentConfig() {
    return {
      pythonExecutable: process.env.PYTHON_PATH || '/usr/local/bin/python3',
      pythonPath: this.sanitizePath(process.env.MEM0_PROJECT_PATH),
      configPath: process.env.MEM0_CONFIG_PATH || './mem0_config.json'
    };
  }
}