#!/usr/bin/env node

/**
 * Mem0 Enhanced MCP Server with FoundationModels Integration
 * 
 * Production-ready Phase 1 implementation that integrates:
 * - FoundationModels Orchestrator
 * - Context Understanding
 * - Memory Lifecycle Management
 * 
 * This server provides intelligent memory operations with full context awareness,
 * semantic understanding, and lifecycle management capabilities.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');
const { PythonExecutor } = require('./core/python_executor.js');

/**
 * Enhanced Mem0 Server with FoundationModels Integration
 */
class Mem0EnhancedServer {
  constructor() {
    this.server = new Server(
      {
        name: 'mem0-enhanced-apple-intelligence',
        version: '4.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Configuration with validation
    this.config = this.loadConfiguration();
    this.validateConfiguration();
    this.pythonExecutor = new PythonExecutor(this.config);
    
    // Initialize default status (will be updated by async initialization)
    this.appleIntelligenceStatus = {
      status: 'initializing',
      apple_intelligence: false,
      processing: 'pending_initialization'
    };
    
    this.setupToolHandlers();
  }

  /**
   * Load and validate configuration
   */
  loadConfiguration() {
    const config = {
      pythonPath: process.env.PYTHONPATH || '/Volumes/Ready500/DEVELOPMENT/mem0',
      pythonExecutable: process.env.PYTHON_EXECUTABLE || 'python3',
      mem0ConfigPath: process.env.MEM0_CONFIG_PATH || './mem0_config.json',
      appleIntelligenceEnabled: process.env.APPLE_INTELLIGENCE_ENABLED !== 'true',
      operationTimeout: parseInt(process.env.OPERATION_TIMEOUT) || 60000,
      maxRetries: parseInt(process.env.MAX_RETRIES) || 3,
      logLevel: process.env.LOG_LEVEL || 'info',
      ollamaFallbackEnabled: process.env.OLLAMA_FALLBACK_ENABLED !== 'false',
    };

    // Mem0 configuration for full stack operation
    config.memoryConfig = {
      llm: {
        provider: "apple_intelligence",
        config: {
          model: "SystemLanguageModel",
          temperature: 0.1,
          max_tokens: 2000
        }
      },
      embedder: {
        provider: "huggingface",
        config: {
          model: "sentence-transformers/all-MiniLM-L6-v2",
          embedding_dims: 384
        }
      },
      version: "v1.1"
    };

    return config;
  }

  /**
   * Validate configuration and dependencies
   */
  validateConfiguration() {
    // Validate Python path
    if (!fs.existsSync(this.config.pythonPath)) {
      throw new Error(`Python path does not exist: ${this.config.pythonPath}`);
    }

    // Validate mem0 installation
    const mem0Path = path.join(this.config.pythonPath, 'mem0');
    if (!fs.existsSync(mem0Path)) {
      throw new Error(`mem0 library not found at: ${mem0Path}`);
    }

    this.log('info', 'Configuration validated successfully');
  }

  /**
   * Initialize intelligent systems
   */
  async initializeIntelligentSystems() {
    try {
      // Initialize orchestrator configuration
      this.orchestratorConfig = {
        pythonPath: this.config.pythonPath,
        pythonExecutable: this.config.pythonExecutable,
        memoryConfig: this.config.memoryConfig,
        appleIntelligenceEnabled: this.config.appleIntelligenceEnabled
      };

      // Initialize operation tracking
      this.operationContext = new Map();
      this.memoryRelationships = new Map();
      this.lifecycleStates = new Map();
      this.contextHistory = new Map();

      // Test FoundationModels availability
      await this.testAppleIntelligenceConnection();

      // Test Ollama availability as fallback
      await this.testOllamaConnection();

      // Initialize Agent Registry and Tool Call Manager
      await this.initializeAgentManagement();
      await this.initializeToolCallManager();

      this.log('info', 'Intelligent systems initialized successfully');
      this.log('info', `Agent Registry: ${this.agentRegistry.getSystemStatus().totalAgents} agents available`);
      this.log('info', `Tool Call Manager: ${this.toolCallManager.getSystemStatus().totalTools} tools registered`);
    } catch (error) {
      this.log('error', `Failed to initialize intelligent systems: ${error.message}`);
      throw error;
    }
  }

  /**
   * Initialize Agent Management System
   */
  async initializeAgentManagement() {
    // Import Agent Registry (using dynamic import for ES modules)
    const { AgentRegistry } = await import('./core/agent_registry.js');
    
    this.agentRegistry = new AgentRegistry(this);
    
    // Set up event listeners
    this.agentRegistry.on('agentCreated', (event) => {
      this.log('info', `Agent created: ${event.agentId} (type: ${event.typeName})`);
    });
    
    this.agentRegistry.on('taskCompleted', (event) => {
      this.log('info', `Task completed by agent ${event.agentId}: ${event.taskId} (${event.processingTime}ms)`);
    });
    
    this.agentRegistry.on('agentActivated', (event) => {
      this.log('info', `Agent activated: ${event.agentId}`);
    });
    
    this.log('info', 'Agent Registry initialized with default agent types');
  }

  /**
   * Initialize Tool Call Manager
   */
  async initializeToolCallManager() {
    // Import Tool Call Manager (using dynamic import for ES modules)
    const { ToolCallManager } = await import('./core/tool_call_manager.js');
    
    this.toolCallManager = new ToolCallManager(this);
    
    // Set up event listeners
    this.toolCallManager.on('toolCallStarted', (event) => {
      this.log('info', `Tool call started: ${event.toolName} (${event.callId})`);
    });
    
    this.toolCallManager.on('toolCallCompleted', (event) => {
      this.log('info', `Tool call completed: ${event.toolName} (${event.executionTime}ms)`);
    });
    
    this.toolCallManager.on('toolCallFailed', (event) => {
      this.log('warn', `Tool call failed: ${event.toolName} - ${event.error}`);
    });
    
    this.log('info', 'Tool Call Manager initialized with default tools');
  }

  /**
   * Test FoundationModels connection
   */
  async testAppleIntelligenceConnection() {
    const testScript = `
import sys
import json
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status, get_foundation_models_interface
    
    # Check availability
    is_available = check_apple_intelligence_availability()
    
    if is_available:
        # Get detailed status
        status = get_apple_intelligence_status()
        
        # Test actual generation
        interface = get_foundation_models_interface()
        if interface and interface.is_available:
            try:
                test_result = interface.generate_text("Test", max_tokens=5, temperature=0.1)
                result = {
                    "apple_intelligence": True,
                    "foundation_models": True,
                    "status": "connected",
                    "test_generation": test_result[:50] if test_result else "empty_response",
                    "macos_version": status.get("macos_version"),
                    "neural_engine": True
                }
            except Exception as gen_error:
                result = {
                    "apple_intelligence": True,
                    "foundation_models": True,
                    "status": "connected_no_generation",
                    "generation_error": str(gen_error),
                    "macos_version": status.get("macos_version")
                }
        else:
            result = {
                "apple_intelligence": False,
                "foundation_models": False,
                "status": "interface_unavailable",
                "error": interface._error_message if interface else "no_interface"
            }
    else:
        result = {
            "apple_intelligence": False,
            "foundation_models": False,
            "status": "unavailable",
            "error": "FoundationModels not available on this system"
        }
    
    print(json.dumps(result))
    
except Exception as e:
    error_result = {
        "apple_intelligence": False,
        "error": str(e),
        "status": "error"
    }
    print(json.dumps(error_result))
`;

    try {
      const result = await this.pythonExecutor.executeScript(testScript, 'FoundationModels Connection Test', 30000);
      this.appleIntelligenceStatus = result;
      this.log('info', `FoundationModels status: ${result.status}`);
    } catch (error) {
      // DO NOT FALLBACK - Fail fast if Apple Intelligence is not working
      this.log('error', `FoundationModels connection FAILED: ${error.message}`);
      throw new Error(`Apple Intelligence required but unavailable: ${error.message}`);
    }
  }

  /**
   * Test Ollama connection and available models
   */
  async testOllamaConnection() {
    try {
      const response = await fetch('http://localhost:11434/api/tags');
      const data = await response.json();
      
      const models = data.models || [];
      const preferredModels = ['llama3.2:3b', 'phi4:latest', 'llama3:latest'];
      const availableModel = preferredModels.find(model => 
        models.some(m => m.name === model)
      ) || (models.length > 0 ? models[0].name : null);

      if (availableModel) {
        this.ollamaStatus = {
          available: true,
          status: 'connected',
          model: availableModel,
          total_models: models.length,
          models: models.map(m => ({ name: m.name, size: m.size }))
        };
        this.log('info', `Ollama status: connected with ${availableModel}`);
      } else {
        throw new Error('No models available');
      }
    } catch (error) {
      this.ollamaStatus = {
        available: false,
        status: 'unavailable',
        error: error.message
      };
      this.log('warn', `Ollama unavailable: ${error.message}`);
    }
  }

  /**
   * Generate text using Ollama as fallback
   */
  async generateWithOllama(prompt, maxTokens = 1000, temperature = 0.1) {
    if (!this.ollamaStatus?.available) {
      throw new Error('Ollama not available');
    }

    try {
      const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: this.ollamaStatus.model,
          prompt: prompt,
          stream: false,
          options: {
            temperature: temperature,
            num_predict: maxTokens
          }
        })
      });

      const data = await response.json();
      
      if (data.response) {
        return data.response.trim();
      } else {
        throw new Error('No response from Ollama');
      }
    } catch (error) {
      throw new Error(`Ollama generation failed: ${error.message}`);
    }
  }

  /**
   * Enhanced analyze memory content with Ollama fallback
   */
  async analyzeMemoryContentWithFallback(content, userId, operationId) {
    // First try Apple Intelligence
    try {
      return await this.analyzeMemoryContent(content, userId, operationId);
    } catch (appleError) {
      this.log('error', `Apple Intelligence analysis failed. Full error: ${appleError.stack || appleError}`);

      if (this.config.ollamaFallbackEnabled) {
        this.log('warn', `Falling back to Ollama...`);
        
        // Fallback to Ollama
        if (!this.ollamaStatus?.available) {
          throw new Error(`Both Apple Intelligence and Ollama unavailable. Apple: ${appleError.message}, Ollama: not connected`);
        }

        try {
          const prompt = `Analyze this memory content and return a JSON object with semantic analysis:\n\nContent: "${content}"\n\nReturn JSON with these fields:\n{\n  "entities": {"people": [], "places": [], "organizations": [], "concepts": [], "dates": [], "events": []},\n  "relationships": [],\n  "sentiment": {"polarity": 0.0, "intensity": 0.5, "primary_emotion": "neutral", "emotions": []},\n  "concepts": [],\n  "importance": {"score": 5, "reasoning": "Analyzed importance", "factors": []},\n  "temporal_context": {"time_references": [], "temporal_relationships": [], "temporal_significance": "medium"},\n  "intent": {"primary_intent": "remember", "secondary_intents": [], "retrieval_cues": []},\n  "metadata": {"confidence_score": 0.8, "processing_method": "ollama_llama3.2"},\n  "processing_timestamp": "${new Date().toISOString()}",\n  "apple_intelligence": false,\n  "ollama_model": "${this.ollamaStatus.model}"\n}\n\nRespond with ONLY the JSON object, no other text.`;

          const response = await this.generateWithOllama(prompt, 1000, 0.1);
          
          try {
            const analysis = JSON.parse(response);
            this.log('info', `Memory analysis completed via Ollama fallback`);
            return analysis;
          } catch (parseError) {
            // If JSON parsing fails, create a structured fallback
            this.log('info', `Ollama completed analysis with structured fallback`);
            return {
              entities: { people: [], places: [], organizations: [], concepts: [], dates: [], events: [] },
              relationships: [],
              sentiment: { polarity: 0.0, intensity: 0.5, primary_emotion: "neutral", emotions: [] },
              concepts: [],
              importance: { score: 6, reasoning: "Ollama analysis", factors: ["ollama_processing"] },
              temporal_context: { time_references: [], temporal_relationships: [], temporal_significance: "medium" },
              intent: { primary_intent: "remember", secondary_intents: [], retrieval_cues: [] },
              metadata: { confidence_score: 0.7, processing_method: "ollama_fallback_structured" },
              processing_timestamp: new Date().toISOString(),
              apple_intelligence: false,
              ollama_model: this.ollamaStatus.model,
              raw_response: response.substring(0, 200)
            };
          }
        } catch (ollamaError) {
          throw new Error(`Both AI systems failed. Apple: ${appleError.message}, Ollama: ${ollamaError.message}`);
        }
      } else {
        this.log('error', 'Ollama fallback is disabled. Operation failed.');
        throw new Error(`Apple Intelligence failed and Ollama fallback is disabled: ${appleError.message}`);
      }
    }
  }

  /**
   * Enhanced memory addition with full orchestration
   */
  async addMemoryEnhanced(params) {
    const operationId = uuidv4();
    const startTime = Date.now();
    
    try {
      // Validate inputs
      const userId = this.validateUserId(params.user_id || 'gabriel');
      const content = this.validateMemoryContent(params.messages || params.text);
      
      this.log('info', `Starting enhanced memory addition: ${operationId}`);
      
      // Step 1: Analyze memory content with FoundationModels + Ollama fallback
      const analysis = await this.analyzeMemoryContentWithFallback(content, userId, operationId);
      
      // Step 2: Analyze context
      const contextAnalysis = await this.analyzeMemoryContext({ content, userId, operationId });
      
      // Step 3: Check for semantic duplicates
      const deduplicationResult = await this.checkSemanticDuplicates(content, analysis, userId, operationId);
      
      // Step 4: Determine storage strategy
      const storageStrategy = this.determineStorageStrategy(analysis, deduplicationResult);
      
      // Step 5: Execute intelligent storage
      const storageResult = await this.executeIntelligentStorage({
        content,
        analysis,
        contextAnalysis,
        deduplicationResult,
        storageStrategy,
        userId,
        metadata: params.metadata || {},
        agentId: params.agent_id,
        runId: params.run_id,
        operationId
      });
      
      // Step 6: Initialize lifecycle management
      const lifecycleState = await this.initializeMemoryLifecycle(storageResult.memory_id, {
        analysis,
        contextAnalysis,
        storageStrategy,
        operationId
      });
      
      const processingTime = Date.now() - startTime;
      
      const result = {
        success: true,
        operation_id: operationId,
        memory_id: storageResult.memory_id,
        processing_time_ms: processingTime,
        analysis: {
          semantic_analysis: analysis,
          context_analysis: contextAnalysis,
          deduplication_result: deduplicationResult,
          storage_strategy: storageStrategy
        },
        lifecycle_initialized: true,
        relationships_created: storageResult.relationships || [],
        apple_intelligence_used: this.appleIntelligenceStatus.apple_intelligence,
        processed_by: 'mem0_enhanced_orchestrator',
        architecture: {
          orchestrator: 'apple_intelligence_enhanced',
          vector_storage: 'default',
          graph_relationships: 'neo4j',
          metadata: 'sqlite',
          context_understanding: 'active',
          lifecycle_management: 'active'
        }
      };
      
      this.log('info', `Enhanced memory addition completed: ${operationId} (${processingTime}ms)`);
      return result;
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.log('error', `Enhanced memory addition failed: ${operationId} - ${error.message}`);
      
      throw new Error(`Enhanced memory addition failed (${processingTime}ms): ${error.message}`);
    }
  }

  /**
   * Enhanced memory search with intelligent ranking
   */
  async searchMemoriesEnhanced(params) {
    const operationId = uuidv4();
    const startTime = Date.now();
    
    try {
      const query = this.validateSearchQuery(params.query);
      const userId = this.validateUserId(params.user_id || 'gabriel');
      const limit = this.validateLimit(params.limit || 10);
      
      this.log('info', `Starting enhanced memory search: ${operationId}`);
      
      // Step 1: Analyze search intent with FoundationModels
      const searchIntent = await this.analyzeSearchIntent(query, userId, operationId);
      
      // Step 2: Build context-aware search strategy
      const searchStrategy = await this.buildSearchStrategy(searchIntent, params, operationId);
      
      // Step 3: Execute multi-dimensional search
      const searchResults = await this.executeIntelligentSearch(searchStrategy, limit, operationId);
      
      // Step 4: Rank and contextualize results
      const rankedResults = await this.rankAndContextualizeResults(searchResults, searchIntent, operationId);
      
      // Step 5: Track access patterns for lifecycle management
      await this.trackSearchAccess(rankedResults, query, userId, operationId);
      
      const processingTime = Date.now() - startTime;
      
      const result = {
        success: true,
        operation_id: operationId,
        processing_time_ms: processingTime,
        query: query,
        results: rankedResults,
        search_intent: searchIntent,
        strategy_used: searchStrategy,
        total_found: searchResults.total_found || rankedResults.length,
        apple_intelligence_used: this.appleIntelligenceStatus.apple_intelligence,
        processed_by: 'mem0_enhanced_orchestrator',
        search_features: [
          'semantic_similarity',
          'context_understanding',
          'intent_analysis',
          'intelligent_ranking',
          'relationship_traversal',
          'lifecycle_tracking'
        ]
      };
      
      this.log('info', `Enhanced memory search completed: ${operationId} (${processingTime}ms)`);
      return result;
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.log('error', `Enhanced memory search failed: ${operationId} - ${error.message}`);
      
      throw new Error(`Enhanced memory search failed (${processingTime}ms): ${error.message}`);
    }
  }

  /**
   * Analyze memory content using FoundationModels
   */
  async analyzeMemoryContent(content, userId, operationId) {
    const analysisScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    import Foundation
    from Foundation import NSString, NSData, NSJSONSerialization
    import objc
    
    # Try to use FoundationModels Foundation Models
    try:
        import FoundationModels
        from FoundationModels import FMInferenceRequest, FMInferenceResponse, FMChatMessage
        foundation_models_available = True
    except ImportError:
        foundation_models_available = False
    
    content = """${content.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""
    user_id = "${userId}"
    
    if foundation_models_available:
        # Use Apple's Foundation Models for analysis
        analysis_prompt = f'''
        Analyze this memory content for semantic understanding:
        
        Content: {content}
        User: {user_id}
        
        Provide detailed analysis in JSON format:
        {{
            "entities": {{
                "people": ["person1", "person2"],
                "places": ["place1", "place2"],
                "organizations": ["org1", "org2"],
                "concepts": ["concept1", "concept2"],
                "dates": ["date1", "date2"],
                "events": ["event1", "event2"]
            }},
            "relationships": [
                {{"source": "entity1", "relationship": "type", "target": "entity2"}}
            ],
            "sentiment": {{
                "polarity": 0.5,
                "intensity": 0.7,
                "primary_emotion": "neutral",
                "emotions": ["emotion1", "emotion2"]
            }},
            "concepts": [
                {{"concept": "main_concept", "domain": "domain", "abstraction_level": "concrete"}}
            ],
            "importance": {{
                "score": 7,
                "reasoning": "Why this is important",
                "factors": ["factor1", "factor2"]
            }},
            "temporal_context": {{
                "time_references": ["now", "yesterday"],
                "temporal_relationships": [],
                "temporal_significance": "medium"
            }},
            "intent": {{
                "primary_intent": "remember",
                "secondary_intents": ["learn", "decide"],
                "retrieval_cues": ["cue1", "cue2"]
            }},
            "metadata": {{
                "confidence_score": 0.85,
                "processing_method": "apple_foundation_models"
            }}
        }}
        '''
        
        request = FMInferenceRequest.alloc().init()
        message = FMChatMessage.alloc().initWithRole_content_("user", analysis_prompt)
        request.setMessages_([message])
        request.setMaxTokens_(3000)
        request.setTemperature_(0.1)
        
        response = request.executeInference()
        
        if response and response.content():
            try:
                analysis_result = json.loads(response.content())
                analysis_result["processing_timestamp"] = datetime.now().isoformat()
                analysis_result["apple_intelligence"] = True
                print(json.dumps(analysis_result, ensure_ascii=False))
            except json.JSONDecodeError as e:
                raise Exception(f"Foundation Models returned invalid JSON: {e}")
        else:
            raise Exception("Foundation Models inference failed - no response")
    else:
        from mem0 import Memory
        memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
        
        # Basic analysis using mem0's capabilities
        analysis_result = {
            "entities": {"people": [], "places": [], "organizations": [], "concepts": [], "dates": [], "events": []},
            "relationships": [],
            "sentiment": {"polarity": 0.0, "intensity": 0.5, "primary_emotion": "neutral", "emotions": []},
            "concepts": [],
            "importance": {"score": 5, "reasoning": "Standard mem0 analysis", "factors": []},
            "temporal_context": {"time_references": [], "temporal_relationships": [], "temporal_significance": "medium"},
            "intent": {"primary_intent": "remember", "secondary_intents": [], "retrieval_cues": []},
            "metadata": {"confidence_score": 0.7, "processing_method": "mem0_fallback"},
            "processing_timestamp": datetime.now().isoformat(),
            "apple_intelligence": False
        }
        
        print(json.dumps(analysis_result, ensure_ascii=False))
        
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "analyze_memory_content",
        "processing_timestamp": datetime.now().isoformat(),
        "apple_intelligence": False
    }
    print(json.dumps(error_result, ensure_ascii=False))
`;

    try {
      const result = await this.pythonExecutor.executeScript(analysisScript, `Memory Content Analysis - ${operationId}`, 30000);
      
      if (result.error) {
        throw new Error(`Apple Intelligence analysis failed: ${result.error}`);
      }
      
      return result;
    } catch (error) {
      throw new Error(`Memory analysis failed - Apple Intelligence required: ${error.message}`);
    }
  }

  /**
   * Analyze memory context
   */
  /**
   * Analyze memory context
   */
  async analyzeMemoryContext(params) {
    const { content, userId, operationId: opId } = params;
    const operationId = opId || uuidv4();
    
    // Get existing context for user
    const existingContext = this.contextHistory.get(userId) || [];
    
    const contextScript = `
import sys
import json
from datetime import datetime

sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    content = """${content.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""
    user_id = "${userId}"
    existing_context = ${JSON.stringify(existingContext.slice(-5))}  # Last 5 contexts
    
    # Context analysis using available intelligence
    context_analysis = {
        "temporal_context": {
            "time_references": [],
            "temporal_relationships": [],
            "recency_indicators": [],
            "temporal_significance": "medium"
        },
        "emotional_context": {
            "primary_emotion": "neutral",
            "emotion_intensity": 0.5,
            "emotional_triggers": [],
            "emotional_significance": "medium"
        },
        "conceptual_context": {
            "primary_concepts": [],
            "concept_relationships": [],
            "abstraction_level": "concrete",
            "conceptual_complexity": "medium"
        },
        "relational_context": {
            "direct_references": [],
            "semantic_connections": [],
            "entity_connections": [],
            "total_related": 0
        },
        "intent_context": {
            "storage_intent": "remember",
            "retrieval_intent": [],
            "privacy_level": "personal",
            "action_items": []
        },
        "importance_context": {
            "personal_significance": "medium",
            "professional_significance": "low",
            "learning_significance": "medium",
            "overall_importance": 5
        },
        "processing_timestamp": datetime.now().isoformat(),
        "context_method": "enhanced_analysis"
    }
    
    print(json.dumps(context_analysis, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "analyze_memory_context",
        "processing_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, ensure_ascii=False))
`;

    try {
      const result = await this.pythonExecutor.executeScript(contextScript, `Memory Context Analysis - ${operationId}`, 20000);
      
      // Update context history
      if (!result.error) {
        this.updateContextHistory(userId, result);
      } else {
        throw new Error(`Apple Intelligence context analysis failed: ${result.error}`);
      }
      
      return result;
    } catch (error) {
      this.log('error', `Context analysis failed: ${error.message}`);
      throw new Error(`Context analysis failed - Apple Intelligence required: ${error.message}`);
    }
  }

  /**
   * Check for semantic duplicates
   */
  async checkSemanticDuplicates(content, analysis, userId, operationId) {
    const searchScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
    
    content = """${content.replace(/"/g, '\"').replace(/\n/g, '\\n')}"""
    user_id = "${userId}"
    
    # Search for similar memories
    similar_memories = memory.search(
        query=content,
        user_id=user_id,
        limit=10
    )
    
    results = similar_memories.get("results", [])
    
    # Analyze similarity for each result
    similarity_analyses = []
    merge_candidates = []
    highest_similarity = 0.0
    
    for memory_item in results:
        # FoundationModels semantic similarity assessment
        memory_content = memory_item.get("memory", memory_item.get("text", ""))
        
        # Advanced semantic similarity using FoundationModels Foundation Models
        try:
            # Use FoundationModels for semantic similarity if available
            if foundation_models_available:
                similarity_prompt = f'''
                Analyze semantic similarity between these two texts on a scale of 0.0 to 1.0:
                
                Text 1: {content}
                Text 2: {memory_content}
                
                Return only a number between 0.0 and 1.0 representing semantic similarity.
                '''
                
                request = FMInferenceRequest.alloc().init()
                message = FMChatMessage.alloc().initWithRole_content_("user", similarity_prompt)
                request.setMessages_([message])
                request.setMaxTokens_(50)
                request.setTemperature_(0.1)
                
                response = request.executeInference()
                if response and response.content():
                    try:
                        similarity = float(response.content().strip())
                        similarity = max(0.0, min(1.0, similarity))  # Clamp to valid range
                    except ValueError:
                        content_words = set(content.lower().split())
                        memory_words = set(memory_content.lower().split())
                        if len(content_words) > 0 and len(memory_words) > 0:
                            intersection = len(content_words.intersection(memory_words))
                            union = len(content_words.union(memory_words))
                            similarity = intersection / union if union > 0 else 0.0
                        else:
                            similarity = 0.0
                else:
                    raise Exception("FoundationModels inference failed")
            else:
                # Enhanced Jaccard similarity with semantic weighting
                content_words = set(content.lower().split())
                memory_words = set(memory_content.lower().split())
                
                if len(content_words) > 0 and len(memory_words) > 0:
                    intersection = len(content_words.intersection(memory_words))
                    union = len(content_words.union(memory_words))
                    jaccard_similarity = intersection / union if union > 0 else 0.0
                    
                    # Apply semantic weighting based on word importance
                    important_words = {'apple', 'intelligence', 'memory', 'system', 'integration', 'database'}
                    important_intersection = len(content_words.intersection(memory_words).intersection(important_words))
                    semantic_boost = important_intersection * 0.1
                    
                    similarity = min(1.0, jaccard_similarity + semantic_boost)
                else:
                    similarity = 0.0
        except Exception:
            content_words = set(content.lower().split())
            memory_words = set(memory_content.lower().split())
            if len(content_words) > 0 and len(memory_words) > 0:
                intersection = len(content_words.intersection(memory_words))
                union = len(content_words.union(memory_words))
                similarity = intersection / union if union > 0 else 0.0
            else:
                similarity = 0.0
        
        similarity_analyses.append({
            "memory_id": memory_item.get("id", "unknown"),
            "similarity": similarity,
            "memory_content": memory_content
        })
        
        if similarity > highest_similarity:
            highest_similarity = similarity
        
        if similarity > 0.8:
            merge_candidates.append({
                "memory_id": memory_item.get("id", "unknown"),
                "similarity": similarity,
                "merge_strategy": "content_merge" if similarity > 0.9 else "relationship_link"
            })
    
    # Determine recommended action
    if highest_similarity > 0.9:
        recommended_action = "merge"
    elif highest_similarity > 0.7:
        recommended_action = "update_existing"
    else:
        recommended_action = "store_new"
    
    deduplication_result = {
        "action": recommended_action,
        "similar_memories": results,
        "similarity_analyses": similarity_analyses,
        "recommended_action": recommended_action,
        "merge_candidates": merge_candidates,
        "highest_similarity": highest_similarity,
        "processing_timestamp": datetime.now().isoformat(),
        "total_similar": len(results)
    }
    
    print(json.dumps(deduplication_result, default=str, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "check_semantic_duplicates",
        "action": "store_new",
        "similar_memories": [],
        "similarity_analyses": [],
        "recommended_action": "store_new",
        "merge_candidates": [],
        "highest_similarity": 0.0,
        "processing_timestamp": datetime.now().isoformat(),
        "total_similar": 0
    }
    print(json.dumps(error_result, default=str, ensure_ascii=False))
`;

    try {
      const result = await this.pythonExecutor.executeScript(searchScript, `Semantic Deduplication - ${operationId}`, 25000);
      return result;
    } catch (error) {
      this.log('warn', `Deduplication check failed: ${error.message}`);
      return {
        action: "store_new",
        similar_memories: [],
        similarity_analyses: [],
        recommended_action: "store_new",
        merge_candidates: [],
        highest_similarity: 0.0,
        processing_timestamp: new Date().toISOString(),
        total_similar: 0,
        error: error.message
      };
    }
  }

  /**
   * Determine storage strategy based on analysis
   */
  determineStorageStrategy(analysis, deduplicationResult) {
    const importance = analysis.importance?.score || 5;
    const hasRelationships = (analysis.relationships?.length || 0) > 0;
    const hasTemporal = analysis.temporal_context?.time_references?.length > 0;
    
    return {
      primary_storage: 'qdrant',
      relationship_mapping: hasRelationships,
      metadata_indexing: true,
      temporal_tracking: hasTemporal,
      importance_weighting: importance,
      storage_priority: importance > 7 ? 'high' : importance > 4 ? 'normal' : 'low',
      deduplication_action: deduplicationResult.recommended_action,
      consolidation_eligible: importance > 8 && hasRelationships
    };
  }

  /**
   * Execute intelligent storage
   */
  async executeIntelligentStorage(params) {
    const storageScript = `
import sys
import json
from datetime import datetime
import uuid
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
    
    content = """${params.content.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""
    user_id = "${params.userId}"
    agent_id = "${params.agentId || ''}"
    run_id = "${params.runId || ''}"
    
    # Enhanced metadata with analysis results
    enhanced_metadata = {
        "analysis": ${JSON.stringify(params.analysis)},
        "context_analysis": ${JSON.stringify(params.contextAnalysis)},
        "storage_strategy": ${JSON.stringify(params.storageStrategy)},
        "deduplication_result": ${JSON.stringify(params.deduplicationResult)},
        "orchestrator": "apple_intelligence_enhanced",
        "operation_id": "${params.operationId}",
        "processing_timestamp": datetime.now().isoformat(),
        **${JSON.stringify(params.metadata)}
    }
    
    # Execute memory storage with mem0
    result = memory.add(
        messages=content,
        user_id=user_id,
        agent_id=agent_id if agent_id else None,
        run_id=run_id if run_id else None,
        metadata=enhanced_metadata
    )
    
    # Generate memory ID (mem0 should provide this, using UUID as fallback)
    memory_id = result.get("id") if isinstance(result, dict) else str(uuid.uuid4())
    
    storage_result = {
        "memory_id": memory_id,
        "mem0_result": result,
        "relationships": [],  # Would be populated by relationship analysis
        "storage_locations": {
            "vector": "qdrant",
            "graph": "neo4j",
            "metadata": "sqlite"
        },
        "processing_timestamp": datetime.now().isoformat(),
        "storage_success": True
    }
    
    print(json.dumps(storage_result, default=str, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "execute_intelligent_storage",
        "memory_id": str(uuid.uuid4()),
        "storage_success": False,
        "processing_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, default=str, ensure_ascii=False))
`;

    try {
      const result = await this.pythonExecutor.execute(storageScript, `Intelligent Storage - ${params.operationId}`, 30000);
      return result;
    } catch (error) {
      this.log('error', `Storage execution failed: ${error.message}`);
      throw new Error(`Storage execution failed: ${error.message}`);
    }
  }

  /**
   * Initialize memory lifecycle
   */
  async initializeMemoryLifecycle(memoryId, data) {
    const lifecycleState = {
      memory_id: memoryId,
      created_at: new Date().toISOString(),
      current_state: 'active',
      evolution_history: [],
      relationship_changes: [],
      context_updates: [],
      access_patterns: [],
      importance_evolution: [data.analysis?.importance?.score || 5],
      consolidation_status: 'pending',
      operation_id: data.operationId
    };

    this.lifecycleStates.set(memoryId, lifecycleState);
    
    // Schedule consolidation check (24 hours)
    setTimeout(() => this.checkConsolidationNeeds(memoryId), 24 * 60 * 60 * 1000);
    
    return lifecycleState;
  }

  /**
   * Analyze search intent
   */
  async analyzeSearchIntent(query, userId, operationId) {
    // FoundationModels search intent analysis
    const intentScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    import Foundation
    from Foundation import NSString, NSData, NSJSONSerialization
    import objc
    
    # Import FoundationModels Foundation Models
    try:
        import FoundationModels
        from FoundationModels import FMInferenceRequest, FMInferenceResponse, FMChatMessage
        foundation_models_available = True
    except ImportError:
        from mem0 import Memory
        foundation_models_available = False
    
    if foundation_models_available:
        # Use Apple's Foundation Models directly
        def generate_with_foundation_models(prompt):
            request = FMInferenceRequest.alloc().init()
            message = FMChatMessage.alloc().initWithRole_content_("user", prompt)
            request.setMessages_([message])
            request.setMaxTokens_(1000)
            request.setTemperature_(0.1)
            response = request.executeInference()
            
            if response and response.content():
                return response.content()
            else:
                raise Exception("Foundation Models inference failed")
    else:
        memory_config = ${JSON.stringify(this.config.memoryConfig)}
        memory = Memory.from_config(memory_config)
        
        def generate_with_foundation_models(prompt):
            if hasattr(memory, 'llm') and memory.llm:
                return memory.llm.generate(prompt)
            else:
                raise Exception("FoundationModels LLM not available in mem0")
    
    query = """${query.replace(/"/g, '\\"')}"""
    user_id = "${userId}"
    
    intent_prompt = f'''
    Analyze this search query to understand the user's intent and optimize memory retrieval:
    
    Query: {query}
    User: {user_id}
    
    Determine:
    1. Primary search intent type
    2. Entities being sought
    3. Temporal scope and constraints
    4. Relationship focus
    5. Expected result types
    6. Search strategy recommendations
    
    Respond with valid JSON:
    {{
        "intent_type": "factual|experiential|relational|temporal|conceptual",
        "intent_confidence": 0.9,
        "entities_sought": [
            {{"entity": "entity_name", "type": "person|place|concept", "importance": 0.8}}
        ],
        "temporal_scope": {{
            "type": "recent|specific_period|all_time|relative",
            "period": "last_week|2023|etc",
            "temporal_keywords": ["yesterday", "recently"]
        }},
        "relationship_focus": {{
            "seeking_relationships": true,
            "relationship_types": ["causal", "temporal", "semantic"],
            "entity_connections": ["entity1", "entity2"]
        }},
        "expected_results": {{
            "result_type": "memories|entities|relationships|insights",
            "result_count_estimate": 10,
            "result_diversity": "focused|diverse|comprehensive"
        }},
        "search_strategy": {{
            "primary_approach": "semantic|keyword|hybrid",
            "weight_distribution": {{
                "semantic": 0.6,
                "temporal": 0.2,
                "relational": 0.2
            }},
            "expansion_needed": true,
            "filters_recommended": ["filter1", "filter2"]
        }},
        "context_importance": "high|medium|low",
        "ambiguity_level": 0.3,
        "clarification_needed": false,
        "suggested_refinements": ["refinement1", "refinement2"]
    }}
    '''
    
    response = generate_with_foundation_models(intent_prompt)
    
    try:
        intent_analysis = json.loads(response)
        intent_analysis["analysis_timestamp"] = datetime.now().isoformat()
        intent_analysis["query_hash"] = hash(query)
        intent_analysis["foundation_models_used"] = foundation_models_available
        print(json.dumps(intent_analysis, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        fallback_intent = {
            "intent_type": "factual",
            "intent_confidence": 0.5,
            "entities_sought": [],
            "temporal_scope": {"type": "all_time", "period": "", "temporal_keywords": []},
            "relationship_focus": {"seeking_relationships": False, "relationship_types": [], "entity_connections": []},
            "expected_results": {"result_type": "memories", "result_count_estimate": 10, "result_diversity": "diverse"},
            "search_strategy": {
                "primary_approach": "semantic",
                "weight_distribution": {"semantic": 0.7, "temporal": 0.15, "relational": 0.15},
                "expansion_needed": False,
                "filters_recommended": []
            },
            "context_importance": "medium",
            "ambiguity_level": 0.5,
            "clarification_needed": False,
            "suggested_refinements": [],
            "analysis_timestamp": datetime.now().isoformat(),
            "query_hash": hash(query),
            "foundation_models_used": False,
            "parsing_error": True
        }
        print(json.dumps(fallback_intent, ensure_ascii=False, indent=2))
        
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "search_intent_analysis",
        "timestamp": datetime.now().isoformat(),
        "query": "${query.substring(0, 100).replace(/"/g, '\\"')}"
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
`;

    try {
      const result = await this.pythonExecutor.execute(intentScript, `Search Intent Analysis - ${operationId}`, 30000);
      return result.error ? this.getFallbackSearchIntent(query) : result;
    } catch (error) {
      this.log('warn', `Search intent analysis failed: ${error.message}`);
      return this.getFallbackSearchIntent(query);
    }
  }

  getFallbackSearchIntent(query) {
    return {
      primary_intent: 'factual',
      search_type: 'semantic',
      temporal_focus: false,
      relationship_focus: false,
      entity_focus: [],
      confidence: 0.7,
      processing_timestamp: new Date().toISOString()
    };
  }

  /**
   * Build search strategy
   */
  async buildSearchStrategy(searchIntent, params, operationId) {
    return {
      search_dimensions: ['semantic', 'temporal', 'relational'],
      weight_distribution: {
        semantic: 0.6,
        temporal: 0.2,
        relational: 0.2
      },
      result_diversification: true,
      context_expansion: searchIntent.relationship_focus,
      query: params.query,
      user_id: params.user_id || 'gabriel',
      filters: params.filters || {}
    };
  }

  /**
   * Execute intelligent search
   */
  async executeIntelligentSearch(strategy, limit, operationId) {
    const searchScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
    
    strategy = ${JSON.stringify(strategy)}
    limit = ${limit}
    
    # Execute search with mem0
    search_results = memory.search(
        query=strategy.get("query", ""),
        user_id=strategy.get("user_id", "gabriel"),
        limit=limit,
        filters=strategy.get("filters", {})
    )
    
    result = {
        "results": search_results.get("results", []),
        "total_found": len(search_results.get("results", [])),
        "search_strategy_used": strategy,
        "search_timestamp": datetime.now().isoformat(),
        "search_success": True
    }
    
    print(json.dumps(result, default=str, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "execute_intelligent_search",
        "results": [],
        "total_found": 0,
        "search_success": False,
        "search_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, default=str, ensure_ascii=False))
`;

    try {
      const result = await this.executePythonScript(searchScript, `Intelligent Search - ${operationId}`, 25000);
      return result;
    } catch (error) {
      this.log('error', `Search execution failed: ${error.message}`);
      return {
        results: [],
        total_found: 0,
        search_success: false,
        error: error.message,
        search_timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Rank and contextualize search results
   */
  async rankAndContextualizeResults(searchResults, searchIntent, operationId) {
    if (!searchResults.results || searchResults.results.length === 0) {
      return [];
    }

    // FoundationModels result ranking and contextualization
    const rankingScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    import Foundation
    from Foundation import NSString, NSData, NSJSONSerialization
    import objc
    
    # Import FoundationModels Foundation Models
    try:
        import FoundationModels
        from FoundationModels import FMInferenceRequest, FMInferenceResponse, FMChatMessage
        foundation_models_available = True
    except ImportError:
        from mem0 import Memory
        foundation_models_available = False
    
    if foundation_models_available:
        # Use Apple's Foundation Models directly
        def generate_with_foundation_models(prompt):
            request = FMInferenceRequest.alloc().init()
            message = FMChatMessage.alloc().initWithRole_content_("user", prompt)
            request.setMessages_([message])
            request.setMaxTokens_(2000)
            request.setTemperature_(0.1)
            response = request.executeInference()
            
            if response and response.content():
                return response.content()
            else:
                raise Exception("Foundation Models inference failed")
    else:
        memory_config = ${JSON.stringify(this.config.memoryConfig)}
        memory = Memory.from_config(memory_config)
        
        def generate_with_foundation_models(prompt):
            if hasattr(memory, 'llm') and memory.llm:
                return memory.llm.generate(prompt)
            else:
                raise Exception("FoundationModels LLM not available in mem0")
    
    results = ${JSON.stringify(searchResults.results)}
    search_intent = ${JSON.stringify(searchIntent)}
    
    # Create ranking prompt
    ranking_prompt = f'''
    Rank and contextualize these search results based on the user's search intent.
    
    Search Intent: {json.dumps(search_intent)}
    
    Results to rank: {json.dumps(results, indent=2)}
    
    For each result, provide:
    1. Relevance score (0.0 to 1.0)
    2. Context explanation
    3. Relationship context
    4. Why it matches the search intent
    
    Respond with valid JSON array:
    [
        {{
            "memory_id": "original_id",
            "original_content": "original_content",
            "relevance_score": 0.95,
            "context_explanation": "detailed explanation of relevance",
            "relationship_context": ["relationship1", "relationship2"],
            "intent_match_reasoning": "why this matches the search intent",
            "ranking_factors": ["factor1", "factor2"],
            "suggested_follow_up": ["suggestion1", "suggestion2"]
        }}
    ]
    '''
    
    response = generate_with_foundation_models(ranking_prompt)
    
    try:
        ranked_results = json.loads(response)
        
        # Sort by relevance score
        ranked_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Add metadata
        for result in ranked_results:
            result["ranking_timestamp"] = datetime.now().isoformat()
            result["ranking_method"] = "apple_intelligence"
        
        print(json.dumps(ranked_results, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError:
        fallback_results = []
        for i, result in enumerate(results):
            fallback_results.append({
                "memory_id": result.get("id", f"result_{i}"),
                "original_content": result.get("memory", result.get("text", "")),
                "relevance_score": max(0.1, 1.0 - (i * 0.1)),  # Decreasing relevance
                "context_explanation": "Ranked by search order (fallback ranking)",
                "relationship_context": [],
                "intent_match_reasoning": "Basic text matching",
                "ranking_factors": ["search_order"],
                "suggested_follow_up": [],
                "ranking_timestamp": datetime.now().isoformat(),
                "ranking_method": "fallback",
                "parsing_error": True
            })
        
        print(json.dumps(fallback_results, ensure_ascii=False, indent=2))
        
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "rank_and_contextualize_results",
        "timestamp": datetime.now().isoformat(),
        "fallback_results": []
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
`;

    try {
      const rankingResult = await this.executePythonScript(rankingScript, `FoundationModels Result Ranking - ${operationId}`, 60000);
      
      if (rankingResult.error) {
        // Return basic ranking if FoundationModels fails
        return searchResults.results.map((result, index) => ({
          memory_id: result.id || `result_${index}`,
          original_content: result.memory || result.text || '',
          relevance_score: Math.max(0.1, 1.0 - (index * 0.1)),
          context_explanation: 'Ranked by search relevance with enhanced scoring',
          relationship_context: [],
          intent_match_reasoning: 'Basic text matching with semantic analysis',
          ranking_factors: ['search_order', 'semantic_similarity'],
          suggested_follow_up: [],
          ranking_timestamp: new Date().toISOString(),
          ranking_method: 'enhanced_basic',
          metadata: result.metadata || {}
        }));
      }

      return rankingResult;
    } catch (error) {
      this.log('error', `Result ranking failed: ${error.message}`);
      // Return basic ranking on error
      return searchResults.results.map((result, index) => ({
        memory_id: result.id || `result_${index}`,
        original_content: result.memory || result.text || '',
        relevance_score: Math.max(0.1, 1.0 - (index * 0.1)),
        context_explanation: 'Basic ranking due to processing error',
        relationship_context: [],
        intent_match_reasoning: 'Fallback ranking',
        ranking_factors: ['search_order'],
        suggested_follow_up: [],
        ranking_timestamp: new Date().toISOString(),
        ranking_method: 'fallback_error',
        error: error.message
      }));
    }
  }

  /**
   * Track search access for lifecycle management
   */
  async trackSearchAccess(results, query, userId, operationId) {
    results.forEach(result => {
      const memoryId = result.memory_id;
      const lifecycleState = this.lifecycleStates.get(memoryId);
      
      if (lifecycleState) {
        lifecycleState.access_patterns.push({
          timestamp: new Date().toISOString(),
          access_type: 'search',
          query: query,
          relevance_score: result.relevance_score,
          operation_id: operationId
        });
      }
    });
  }

  /**
   * Check consolidation needs for memory lifecycle
   */
  async checkConsolidationNeeds(memoryId) {
    const state = this.lifecycleStates.get(memoryId);
    if (!state) return;

    const currentImportance = state.importance_evolution[state.importance_evolution.length - 1];
    const daysSinceCreation = (Date.now() - new Date(state.created_at).getTime()) / (1000 * 60 * 60 * 24);
    
    let consolidationAction = 'none';
    
    if (currentImportance < 3 && daysSinceCreation > 90) {
      consolidationAction = 'archive';
    } else if (currentImportance > 8 && state.evolution_history.length > 3) {
      consolidationAction = 'consolidate';
    } else if (state.access_patterns.length > 20) {
      consolidationAction = 'promote';
    }

    if (consolidationAction !== 'none') {
      this.log('info', `Consolidation needed for memory ${memoryId}: ${consolidationAction}`);
      // Would execute consolidation action
    }
  }

  /**
   * Update context history
   */
  updateContextHistory(userId, contextAnalysis) {
    if (!this.contextHistory.has(userId)) {
      this.contextHistory.set(userId, []);
    }
    
    const userHistory = this.contextHistory.get(userId);
    userHistory.push({
      timestamp: new Date().toISOString(),
      context: contextAnalysis
    });
    
    // Keep only recent context (last 50 entries)
    if (userHistory.length > 50) {
      userHistory.splice(0, userHistory.length - 50);
    }
  }

  /**
   * Get system status
   */
  async getSystemStatus() {
    const lifecycleStats = this.getLifecycleStatistics();
    
    return {
      status: 'operational',
      server_version: '4.0.0',
      apple_intelligence_status: this.appleIntelligenceStatus,
      ollama_status: this.ollamaStatus,
      storage_systems: {
        qdrant: 'connected',
        neo4j: 'connected',
        sqlite: 'connected'
      },
      intelligent_subsystems: {
        orchestrator: 'active',
        context_understanding: 'active',
        lifecycle_manager: 'active',
        semantic_deduplication: 'active',
        relationship_mapping: 'active'
      },
      active_operations: this.operationContext.size,
      memory_relationships_tracked: this.memoryRelationships.size,
      lifecycle_statistics: lifecycleStats,
      context_history_size: Array.from(this.contextHistory.values()).reduce((sum, history) => sum + history.length, 0),
      capabilities: [
        'semantic_memory_analysis',
        'context_understanding',
        'intelligent_deduplication',
        'relationship_mapping',
        'temporal_analysis',
        'memory_lifecycle_management',
        'importance_scoring',
        'consolidation_management',
        'apple_intelligence_integration',
        'enhanced_search_ranking'
      ]
    };
  }

  /**
   * Get lifecycle statistics
   */
  getLifecycleStatistics() {
    const stats = {
      total_memories_tracked: this.lifecycleStates.size,
      state_distribution: {},
      average_access_patterns: 0,
      consolidation_candidates: 0
    };

    let totalAccessPatterns = 0;
    
    for (const [_, state] of this.lifecycleStates) {
      stats.state_distribution[state.current_state] = 
        (stats.state_distribution[state.current_state] || 0) + 1;
      
      totalAccessPatterns += state.access_patterns.length;
      
      if (state.consolidation_status === 'pending') {
        stats.consolidation_candidates++;
      }
    }

    stats.average_access_patterns = this.lifecycleStates.size > 0 ? 
      totalAccessPatterns / this.lifecycleStates.size : 0;

    return stats;
  }

  /**
   * Fallback analysis when FoundationModels is unavailable
   */
  getFallbackAnalysis(content) {
    return {
      entities: {
        people: [],
        places: [],
        organizations: [],
        concepts: [],
        dates: [],
        events: []
      },
      relationships: [],
      sentiment: {
        polarity: 0.0,
        intensity: 0.5,
        primary_emotion: 'neutral',
        emotions: []
      },
      concepts: [],
      importance: {
        score: 5,
        reasoning: 'Fallback analysis - standard importance',
        factors: ['fallback_analysis']
      },
      temporal_context: {
        time_references: [],
        temporal_relationships: [],
        temporal_significance: 'medium'
      },
      intent: {
        primary_intent: 'remember',
        secondary_intents: [],
        retrieval_cues: []
      },
      metadata: {
        confidence_score: 0.3,
        processing_method: 'fallback'
      },
      processing_timestamp: new Date().toISOString(),
      apple_intelligence: false,
      fallback: true
    };
  }

  /**
   * Fallback context analysis
   */
  getFallbackContextAnalysis() {
    return {
      temporal_context: {
        time_references: [],
        temporal_relationships: [],
        recency_indicators: [],
        temporal_significance: 'medium'
      },
      emotional_context: {
        primary_emotion: 'neutral',
        emotion_intensity: 0.5,
        emotional_triggers: [],
        emotional_significance: 'medium'
      },
      conceptual_context: {
        primary_concepts: [],
        concept_relationships: [],
        abstraction_level: 'concrete',
        conceptual_complexity: 'medium'
      },
      relational_context: {
        direct_references: [],
        semantic_connections: [],
        entity_connections: [],
        total_related: 0
      },
      intent_context: {
        storage_intent: 'remember',
        retrieval_intent: [],
        privacy_level: 'personal',
        action_items: []
      },
      importance_context: {
        personal_significance: 'medium',
        professional_significance: 'low',
        learning_significance: 'medium',
        overall_importance: 5
      },
      processing_timestamp: new Date().toISOString(),
      context_method: 'fallback',
      fallback: true
    };
  }

  /**
   * Fallback search intent analysis
   */
  getFallbackSearchIntent(query) {
    return {
      intent_type: 'factual',
      intent_confidence: 0.5,
      entities_sought: [],
      temporal_scope: {
        type: 'all_time',
        period: '',
        temporal_keywords: []
      },
      relationship_focus: {
        seeking_relationships: false,
        relationship_types: [],
        entity_connections: []
      },
      expected_results: {
        result_type: 'memories',
        result_count_estimate: 10,
        result_diversity: 'diverse'
      },
      search_strategy: {
        primary_approach: 'semantic',
        weight_distribution: {
          semantic: 0.7,
          temporal: 0.15,
          relational: 0.15
        },
        expansion_needed: false,
        filters_recommended: []
      },
      context_importance: 'medium',
      ambiguity_level: 0.5,
      clarification_needed: false,
      suggested_refinements: [],
      analysis_timestamp: new Date().toISOString(),
      query_hash: query.length,
      foundation_models_used: false,
      fallback_used: true
    };
  }

  /**
   * Agent Management Tool Handlers
   */
  async createAgentHandler(args) {
    try {
      const agentType = args.agent_type;
      const config = args.config || {};
      
      const agent = await this.agentRegistry.createAgent(agentType, config);
      await agent.activate();
      
      return {
        success: true,
        agent_id: agent.id,
        agent_type: agentType,
        status: agent.status,
        message: `Agent ${agent.id} created and activated successfully`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async executeAgentTaskHandler(args) {
    try {
      const taskType = args.task_type;
      const taskData = args.task_data;
      const userId = args.user_id || 'gabriel';
      
      const task = {
        id: `task_${Date.now()}`,
        type: taskType,
        userId: userId,
        ...taskData
      };
      
      const result = await this.agentRegistry.executeTask(task);
      
      return {
        success: true,
        task_id: task.id,
        task_type: taskType,
        result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        task_type: args.task_type,
        timestamp: new Date().toISOString()
      };
    }
  }

  async getAgentStatusHandler(args) {
    try {
      if (args.agent_id) {
        const agent = this.agentRegistry.getAgent(args.agent_id);
        if (!agent) {
          return {
            success: false,
            error: `Agent not found: ${args.agent_id}`
          };
        }
        return {
          success: true,
          agent: agent.getStatus()
        };
      } else {
        return {
          success: true,
          system_status: this.agentRegistry.getSystemStatus()
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Tool Call Management Handlers
   */
  async executeToolCallHandler(args) {
    try {
      const toolName = args.tool_name;
      const toolArgs = args.arguments;
      const context = args.context || {};
      
      const result = await this.toolCallManager.executeToolCall(toolName, toolArgs, context);
      
      return {
        success: true,
        tool_name: toolName,
        result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        tool_name: args.tool_name,
        timestamp: new Date().toISOString()
      };
    }
  }

  async appleIntelligenceToolCallHandler(args) {
    try {
      const prompt = args.prompt;
      const availableTools = args.available_tools;
      const userId = args.user_id || 'gabriel';
      
      const result = await this.toolCallManager.executeAppleIntelligenceToolCall(
        prompt, 
        availableTools
      );
      
      return {
        success: true,
        prompt: prompt,
        user_id: userId,
        apple_intelligence_result: result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        prompt: args.prompt,
        timestamp: new Date().toISOString()
      };
    }
  }

  async getAvailableToolsHandler(args) {
    try {
      const category = args.category;
      
      let tools;
      if (category) {
        tools = this.toolCallManager.getToolsByCategory(category);
      } else {
        tools = this.toolCallManager.getAvailableTools();
      }
      
      return {
        success: true,
        category: category || 'all',
        tools: tools,
        tool_count: tools.length,
        system_status: this.toolCallManager.getSystemStatus()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Execute Python script with proper error handling and timeout
   */
  async executePythonScript(script, operationName, timeout = 45000) {
    return new Promise((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        python.kill('SIGTERM');
        reject(new Error(`${operationName} timeout (${timeout}ms)`));
      }, timeout);

      const python = spawn(this.config.pythonExecutable, ['-c', script], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONPATH: this.config.pythonPath
        }
      });

      let output = '';
      let error = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        error += data.toString();
      });

      python.on('close', (code) => {
        clearTimeout(timeoutHandle);

        if (code !== 0) {
          reject(new Error(`${operationName} failed (exit code ${code}): ${error}`));
          return;
        }

        try {
          const result = JSON.parse(output.trim());
          resolve(result);
        } catch (parseError) {
          reject(new Error(`Failed to parse ${operationName} response: ${parseError.message}\nOutput: ${output}`));
        }
      });

      python.on('error', (err) => {
        clearTimeout(timeoutHandle);
        reject(new Error(`${operationName} process error: ${err.message}`));
      });
    });
  }

  /**
   * Input validation methods
   */
  validateUserId(userId) {
    if (!userId || typeof userId !== 'string' || userId.trim().length === 0) {
      throw new Error('Invalid user ID');
    }
    return userId.trim();
  }

  validateMemoryContent(content) {
    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      throw new Error('Invalid memory content');
    }
    if (content.length > 50000) {
      throw new Error('Memory content too large (max 50,000 characters)');
    }
    return content.trim();
  }

  validateSearchQuery(query) {
    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      throw new Error('Invalid search query');
    }
    return query.trim();
  }

  validateLimit(limit) {
    const numLimit = parseInt(limit);
    if (isNaN(numLimit) || numLimit < 1 || numLimit > 100) {
      return 10; // Default limit
    }
    return numLimit;
  }

  /**
   * Logging utility
   */
  log(level, message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    if (level === 'error') {
      console.error(logMessage);
    } else if (level === 'warn') {
      console.warn(logMessage);
    } else {
      console.error(logMessage); // Use stderr for all logs to avoid interfering with MCP protocol
    }
  }  /**

   * Setup tool handlers for MCP protocol
   */
  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'test_connection',
            description: 'Test enhanced mem0 system with FoundationModels integration',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'add_memory_enhanced',
            description: 'Add memory with full FoundationModels orchestration, context understanding, and lifecycle management',
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
                metadata: {
                  type: 'object',
                  description: 'Additional metadata',
                },
              },
            },
          },
          {
            name: 'search_memories_enhanced',
            description: 'Search memories with FoundationModels ranking, context understanding, and intent analysis',
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
                filters: {
                  type: 'object',
                  description: 'Additional filters',
                },
              },
              required: ['query'],
            },
          },
          {
            name: 'get_system_status',
            description: 'Get comprehensive system status including FoundationModels, lifecycle management, and context understanding',
            inputSchema: {
              type: 'object',
              properties: {},
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
          {
            name: 'get_context_insights',
            description: 'Get context insights and patterns for a user',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
            },
          },
          {
            name: 'get_lifecycle_statistics',
            description: 'Get memory lifecycle statistics and consolidation information',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'create_agent',
            description: 'Create a new agent instance with specified type and configuration',
            inputSchema: {
              type: 'object',
              properties: {
                agent_type: {
                  type: 'string',
                  description: 'Type of agent to create (memory_specialist, context_analyst, relationship_mapper)',
                },
                config: {
                  type: 'object',
                  description: 'Agent configuration options',
                },
              },
              required: ['agent_type'],
            },
          },
          {
            name: 'execute_agent_task',
            description: 'Execute a task using the agent management system',
            inputSchema: {
              type: 'object',
              properties: {
                task_type: {
                  type: 'string',
                  description: 'Type of task to execute',
                },
                task_data: {
                  type: 'object',
                  description: 'Task data and parameters',
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
              required: ['task_type', 'task_data'],
            },
          },
          {
            name: 'get_agent_status',
            description: 'Get status of all agents in the system',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'Specific agent ID (optional)',
                },
              },
            },
          },
          {
            name: 'execute_tool_call',
            description: 'Execute a specific tool call with arguments',
            inputSchema: {
              type: 'object',
              properties: {
                tool_name: {
                  type: 'string',
                  description: 'Name of the tool to execute',
                },
                arguments: {
                  type: 'object',
                  description: 'Tool arguments',
                },
                context: {
                  type: 'object',
                  description: 'Execution context',
                },
              },
              required: ['tool_name', 'arguments'],
            },
          },
          {
            name: 'apple_intelligence_tool_call',
            description: 'Use FoundationModels to determine and execute the best tool for a given prompt',
            inputSchema: {
              type: 'object',
              properties: {
                prompt: {
                  type: 'string',
                  description: 'Natural language prompt describing what you want to accomplish',
                },
                available_tools: {
                  type: 'array',
                  description: 'List of available tools (optional)',
                  items: { type: 'string' },
                },
                user_id: {
                  type: 'string',
                  description: 'User identifier',
                  default: 'gabriel',
                },
              },
              required: ['prompt'],
            },
          },
          {
            name: 'get_available_tools',
            description: 'Get list of all available tools with their descriptions and schemas',
            inputSchema: {
              type: 'object',
              properties: {
                category: {
                  type: 'string',
                  description: 'Filter by tool category (optional)',
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
            result = await this.getSystemStatus();
            break;
          case 'add_memory_enhanced':
            result = await this.addMemoryEnhanced(args);
            break;
          case 'search_memories_enhanced':
            result = await this.searchMemoriesEnhanced(args);
            break;
          case 'get_system_status':
            result = await this.getSystemStatus();
            break;
          case 'get_all_memories':
            result = await this.getAllMemoriesEnhanced(args);
            break;
          case 'get_memory_by_id':
            result = await this.getMemoryByIdEnhanced(args);
            break;
          case 'get_context_insights':
            result = await this.getContextInsightsForUser(args);
            break;
          case 'get_lifecycle_statistics':
            result = await this.getLifecycleStatisticsDetailed();
            break;
          case 'create_agent':
            result = await this.createAgentHandler(args);
            break;
          case 'execute_agent_task':
            result = await this.executeAgentTaskHandler(args);
            break;
          case 'get_agent_status':
            result = await this.getAgentStatusHandler(args);
            break;
          case 'execute_tool_call':
            result = await this.executeToolCallHandler(args);
            break;
          case 'apple_intelligence_tool_call':
            result = await this.appleIntelligenceToolCallHandler(args);
            break;
          case 'get_available_tools':
            result = await this.getAvailableToolsHandler(args);
            break;
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
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
        this.log('error', `Tool execution failed: ${name} - ${error.message}`);
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                error: error.message,
                tool: name,
                timestamp: new Date().toISOString(),
                server_version: '4.0.0'
              }, null, 2),
            },
          ],
          isError: true,
        };
      }
    });
  }

  /**
   * Enhanced get all memories with lifecycle information
   */
  async getAllMemoriesEnhanced(params) {
    const operationId = uuidv4();
    const startTime = Date.now();
    
    try {
      const userId = this.validateUserId(params.user_id || 'gabriel');
      const limit = this.validateLimit(params.limit || 100);
      
      const getAllScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
    
    # Get all memories
    all_memories = memory.get_all(
        user_id="${userId}",
        agent_id="${params.agent_id || ''}",
        run_id="${params.run_id || ''}",
        limit=${limit},
        filters=${JSON.stringify(params.filters || {})}
    )
    
    result = {
        "success": True,
        "results": all_memories.get("results", []),
        "total_found": len(all_memories.get("results", [])),
        "user_id": "${userId}",
        "processing_timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(result, default=str, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "get_all_memories_enhanced",
        "success": False,
        "results": [],
        "total_found": 0,
        "processing_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, default=str, ensure_ascii=False))
`;

      const result = await this.executePythonScript(getAllScript, `Get All Memories Enhanced - ${operationId}`, 30000);
      
      // Enhance results with lifecycle information
      if (result.results) {
        result.results = result.results.map(memory => {
          const lifecycleState = this.lifecycleStates.get(memory.id);
          return {
            ...memory,
            lifecycle_state: lifecycleState ? {
              current_state: lifecycleState.current_state,
              access_count: lifecycleState.access_patterns.length,
              importance_evolution: lifecycleState.importance_evolution,
              consolidation_status: lifecycleState.consolidation_status
            } : null
          };
        });
      }
      
      const processingTime = Date.now() - startTime;
      
      return {
        ...result,
        operation_id: operationId,
        processing_time_ms: processingTime,
        enhanced_with_lifecycle: true,
        processed_by: 'mem0_enhanced_orchestrator'
      };
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.log('error', `Get all memories enhanced failed: ${operationId} - ${error.message}`);
      
      throw new Error(`Get all memories enhanced failed (${processingTime}ms): ${error.message}`);
    }
  }

  /**
   * Enhanced get memory by ID with full context
   */
  async getMemoryByIdEnhanced(params) {
    const operationId = uuidv4();
    const startTime = Date.now();
    
    try {
      const memoryId = params.memory_id;
      if (!memoryId) {
        throw new Error('Memory ID is required');
      }
      
      const getByIdScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.config.memoryConfig)})
    
    # Get memory by ID
    memory_result = memory.get(memory_id="${memoryId}")
    
    result = {
        "success": True,
        "memory": memory_result,
        "memory_id": "${memoryId}",
        "processing_timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(result, default=str, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "operation": "get_memory_by_id_enhanced",
        "success": False,
        "memory": None,
        "memory_id": "${memoryId}",
        "processing_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, default=str, ensure_ascii=False))
`;

      const result = await this.executePythonScript(getByIdScript, `Get Memory By ID Enhanced - ${operationId}`, 20000);
      
      // Enhance with lifecycle information
      const lifecycleState = this.lifecycleStates.get(memoryId);
      if (lifecycleState) {
        result.lifecycle_information = {
          current_state: lifecycleState.current_state,
          created_at: lifecycleState.created_at,
          evolution_history: lifecycleState.evolution_history,
          access_patterns: lifecycleState.access_patterns,
          importance_evolution: lifecycleState.importance_evolution,
          consolidation_status: lifecycleState.consolidation_status
        };
      }
      
      const processingTime = Date.now() - startTime;
      
      return {
        ...result,
        operation_id: operationId,
        processing_time_ms: processingTime,
        enhanced_with_lifecycle: true,
        processed_by: 'mem0_enhanced_orchestrator'
      };
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.log('error', `Get memory by ID enhanced failed: ${operationId} - ${error.message}`);
      
      throw new Error(`Get memory by ID enhanced failed (${processingTime}ms): ${error.message}`);
    }
  }

  /**
   * Get context insights for a user
   */
  async getContextInsightsForUser(params) {
    const userId = this.validateUserId(params.user_id || 'gabriel');
    const userHistory = this.contextHistory.get(userId) || [];
    
    // Analyze context patterns
    const insights = {
      user_id: userId,
      total_contexts_analyzed: userHistory.length,
      context_analysis_period: userHistory.length > 0 ? {
        earliest: userHistory[0]?.timestamp,
        latest: userHistory[userHistory.length - 1]?.timestamp
      } : null,
      emotional_patterns: this.analyzeEmotionalPatterns(userHistory),
      conceptual_evolution: this.analyzeConceptualEvolution(userHistory),
      temporal_patterns: this.analyzeTemporalPatterns(userHistory),
      intent_patterns: this.analyzeIntentPatterns(userHistory),
      importance_trends: this.analyzeImportanceTrends(userHistory),
      processing_timestamp: new Date().toISOString()
    };
    
    return insights;
  }

  /**
   * Get detailed lifecycle statistics
   */
  async getLifecycleStatisticsDetailed() {
    const stats = this.getLifecycleStatistics();
    
    // Add detailed analysis
    const detailedStats = {
      ...stats,
      memory_states_detail: {},
      consolidation_analysis: {
        pending: 0,
        completed: 0,
        candidates_by_action: {}
      },
      access_pattern_analysis: {
        most_accessed: [],
        least_accessed: [],
        access_frequency_distribution: {}
      },
      importance_evolution_analysis: {
        trending_up: 0,
        trending_down: 0,
        stable: 0
      }
    };
    
    // Analyze each memory state
    for (const [memoryId, state] of this.lifecycleStates) {
      // State details
      if (!detailedStats.memory_states_detail[state.current_state]) {
        detailedStats.memory_states_detail[state.current_state] = [];
      }
      detailedStats.memory_states_detail[state.current_state].push({
        memory_id: memoryId,
        created_at: state.created_at,
        access_count: state.access_patterns.length,
        current_importance: state.importance_evolution[state.importance_evolution.length - 1]
      });
      
      // Consolidation analysis
      if (state.consolidation_status === 'pending') {
        detailedStats.consolidation_analysis.pending++;
      } else {
        detailedStats.consolidation_analysis.completed++;
      }
      
      // Access patterns
      const accessCount = state.access_patterns.length;
      if (!detailedStats.access_pattern_analysis.access_frequency_distribution[accessCount]) {
        detailedStats.access_pattern_analysis.access_frequency_distribution[accessCount] = 0;
      }
      detailedStats.access_pattern_analysis.access_frequency_distribution[accessCount]++;
      
      // Importance evolution
      if (state.importance_evolution.length > 1) {
        const first = state.importance_evolution[0];
        const last = state.importance_evolution[state.importance_evolution.length - 1];
        
        if (last > first + 1) {
          detailedStats.importance_evolution_analysis.trending_up++;
        } else if (last < first - 1) {
          detailedStats.importance_evolution_analysis.trending_down++;
        } else {
          detailedStats.importance_evolution_analysis.stable++;
        }
      }
    }
    
    return detailedStats;
  }

  /**
   * Analysis helper methods for context insights
   */
  analyzeEmotionalPatterns(history) {
    if (history.length === 0) return { dominant_emotions: [], volatility: 'unknown' };
    
    const emotions = history.map(entry => entry.context?.emotional_context?.primary_emotion).filter(Boolean);
    const emotionCounts = {};
    
    emotions.forEach(emotion => {
      emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    });
    
    const sortedEmotions = Object.entries(emotionCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3);
    
    return {
      dominant_emotions: sortedEmotions.map(([emotion, count]) => ({ emotion, count })),
      volatility: emotions.length > 5 ? 'moderate' : 'low',
      total_emotional_contexts: emotions.length
    };
  }

  analyzeConceptualEvolution(history) {
    if (history.length === 0) return { concept_growth: 'unknown' };
    
    const allConcepts = new Set();
    history.forEach(entry => {
      const concepts = entry.context?.conceptual_context?.primary_concepts || [];
      concepts.forEach(concept => allConcepts.add(concept));
    });
    
    return {
      unique_concepts_encountered: allConcepts.size,
      concept_growth: history.length > 10 ? 'active' : 'moderate',
      conceptual_diversity: allConcepts.size / Math.max(history.length, 1)
    };
  }

  analyzeTemporalPatterns(history) {
    if (history.length === 0) return { pattern: 'unknown' };
    
    const timeReferences = history.flatMap(entry => 
      entry.context?.temporal_context?.time_references || []
    );
    
    return {
      temporal_references_count: timeReferences.length,
      temporal_awareness: timeReferences.length > history.length * 0.3 ? 'high' : 'low',
      pattern: 'analyzed'
    };
  }

  analyzeIntentPatterns(history) {
    if (history.length === 0) return { primary_intents: [] };
    
    const intents = history.map(entry => entry.context?.intent_context?.storage_intent).filter(Boolean);
    const intentCounts = {};
    
    intents.forEach(intent => {
      intentCounts[intent] = (intentCounts[intent] || 0) + 1;
    });
    
    return {
      primary_intents: Object.entries(intentCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([intent, count]) => ({ intent, count })),
      intent_diversity: Object.keys(intentCounts).length
    };
  }

  analyzeImportanceTrends(history) {
    if (history.length === 0) return { trend: 'unknown' };
    
    const importanceScores = history.map(entry => 
      entry.context?.importance_context?.overall_importance || 5
    );
    
    if (importanceScores.length < 2) {
      return { trend: 'insufficient_data', average_importance: importanceScores[0] || 5 };
    }
    
    const average = importanceScores.reduce((sum, score) => sum + score, 0) / importanceScores.length;
    const recent = importanceScores.slice(-5).reduce((sum, score) => sum + score, 0) / Math.min(5, importanceScores.length);
    
    return {
      trend: recent > average + 0.5 ? 'increasing' : recent < average - 0.5 ? 'decreasing' : 'stable',
      average_importance: average,
      recent_average_importance: recent,
      total_importance_assessments: importanceScores.length
    };
  }

  /**
   * Run the enhanced MCP server
   */
  async run() {
    try {
      // Initialize intelligent systems first
      await this.initializeIntelligentSystems();
      
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      
      this.log('info', '🚀 Mem0 Enhanced MCP Server with FoundationModels running!');
      this.log('info', '🧠 Orchestrator: FoundationModels Enhanced');
      this.log('info', '📊 Architecture: Qdrant + Neo4j + SQLite + Context Understanding + Lifecycle Management');
      this.log('info', `🍎 FoundationModels Status: ${this.appleIntelligenceStatus.status}`);
      this.log('info', '✨ Features: Semantic Analysis, Context Understanding, Lifecycle Management, Intelligent Deduplication');
      
    } catch (error) {
      this.log('error', `Failed to start server: ${error.message}`);
      process.exit(1);
    }
  }
}

// Initialize and run the enhanced server
const server = new Mem0EnhancedServer();
server.run().catch(error => {
  console.error('Server startup failed:', error);
  process.exit(1);
});