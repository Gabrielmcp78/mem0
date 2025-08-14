/**
 * Individual Agent Instance
 * 
 * Represents a single agent with state management and task execution
 */

import { EventEmitter } from 'events';
import { AgentTaskProcessor } from './AgentTaskProcessor.js';
import { AgentMetrics } from './AgentMetrics.js';

export class Agent extends EventEmitter {
  constructor(id, type, config, orchestrator) {
    super();
    this.id = id;
    this.type = type;
    this.config = { ...type.defaultConfig, ...config };
    this.orchestrator = orchestrator;
    
    // Initialize components
    this.taskProcessor = new AgentTaskProcessor(this);
    this.metrics = new AgentMetrics();
    
    // Agent state
    this.status = 'inactive'; // inactive, active, busy, error, suspended
    this.currentTask = null;
    this.context = new Map();
    this.memory = new Map();
    
    // Resource tracking
    this.resourceUsage = {
      memory: 0,
      cpu: 0,
      tokens: 0,
      apiCalls: 0
    };
    
    this.createdAt = new Date();
    this.lastActivity = new Date();
  }

  async activate() {
    if (this.status !== 'inactive') {
      throw new Error(`Cannot activate agent ${this.id} - current status: ${this.status}`);
    }
    
    this.status = 'active';
    this.lastActivity = new Date();
    this.emit('activated', { agentId: this.id, timestamp: this.lastActivity });
    
    await this.initializeResources();
  }

  async deactivate() {
    if (this.currentTask) {
      throw new Error(`Cannot deactivate agent ${this.id} - task in progress: ${this.currentTask.id}`);
    }
    
    this.status = 'inactive';
    this.emit('deactivated', { agentId: this.id, timestamp: new Date() });
    
    await this.cleanupResources();
  }

  async executeTask(task) {
    if (this.status !== 'active') {
      throw new Error(`Agent ${this.id} is not active (status: ${this.status})`);
    }

    if (!this.type.canHandle(task)) {
      throw new Error(`Agent ${this.id} cannot handle task type: ${task.type}`);
    }

    this.status = 'busy';
    this.currentTask = task;
    const startTime = Date.now();

    try {
      this.emit('taskStarted', { agentId: this.id, taskId: task.id, timestamp: new Date() });
      
      const result = await this.taskProcessor.processTask(task);
      
      const processingTime = Date.now() - startTime;
      this.metrics.recordSuccess(processingTime);
      
      this.emit('taskCompleted', { 
        agentId: this.id, 
        taskId: task.id, 
        result, 
        processingTime,
        timestamp: new Date() 
      });
      
      return result;
      
    } catch (error) {
      this.metrics.recordFailure(Date.now() - startTime);
      this.emit('taskFailed', { 
        agentId: this.id, 
        taskId: task.id, 
        error: error.message,
        timestamp: new Date() 
      });
      throw error;
      
    } finally {
      this.status = 'active';
      this.currentTask = null;
      this.lastActivity = new Date();
    }
  }

  async initializeResources() {
    // Initialize agent-specific resources
    // This could include loading agent-specific models, configurations, etc.
  }

  async cleanupResources() {
    // Clean up agent-specific resources
    this.context.clear();
    this.memory.clear();
  }

  getStatus() {
    return {
      id: this.id,
      type: this.type.name,
      status: this.status,
      currentTask: this.currentTask?.id || null,
      metrics: this.metrics.getMetrics(),
      resourceUsage: this.resourceUsage,
      contextSize: this.context.size,
      memorySize: this.memory.size,
      createdAt: this.createdAt,
      lastActivity: this.lastActivity
    };
  }
}