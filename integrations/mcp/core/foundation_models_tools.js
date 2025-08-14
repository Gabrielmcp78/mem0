#!/usr/bin/env node

/**
 * Foundation Models Tool Implementations
 * Contains the business logic for Foundation Models operations
 */

export class FoundationModelsTools {
  constructor(pythonExecutor) {
    this.pythonExecutor = pythonExecutor;
  }

  getToolDefinitions() {
    return [
      {
        name: 'test_connection',
        description: 'Test the Foundation Models connection',
        inputSchema: {
          type: 'object',
          properties: {},
        },
        handler: this.testConnection.bind(this)
      },
      {
        name: 'analyze_semantic_content',
        description: 'Analyze semantic content using Foundation Models',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Content to analyze',
            },
            userId: {
              type: 'string',
              description: 'User ID',
            },
            context: {
              type: 'object',
              description: 'Additional context',
              default: {},
            },
          },
          required: ['content', 'userId'],
        },
        handler: this.analyzeSemanticContent.bind(this)
      }
    ];
  }

  async testConnection() {
    try {
      const script = this.pythonExecutor.createConnectionTestScript();
      const result = await this.pythonExecutor.executeScript(
        script, 
        'Connection Test', 
        10000
      );
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Connection test failed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async analyzeSemanticContent(args) {
    const { content, userId, context = {} } = args;
    
    try {
      const script = this.pythonExecutor.createSemanticAnalysisScript(content, userId);
      const result = await this.pythonExecutor.executeScript(
        script,
        'Semantic Analysis',
        30000
      );
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Semantic analysis failed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
}