/**
 * @fileoverview Centralized logging for Mem0 MCP Server
 */

/**
 * Simple, structured logger
 */
class Logger {
  constructor(level = 'info') {
    this.level = level;
    this.levels = {
      'error': 0,
      'warn': 1,
      'info': 2,
      'debug': 3
    };
  }

  /**
   * Check if message should be logged at given level
   * @param {string} level 
   * @returns {boolean}
   */
  shouldLog(level) {
    return this.levels[level] <= this.levels[this.level];
  }

  /**
   * Format log message with timestamp
   * @param {string} level 
   * @param {string} message 
   * @param {Object} [meta] 
   * @returns {string}
   */
  formatMessage(level, message, meta = {}) {
    const timestamp = new Date().toISOString();
    const levelUpper = level.toUpperCase();
    const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
    return `[${timestamp}] [${levelUpper}] ${message}${metaStr}`;
  }

  /**
   * Log error message
   * @param {string} message 
   * @param {Object} [meta] 
   */
  error(message, meta) {
    if (this.shouldLog('error')) {
      console.error(this.formatMessage('error', message, meta));
    }
  }

  /**
   * Log warning message
   * @param {string} message 
   * @param {Object} [meta] 
   */
  warn(message, meta) {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message, meta));
    }
  }

  /**
   * Log info message
   * @param {string} message 
   * @param {Object} [meta] 
   */
  info(message, meta) {
    if (this.shouldLog('info')) {
      console.log(this.formatMessage('info', message, meta));
    }
  }

  /**
   * Log debug message
   * @param {string} message 
   * @param {Object} [meta] 
   */
  debug(message, meta) {
    if (this.shouldLog('debug')) {
      console.log(this.formatMessage('debug', message, meta));
    }
  }
}

module.exports = { Logger };