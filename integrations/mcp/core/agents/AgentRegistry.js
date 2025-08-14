/**
 * Agent Registry - Central management system for all agents
 * 
 * Simplified registry focused on agent lifecycle management
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { Agent } from './Agent.js';
import { AgentTypeRegistry } from './AgentTypeRegistry.js';

export class AgentRegistry extends EventEmitter {
  constructor(orchestrator) {
    super();
    this.orchestrator = orchestrator;
    
    // Initialize type registry
    this.typeRegistry = new AgentTypeRegistry();
    
    // Registry storage
    this.agents = new Map();
    this.activeAgents = new Map();
    this.taskQueue = [];
    
    // System metrics
    this.systemMetrics = {
      totalAgentsCreated: 0,
      activeAgentCount: 0,
      totalTasksProcessed: 0,
      averageSystemLoad: 0
    };
  }

  async createAgent(typeName, config = {}) {
    const agentType = this.typeRegistry.getAgentType(typeName);
    if (!agentType) {
      throw new Error(`Unknown agent type: ${typeName}`);
    }

    const agentId = config.id || `${typeName}_${uuidv4()}`;
    const agent = new Agent(agentId, agentType, config, this.orchestrator);
    
    this.agents.set(agentId, agent);
    this.systemMetrics.totalAgentsCreated++;
    
    this.setupAgentEventListeners(agent, agentId);
    
    this.emit('agentCreated', { agentId, typeName, config });
    return agent;
  }

  setupAgentEventListeners(agent, agentId) {
    agent.on('activated', (event) => {
      this.activeAgents.set(agentId, agent);
      this.systemMetrics.activeAgentCount++;
      this.emit('agentActivated', event);
    });
    
    agent.on('deactivated', (event) => {
      this.activeAgents.delete(agentId);
      this.systemMetrics.activeAgentCount--;
      this.emit('agentDeactivated', event);
    });
    
    agent.on('taskCompleted', (event) => {
      this.systemMetrics.totalTasksProcessed++;
      this.emit('taskCompleted', event);
    });
  }

  async getOrCreateAgent(typeName, config = {}) {
    // Try to find an available agent of the requested type
    const availableAgent = Array.from(this.activeAgents.values())
      .find(agent => agent.type.name === typeName && agent.status === 'active');
    
    if (availableAgent) {
      return availableAgent;
    }
    
    // Create a new agent if none available
    const agent = await this.createAgent(typeName, config);
    await agent.activate();
    return agent;
  }

  async executeTask(task) {
    // Determine the best agent type for this task
    const suitableAgentType = this.typeRegistry.findSuitableAgentType(task);
    if (!suitableAgentType) {
      throw new Error(`No suitable agent type found for task: ${task.type}`);
    }
    
    // Get or create an agent of the suitable type
    const agent = await this.getOrCreateAgent(suitableAgentType.name);
    
    // Execute the task
    return await agent.executeTask(task);
  }

  getAgent(agentId) {
    return this.agents.get(agentId);
  }

  getActiveAgents() {
    return Array.from(this.activeAgents.values());
  }

  getAgentsByType(typeName) {
    return Array.from(this.agents.values())
      .filter(agent => agent.type.name === typeName);
  }

  async destroyAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    
    if (agent.status !== 'inactive') {
      await agent.deactivate();
    }
    
    this.agents.delete(agentId);
    this.activeAgents.delete(agentId);
    
    this.emit('agentDestroyed', { agentId });
  }

  getSystemStatus() {
    return {
      agentTypes: this.typeRegistry.getAgentTypeNames(),
      totalAgents: this.agents.size,
      activeAgents: this.activeAgents.size,
      systemMetrics: this.systemMetrics,
      agentStatuses: Array.from(this.agents.values()).map(agent => agent.getStatus())
    };
  }

  // Delegate agent type operations to type registry
  registerAgentType(name, config) {
    return this.typeRegistry.registerAgentType(name, config);
  }

  getAgentType(name) {
    return this.typeRegistry.getAgentType(name);
  }
}