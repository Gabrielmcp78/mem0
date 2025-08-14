# Agent Management System

A modular, enterprise-grade agent orchestration system following Foundation Models best practices.

## Architecture

The agent system has been refactored into focused, single-responsibility modules:

```
agents/
├── Agent.js                 # Individual agent instance
├── AgentType.js            # Agent type definitions
├── AgentRegistry.js        # Central agent management
├── AgentTypeRegistry.js    # Agent type management
├── AgentTaskProcessor.js   # Task processing logic
├── AgentMetrics.js         # Performance metrics
├── index.js               # Centralized exports
└── README.md              # This file
```

## Key Components

### AgentType
Defines agent capabilities, permissions, and resource limits.

```javascript
import { AgentType } from './agents/AgentType.js';

const memorySpecialist = new AgentType('memory_specialist', {
  description: 'Specialized in memory operations',
  capabilities: ['memory_storage', 'memory_query'],
  permissions: [{ action: 'read', resource: 'memories' }],
  resourceLimits: { maxConcurrentTasks: 5 }
});
```

### Agent
Individual agent instance with state management and task execution.

```javascript
import { Agent } from './agents/Agent.js';

const agent = new Agent(id, type, config, orchestrator);
await agent.activate();
const result = await agent.executeTask(task);
```

### AgentRegistry
Central management system for all agents.

```javascript
import { AgentRegistry } from './agents/AgentRegistry.js';

const registry = new AgentRegistry(orchestrator);
const agent = await registry.createAgent('memory_specialist');
const result = await registry.executeTask(task);
```

## Benefits of Modular Design

### 1. Single Responsibility Principle
- Each class has one clear purpose
- Easier to understand and maintain
- Reduced cognitive load

### 2. Improved Testability
- Individual components can be tested in isolation
- Mock dependencies easily
- Better test coverage

### 3. Enhanced Maintainability
- Changes to one component don't affect others
- Easier to debug and fix issues
- Clear separation of concerns

### 4. Better Extensibility
- Easy to add new agent types
- Simple to extend functionality
- Plugin-like architecture

### 5. Reduced File Size
- No single file over 150 lines
- Focused, readable modules
- Better IDE performance

## Usage Examples

### Basic Agent Creation
```javascript
import { AgentRegistry } from './agents/index.js';

const registry = new AgentRegistry(orchestrator);
const agent = await registry.createAgent('memory_specialist', {
  searchDepth: 'comprehensive'
});
```

### Custom Agent Type
```javascript
import { AgentTypeRegistry } from './agents/index.js';

const typeRegistry = new AgentTypeRegistry();
typeRegistry.registerAgentType('custom_agent', {
  description: 'Custom agent for specific tasks',
  capabilities: ['custom_capability'],
  permissions: [{ action: 'execute', resource: 'custom_resource' }]
});
```

### Task Execution
```javascript
const task = {
  id: 'task_123',
  type: 'memory_query',
  query: 'Find memories about FoundationModels',
  userId: 'gabriel'
};

const result = await registry.executeTask(task);
```

## Migration Guide

### From Legacy agent_registry.js
The original `agent_registry.js` now serves as a compatibility wrapper. New code should import directly from the modular system:

```javascript
// Old way (still works)
import { AgentRegistry } from './agent_registry.js';

// New way (recommended)
import { AgentRegistry } from './agents/index.js';
```

### Extending the System
To add new functionality:

1. **New Agent Type**: Extend `AgentTypeRegistry`
2. **New Task Handler**: Extend `AgentTaskProcessor`
3. **New Metrics**: Extend `AgentMetrics`
4. **New Agent Behavior**: Extend `Agent`

## Performance Considerations

- **Memory Usage**: Each agent tracks its own memory usage
- **Task Processing**: Parallel task execution where possible
- **Resource Limits**: Configurable limits per agent type
- **Metrics Collection**: Lightweight performance tracking

## Error Handling

- Graceful degradation when agents fail
- Automatic cleanup of resources
- Comprehensive error reporting
- Retry mechanisms for transient failures

## Future Enhancements

- Agent clustering and load balancing
- Advanced scheduling algorithms
- Cross-agent communication protocols
- Dynamic agent scaling based on load