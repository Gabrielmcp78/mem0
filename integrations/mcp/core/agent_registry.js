/**
 * Agent Registry and Management System
 * 
 * Legacy compatibility wrapper for the modular agent system.
 * New code should import from './agents/index.js' directly.
 */

// Re-export the modular agent system for backward compatibility
export { 
  Agent, 
  AgentType, 
  AgentRegistry, 
  AgentTypeRegistry,
  AgentTaskProcessor,
  AgentMetrics 
} from './agents/index.js';