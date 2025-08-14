/**
 * Security utilities for Mem0 MCP Server
 * Handles input validation, sanitization, and security checks
 */

export class SecurityValidator {
  static sanitizeInput(input) {
    if (typeof input !== 'string') {
      return input;
    }
    
    // Remove potentially dangerous characters
    return input
      .replace(/[<>]/g, '') // Remove HTML tags
      .replace(/['"\\]/g, '') // Remove quotes and backslashes
      .replace(/\$\{.*?\}/g, '') // Remove template literals
      .trim();
  }

  static validateUserId(userId) {
    if (!userId || typeof userId !== 'string') {
      throw new Error('Invalid user ID');
    }
    
    // Allow alphanumeric, underscore, hyphen
    if (!/^[a-zA-Z0-9_-]+$/.test(userId)) {
      throw new Error('User ID contains invalid characters');
    }
    
    if (userId.length > 50) {
      throw new Error('User ID too long');
    }
    
    return userId;
  }

  static validateMemoryContent(content) {
    if (!content || typeof content !== 'string') {
      throw new Error('Invalid memory content');
    }
    
    if (content.length > 10000) {
      throw new Error('Memory content too long (max 10000 characters)');
    }
    
    return content;
  }

  static validateSearchQuery(query) {
    if (!query || typeof query !== 'string') {
      throw new Error('Invalid search query');
    }
    
    if (query.length > 500) {
      throw new Error('Search query too long');
    }
    
    return this.sanitizeInput(query);
  }

  static validateLimit(limit) {
    if (limit === undefined || limit === null) {
      return 10; // default
    }
    
    const numLimit = parseInt(limit);
    if (isNaN(numLimit) || numLimit < 1 || numLimit > 1000) {
      throw new Error('Invalid limit (must be 1-1000)');
    }
    
    return numLimit;
  }

  static validateEnvironment() {
    const required = ['MEM0_PROJECT_PATH'];
    const missing = required.filter(env => !process.env[env]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  static sanitizePythonPath(path) {
    // Basic path sanitization
    return path.replace(/['"\\$`]/g, '');
  }
}