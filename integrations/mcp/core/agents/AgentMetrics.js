/**
 * Agent Metrics Tracker
 * 
 * Tracks performance metrics for individual agents
 */

export class AgentMetrics {
  constructor() {
    this.metrics = {
      tasksCompleted: 0,
      tasksSucceeded: 0,
      tasksFailed: 0,
      averageResponseTime: 0,
      totalProcessingTime: 0,
      lastActivity: null
    };
  }

  recordSuccess(processingTime) {
    this.metrics.tasksCompleted++;
    this.metrics.tasksSucceeded++;
    this.updateProcessingTime(processingTime);
  }

  recordFailure(processingTime) {
    this.metrics.tasksCompleted++;
    this.metrics.tasksFailed++;
    this.updateProcessingTime(processingTime);
  }

  updateProcessingTime(processingTime) {
    this.metrics.totalProcessingTime += processingTime;
    this.metrics.averageResponseTime = this.metrics.totalProcessingTime / this.metrics.tasksCompleted;
    this.metrics.lastActivity = new Date();
  }

  getMetrics() {
    return { ...this.metrics };
  }

  getSuccessRate() {
    if (this.metrics.tasksCompleted === 0) return 0;
    return this.metrics.tasksSucceeded / this.metrics.tasksCompleted;
  }

  reset() {
    this.metrics = {
      tasksCompleted: 0,
      tasksSucceeded: 0,
      tasksFailed: 0,
      averageResponseTime: 0,
      totalProcessingTime: 0,
      lastActivity: null
    };
  }
}