"""
Apple Foundation Models Integration
Proper integration with Apple's Foundation Models for intelligent memory processing
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    # Try to import Apple's Foundation Models
    import Foundation
    from Foundation import NSString, NSData, NSJSONSerialization
    import objc
    
    # Import Foundation Models framework
    import FoundationModels
    from FoundationModels import (
        FMInferenceRequest, 
        FMInferenceResponse, 
        FMChatMessage,
        FMModelConfiguration
    )
    FOUNDATION_MODELS_AVAILABLE = True
    
except ImportError as e:
    print(f"Foundation Models not available: {e}", file=sys.stderr)
    FOUNDATION_MODELS_AVAILABLE = False


class AppleIntelligenceFoundationModels:
    """
    Proper FoundationModels Foundation Models integration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.temperature = self.config.get('temperature', 0.1)
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.model_name = self.config.get('model', 'apple_intelligence')
        
        if not FOUNDATION_MODELS_AVAILABLE:
            raise RuntimeError("Apple Foundation Models framework not available")
    
    def generate_structured_response(self, prompt: str, system_prompt: str = None, max_attempts: int = 2) -> str:
        """
        Generate structured response using Apple Foundation Models with guided generation
        Following Apple's best practices for reliable JSON output
        """
        # Use low temperature for structural fidelity
        structured_params = {
            'temperature': 0.2,  # Low for structure reliability
            'topP': 0.9,
            'maxTokens': self.max_tokens,
            'stop': ["\n\n"]  # Prevent excessive output
        }
        
        attempt = 0
        last_error = None
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                # Create inference request
                request = FMInferenceRequest.alloc().init()
                
                # Create messages array
                messages = []
                
                # Add structured system message following Apple's patterns
                structured_system = system_prompt or """You are a data formatter. Output ONLY compact JSON matching the requested schema.
- No commentary, no Markdown, no code fences
- No keys beyond the schema
- Use ISO 8601 UTC timestamps where applicable
- Ensure valid JSON structure"""
                
                system_message = FMChatMessage.alloc().initWithRole_content_("system", structured_system)
                messages.append(system_message)
                
                # Add user message
                user_message = FMChatMessage.alloc().initWithRole_content_("user", prompt)
                messages.append(user_message)
                
                # Set messages
                request.setMessages_(messages)
                
                # Configure parameters for structured output
                request.setMaxTokens_(structured_params['maxTokens'])
                request.setTemperature_(structured_params['temperature'])
                
                # Set topP if available
                if hasattr(request, 'setTopP_'):
                    request.setTopP_(structured_params['topP'])
                
                # Set stop sequences if available
                if hasattr(request, 'setStopSequences_') and structured_params.get('stop'):
                    request.setStopSequences_(structured_params['stop'])
                
                # Execute inference
                response = request.executeInference()
                
                if response and response.content():
                    raw_output = response.content()
                    
                    # Apply repair heuristics following Apple's guidance
                    cleaned_output = self.repair_json_output(raw_output)
                    
                    # Validate JSON structure
                    try:
                        json.loads(cleaned_output)  # Validate JSON
                        return cleaned_output
                    except json.JSONDecodeError as json_err:
                        if attempt < max_attempts:
                            # Retry with repair prompt
                            repair_prompt = f"""The previous output had JSON errors: {str(json_err)}

Original output: {raw_output[:200]}...

Please provide the same information as valid, compact JSON only. Fix any syntax errors."""
                            prompt = repair_prompt
                            continue
                        else:
                            raise Exception(f"JSON validation failed after {max_attempts} attempts: {json_err}")
                else:
                    raise Exception("Foundation Models inference returned empty response")
                    
            except Exception as e:
                last_error = e
                if attempt >= max_attempts:
                    raise Exception(f"Foundation Models inference failed after {max_attempts} attempts: {str(e)}")
                
                # Reduce temperature for retry
                structured_params['temperature'] = max(0.1, structured_params['temperature'] - 0.1)
        
        raise Exception(f"All attempts failed. Last error: {last_error}")
    
    def repair_json_output(self, raw_output: str) -> str:
        """
        Apply repair heuristics following Apple's guidance for robust JSON extraction
        """
        # Strip whitespace
        cleaned = raw_output.strip()
        
        # Remove code fences
        cleaned = cleaned.replace('```json', '').replace('```', '')
        
        # Remove common prefixes/suffixes
        if cleaned.startswith('Here is') or cleaned.startswith('Here\'s'):
            lines = cleaned.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    cleaned = '\n'.join(lines[i:])
                    break
        
        # Find JSON boundaries
        start_idx = cleaned.find('{')
        if start_idx == -1:
            return cleaned
        
        # Find matching closing brace
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(cleaned)):
            if cleaned[i] == '{':
                brace_count += 1
            elif cleaned[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx != -1:
            cleaned = cleaned[start_idx:end_idx]
        
        # Remove trailing commas (common issue)
        import re
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        return cleaned.strip()
    
    def analyze_semantic_content(self, content: str, user_id: str) -> Dict[str, Any]:
        """
        Analyze content semantically using Foundation Models with guided generation
        """
        # Schema-first system prompt following Apple's patterns
        system_prompt = """You are a data formatter for semantic memory analysis.
Output ONLY compact JSON matching the exact schema below.
- No commentary, no Markdown, no code fences
- Use ISO 8601 UTC timestamps (e.g., 2025-08-12T17:30:00Z)
- Keep arrays concise and relevant
- Use lowercase for tags and categories"""
        
        analysis_prompt = f"""
        Analyze this memory content and provide comprehensive semantic analysis:
        
        Content: {content}
        User: {user_id}
        
        Extract and analyze:
        1. ENTITIES: People, places, organizations, concepts, dates, events
        2. RELATIONSHIPS: How entities relate to each other
        3. SENTIMENT: Emotional tone and sentiment analysis
        4. TEMPORAL_CONTEXT: Time references, sequences, durations
        5. IMPORTANCE: Rate importance 1-10 with reasoning
        6. MEMORY_TYPE: Categorize (fact, experience, preference, skill, goal, etc.)
        7. CONCEPTS: Abstract concepts and themes
        8. INTENT: Why is this being remembered?
        9. CONNECTIONS: Potential links to other memories
        10. CONTEXT: Situational and environmental context
        
        Respond with valid JSON:
        {{
            "entities": {{
                "people": ["person1", "person2"],
                "places": ["place1", "place2"],
                "organizations": ["org1", "org2"],
                "concepts": ["concept1", "concept2"],
                "dates": ["date1", "date2"],
                "events": ["event1", "event2"]
            }},
            "relationships": [
                {{"source": "entity1", "relationship": "type", "target": "entity2", "confidence": 0.9}}
            ],
            "sentiment": {{
                "primary_emotion": "emotion_name",
                "polarity": 0.5,
                "intensity": 0.7,
                "emotions": ["emotion1", "emotion2"]
            }},
            "temporal_context": {{
                "time_references": ["reference1", "reference2"],
                "temporal_type": "past|present|future",
                "duration_indicators": ["duration1"],
                "sequence_indicators": ["first", "then", "finally"]
            }},
            "importance": {{
                "score": 7,
                "reasoning": "explanation of importance",
                "factors": ["factor1", "factor2"]
            }},
            "memory_type": "primary_type",
            "concepts": [
                {{"concept": "concept_name", "abstraction_level": "concrete|abstract", "domain": "domain_name"}}
            ],
            "intent": {{
                "primary_intent": "remember|learn|reference|share",
                "secondary_intents": ["intent1", "intent2"],
                "retrieval_cues": ["cue1", "cue2"]
            }},
            "potential_connections": [
                {{"type": "semantic|temporal|causal", "description": "connection description", "strength": 0.8}}
            ],
            "context": {{
                "situational": "context description",
                "environmental": "environment description",
                "social": "social context",
                "professional": "work context"
            }},
            "metadata": {{
                "content_hash": "hash_value",
                "analysis_timestamp": "{datetime.now().isoformat()}",
                "confidence_score": 0.85,
                "processing_time_ms": 1500
            }}
        }}
        """
        
        try:
            start_time = datetime.now()
            response = self.generate_structured_response(analysis_prompt, system_prompt, max_attempts=3)
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse JSON response with validation
            analysis = json.loads(response)
            
            # Validate required structure
            required_keys = ['entities', 'relationships', 'sentiment', 'temporal_context', 
                           'importance', 'memory_type', 'concepts', 'intent', 
                           'potential_connections', 'context', 'metadata']
            
            for key in required_keys:
                if key not in analysis:
                    analysis[key] = self._get_default_value_for_key(key)
            
            # Add computed metadata
            analysis["metadata"]["content_hash"] = hash(content) & 0x7FFFFFFF  # Positive hash
            analysis["metadata"]["analysis_timestamp"] = datetime.now().isoformat()
            analysis["metadata"]["processing_time_ms"] = processing_time
            analysis["metadata"]["user_id"] = user_id
            analysis["metadata"]["foundation_models_used"] = True
            
            return analysis
            
        except (json.JSONDecodeError, Exception) as e:
            # Return structured fallback following Apple's error handling patterns
            return self._create_fallback_analysis(content, user_id, str(e))
    
    def _get_default_value_for_key(self, key: str) -> Any:
        """Get default value for missing keys in analysis"""
        defaults = {
            'entities': {"people": [], "places": [], "organizations": [], "concepts": [], "dates": [], "events": []},
            'relationships': [],
            'sentiment': {"primary_emotion": "neutral", "polarity": 0.0, "intensity": 0.5, "emotions": []},
            'temporal_context': {"time_references": [], "temporal_type": "present", "duration_indicators": [], "sequence_indicators": []},
            'importance': {"score": 5, "reasoning": "Default importance", "factors": []},
            'memory_type': "general",
            'concepts': [],
            'intent': {"primary_intent": "remember", "secondary_intents": [], "retrieval_cues": []},
            'potential_connections': [],
            'context': {"situational": "", "environmental": "", "social": "", "professional": ""},
            'metadata': {}
        }
        return defaults.get(key, {})
    
    def _create_fallback_analysis(self, content: str, user_id: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback analysis structure when parsing fails"""
        return {
            "entities": {"people": [], "places": [], "organizations": [], "concepts": [], "dates": [], "events": []},
            "relationships": [],
            "sentiment": {"primary_emotion": "neutral", "polarity": 0.0, "intensity": 0.5, "emotions": []},
            "temporal_context": {"time_references": [], "temporal_type": "present", "duration_indicators": [], "sequence_indicators": []},
            "importance": {"score": 5, "reasoning": "Fallback analysis due to parsing error", "factors": ["parsing_error"]},
            "memory_type": "general",
            "concepts": [],
            "intent": {"primary_intent": "remember", "secondary_intents": [], "retrieval_cues": []},
            "potential_connections": [],
            "context": {"situational": "", "environmental": "", "social": "", "professional": ""},
            "metadata": {
                "content_hash": hash(content) & 0x7FFFFFFF,
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": 0.2,
                "processing_time_ms": 0,
                "user_id": user_id,
                "foundation_models_used": True,
                "parsing_error": error_msg,
                "fallback_used": True
            }
        }
    
    def analyze_similarity(self, content1: str, content2: str) -> Dict[str, Any]:
        """
        Analyze semantic similarity using guided generation
        """
        system_prompt = """You are a data formatter for similarity analysis.
Output ONLY compact JSON matching the exact schema.
- No commentary, no Markdown, no code fences
- Similarity scores must be numbers between 0.0 and 1.0
- Use specific, actionable recommendations"""
        
        similarity_prompt = f"""
        Analyze the semantic similarity between these two memory contents:
        
        Content 1: {content1}
        Content 2: {content2}
        
        Provide detailed similarity analysis:
        1. Overall semantic similarity (0.0 to 1.0)
        2. Entity overlap and relationships
        3. Conceptual similarity
        4. Temporal relationship
        5. Contextual similarity
        6. Recommended action (merge, keep_separate, update_existing)
        
        Respond with valid JSON:
        {{
            "overall_similarity": 0.85,
            "similarity_breakdown": {{
                "semantic": 0.9,
                "entity": 0.8,
                "conceptual": 0.85,
                "temporal": 0.7,
                "contextual": 0.75
            }},
            "shared_entities": [
                {{"entity": "entity_name", "type": "person|place|concept", "similarity": 0.95}}
            ],
            "conceptual_overlap": [
                {{"concept": "concept_name", "overlap_strength": 0.8}}
            ],
            "differences": [
                {{"aspect": "difference_type", "description": "what differs", "significance": 0.6}}
            ],
            "recommended_action": "merge|keep_separate|update_existing",
            "merge_strategy": {{
                "primary_content": "content1|content2|combined",
                "preserve_elements": ["element1", "element2"],
                "merge_approach": "append|replace|integrate"
            }},
            "confidence": 0.9,
            "reasoning": "detailed explanation of similarity assessment"
        }}
        """
        
        try:
            response = self.generate_structured_response(similarity_prompt, system_prompt, max_attempts=3)
            similarity_analysis = json.loads(response)
            
            # Validate and normalize similarity scores
            if "overall_similarity" in similarity_analysis:
                similarity_analysis["overall_similarity"] = max(0.0, min(1.0, float(similarity_analysis["overall_similarity"])))
            
            # Add metadata
            similarity_analysis["analysis_timestamp"] = datetime.now().isoformat()
            similarity_analysis["foundation_models_used"] = True
            
            return similarity_analysis
            
        except (json.JSONDecodeError, Exception) as e:
            return self._create_fallback_similarity(str(e))
    
    def analyze_search_intent(self, query: str, user_id: str, context: Dict = None) -> Dict[str, Any]:
        """
        Analyze search intent using guided generation
        """
        system_prompt = """You are a data formatter for search intent analysis.
Output ONLY compact JSON matching the exact schema.
- No commentary, no Markdown, no code fences
- Confidence scores must be numbers between 0.0 and 1.0
- Use specific intent categories and actionable strategies"""
        
        intent_prompt = f"""
        Analyze this search query to understand the user's intent:
        
        Query: {query}
        User: {user_id}
        Context: {json.dumps(context or {})}
        
        Determine:
        1. Primary search intent type
        2. Entities being sought
        3. Temporal scope and constraints
        4. Relationship focus
        5. Expected result types
        6. Search strategy recommendations
        
        Respond with valid JSON:
        {{
            "intent_type": "factual|experiential|relational|temporal|conceptual",
            "intent_confidence": 0.9,
            "entities_sought": [
                {{"entity": "entity_name", "type": "person|place|concept", "importance": 0.8}}
            ],
            "temporal_scope": {{
                "type": "recent|specific_period|all_time|relative",
                "period": "last_week|2023|etc",
                "temporal_keywords": ["yesterday", "recently"]
            }},
            "relationship_focus": {{
                "seeking_relationships": true,
                "relationship_types": ["causal", "temporal", "semantic"],
                "entity_connections": ["entity1", "entity2"]
            }},
            "expected_results": {{
                "result_type": "memories|entities|relationships|insights",
                "result_count_estimate": 10,
                "result_diversity": "focused|diverse|comprehensive"
            }},
            "search_strategy": {{
                "primary_approach": "semantic|keyword|hybrid",
                "weight_distribution": {{
                    "semantic": 0.6,
                    "temporal": 0.2,
                    "relational": 0.2
                }},
                "expansion_needed": true,
                "filters_recommended": ["filter1", "filter2"]
            }},
            "context_importance": "high|medium|low",
            "ambiguity_level": 0.3,
            "clarification_needed": false,
            "suggested_refinements": ["refinement1", "refinement2"]
        }}
        """
        
        try:
            response = self.generate_structured_response(intent_prompt, system_prompt, max_attempts=3)
            intent_analysis = json.loads(response)
            
            # Validate confidence scores
            if "intent_confidence" in intent_analysis:
                intent_analysis["intent_confidence"] = max(0.0, min(1.0, float(intent_analysis["intent_confidence"])))
            
            # Add metadata
            intent_analysis["analysis_timestamp"] = datetime.now().isoformat()
            intent_analysis["query_hash"] = hash(query) & 0x7FFFFFFF
            intent_analysis["foundation_models_used"] = True
            
            return intent_analysis
            
        except (json.JSONDecodeError, Exception) as e:
            return self._create_fallback_intent(query, str(e))


    def _create_fallback_similarity(self, error_msg: str) -> Dict[str, Any]:
        """Create fallback similarity analysis when parsing fails"""
        return {
            "overall_similarity": 0.5,
            "similarity_breakdown": {"semantic": 0.5, "entity": 0.5, "conceptual": 0.5, "temporal": 0.5, "contextual": 0.5},
            "shared_entities": [],
            "conceptual_overlap": [],
            "differences": [],
            "recommended_action": "keep_separate",
            "merge_strategy": {"primary_content": "content1", "preserve_elements": [], "merge_approach": "keep_separate"},
            "confidence": 0.2,
            "reasoning": "Fallback analysis due to parsing error",
            "analysis_timestamp": datetime.now().isoformat(),
            "foundation_models_used": True,
            "parsing_error": error_msg,
            "fallback_used": True
        }
    
    def _create_fallback_intent(self, query: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback intent analysis when parsing fails"""
        return {
            "intent_type": "factual",
            "intent_confidence": 0.5,
            "entities_sought": [],
            "temporal_scope": {"type": "all_time", "period": "", "temporal_keywords": []},
            "relationship_focus": {"seeking_relationships": False, "relationship_types": [], "entity_connections": []},
            "expected_results": {"result_type": "memories", "result_count_estimate": 10, "result_diversity": "diverse"},
            "search_strategy": {
                "primary_approach": "semantic",
                "weight_distribution": {"semantic": 0.7, "temporal": 0.15, "relational": 0.15},
                "expansion_needed": False,
                "filters_recommended": []
            },
            "context_importance": "medium",
            "ambiguity_level": 0.5,
            "clarification_needed": False,
            "suggested_refinements": [],
            "analysis_timestamp": datetime.now().isoformat(),
            "query_hash": hash(query) & 0x7FFFFFFF,
            "foundation_models_used": True,
            "parsing_error": error_msg,
            "fallback_used": True
        }


def create_foundation_models_instance(config: Dict[str, Any] = None) -> AppleIntelligenceFoundationModels:
    """
    Factory function to create Foundation Models instance
    """
    if not FOUNDATION_MODELS_AVAILABLE:
        raise RuntimeError("Apple Foundation Models framework not available on this system")
    
    return AppleIntelligenceFoundationModels(config)


# Test function
if __name__ == "__main__":
    if FOUNDATION_MODELS_AVAILABLE:
        try:
            fm = create_foundation_models_instance()
            test_result = fm.analyze_semantic_content("I learned Python today", "test_user")
            print(json.dumps(test_result, indent=2))
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("Foundation Models not available for testing")