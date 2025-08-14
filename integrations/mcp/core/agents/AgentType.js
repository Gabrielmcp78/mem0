/**
 * Agent Type Definition
 * 
 * Defines agent capabilities, permissions, and configuration
 */

export class AgentType {
  constructor(name, config) {
    this.name = name;
    this.description = config.description;
    this.capabilities = config.capabilities || [];
    this.permissions = config.permissions || [];
    this.resourceLimits = config.resourceLimits || {};
    this.defaultConfig = config.defaultConfig || {};
    this.handoffRules = config.handoffRules || [];
  }

  canHandle(task) {
    return this.capabilities.some(capability => 
      task.requiredCapabilities?.includes(capability)
    );
  }

  hasPermission(action, resource) {
    return this.permissions.some(permission => 
      permission.action === action && 
      (permission.resource === '*' || permission.resource === resource)
    );
  }

  validateConfig(config) {
    // Validate agent configuration against type constraints
    const errors = [];
    
    if (this.resourceLimits.maxMemoryUsage && config.memoryUsage > this.resourceLimits.maxMemoryUsage) {
      errors.push(`Memory usage exceeds limit: ${this.resourceLimits.maxMemoryUsage}`);
    }
    
    return errors;
  }

  getCapabilityDescription(capability) {
    const descriptions = {
      'memory_storage': 'Store and manage memory data',
      'memory_query': 'Search and retrieve memories',
      'semantic_search': 'Perform semantic similarity searches',
      'context_analysis': 'Analyze contextual information',
      'relationship_mapping': 'Map entity relationships'
    };
    
    return descriptions[capability] || capability;
  }
}