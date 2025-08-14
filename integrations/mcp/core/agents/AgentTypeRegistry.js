/**
 * Agent Type Registry
 * 
 * Manages agent type definitions and default configurations
 */

import { AgentType } from './AgentType.js';

export class AgentTypeRegistry {
  constructor() {
    this.agentTypes = new Map();
    this.initializeDefaultAgentTypes();
  }

  initializeDefaultAgentTypes() {
    // Memory Specialist Agent
    this.registerAgentType('memory_specialist', {
      description: 'Specialized in memory operations, storage, and retrieval',
      capabilities: [
        'memory_storage',
        'memory_query',
        'semantic_search',
        'memory_consolidation'
      ],
      permissions: [
        { action: 'read', resource: 'memories' },
        { action: 'write', resource: 'memories' },
        { action: 'delete', resource: 'memories' }
      ],
      resourceLimits: {
        maxConcurrentTasks: 5,
        maxMemoryUsage: '512MB',
        maxTokensPerHour: 10000
      },
      defaultConfig: {
        searchDepth: 'deep',
        consolidationThreshold: 0.8
      }
    });

    // Context Analyst Agent
    this.registerAgentType('context_analyst', {
      description: 'Specialized in context understanding and analysis',
      capabilities: [
        'context_analysis',
        'intent_detection',
        'entity_extraction',
        'sentiment_analysis'
      ],
      permissions: [
        { action: 'read', resource: 'memories' },
        { action: 'analyze', resource: 'context' }
      ],
      resourceLimits: {
        maxConcurrentTasks: 3,
        maxMemoryUsage: '256MB',
        maxTokensPerHour: 5000
      },
      defaultConfig: {
        analysisDepth: 'comprehensive',
        confidenceThreshold: 0.7
      }
    });

    // Relationship Mapper Agent
    this.registerAgentType('relationship_mapper', {
      description: 'Specialized in mapping and managing entity relationships',
      capabilities: [
        'relationship_mapping',
        'entity_linking',
        'graph_traversal',
        'pattern_recognition'
      ],
      permissions: [
        { action: 'read', resource: 'memories' },
        { action: 'read', resource: 'relationships' },
        { action: 'write', resource: 'relationships' }
      ],
      resourceLimits: {
        maxConcurrentTasks: 2,
        maxMemoryUsage: '1GB',
        maxTokensPerHour: 3000
      },
      defaultConfig: {
        mappingStrategy: 'comprehensive',
        relationshipThreshold: 0.6
      }
    });
  }

  registerAgentType(name, config) {
    const agentType = new AgentType(name, config);
    this.agentTypes.set(name, agentType);
    return agentType;
  }

  getAgentType(name) {
    return this.agentTypes.get(name);
  }

  getAllAgentTypes() {
    return Array.from(this.agentTypes.values());
  }

  findSuitableAgentType(task) {
    return Array.from(this.agentTypes.values())
      .find(agentType => agentType.canHandle(task));
  }

  getAgentTypeNames() {
    return Array.from(this.agentTypes.keys());
  }
}