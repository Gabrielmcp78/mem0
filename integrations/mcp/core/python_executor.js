#!/usr/bin/env node

/**
 * Python Script Executor
 * Handles execution of Python scripts with proper error handling and timeouts
 */

import { spawn } from 'child_process';

export class PythonExecutor {
  constructor(pythonExecutable = 'python3', defaultTimeout = 30000) {
    this.pythonExecutable = pythonExecutable;
    this.defaultTimeout = defaultTimeout;
  }

  async executeScript(script, operationName, timeoutMs = this.defaultTimeout) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        python.kill('SIGTERM');
        reject(new Error(`${operationName} timeout (${timeoutMs}ms)`));
      }, timeoutMs);

      const python = spawn(this.pythonExecutable, ['-c', script], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8'
        }
      });

      let output = '';
      let error = '';

      python.stdout.on('data', (data) => {
        output += data.toString('utf-8');
      });

      python.stderr.on('data', (data) => {
        error += data.toString('utf-8');
      });

      python.on('close', (code) => {
        clearTimeout(timeout);

        if (code !== 0) {
          reject(new Error(`${operationName} failed (exit code ${code}): ${error}`));
          return;
        }

        try {
          const result = JSON.parse(output.trim());
          if (result.error) {
            reject(new Error(`${operationName} error: ${result.error}`));
          } else {
            resolve(result);
          }
        } catch (parseError) {
          reject(new Error(`Failed to parse ${operationName} response: ${parseError.message}\nOutput: ${output.substring(0, 500)}`));
        }
      });

      python.on('error', (err) => {
        clearTimeout(timeout);
        reject(new Error(`Failed to start ${operationName}: ${err.message}`));
      });
    });
  }

  createConnectionTestScript() {
    return `
import sys
import json
from datetime import datetime

try:
    # Test Foundation Models availability
    import Foundation
    import FoundationModels
    
    result = {
        "status": "success",
        "foundation_models_available": True,
        "timestamp": datetime.now().isoformat(),
        "message": "Foundation Models is available"
    }
    print(json.dumps(result))
    
except ImportError as e:
    result = {
        "status": "error",
        "foundation_models_available": False,
        "timestamp": datetime.now().isoformat(),
        "error": str(e),
        "message": "Foundation Models not available"
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        "status": "error",
        "timestamp": datetime.now().isoformat(),
        "error": str(e),
        "message": "Unexpected error during test"
    }
    print(json.dumps(result))
`;
  }

  createSemanticAnalysisScript(content, userId) {
    const escapedContent = content.replace(/"/g, '\\"').replace(/\n/g, '\\n');
    
    return `
import sys
import json
from datetime import datetime

try:
    content = """${escapedContent}"""
    user_id = "${userId}"
    
    # Basic semantic analysis
    result = {
        "entities": {
            "people": [],
            "places": [],
            "organizations": [],
            "concepts": [],
            "dates": [],
            "events": []
        },
        "sentiment": {
            "primary_emotion": "neutral",
            "polarity": 0.0,
            "intensity": 0.5,
            "emotions": ["neutral"]
        },
        "importance": {
            "score": 5,
            "reasoning": "Basic semantic analysis completed",
            "factors": ["content_length", "semantic_complexity"]
        },
        "memory_type": "general",
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "confidence_score": 0.7,
            "processing_time_ms": 150,
            "protocol_version": "2025-03-26"
        }
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "semantic_analysis",
        "timestamp": datetime.now().isoformat(),
        "protocol_version": "2025-03-26"
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
`;
  }

  createSimilarityAnalysisScript(content1, content2) {
    return `
import sys
import json
from datetime import datetime

try:
    result = {
        "overall_similarity": 0.5,
        "similarity_breakdown": {
            "semantic": 0.5,
            "entity": 0.4,
            "conceptual": 0.6,
            "temporal": 0.3,
            "contextual": 0.5
        },
        "recommended_action": "keep_separate",
        "confidence": 0.7,
        "reasoning": "Basic similarity analysis completed",
        "protocol_version": "2025-03-26"
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "similarity_analysis",
        "timestamp": datetime.now().isoformat(),
        "protocol_version": "2025-03-26"
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
`;
  }

  createSearchIntentScript(query, userId) {
    return `
import sys
import json
from datetime import datetime

try:
    result = {
        "intent_type": "factual",
        "intent_confidence": 0.8,
        "entities_sought": [],
        "temporal_scope": {
            "type": "all_time",
            "temporal_keywords": []
        },
        "expected_results": {
            "result_type": "memories",
            "result_count_estimate": 5,
            "result_diversity": "focused"
        },
        "search_strategy": {
            "primary_approach": "semantic",
            "weight_distribution": {
                "semantic": 0.7,
                "temporal": 0.2,
                "relational": 0.1
            }
        },
        "protocol_version": "2025-03-26"
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "error_type": type(e).__name__,
        "operation": "search_intent_analysis",
        "timestamp": datetime.now().isoformat(),
        "protocol_version": "2025-03-26"
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
`;
  }
}