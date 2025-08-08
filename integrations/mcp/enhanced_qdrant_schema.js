/**
 * Enhanced Qdrant Schema for Sophisticated Memory System
 * 
 * This shows how to use Qdrant's advanced features for a rich memory system
 */

// Enhanced Memory Payload Structure
const ENHANCED_MEMORY_SCHEMA = {
  // Core content
  id: "uuid",
  content: "string",
  content_type: "text|code|conversation|fact|insight|question",
  
  // Semantic enrichment
  semantic_tags: ["array", "of", "extracted", "concepts"],
  entities: {
    people: ["John", "Sarah"],
    places: ["San Francisco", "office"],
    organizations: ["OpenAI", "Apple"],
    concepts: ["machine learning", "productivity"]
  },
  
  // Relationships
  relationships: {
    references: ["memory_id_1", "memory_id_2"], // What this memory references
    referenced_by: ["memory_id_3"], // What references this memory
    similar_to: ["memory_id_4"], // Semantically similar memories
    contradicts: ["memory_id_5"], // Conflicting information
    builds_on: ["memory_id_6"], // Builds upon previous memories
    parent_thread: "conversation_id", // Part of larger conversation
    child_memories: ["memory_id_7"] // Spawned sub-memories
  },
  
  // Temporal context
  temporal: {
    created_at: "2025-01-08T10:30:00Z",
    updated_at: "2025-01-08T11:15:00Z",
    accessed_at: "2025-01-08T12:00:00Z",
    access_count: 5,
    last_modified_by: "claude",
    time_period: "morning|afternoon|evening|night",
    day_of_week: "tuesday",
    context_window: "work_hours|personal_time|meeting"
  },
  
  // Importance and relevance
  scoring: {
    importance: 0.85, // 0-1 scale
    confidence: 0.92, // How confident we are in this memory
    relevance_decay: 0.95, // How quickly this becomes less relevant
    emotional_weight: 0.3, // Emotional significance
    factual_accuracy: 0.98, // How factually accurate
    uniqueness: 0.7 // How unique/novel this information is
  },
  
  // Context and source
  context: {
    user_id: "gabriel",
    agent_id: "claude",
    run_id: "session_123",
    source: "conversation|document|web|api",
    conversation_turn: 15,
    topic_thread: "project_planning",
    user_intent: "learning|problem_solving|creative|factual",
    interaction_mode: "chat|voice|document_analysis"
  },
  
  // Processing metadata
  processing: {
    processed_by: "apple_intelligence_native",
    processing_version: "2.0.0",
    embedding_model: "apple_foundation_models",
    extraction_method: "llm_structured",
    validation_status: "verified|pending|flagged",
    processing_time_ms: 1250,
    apple_intelligence_features: {
      sentiment: "positive|negative|neutral",
      language: "en",
      complexity_score: 0.6,
      readability_score: 0.8
    }
  },
  
  // Advanced features
  advanced: {
    memory_type: "episodic|semantic|procedural|working",
    consolidation_status: "fresh|consolidating|consolidated|archived",
    retrieval_cues: ["keyword1", "keyword2"], // What triggers this memory
    associated_skills: ["programming", "project_management"],
    learning_objective: "understand_concept|solve_problem|remember_fact",
    memory_strength: 0.9, // How well consolidated this memory is
    interference_risk: 0.1 // Risk of being overwritten by similar memories
  }
};

// Enhanced Collection Configuration
const ENHANCED_COLLECTION_CONFIG = {
  vectors: {
    // Primary semantic embedding
    content: {
      size: 1536,
      distance: "Cosine"
    },
    // Entity embeddings for entity-based search
    entities: {
      size: 768,
      distance: "Cosine"
    },
    // Temporal embeddings for time-based patterns
    temporal: {
      size: 256,
      distance: "Cosine"
    }
  },
  
  // Optimized for complex queries
  optimizers_config: {
    deleted_threshold: 0.2,
    vacuum_min_vector_number: 1000,
    default_segment_number: 2
  },
  
  // Enable quantization for performance
  quantization_config: {
    scalar: {
      type: "int8",
      quantile: 0.99,
      always_ram: true
    }
  }
};

// Advanced Query Examples
const ADVANCED_QUERIES = {
  
  // Multi-vector search with relationship filtering
  semanticWithRelationships: {
    vector: {
      name: "content",
      vector: [/* embedding */]
    },
    filter: {
      must: [
        { key: "context.user_id", match: { value: "gabriel" } },
        { key: "scoring.importance", range: { gte: 0.7 } }
      ],
      should: [
        { key: "relationships.similar_to", match: { any: ["memory_id_1"] } },
        { key: "semantic_tags", match: { any: ["machine_learning"] } }
      ]
    },
    limit: 10,
    with_payload: true,
    score_threshold: 0.7
  },
  
  // Temporal pattern search
  temporalPatterns: {
    vector: {
      name: "temporal", 
      vector: [/* temporal embedding */]
    },
    filter: {
      must: [
        { key: "temporal.time_period", match: { value: "morning" } },
        { key: "temporal.day_of_week", match: { value: "tuesday" } }
      ]
    }
  },
  
  // Entity-based discovery
  entitySearch: {
    vector: {
      name: "entities",
      vector: [/* entity embedding */]
    },
    filter: {
      must: [
        { key: "entities.people", match: { any: ["John"] } },
        { key: "content_type", match: { value: "conversation" } }
      ]
    }
  },
  
  // Complex relationship traversal
  relationshipTraversal: {
    // First find memories that reference a specific memory
    step1: {
      filter: {
        must: [
          { key: "relationships.references", match: { any: ["target_memory_id"] } }
        ]
      }
    },
    // Then find what those memories are referenced by
    step2: {
      filter: {
        must: [
          { key: "relationships.referenced_by", match: { any: ["results_from_step1"] } }
        ]
      }
    }
  }
};

export { ENHANCED_MEMORY_SCHEMA, ENHANCED_COLLECTION_CONFIG, ADVANCED_QUERIES };