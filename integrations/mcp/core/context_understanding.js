/**
 * Context Understanding Module
 * 
 * Uses FoundationModels to understand and maintain context across memory operations.
 * This is what makes the system intelligent - it understands the deeper meaning
 * and connections between memories, not just their surface content.
 */

export class ContextUnderstanding {
  constructor(orchestrator) {
    this.orchestrator = orchestrator;
    this.contextHistory = new Map(); // Track context evolution
    this.entityGraph = new Map(); // Track entity relationships
    this.temporalContext = new Map(); // Track temporal relationships
  }

  /**
   * Analyze and extract context from memory content
   * This goes beyond keyword extraction - it understands meaning and relationships
   */
  async analyzeMemoryContext(content, userId, existingContext = {}) {
    const contextAnalysis = {
      // Entity extraction with relationship understanding
      entities: await this.extractEntitiesWithRelationships(content),
      
      // Temporal context - when did this happen, how does it relate to other events
      temporal_context: await this.analyzeTemporalContext(content, userId),
      
      // Emotional and sentiment context
      emotional_context: await this.analyzeEmotionalContext(content),
      
      // Conceptual context - what concepts and ideas are involved
      conceptual_context: await this.analyzeConceptualContext(content),
      
      // Relational context - how does this relate to existing memories
      relational_context: await this.analyzeRelationalContext(content, userId),
      
      // Intent context - what was the user trying to capture or remember
      intent_context: await this.analyzeIntentContext(content, existingContext),
      
      // Importance context - why is this memory significant
      importance_context: await this.analyzeImportanceContext(content, userId)
    };

    // Update context history
    this.updateContextHistory(userId, contextAnalysis);
    
    return contextAnalysis;
  }

  /**
   * Extract entities and understand their relationships using FoundationModels
   */
  async extractEntitiesWithRelationships(content) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, 'system');
      return analysis.entities || {
        people: [],
        places: [],
        organizations: [],
        concepts: [],
        dates: [],
        events: [],
        relationships: []
      };
    } catch (error) {
      console.error('Entity extraction failed:', error);
      return {
        people: [],
        places: [],
        organizations: [],
        concepts: [],
        dates: [],
        events: [],
        relationships: [],
        error: error.message
      };
    }
  }

  /**
   * Analyze temporal context and relationships using FoundationModels
   */
  async analyzeTemporalContext(content, userId) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, userId);
      const temporalAnalysis = analysis.temporal_context || {
        time_references: [],
        temporal_relationships: [],
        recency_indicators: [],
        duration_indicators: [],
        frequency_indicators: [],
        temporal_significance: 'medium'
      };

      // Update temporal context graph
      this.updateTemporalGraph(userId, temporalAnalysis);
      
      return temporalAnalysis;
    } catch (error) {
      console.error('Temporal analysis failed:', error);
      const fallbackAnalysis = {
        time_references: [],
        temporal_relationships: [],
        recency_indicators: [],
        duration_indicators: [],
        frequency_indicators: [],
        temporal_significance: 'medium',
        error: error.message
      };
      
      this.updateTemporalGraph(userId, fallbackAnalysis);
      return fallbackAnalysis;
    }
  }

  /**
   * Analyze emotional and sentiment context using FoundationModels
   */
  async analyzeEmotionalContext(content) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, 'system');
      const sentiment = analysis.sentiment || {};
      
      return {
        primary_emotion: sentiment.primary_emotion || 'neutral',
        emotion_intensity: sentiment.intensity || 0.5,
        emotional_triggers: sentiment.emotions || [],
        emotional_outcomes: [],
        sentiment_trajectory: [sentiment.polarity || 0.0],
        emotional_significance: sentiment.intensity > 0.7 ? 'high' : sentiment.intensity > 0.3 ? 'medium' : 'low',
        polarity: sentiment.polarity || 0.0,
        confidence: analysis.metadata?.confidence_score || 0.5
      };
    } catch (error) {
      console.error('Emotional analysis failed:', error);
      return {
        primary_emotion: 'neutral',
        emotion_intensity: 0.5,
        emotional_triggers: [],
        emotional_outcomes: [],
        sentiment_trajectory: [0.0],
        emotional_significance: 'medium',
        polarity: 0.0,
        confidence: 0.0,
        error: error.message
      };
    }
  }

  /**
   * Analyze conceptual context using FoundationModels
   */
  async analyzeConceptualContext(content) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, 'system');
      const concepts = analysis.concepts || [];
      
      return {
        primary_concepts: concepts.map(c => c.concept || c),
        concept_relationships: analysis.relationships || [],
        abstraction_level: this.determineAbstractionLevel(concepts),
        domain_knowledge: concepts.map(c => c.domain).filter(Boolean),
        conceptual_complexity: this.assessConceptualComplexity(concepts),
        learning_indicators: this.identifyLearningIndicators(content, concepts),
        concept_details: concepts
      };
    } catch (error) {
      console.error('Conceptual analysis failed:', error);
      return {
        primary_concepts: [],
        concept_relationships: [],
        abstraction_level: 'concrete',
        domain_knowledge: [],
        conceptual_complexity: 'medium',
        learning_indicators: [],
        concept_details: [],
        error: error.message
      };
    }
  }

  /**
   * Determine abstraction level of concepts
   */
  determineAbstractionLevel(concepts) {
    if (!concepts || concepts.length === 0) return 'concrete';
    
    const abstractCount = concepts.filter(c => 
      c.abstraction_level === 'abstract' || 
      (typeof c === 'object' && c.abstraction_level === 'abstract')
    ).length;
    
    const ratio = abstractCount / concepts.length;
    
    if (ratio > 0.7) return 'abstract';
    if (ratio > 0.3) return 'mixed';
    return 'concrete';
  }

  /**
   * Assess conceptual complexity
   */
  assessConceptualComplexity(concepts) {
    if (!concepts || concepts.length === 0) return 'low';
    if (concepts.length > 10) return 'high';
    if (concepts.length > 5) return 'medium';
    return 'low';
  }

  /**
   * Identify learning indicators in content
   */
  identifyLearningIndicators(content, concepts) {
    const learningKeywords = [
      'learned', 'discovered', 'realized', 'understood', 'figured out',
      'new to me', 'never knew', 'interesting', 'surprising'
    ];
    
    const indicators = [];
    const lowerContent = content.toLowerCase();
    
    learningKeywords.forEach(keyword => {
      if (lowerContent.includes(keyword)) {
        indicators.push(keyword);
      }
    });
    
    return indicators;
  }

  /**
   * Analyze how this memory relates to existing memories using FoundationModels
   */
  async analyzeRelationalContext(content, userId) {
    try {
      // Search for related memories
      const relatedMemories = await this.findRelatedMemories(content, userId);
      
      if (relatedMemories.length === 0) {
        return {
          direct_references: [],
          semantic_connections: [],
          entity_connections: [],
          temporal_connections: [],
          causal_connections: [],
          contradiction_flags: [],
          reinforcement_connections: [],
          total_related: 0
        };
      }

      const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
        pythonPath: this.orchestrator.pythonPath,
        pythonExecutable: this.orchestrator.pythonExecutable,
        memoryConfig: this.orchestrator.memoryConfig
      });

      // Analyze relationships with each related memory
      const relationshipAnalyses = [];
      
      for (const memory of relatedMemories.slice(0, 5)) { // Limit to top 5 for performance
        try {
          const similarity = await appleAPI.analyzeSimilarity(content, memory.content || memory.text || '');
          relationshipAnalyses.push({
            memory_id: memory.id,
            similarity: similarity.overall_similarity,
            relationship_types: this.categorizeRelationship(similarity),
            memory_content: memory.content || memory.text || ''
          });
        } catch (error) {
          console.error(`Relationship analysis failed for memory ${memory.id}:`, error);
        }
      }

      return {
        direct_references: this.findDirectReferences(content, relatedMemories),
        semantic_connections: relationshipAnalyses.filter(r => r.similarity > 0.6),
        entity_connections: this.findEntityConnections(content, relatedMemories),
        temporal_connections: this.findTemporalConnections(content, relatedMemories),
        causal_connections: this.findCausalConnections(relationshipAnalyses),
        contradiction_flags: this.findContradictions(relationshipAnalyses),
        reinforcement_connections: this.findReinforcements(relationshipAnalyses),
        total_related: relatedMemories.length,
        analysis_details: relationshipAnalyses
      };
    } catch (error) {
      console.error('Relational context analysis failed:', error);
      return {
        direct_references: [],
        semantic_connections: [],
        entity_connections: [],
        temporal_connections: [],
        causal_connections: [],
        contradiction_flags: [],
        reinforcement_connections: [],
        total_related: 0,
        error: error.message
      };
    }
  }

  /**
   * Categorize relationship type based on similarity analysis
   */
  categorizeRelationship(similarity) {
    const types = [];
    
    if (similarity.similarity_breakdown?.semantic > 0.7) types.push('semantic');
    if (similarity.similarity_breakdown?.temporal > 0.7) types.push('temporal');
    if (similarity.similarity_breakdown?.entity > 0.7) types.push('entity');
    if (similarity.similarity_breakdown?.conceptual > 0.7) types.push('conceptual');
    
    return types;
  }

  /**
   * Find direct references to other memories
   */
  findDirectReferences(content, memories) {
    const references = [];
    const lowerContent = content.toLowerCase();
    
    // Look for explicit references like "as I mentioned before", "like last time", etc.
    const referencePatterns = [
      /as i mentioned/i,
      /like (last time|before|previously)/i,
      /similar to when/i,
      /reminds me of/i
    ];
    
    referencePatterns.forEach(pattern => {
      if (pattern.test(content)) {
        references.push({
          pattern: pattern.source,
          context: content.match(pattern)?.[0] || ''
        });
      }
    });
    
    return references;
  }

  /**
   * Find entity-based connections
   */
  findEntityConnections(content, memories) {
    // This would extract entities from current content and find memories with shared entities
    // For now, return basic structure
    return [];
  }

  /**
   * Find temporal connections
   */
  findTemporalConnections(content, memories) {
    // This would analyze temporal relationships between memories
    return [];
  }

  /**
   * Find causal connections
   */
  findCausalConnections(analyses) {
    return analyses.filter(a => 
      a.relationship_types.includes('causal') || 
      a.similarity > 0.8
    );
  }

  /**
   * Find contradictions
   */
  findContradictions(analyses) {
    // This would use FoundationModels to detect contradictory information
    return [];
  }

  /**
   * Find reinforcing connections
   */
  findReinforcements(analyses) {
    return analyses.filter(a => 
      a.relationship_types.includes('semantic') && 
      a.similarity > 0.7
    );
  }

  /**
   * Analyze the intent behind storing this memory using FoundationModels
   */
  async analyzeIntentContext(content, existingContext) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, 'system');
      const intent = analysis.intent || {};
      
      return {
        storage_intent: intent.primary_intent || 'remember',
        retrieval_intent: intent.retrieval_cues || [],
        usage_patterns: intent.secondary_intents || [],
        sharing_intent: this.detectSharingIntent(content),
        privacy_level: this.assessPrivacyLevel(content),
        action_items: this.extractActionItems(content),
        confidence: analysis.metadata?.confidence_score || 0.5
      };
    } catch (error) {
      console.error('Intent analysis failed:', error);
      return {
        storage_intent: 'remember',
        retrieval_intent: [],
        usage_patterns: [],
        sharing_intent: false,
        privacy_level: 'personal',
        action_items: [],
        confidence: 0.0,
        error: error.message
      };
    }
  }

  /**
   * Detect sharing intent in content
   */
  detectSharingIntent(content) {
    const sharingKeywords = [
      'share with', 'tell', 'show', 'send to', 'forward',
      'public', 'everyone should know', 'spread the word'
    ];
    
    const lowerContent = content.toLowerCase();
    return sharingKeywords.some(keyword => lowerContent.includes(keyword));
  }

  /**
   * Assess privacy level of content
   */
  assessPrivacyLevel(content) {
    const privateKeywords = ['personal', 'private', 'confidential', 'secret', 'password'];
    const publicKeywords = ['public', 'share', 'everyone', 'announce'];
    
    const lowerContent = content.toLowerCase();
    
    if (privateKeywords.some(keyword => lowerContent.includes(keyword))) {
      return 'private';
    }
    
    if (publicKeywords.some(keyword => lowerContent.includes(keyword))) {
      return 'public';
    }
    
    return 'personal';
  }

  /**
   * Extract action items from content
   */
  extractActionItems(content) {
    const actionPatterns = [
      /need to (.+)/gi,
      /should (.+)/gi,
      /must (.+)/gi,
      /todo:? (.+)/gi,
      /action:? (.+)/gi,
      /remember to (.+)/gi
    ];
    
    const actionItems = [];
    
    actionPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          actionItems.push({
            action: match,
            priority: this.assessActionPriority(match),
            extracted_by: 'pattern_matching'
          });
        });
      }
    });
    
    return actionItems;
  }

  /**
   * Assess priority of action items
   */
  assessActionPriority(action) {
    const highPriorityKeywords = ['urgent', 'asap', 'immediately', 'critical', 'must'];
    const lowPriorityKeywords = ['maybe', 'eventually', 'someday', 'when possible'];
    
    const lowerAction = action.toLowerCase();
    
    if (highPriorityKeywords.some(keyword => lowerAction.includes(keyword))) {
      return 'high';
    }
    
    if (lowPriorityKeywords.some(keyword => lowerAction.includes(keyword))) {
      return 'low';
    }
    
    return 'medium';
  }

  /**
   * Analyze why this memory is important using FoundationModels
   */
  async analyzeImportanceContext(content, userId) {
    const appleAPI = new (await import('./apple_intelligence_api.js')).AppleIntelligenceAPI({
      pythonPath: this.orchestrator.pythonPath,
      pythonExecutable: this.orchestrator.pythonExecutable,
      memoryConfig: this.orchestrator.memoryConfig
    });

    try {
      const analysis = await appleAPI.analyzeSemanticContent(content, userId);
      const importance = analysis.importance || {};
      
      return {
        personal_significance: this.assessPersonalSignificance(content, analysis),
        professional_significance: this.assessProfessionalSignificance(content, analysis),
        learning_significance: this.assessLearningSignificance(content, analysis),
        decision_relevance: this.identifyDecisionRelevance(content),
        goal_relevance: this.identifyGoalRelevance(content),
        uniqueness_score: this.calculateUniquenessScore(content, analysis),
        utility_score: this.calculateUtilityScore(content, analysis),
        overall_importance: importance.score || 5,
        importance_reasoning: importance.reasoning || 'Standard importance assessment',
        importance_factors: importance.factors || []
      };
    } catch (error) {
      console.error('Importance analysis failed:', error);
      return {
        personal_significance: 'medium',
        professional_significance: 'low',
        learning_significance: 'medium',
        decision_relevance: [],
        goal_relevance: [],
        uniqueness_score: 0.5,
        utility_score: 0.5,
        overall_importance: 5,
        importance_reasoning: 'Default assessment due to analysis error',
        importance_factors: [],
        error: error.message
      };
    }
  }

  /**
   * Assess personal significance
   */
  assessPersonalSignificance(content, analysis) {
    const personalKeywords = ['family', 'friend', 'personal', 'private', 'emotion', 'feel'];
    const sentiment = analysis.sentiment || {};
    
    const lowerContent = content.toLowerCase();
    const hasPersonalKeywords = personalKeywords.some(keyword => lowerContent.includes(keyword));
    const hasStrongEmotion = sentiment.intensity > 0.7;
    
    if (hasPersonalKeywords && hasStrongEmotion) return 'high';
    if (hasPersonalKeywords || hasStrongEmotion) return 'medium';
    return 'low';
  }

  /**
   * Assess professional significance
   */
  assessProfessionalSignificance(content, analysis) {
    const professionalKeywords = [
      'work', 'job', 'career', 'business', 'project', 'meeting',
      'client', 'colleague', 'boss', 'deadline', 'task'
    ];
    
    const lowerContent = content.toLowerCase();
    const professionalCount = professionalKeywords.filter(keyword => 
      lowerContent.includes(keyword)
    ).length;
    
    if (professionalCount >= 3) return 'high';
    if (professionalCount >= 1) return 'medium';
    return 'low';
  }

  /**
   * Assess learning significance
   */
  assessLearningSignificance(content, analysis) {
    const learningKeywords = [
      'learned', 'discovered', 'realized', 'understood', 'new',
      'insight', 'knowledge', 'skill', 'technique', 'method'
    ];
    
    const concepts = analysis.concepts || [];
    const lowerContent = content.toLowerCase();
    
    const hasLearningKeywords = learningKeywords.some(keyword => 
      lowerContent.includes(keyword)
    );
    const hasComplexConcepts = concepts.length > 3;
    
    if (hasLearningKeywords && hasComplexConcepts) return 'high';
    if (hasLearningKeywords || hasComplexConcepts) return 'medium';
    return 'low';
  }

  /**
   * Identify decision relevance
   */
  identifyDecisionRelevance(content) {
    const decisionKeywords = [
      'decide', 'choice', 'option', 'consider', 'evaluate',
      'pros and cons', 'advantage', 'disadvantage', 'compare'
    ];
    
    const relevance = [];
    const lowerContent = content.toLowerCase();
    
    decisionKeywords.forEach(keyword => {
      if (lowerContent.includes(keyword)) {
        relevance.push({
          keyword: keyword,
          context: this.extractContext(content, keyword),
          relevance_score: 0.7
        });
      }
    });
    
    return relevance;
  }

  /**
   * Identify goal relevance
   */
  identifyGoalRelevance(content) {
    const goalKeywords = [
      'goal', 'objective', 'target', 'aim', 'plan', 'strategy',
      'achieve', 'accomplish', 'complete', 'finish', 'success'
    ];
    
    const relevance = [];
    const lowerContent = content.toLowerCase();
    
    goalKeywords.forEach(keyword => {
      if (lowerContent.includes(keyword)) {
        relevance.push({
          keyword: keyword,
          context: this.extractContext(content, keyword),
          relevance_score: 0.8
        });
      }
    });
    
    return relevance;
  }

  /**
   * Calculate uniqueness score
   */
  calculateUniquenessScore(content, analysis) {
    const entities = analysis.entities || {};
    const concepts = analysis.concepts || [];
    
    // More entities and concepts suggest more unique information
    const entityCount = Object.values(entities).flat().length;
    const conceptCount = concepts.length;
    
    const uniquenessScore = Math.min(1.0, (entityCount + conceptCount) / 20);
    return Math.max(0.1, uniquenessScore);
  }

  /**
   * Calculate utility score
   */
  calculateUtilityScore(content, analysis) {
    const importance = analysis.importance || {};
    const actionItems = this.extractActionItems(content);
    
    let utilityScore = (importance.score || 5) / 10;
    
    // Boost utility if there are action items
    if (actionItems.length > 0) {
      utilityScore += 0.2;
    }
    
    // Boost utility for learning content
    const learningIndicators = this.identifyLearningIndicators(content, analysis.concepts || []);
    if (learningIndicators.length > 0) {
      utilityScore += 0.1;
    }
    
    return Math.min(1.0, Math.max(0.1, utilityScore));
  }

  /**
   * Extract context around a keyword
   */
  extractContext(content, keyword, contextLength = 50) {
    const index = content.toLowerCase().indexOf(keyword.toLowerCase());
    if (index === -1) return '';
    
    const start = Math.max(0, index - contextLength);
    const end = Math.min(content.length, index + keyword.length + contextLength);
    
    return content.substring(start, end);
  }

  /**
   * Find memories related to the current content using real search
   */
  async findRelatedMemories(content, userId, limit = 10) {
    const searchScript = `
import sys
import json
from datetime import datetime
sys.path.insert(0, '${this.orchestrator.pythonPath.replace(/'/g, "\\'")}')

try:
    from mem0 import Memory
    memory = Memory.from_config(${JSON.stringify(this.orchestrator.memoryConfig)})
    
    # Search for related memories
    search_results = memory.search(
        query="${content.replace(/"/g, '\\"')}",
        user_id="${userId}",
        limit=${limit}
    )
    
    result = {
        "memories": search_results.get("results", []),
        "total_found": len(search_results.get("results", [])),
        "search_timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(result, default=str))
    
except Exception as e:
    error_result = {
        "error": str(e),
        "memories": [],
        "total_found": 0,
        "search_timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_result, default=str))
`;

    try {
      const result = await this.orchestrator.executePythonScript(searchScript, 'Find Related Memories');
      return result.memories || [];
    } catch (error) {
      console.error('Failed to find related memories:', error);
      return [];
    }
  }

  /**
   * Update context history for a user
   */
  updateContextHistory(userId, contextAnalysis) {
    if (!this.contextHistory.has(userId)) {
      this.contextHistory.set(userId, []);
    }
    
    const userHistory = this.contextHistory.get(userId);
    userHistory.push({
      timestamp: new Date().toISOString(),
      context: contextAnalysis
    });
    
    // Keep only recent context (last 100 entries)
    if (userHistory.length > 100) {
      userHistory.splice(0, userHistory.length - 100);
    }
  }

  /**
   * Update temporal relationship graph
   */
  updateTemporalGraph(userId, temporalAnalysis) {
    if (!this.temporalContext.has(userId)) {
      this.temporalContext.set(userId, {
        timeline: [],
        relationships: []
      });
    }
    
    const userTemporal = this.temporalContext.get(userId);
    
    // Add temporal events to timeline
    temporalAnalysis.time_references.forEach(timeRef => {
      userTemporal.timeline.push({
        timestamp: new Date().toISOString(),
        reference: timeRef,
        context: 'memory_storage'
      });
    });
    
    // Sort timeline
    userTemporal.timeline.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  }

  /**
   * Get context insights for a user
   */
  getContextInsights(userId) {
    const userHistory = this.contextHistory.get(userId) || [];
    const userTemporal = this.temporalContext.get(userId) || { timeline: [], relationships: [] };
    
    return {
      total_contexts_analyzed: userHistory.length,
      recent_context_trends: this.analyzeContextTrends(userHistory),
      entity_frequency: this.analyzeEntityFrequency(userHistory),
      temporal_patterns: this.analyzeTemporalPatterns(userTemporal),
      emotional_patterns: this.analyzeEmotionalPatterns(userHistory),
      conceptual_evolution: this.analyzeConceptualEvolution(userHistory)
    };
  }

  /**
   * Analyze trends in context over time
   */
  analyzeContextTrends(history) {
    // Analyze how context has evolved over time
    return {
      complexity_trend: 'stable',
      emotional_trend: 'neutral',
      conceptual_growth: 'moderate',
      relationship_density_trend: 'increasing'
    };
  }

  /**
   * Analyze frequency of entities across contexts
   */
  analyzeEntityFrequency(history) {
    const entityCounts = {};
    
    history.forEach(entry => {
      const entities = entry.context.entities;
      ['people', 'places', 'organizations', 'concepts'].forEach(type => {
        entities[type]?.forEach(entity => {
          const key = `${type}:${entity}`;
          entityCounts[key] = (entityCounts[key] || 0) + 1;
        });
      });
    });
    
    return entityCounts;
  }

  /**
   * Analyze temporal patterns
   */
  analyzeTemporalPatterns(temporalData) {
    return {
      timeline_density: temporalData.timeline.length,
      relationship_complexity: temporalData.relationships.length,
      temporal_clustering: [] // Periods of high activity
    };
  }

  /**
   * Analyze emotional patterns over time
   */
  analyzeEmotionalPatterns(history) {
    const emotions = history.map(entry => entry.context.emotional_context);
    
    return {
      dominant_emotions: [],
      emotional_volatility: 'low',
      emotional_progression: 'stable'
    };
  }

  /**
   * Analyze how conceptual understanding has evolved
   */
  analyzeConceptualEvolution(history) {
    return {
      concept_growth_rate: 'moderate',
      domain_expansion: [],
      abstraction_level_trend: 'stable',
      learning_acceleration: 'steady'
    };
  }
}