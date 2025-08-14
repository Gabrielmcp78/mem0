#!/usr/bin/env node

/**
 * Gabriel's FoundationModels Mem0 MCP Server
 * 
 * Full stack with FoundationModels LLM:
 * - Qdrant (vector embeddings)
 * - Neo4j (graph relationships) 
 * - SQLite (structured metadata)
 * - FoundationModels (LLM processing)
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
import { v4 as uuidv4 } from 'uuid';

class AppleIntelligenceMem0Server {
  constructor() {
    this.server = new Server(
      {
        name: 'gabriel-apple-intelligence-mem0',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Configuration
    this.pythonPath = process.env.PYTHONPATH || '/Volumes/Ready500/DEVELOPMENT/mem0';
    this.setupToolHandlers();
  }

  async executePythonMemory(operation, params = {}) {
    // Convert JavaScript booleans to Python booleans
    const pythonParams = JSON.stringify(params)
      .replace(/true/g, 'True')
      .replace(/false/g, 'False')
      .replace(/null/g, 'None');
    
    const pythonScript = `
import sys
import os
import json
from datetime import datetime, timedelta

# Add mem0 to path
sys.path.insert(0, '${this.pythonPath}')

try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig
    
    # FoundationModels configuration
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "gabriel_local_apple_intelligence_384",
                "host": "localhost",
                "port": 6333,
                "embedding_model_dims": 384
            }
        },
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password"
            }
        },
        "llm": {
            "provider": "apple_intelligence",
            "config": {
                "model": "foundation_models",
                "temperature": 0.1
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dims": 384
            }
        },
        "version": "v1.1"
    }
    
    memory = Memory.from_config(config)
    operation = "${operation}"
    params = ${pythonParams}
    
    if operation == "test":
        result = {
            "success": True,
            "server": "gabriel-apple-intelligence-mem0",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "apple_intelligence": True,
            "databases": {
                "qdrant": "localhost:6333",
                "neo4j": "localhost:7687",
                "sqlite": "file-based"
            },
            "status": "FoundationModels memory system operational"
        }
    
    elif operation == "add":
        result = memory.add(
            messages=params.get("messages", params.get("text", "")),
            user_id=params.get("user_id", "gabriel"),
            agent_id=params.get("agent_id"),
            run_id=params.get("run_id"),
            metadata=params.get("metadata", {})
        )
        
    elif operation == "search":
        result = memory.search(
            query=params.get("query"),
            user_id=params.get("user_id", "gabriel"),
            agent_id=params.get("agent_id"),
            run_id=params.get("run_id"),
            limit=params.get("limit", 10),
            filters=params.get("filters")
        )
        
    elif operation == "get_all":
        result = memory.get_all(
            user_id=params.get("user_id", "gabriel"),
            agent_id=params.get("agent_id"),
            run_id=params.get("run_id"),
            limit=params.get("limit", 100),
            filters=params.get("filters")
        )
        
    elif operation == "get":
        result = memory.get(memory_id=params.get("memory_id"))
        
    elif operation == "history":
        all_memories = memory.get_all(
            user_id=params.get("user_id", "gabriel"),
            limit=1000
        )
        
        days = params.get("days", 30)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_memories = []
        for mem in all_memories.get("results", []):
            if mem.get("created_at"):
                try:
                    created_date = datetime.fromisoformat(mem["created_at"].replace('Z', '+00:00'))
                    if created_date >= cutoff_date:
                        recent_memories.append(mem)
                except:
                    pass
        
        result = {
            "success": True,
            "user_id": params.get("user_id", "gabriel"),
            "period_days": days,
            "total_memories": len(recent_memories),
            "memories": recent_memories[:50]
        }
        
    else:
        result = {"error": f"Unknown operation: {operation}"}
    
    print(json.dumps(result, default=str))
    
except Exception as e:
    import traceback
    error_result = {
        "error": str(e),
        "traceback": traceback.format_exc(),
        "operation": "${operation}",
        "params": ${JSON.stringify(params)}
    }
    print(json.dumps(error_result, default=str))
`;

    return new Promise((resolve, reject) => {
      const python = spawn('python3', ['-c', pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONPATH: this.pythonPath
        }
      });

      let output = '';
      let error = '';

      const timeout = setTimeout(() => {
        python.kill('SIGTERM');
        reject(new Error(`FoundationModels mem0 operation timeout (45s): ${operation}`));
      }, 45000);

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        error += data.toString();
      });

      python.on('close', (code) => {
        clearTimeout(timeout);

        if (code !== 0) {
          reject(new Error(`FoundationModels mem0 operation failed (code ${code}): ${error}`));
          return;
        }

        try {
          const result = JSON.parse(output.trim());
          if (result.error) {
            reject(new Error(`FoundationModels error: ${result.error}`));
          } else {
            resolve(result);
          }
        } catch (parseError) {
          reject(new Error(`Failed to parse FoundationModels response: ${parseError.message}\nRaw output: ${output}`));
        }
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
              properties: {}
            }
          },
          {
            name: 'add_memory',
            description: 'Add memory using FoundationModels processing',
            inputSchema: {
              type: 'object',
              properties: {
                text: {
                  type: 'string',
                  description: 'Memory content to add'
                },
                messages: {
                  type: 'array',
                  description: 'Array of message objects'
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel'
                },
                agent_id: {
                  type: 'string',
                  description: 'Agent identifier'
                },
                metadata: {
                  type: 'object',
                  description: 'Additional metadata'
                }
              }
            }
          },
          {
            name: 'search_memories',
            description: 'Search memories with FoundationModels semantic understanding',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query'
                },
                user_id: {
                  type: 'string', 
                  description: 'User identifier',
                  default: 'gabriel'
                },
                limit: {
                  type: 'number',
                  description: 'Maximum results',
                  default: 10
                }
              },
              required: ['query']
            }
          },
          {
            name: 'get_all_memories',
            description: 'Get all memories for a user',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier', 
                  default: 'gabriel'
                },
                limit: {
                  type: 'number',
                  description: 'Maximum results',
                  default: 100
                }
              }
            }
          },
          {
            name: 'get_memory_history',
            description: 'Get memory history for analysis',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel'
                },
                days: {
                  type: 'number', 
                  description: 'Days of history to analyze',
                  default: 30
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
            result = await this.executePythonMemory('test', {});
            break;

          case 'add_memory':
            result = await this.executePythonMemory('add', args);
            break;

          case 'search_memories':
            result = await this.executePythonMemory('search', args);
            break;

          case 'get_all_memories':
            result = await this.executePythonMemory('get_all', args);
            break;

          case 'get_memory_history':
            result = await this.executePythonMemory('history', args);
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
    console.error('🍎 FoundationModels Mem0 Server running!');
    console.error('🧠 Full Stack: Qdrant + Neo4j + SQLite + FoundationModels');
    console.error('✨ Enhanced fact extraction and semantic understanding active');
  }
}

const server = new AppleIntelligenceMem0Server();
server.run().catch(console.error);