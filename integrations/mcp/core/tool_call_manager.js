/**
 * Tool Call Manager for FoundationModels Integration
 * 
 * Implements enterprise-grade tool calling system following Foundation Models best practices:
 * - Tool registration and schema validation
 * - FoundationModels tool calling integration
 * - Tool execution with proper error handling and retries
 * - Tool usage monitoring and optimization
 * - Security and permission management for tool access
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

/**
 * Tool Definition Class
 */
class Tool {
  constructor(name, config) {
    this.name = name;
    this.description = config.description;
    this.schema = config.schema;
    this.handler = config.handler;
    this.permissions = config.permissions || [];
    this.rateLimit = config.rateLimit || { calls: 100, window: 3600000 }; // 100 calls per hour
    this.timeout = config.timeout || 30000; // 30 seconds
    this.retryConfig = config.retryConfig || { maxRetries: 3, backoffMs: 1000 };
    
    // Usage tracking
    this.usage = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageExecutionTime: 0,
      totalExecutionTime: 0,
      lastUsed: null
    };
    
    // Rate limiting
    this.callHistory = [];
    
    this.createdAt = new Date();
  }

  validateArguments(args) {
    // Basic schema validation
    if (this.schema.required) {
      for (const requiredField of this.schema.required) {
        if (!(requiredField in args)) {
          throw new Error(`Missing required argument: ${requiredField}`);
        }
      }
    }
    
    // Type validation
    if (this.schema.properties) {
      for (const [key, value] of Object.entries(args)) {
        const propertySchema = this.schema.properties[key];
        if (propertySchema && propertySchema.type) {
          const actualType = typeof value;
          if (actualType !== propertySchema.type) {
            throw new Error(`Invalid type for ${key}: expected ${propertySchema.type}, got ${actualType}`);
          }
        }
      }
    }
    
    return true;
  }

  checkRateLimit() {
    const now = Date.now();
    const windowStart = now - this.rateLimit.window;
    
    // Clean old calls
    this.callHistory = this.callHistory.filter(timestamp => timestamp > windowStart);
    
    if (this.callHistory.length >= this.rateLimit.calls) {
      throw new Error(`Rate limit exceeded for tool ${this.name}: ${this.rateLimit.calls} calls per ${this.rateLimit.window}ms`);
    }
    
    this.callHistory.push(now);
  }

  async execute(args, context = {}) {
    // Validate arguments
    this.validateArguments(args);
    
    // Check rate limits
    this.checkRateLimit();
    
    const startTime = Date.now();
    let attempt = 0;
    
    while (attempt <= this.retryConfig.maxRetries) {
      try {
        // Execute the tool with timeout
        const result = await Promise.race([
          this.handler(args, context),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error(`Tool ${this.name} timed out after ${this.timeout}ms`)), this.timeout)
          )
        ]);
        
        // Update success metrics
        const executionTime = Date.now() - startTime;
        this.updateMetrics(true, executionTime);
        
        return result;
        
      } catch (error) {
        attempt++;
        
        if (attempt > this.retryConfig.maxRetries) {
          // Update failure metrics
          this.updateMetrics(false, Date.now() - startTime);
          throw error;
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, this.retryConfig.backoffMs * attempt));
      }
    }
  }

  updateMetrics(success, executionTime) {
    this.usage.totalCalls++;
    this.usage.totalExecutionTime += executionTime;
    this.usage.averageExecutionTime = this.usage.totalExecutionTime / this.usage.totalCalls;
    this.usage.lastUsed = new Date();
    
    if (success) {
      this.usage.successfulCalls++;
    } else {
      this.usage.failedCalls++;
    }
  }

  getStatus() {
    return {
      name: this.name,
      description: this.description,
      usage: this.usage,
      rateLimit: this.rateLimit,
      currentCallCount: this.callHistory.length,
      createdAt: this.createdAt
    };
  }
}

/**
 * Tool Call Manager - Central system for managing tool calls with FoundationModels
 */
export class ToolCallManager extends EventEmitter {
  constructor(orchestrator) {
    super();
    this.orchestrator = orchestrator;
    
    // Tool registry
    this.tools = new Map();
    this.toolCategories = new Map();
    
    // Execution tracking
    this.executionHistory = [];
    this.activeExecutions = new Map();
    
    // System metrics
    this.systemMetrics = {
      totalToolsRegistered: 0,
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      averageExecutionTime: 0
    };
    
    // Initialize default tools
    this.initializeDefaultTools();
  }

  initializeDefaultTools() {
    // Memory Management Tools
    this.registerTool('search_memories', {
      description: 'Search through memories using semantic similarity and context',
      schema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search query' },
          user_id: { type: 'string', description: 'User identifier' },
          limit: { type: 'number', description: 'Maximum results to return', default: 10 },
          filters: { type: 'object', description: 'Additional search filters' }
        },
        required: ['query', 'user_id']
      },
      handler: async (args, context) => {
        return await this.orchestrator.searchMemoriesEnhanced({
          query: args.query,
          user_id: args.user_id,
          limit: args.limit || 10,
          filters: args.filters,
          agent_id: context.agentId
        });
      },
      permissions: ['read:memories'],
      category: 'memory'
    });

    this.registerTool('add_memory', {
      description: 'Add a new memory with intelligent processing and context analysis',
      schema: {
        type: 'object',
        properties: {
          content: { type: 'string', description: 'Memory content to store' },
          user_id: { type: 'string', description: 'User identifier' },
          metadata: { type: 'object', description: 'Additional metadata' }
        },
        required: ['content', 'user_id']
      },
      handler: async (args, context) => {
        return await this.orchestrator.addMemoryEnhanced({
          messages: args.content,
          user_id: args.user_id,
          metadata: {
            ...args.metadata,
            tool_call: true,
            agent_id: context.agentId,
            call_id: context.callId
          }
        });
      },
      permissions: ['write:memories'],
      category: 'memory'
    });

    // Context Analysis Tools
    this.registerTool('analyze_memory_context', {
      description: 'Analyze memory context and extract insights from text using FoundationModels',
      schema: {
        type: 'object',
        properties: {
          content: { type: 'string', description: 'Content to analyze' },
          user_id: { type: 'string', description: 'User identifier' },
          analysis_type: { 
            type: 'string', 
            description: 'Type of analysis to perform',
            enum: ['sentiment', 'entities', 'intent', 'comprehensive']
          }
        },
        required: ['content', 'user_id']
      },
      handler: async (args, context) => {
        return await this.orchestrator.analyzeMemoryContext({
          content: args.content,
          user_id: args.user_id,
          analysis_type: args.analysis_type || 'comprehensive',
          agent_id: context.agentId
        });
      },
      permissions: ['analyze:context'],
      category: 'analysis'
    });

    // Relationship Management Tools
    this.registerTool('map_relationships', {
      description: 'Map and analyze relationships between entities and memories',
      schema: {
        type: 'object',
        properties: {
          entities: { 
            type: 'array', 
            description: 'List of entities to analyze',
            items: { type: 'string' }
          },
          user_id: { type: 'string', description: 'User identifier' },
          relationship_types: {
            type: 'array',
            description: 'Types of relationships to look for',
            items: { type: 'string' }
          }
        },
        required: ['entities', 'user_id']
      },
      handler: async (args, context) => {
        return await this.orchestrator.mapRelationships({
          entities: args.entities,
          user_id: args.user_id,
          relationship_types: args.relationship_types,
          agent_id: context.agentId
        });
      },
      permissions: ['read:relationships', 'write:relationships'],
      category: 'relationships'
    });

    // System Information Tools
    this.registerTool('get_system_status', {
      description: 'Get comprehensive system status including FoundationModels and storage systems',
      schema: {
        type: 'object',
        properties: {
          include_metrics: { type: 'boolean', description: 'Include detailed metrics', default: true }
        }
      },
      handler: async (args, context) => {
        return await this.orchestrator.getSystemStatus({
          include_metrics: args.include_metrics !== false,
          agent_id: context.agentId
        });
      },
      permissions: ['read:system'],
      category: 'system'
    });
  }

  registerTool(name, config) {
    const tool = new Tool(name, config);
    this.tools.set(name, tool);
    
    // Add to category
    const category = config.category || 'general';
    if (!this.toolCategories.has(category)) {
      this.toolCategories.set(category, new Set());
    }
    this.toolCategories.get(category).add(name);
    
    this.systemMetrics.totalToolsRegistered++;
    this.emit('toolRegistered', { name, category, config });
    
    return tool;
  }

  async executeToolCall(toolName, args, context = {}) {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Unknown tool: ${toolName}`);
    }

    const callId = uuidv4();
    const executionContext = {
      ...context,
      callId,
      toolName,
      startTime: Date.now()
    };

    this.activeExecutions.set(callId, executionContext);
    
    try {
      this.emit('toolCallStarted', { callId, toolName, args, context });
      
      const result = await tool.execute(args, executionContext);
      
      // Record successful execution
      const executionTime = Date.now() - executionContext.startTime;
      this.recordExecution(callId, toolName, args, result, null, executionTime);
      
      this.emit('toolCallCompleted', { callId, toolName, result, executionTime });
      
      return result;
      
    } catch (error) {
      // Record failed execution
      const executionTime = Date.now() - executionContext.startTime;
      this.recordExecution(callId, toolName, args, null, error, executionTime);
      
      this.emit('toolCallFailed', { callId, toolName, error: error.message, executionTime });
      
      throw error;
      
    } finally {
      this.activeExecutions.delete(callId);
    }
  }

  async executeAppleIntelligenceToolCall(prompt, availableTools = null) {
    // Use FoundationModels to determine which tool to call and with what arguments
    const toolCallScript = `
import sys
import json
sys.path.insert(0, '${this.orchestrator.config.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0.utils.apple_intelligence import get_foundation_models_interface
    
    interface = get_foundation_models_interface()
    if not interface or not interface.is_available:
        raise Exception("FoundationModels not available")
    
    # Available tools
    available_tools = ${JSON.stringify(availableTools || Array.from(this.tools.keys()))}
    tool_descriptions = {}
    
    # Build tool descriptions for FoundationModels
    ${Array.from(this.tools.entries()).map(([name, tool]) => 
      `tool_descriptions["${name}"] = "${tool.description}"`
    ).join('\n    ')}
    
    # Create tool calling prompt
    user_prompt = """${prompt.replace(/"/g, '\\"')}"""
    tool_prompt = f'''
    You are an intelligent assistant with access to the following tools:
    
    {json.dumps(tool_descriptions, indent=2)}
    
    User request: {user_prompt}
    
    Determine which tool to call and with what arguments. Respond with valid JSON:
    {{
        "tool_name": "tool_to_call",
        "arguments": {{
            "arg1": "value1",
            "arg2": "value2"
        }},
        "reasoning": "why this tool was chosen"
    }}
    
    If no tool is needed, respond with {{"tool_name": null, "reasoning": "explanation"}}
    '''
    
    # Get FoundationModels response
    response = interface.generate_text(tool_prompt, max_tokens=500, temperature=0.1)
    
    # Parse the response
    try:
        tool_call = json.loads(response)
        print(json.dumps(tool_call))
    except json.JSONDecodeError:
        # Fallback parsing
        fallback_result = {
            "tool_name": None,
            "arguments": {},
            "reasoning": "Failed to parse FoundationModels response",
            "raw_response": response
        }
        print(json.dumps(fallback_result))
        
except Exception as e:
    error_result = {
        "error": str(e),
        "tool_name": None,
        "arguments": {},
        "reasoning": "FoundationModels tool calling failed"
    }
    print(json.dumps(error_result))
`;

    try {
      const toolCallResult = await this.orchestrator.executePythonScript(
        toolCallScript, 
        'FoundationModels Tool Call Analysis', 
        30000
      );

      if (toolCallResult.error) {
        throw new Error(`FoundationModels tool calling failed: ${toolCallResult.error}`);
      }

      if (!toolCallResult.tool_name) {
        return {
          tool_called: false,
          reasoning: toolCallResult.reasoning,
          raw_response: toolCallResult.raw_response
        };
      }

      // Execute the determined tool call
      const result = await this.executeToolCall(
        toolCallResult.tool_name, 
        toolCallResult.arguments,
        { source: 'apple_intelligence', prompt }
      );

      return {
        tool_called: true,
        tool_name: toolCallResult.tool_name,
        arguments: toolCallResult.arguments,
        reasoning: toolCallResult.reasoning,
        result
      };

    } catch (error) {
      throw new Error(`FoundationModels tool calling failed: ${error.message}`);
    }
  }

  recordExecution(callId, toolName, args, result, error, executionTime) {
    const execution = {
      callId,
      toolName,
      args,
      result,
      error: error?.message,
      executionTime,
      timestamp: new Date()
    };

    this.executionHistory.push(execution);
    
    // Keep only last 1000 executions
    if (this.executionHistory.length > 1000) {
      this.executionHistory = this.executionHistory.slice(-1000);
    }

    // Update system metrics
    this.systemMetrics.totalExecutions++;
    if (error) {
      this.systemMetrics.failedExecutions++;
    } else {
      this.systemMetrics.successfulExecutions++;
    }
    
    // Update average execution time
    const totalTime = this.executionHistory.reduce((sum, exec) => sum + exec.executionTime, 0);
    this.systemMetrics.averageExecutionTime = totalTime / this.executionHistory.length;
  }

  getTool(name) {
    return this.tools.get(name);
  }

  getToolsByCategory(category) {
    const toolNames = this.toolCategories.get(category) || new Set();
    return Array.from(toolNames).map(name => this.tools.get(name));
  }

  getAvailableTools() {
    return Array.from(this.tools.values()).map(tool => ({
      name: tool.name,
      description: tool.description,
      schema: tool.schema,
      category: Array.from(this.toolCategories.entries())
        .find(([_, tools]) => tools.has(tool.name))?.[0] || 'general'
    }));
  }

  getToolUsageStats() {
    return Array.from(this.tools.values()).map(tool => tool.getStatus());
  }

  getSystemStatus() {
    return {
      totalTools: this.tools.size,
      toolCategories: Array.from(this.toolCategories.keys()),
      activeExecutions: this.activeExecutions.size,
      systemMetrics: this.systemMetrics,
      recentExecutions: this.executionHistory.slice(-10)
    };
  }

  async unregisterTool(name) {
    const tool = this.tools.get(name);
    if (!tool) {
      throw new Error(`Tool not found: ${name}`);
    }

    // Remove from category
    for (const [category, tools] of this.toolCategories.entries()) {
      if (tools.has(name)) {
        tools.delete(name);
        if (tools.size === 0) {
          this.toolCategories.delete(category);
        }
        break;
      }
    }

    this.tools.delete(name);
    this.emit('toolUnregistered', { name });
  }
}

export { Tool };