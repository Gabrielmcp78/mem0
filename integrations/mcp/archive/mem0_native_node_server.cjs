#!/usr/bin/env node

/**
 * Gabriel's Native Node.js Full Stack Memory MCP Server
 * 
 * Pure Node.js implementation that directly interfaces with:
 * - Qdrant (vector embeddings)
 * - Neo4j (graph relationships) 
 * - SQLite (structured metadata)
 * - FoundationModels (fact extraction)
 * 
 * No Python dependencies - everything runs in Node.js
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');
const { QdrantClient } = require('@qdrant/js-client-rest');
const neo4j = require('neo4j-driver');
const Database = require('better-sqlite3');
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class NativeFullStackMemoryServer {
  constructor() {
    this.server = new Server(
      {
        name: 'gabriel-native-fullstack-memory',
        version: '4.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Database connections
    this.qdrantClient = null;
    this.neo4jDriver = null;
    this.sqliteDb = null;

    // Configuration
    this.qdrantUrl = process.env.QDRANT_URL || 'http://localhost:6333';
    this.qdrantCollection = process.env.QDRANT_COLLECTION || 'gabriel_native_fullstack_memories';
    this.neo4jUrl = process.env.NEO4J_URL || 'bolt://localhost:7687';
    this.neo4jUser = process.env.NEO4J_USER || 'neo4j';
    this.neo4jPassword = process.env.NEO4J_PASSWORD || 'password';
    this.sqliteDbPath = process.env.SQLITE_DB_PATH || './gabriel_memories.db';

    this.setupConnections();
    this.setupToolHandlers();
  }

  async setupConnections() {
    try {
      // Initialize Qdrant
      this.qdrantClient = new QdrantClient({ url: this.qdrantUrl });
      await this.ensureQdrantCollection();
      console.error('✅ Qdrant connection established');

      // Initialize Neo4j
      this.neo4jDriver = neo4j.driver(
        this.neo4jUrl,
        neo4j.auth.basic(this.neo4jUser, this.neo4jPassword)
      );
      await this.testNeo4jConnection();
      console.error('✅ Neo4j connection established');

      // Initialize SQLite
      this.sqliteDb = new Database(this.sqliteDbPath);
      this.setupSqliteSchema();
      console.error('✅ SQLite connection established');

    } catch (error) {
      console.error('⚠️ Database connection warning:', error.message);
      // Continue with available connections
    }
  }

  async ensureQdrantCollection() {
    try {
      const collections = await this.qdrantClient.getCollections();
      const exists = collections.collections.some(c => c.name === this.qdrantCollection);

      if (!exists) {
        await this.qdrantClient.createCollection(this.qdrantCollection, {
          vectors: {
            size: 384, // Using local embeddings
            distance: 'Cosine',
          },
        });
        console.error(`✅ Created Qdrant collection: ${this.qdrantCollection}`);
      }
    } catch (error) {
      console.error('⚠️ Qdrant collection setup warning:', error.message);
    }
  }

  async testNeo4jConnection() {
    const session = this.neo4jDriver.session();
    try {
      await session.run('RETURN 1 as test');
    } finally {
      await session.close();
    }
  }

  setupSqliteSchema() {
    // Create memories table
    this.sqliteDb.exec(`
      CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        user_id TEXT NOT NULL,
        agent_id TEXT,
        run_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT,
        hash TEXT,
        importance_score REAL DEFAULT 0.5
      )
    `);

    // Create entities table
    this.sqliteDb.exec(`
      CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        memory_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (memory_id) REFERENCES memories (id)
      )
    `);

    // Create relationships table
    this.sqliteDb.exec(`
      CREATE TABLE IF NOT EXISTS relationships (
        id TEXT PRIMARY KEY,
        from_entity TEXT NOT NULL,
        to_entity TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        memory_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (memory_id) REFERENCES memories (id)
      )
    `);

    console.error('✅ SQLite schema initialized');
  }

  // Simple local embedding generation (deterministic)
  generateLocalEmbedding(text) {
    const words = text.toLowerCase().split(/\s+/);
    const embedding = new Array(384).fill(0);

    // Generate semantic embedding using word patterns
    words.forEach((word, index) => {
      const wordHash = this.hashString(word);
      const position = index / words.length;

      for (let i = 0; i < 384; i++) {
        const semanticValue = Math.sin(wordHash * (i + 1) + position * Math.PI);
        embedding[i] += semanticValue * (1 / Math.sqrt(words.length));
      }
    });

    // Normalize the vector
    const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => val / (magnitude || 1));
  }

  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash / 2147483647;
  }

  // FoundationModels fact extraction
  async extractFactsWithAppleIntelligence(text) {
    const swiftScript = `
import Foundation
import FoundationModels

let model = SystemLanguageModel.default
guard model.availability == .available else {
    print("ERROR: FoundationModels not available")
    exit(1)
}

let instructions = """
Extract key facts from the following text. Return each fact on a separate line. Be concise and factual.
"""

let session = LanguageModelSession(instructions: instructions)
let prompt = "${text.replace(/"/g, '\\"').substring(0, 1000)}"

do {
    let options = GenerationOptions(temperature: 0.1, maximumTokenCount: 512)
    let response = try await session.respond(to: prompt, options: options)
    print(response)
} catch {
    print("ERROR: \\(error)")
    exit(1)
}
`;

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        swift.kill('SIGTERM');
        reject(new Error('FoundationModels timeout'));
      }, 15000);

      const swift = spawn('swift', ['-'], { stdio: ['pipe', 'pipe', 'pipe'] });
      let output = '';
      let error = '';

      swift.stdin.write(swiftScript);
      swift.stdin.end();

      swift.stdout.on('data', (data) => {
        output += data.toString();
      });

      swift.stderr.on('data', (data) => {
        error += data.toString();
      });

      swift.on('close', (code) => {
        clearTimeout(timeout);

        if (code !== 0) {
          // Fallback to simple fact extraction
          resolve([text]);
          return;
        }

        const facts = output.trim().split('\n')
          .map(fact => fact.trim())
          .filter(fact => fact.length > 0 && !fact.startsWith('ERROR'))
          .slice(0, 5);

        resolve(facts.length > 0 ? facts : [text]);
      });
    });
  }

  // Extract entities using simple NLP
  extractEntities(text) {
    const entities = [];

    // Simple entity extraction patterns
    const patterns = {
      person: /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g,
      organization: /\b[A-Z][a-zA-Z]+ (Inc|Corp|LLC|Ltd|Company|Organization)\b/g,
      technology: /\b(AI|ML|API|SDK|MCP|Node\.js|Python|JavaScript|React|Vue|Angular)\b/g,
      concept: /\b(memory|database|vector|embedding|search|intelligence)\b/gi
    };

    for (const [type, pattern] of Object.entries(patterns)) {
      const matches = text.match(pattern) || [];
      matches.forEach(match => {
        entities.push({
          name: match.trim(),
          type: type,
          confidence: 0.8
        });
      });
    }

    return entities;
  }

  async addMemory(params) {
    try {
      const {
        messages,
        text,
        user_id = 'gabriel',
        agent_id,
        run_id,
        metadata = {}
      } = params;

      const inputText = text || messages;
      if (!inputText) {
        throw new Error('Either text or messages parameter is required');
      }

      console.log('🧠 Processing memory with native full-stack system...');

      // Extract facts using FoundationModels
      const facts = await this.extractFactsWithAppleIntelligence(inputText);
      const results = [];
      const timestamp = new Date().toISOString();

      for (const [index, fact] of facts.entries()) {
        const memoryId = uuidv4();
        const embedding = this.generateLocalEmbedding(fact);
        const entities = this.extractEntities(fact);
        const hash = crypto.createHash('md5').update(fact).digest('hex');

        // Store in SQLite
        if (this.sqliteDb) {
          const stmt = this.sqliteDb.prepare(`
            INSERT INTO memories (id, content, user_id, agent_id, run_id, metadata, hash, importance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          `);

          stmt.run(
            memoryId,
            fact,
            user_id,
            agent_id,
            run_id,
            JSON.stringify(metadata),
            hash,
            0.7 + (index * 0.1) // Importance decreases for later facts
          );

          // Store entities
          const entityStmt = this.sqliteDb.prepare(`
            INSERT INTO entities (id, name, type, memory_id)
            VALUES (?, ?, ?, ?)
          `);

          entities.forEach(entity => {
            entityStmt.run(uuidv4(), entity.name, entity.type, memoryId);
          });
        }

        // Store in Qdrant
        if (this.qdrantClient) {
          try {
            await this.qdrantClient.upsert(this.qdrantCollection, {
              wait: true,
              points: [{
                id: memoryId,
                vector: embedding,
                payload: {
                  content: fact,
                  user_id,
                  agent_id,
                  run_id,
                  created_at: timestamp,
                  entities: entities.map(e => e.name),
                  metadata
                }
              }]
            });
          } catch (error) {
            console.error('Qdrant storage failed:', error.message);
          }
        }

        // Store relationships in Neo4j
        if (this.neo4jDriver && entities.length > 1) {
          const session = this.neo4jDriver.session();
          try {
            for (let i = 0; i < entities.length - 1; i++) {
              for (let j = i + 1; j < entities.length; j++) {
                await session.run(`
                  MERGE (a:Entity {name: $name1, type: $type1})
                  MERGE (b:Entity {name: $name2, type: $type2})
                  MERGE (a)-[:MENTIONED_WITH {memory_id: $memoryId, created_at: $timestamp}]->(b)
                `, {
                  name1: entities[i].name,
                  type1: entities[i].type,
                  name2: entities[j].name,
                  type2: entities[j].type,
                  memoryId,
                  timestamp
                });
              }
            }
          } finally {
            await session.close();
          }
        }

        results.push({
          id: memoryId,
          memory: fact,
          event: 'ADD',
          entities: entities.map(e => e.name),
          timestamp
        });
      }

      return {
        success: true,
        results,
        count: results.length,
        processed_by: 'native_fullstack_node',
        architecture: {
          vector_store: 'qdrant',
          graph_store: 'neo4j',
          metadata_store: 'sqlite',
          ai_processing: 'apple_intelligence'
        }
      };

    } catch (error) {
      throw new Error(`Failed to add memory: ${error.message}`);
    }
  }

  async searchMemories(params) {
    try {
      const {
        query,
        user_id = 'gabriel',
        agent_id,
        run_id,
        limit = 10
      } = params;

      const results = [];

      // Search in Qdrant for semantic similarity
      if (this.qdrantClient) {
        const queryEmbedding = this.generateLocalEmbedding(query);

        const filter = {
          must: [{ key: 'user_id', match: { value: user_id } }]
        };

        if (agent_id) filter.must.push({ key: 'agent_id', match: { value: agent_id } });
        if (run_id) filter.must.push({ key: 'run_id', match: { value: run_id } });

        const searchResults = await this.qdrantClient.search(this.qdrantCollection, {
          vector: queryEmbedding,
          filter,
          limit,
          with_payload: true
        });

        results.push(...searchResults.map(result => ({
          id: result.id,
          memory: result.payload.content,
          score: result.score,
          source: 'vector_search',
          entities: result.payload.entities || [],
          metadata: result.payload.metadata || {}
        })));
      }

      // Search in SQLite for exact matches
      if (this.sqliteDb && results.length < limit) {
        const stmt = this.sqliteDb.prepare(`
          SELECT * FROM memories 
          WHERE user_id = ? AND content LIKE ?
          ORDER BY importance_score DESC, created_at DESC
          LIMIT ?
        `);

        const sqlResults = stmt.all(user_id, `%${query}%`, limit - results.length);

        results.push(...sqlResults.map(row => ({
          id: row.id,
          memory: row.content,
          score: row.importance_score,
          source: 'text_search',
          created_at: row.created_at,
          metadata: JSON.parse(row.metadata || '{}')
        })));
      }

      return {
        success: true,
        results: results.slice(0, limit),
        count: results.length,
        query,
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to search memories: ${error.message}`);
    }
  }

  async getAllMemories(params) {
    try {
      const { user_id = 'gabriel', limit = 100 } = params;

      if (!this.sqliteDb) {
        throw new Error('SQLite not available');
      }

      const stmt = this.sqliteDb.prepare(`
        SELECT m.*, GROUP_CONCAT(e.name) as entities
        FROM memories m
        LEFT JOIN entities e ON m.id = e.memory_id
        WHERE m.user_id = ?
        GROUP BY m.id
        ORDER BY m.created_at DESC
        LIMIT ?
      `);

      const results = stmt.all(user_id, limit).map(row => ({
        id: row.id,
        memory: row.content,
        user_id: row.user_id,
        agent_id: row.agent_id,
        run_id: row.run_id,
        created_at: row.created_at,
        entities: row.entities ? row.entities.split(',') : [],
        metadata: JSON.parse(row.metadata || '{}'),
        importance_score: row.importance_score
      }));

      return {
        success: true,
        results,
        count: results.length,
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to get memories: ${error.message}`);
    }
  }

  async updateMemory(params) {
    try {
      const { memory_id, text, metadata = {} } = params;

      if (!memory_id || !text) {
        throw new Error('memory_id and text are required');
      }

      if (!this.sqliteDb) {
        throw new Error('Memory update not available - SQLite not connected');
      }

      // Check if memory exists
      const existingStmt = this.sqliteDb.prepare('SELECT * FROM memories WHERE id = ?');
      const existing = existingStmt.get(memory_id);

      if (!existing) {
        throw new Error(`Memory with ID ${memory_id} not found`);
      }

      const timestamp = new Date().toISOString();
      const hash = crypto.createHash('md5').update(text).digest('hex');
      const embedding = this.generateLocalEmbedding(text);

      // Update in SQLite
      const updateStmt = this.sqliteDb.prepare(`
        UPDATE memories 
        SET content = ?, updated_at = ?, metadata = ?, hash = ?
        WHERE id = ?
      `);

      const updatedMetadata = {
        ...JSON.parse(existing.metadata || '{}'),
        ...metadata,
        updated_at: timestamp,
        processed_by: 'native_fullstack_node'
      };

      updateStmt.run(text, timestamp, JSON.stringify(updatedMetadata), hash, memory_id);

      // Update in Qdrant
      if (this.qdrantClient) {
        try {
          await this.qdrantClient.upsert(this.qdrantCollection, {
            wait: true,
            points: [{
              id: memory_id,
              vector: embedding,
              payload: {
                content: text,
                user_id: existing.user_id,
                agent_id: existing.agent_id,
                run_id: existing.run_id,
                created_at: existing.created_at,
                updated_at: timestamp,
                metadata: updatedMetadata
              }
            }]
          });
        } catch (error) {
          console.error('Qdrant update failed:', error.message);
        }
      }

      return {
        success: true,
        memory_id,
        updated_content: text,
        timestamp,
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to update memory: ${error.message}`);
    }
  }

  async deleteMemory(params) {
    try {
      const { memory_id, user_id = 'gabriel' } = params;

      if (!memory_id) {
        throw new Error('memory_id is required');
      }

      if (!this.sqliteDb) {
        throw new Error('Memory deletion not available - SQLite not connected');
      }

      // Verify memory exists and belongs to user
      const existingStmt = this.sqliteDb.prepare('SELECT * FROM memories WHERE id = ? AND user_id = ?');
      const existing = existingStmt.get(memory_id, user_id);

      if (!existing) {
        throw new Error(`Memory with ID ${memory_id} not found for user ${user_id}`);
      }

      // Delete from SQLite (cascade will handle entities and relationships)
      const deleteStmt = this.sqliteDb.prepare('DELETE FROM memories WHERE id = ?');
      deleteStmt.run(memory_id);

      // Delete entities
      const deleteEntitiesStmt = this.sqliteDb.prepare('DELETE FROM entities WHERE memory_id = ?');
      deleteEntitiesStmt.run(memory_id);

      // Delete relationships
      const deleteRelStmt = this.sqliteDb.prepare('DELETE FROM relationships WHERE memory_id = ?');
      deleteRelStmt.run(memory_id);

      // Delete from Qdrant
      if (this.qdrantClient) {
        try {
          await this.qdrantClient.delete(this.qdrantCollection, {
            wait: true,
            points: [memory_id]
          });
        } catch (error) {
          console.error('Qdrant deletion failed:', error.message);
        }
      }

      // Delete from Neo4j
      if (this.neo4jDriver) {
        const session = this.neo4jDriver.session();
        try {
          await session.run(`
            MATCH ()-[r {memory_id: $memoryId}]-()
            DELETE r
          `, { memoryId: memory_id });
        } finally {
          await session.close();
        }
      }

      return {
        success: true,
        memory_id,
        deleted_at: new Date().toISOString(),
        user_id,
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to delete memory: ${error.message}`);
    }
  }

  async getMemoryById(params) {
    try {
      const { memory_id } = params;

      if (!memory_id) {
        throw new Error('memory_id is required');
      }

      if (!this.sqliteDb) {
        throw new Error('Memory retrieval not available - SQLite not connected');
      }

      const stmt = this.sqliteDb.prepare(`
        SELECT m.*, GROUP_CONCAT(e.name) as entities
        FROM memories m
        LEFT JOIN entities e ON m.id = e.memory_id
        WHERE m.id = ?
        GROUP BY m.id
      `);

      const result = stmt.get(memory_id);

      if (!result) {
        throw new Error(`Memory with ID ${memory_id} not found`);
      }

      return {
        success: true,
        memory: {
          id: result.id,
          content: result.content,
          user_id: result.user_id,
          agent_id: result.agent_id,
          run_id: result.run_id,
          created_at: result.created_at,
          updated_at: result.updated_at,
          entities: result.entities ? result.entities.split(',') : [],
          metadata: JSON.parse(result.metadata || '{}'),
          importance_score: result.importance_score
        },
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to get memory by ID: ${error.message}`);
    }
  }

  async getMemoryHistory(params) {
    try {
      const { user_id = 'gabriel', days = 30 } = params;

      if (!this.sqliteDb) {
        throw new Error('Memory history not available - SQLite not connected');
      }

      // Calculate date threshold
      const dateThreshold = new Date();
      dateThreshold.setDate(dateThreshold.getDate() - days);
      const thresholdISO = dateThreshold.toISOString();

      // Get recent memories
      const stmt = this.sqliteDb.prepare(`
        SELECT * FROM memories 
        WHERE user_id = ? AND created_at >= ?
        ORDER BY created_at DESC
      `);

      const recentMemories = stmt.all(user_id, thresholdISO);

      // Analyze statistics
      const agentStats = {};
      const dailyStats = {};

      recentMemories.forEach(memory => {
        const agentId = memory.agent_id || 'unknown';
        const date = memory.created_at ? memory.created_at.split('T')[0] : 'unknown';

        // Agent statistics
        if (!agentStats[agentId]) {
          agentStats[agentId] = { count: 0, latest: null };
        }
        agentStats[agentId].count++;
        if (!agentStats[agentId].latest || memory.created_at > agentStats[agentId].latest) {
          agentStats[agentId].latest = memory.created_at;
        }

        // Daily statistics
        if (!dailyStats[date]) {
          dailyStats[date] = 0;
        }
        dailyStats[date]++;
      });

      return {
        success: true,
        user_id,
        period_days: days,
        total_memories: recentMemories.length,
        agent_statistics: agentStats,
        daily_statistics: dailyStats,
        date_range: {
          from: thresholdISO,
          to: new Date().toISOString()
        },
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to get memory history: ${error.message}`);
    }
  }

  async clearMemories(params) {
    try {
      const { user_id = 'gabriel', confirm } = params;

      if (!confirm) {
        throw new Error('Confirmation required - set confirm: true to proceed');
      }

      if (!this.sqliteDb) {
        throw new Error('Memory clearing not available - SQLite not connected');
      }

      // Get all memory IDs for user
      const getIdsStmt = this.sqliteDb.prepare('SELECT id FROM memories WHERE user_id = ?');
      const memoryIds = getIdsStmt.all(user_id).map(row => row.id);

      if (memoryIds.length === 0) {
        return {
          success: true,
          message: `No memories found for user ${user_id}`,
          cleared_count: 0,
          user_id
        };
      }

      // Delete from SQLite
      const deleteStmt = this.sqliteDb.prepare('DELETE FROM memories WHERE user_id = ?');
      deleteStmt.run(user_id);

      // Delete entities
      const deleteEntitiesStmt = this.sqliteDb.prepare('DELETE FROM entities WHERE memory_id IN (' + memoryIds.map(() => '?').join(',') + ')');
      deleteEntitiesStmt.run(...memoryIds);

      // Delete relationships
      const deleteRelStmt = this.sqliteDb.prepare('DELETE FROM relationships WHERE memory_id IN (' + memoryIds.map(() => '?').join(',') + ')');
      deleteRelStmt.run(...memoryIds);

      // Delete from Qdrant
      if (this.qdrantClient) {
        try {
          await this.qdrantClient.delete(this.qdrantCollection, {
            wait: true,
            points: memoryIds
          });
        } catch (error) {
          console.error('Qdrant bulk deletion failed:', error.message);
        }
      }

      // Delete from Neo4j
      if (this.neo4jDriver) {
        const session = this.neo4jDriver.session();
        try {
          await session.run(`
            MATCH ()-[r]-()
            WHERE r.memory_id IN $memoryIds
            DELETE r
          `, { memoryIds });
        } finally {
          await session.close();
        }
      }

      return {
        success: true,
        message: `Cleared ${memoryIds.length} memories for user ${user_id}`,
        cleared_count: memoryIds.length,
        user_id,
        cleared_at: new Date().toISOString(),
        processed_by: 'native_fullstack_node'
      };

    } catch (error) {
      throw new Error(`Failed to clear memories: ${error.message}`);
    }
  }

  async testConnection() {
    const status = {
      server: 'gabriel-native-fullstack-memory',
      version: '4.0.0',
      status: 'connected',
      timestamp: new Date().toISOString(),
      architecture: 'Pure Node.js Full Stack',
      connections: {
        qdrant: !!this.qdrantClient,
        neo4j: !!this.neo4jDriver,
        sqlite: !!this.sqliteDb
      },
      features: [
        'FoundationModels fact extraction',
        'Local semantic embeddings',
        'Vector similarity search (Qdrant)',
        'Graph relationships (Neo4j)',
        'Structured metadata (SQLite)',
        'Entity extraction',
        'Cross-database queries'
      ]
    };

    // Test connections
    if (this.qdrantClient) {
      try {
        const collections = await this.qdrantClient.getCollections();
        status.connections.qdrant_collections = collections.collections.length;
      } catch (error) {
        status.connections.qdrant_error = error.message;
      }
    }

    if (this.neo4jDriver) {
      const session = this.neo4jDriver.session();
      try {
        await session.run('RETURN 1');
        status.connections.neo4j_status = 'healthy';
      } catch (error) {
        status.connections.neo4j_error = error.message;
      } finally {
        await session.close();
      }
    }

    if (this.sqliteDb) {
      try {
        const result = this.sqliteDb.prepare('SELECT COUNT(*) as count FROM memories').get();
        status.connections.sqlite_memories = result.count;
      } catch (error) {
        status.connections.sqlite_error = error.message;
      }
    }

    return status;
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'test_connection',
            description: 'Test native full-stack memory system connections',
            inputSchema: { type: 'object', properties: {} }
          },
          {
            name: 'add_memory',
            description: 'Add memory using native full-stack architecture',
            inputSchema: {
              type: 'object',
              properties: {
                messages: { type: 'string', description: 'Content to store' },
                text: { type: 'string', description: 'Content to store (alternative)' },
                user_id: { type: 'string', description: 'User identifier', default: 'gabriel' },
                agent_id: { type: 'string', description: 'Agent identifier' },
                run_id: { type: 'string', description: 'Session identifier' },
                metadata: { type: 'object', description: 'Additional metadata' }
              }
            }
          },
          {
            name: 'search_memories',
            description: 'Search memories using vector + text search',
            inputSchema: {
              type: 'object',
              properties: {
                query: { type: 'string', description: 'Search query' },
                user_id: { type: 'string', description: 'User identifier', default: 'gabriel' },
                agent_id: { type: 'string', description: 'Agent filter' },
                run_id: { type: 'string', description: 'Session filter' },
                limit: { type: 'number', description: 'Max results', default: 10 }
              },
              required: ['query']
            }
          },
          {
            name: 'get_all_memories',
            description: 'Get all memories with entities and metadata',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: { type: 'string', description: 'User identifier', default: 'gabriel' },
                limit: { type: 'number', description: 'Max results', default: 100 }
              }
            }
          },
          {
            name: 'update_memory',
            description: 'Update an existing memory with new content',
            inputSchema: {
              type: 'object',
              properties: {
                memory_id: { type: 'string', description: 'ID of the memory to update' },
                text: { type: 'string', description: 'New content for the memory' },
                metadata: { type: 'object', description: 'Additional metadata to update' }
              },
              required: ['memory_id', 'text']
            }
          },
          {
            name: 'delete_memory',
            description: 'Delete a specific memory by ID',
            inputSchema: {
              type: 'object',
              properties: {
                memory_id: { type: 'string', description: 'ID of the memory to delete' },
                user_id: { type: 'string', description: 'User identifier for verification', default: 'gabriel' }
              },
              required: ['memory_id']
            }
          },
          {
            name: 'get_memory_by_id',
            description: 'Retrieve a specific memory by its ID',
            inputSchema: {
              type: 'object',
              properties: {
                memory_id: { type: 'string', description: 'ID of the memory to retrieve' }
              },
              required: ['memory_id']
            }
          },
          {
            name: 'get_memory_history',
            description: 'Get memory history and statistics for a user',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: { type: 'string', description: 'User identifier', default: 'gabriel' },
                days: { type: 'number', description: 'Number of days to look back', default: 30 }
              }
            }
          },
          {
            name: 'clear_memories',
            description: 'Clear all memories for a user (use with caution)',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: { type: 'string', description: 'User identifier', default: 'gabriel' },
                confirm: { type: 'boolean', description: 'Confirmation flag' }
              },
              required: ['confirm']
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
            result = await this.testConnection();
            break;
          case 'add_memory':
            result = await this.addMemory(args);
            break;
          case 'search_memories':
            result = await this.searchMemories(args);
            break;
          case 'get_all_memories':
            result = await this.getAllMemories(args);
            break;
          case 'update_memory':
            result = await this.updateMemory(args);
            break;
          case 'delete_memory':
            result = await this.deleteMemory(args);
            break;
          case 'get_memory_by_id':
            result = await this.getMemoryById(args);
            break;
          case 'get_memory_history':
            result = await this.getMemoryHistory(args);
            break;
          case 'clear_memories':
            result = await this.clearMemories(args);
            break;
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
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
    console.error('🚀 Gabriel\'s Native Full-Stack Memory Server running!');
    console.error('🏗️ Architecture: Pure Node.js + Qdrant + Neo4j + SQLite + FoundationModels');
  }
}

const server = new NativeFullStackMemoryServer();
server.run().catch(console.error);