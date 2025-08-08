# Design Document

## Overview

This design implements Apple Intelligence Foundation Models integration with the existing mem0 memory system. The current system uses Ollama (llama3.2:3b + nomic-embed-text) but needs to be replaced with Apple Intelligence providers that leverage macOS Foundation Models framework for completely local, on-device processing.

## Architecture

### Current Architecture
```
Claude Desktop/Kiro IDE
    ↓ MCP Protocol
Node.js MCP Server (server.js)
    ↓ Python subprocess
Python Memory Operations (memory_operations.py)
    ↓ mem0 with Ollama
Local Infrastructure (Qdrant + PostgreSQL + Redis)
```

### Target Architecture
```
Claude Desktop/Kiro IDE
    ↓ MCP Protocol
Node.js MCP Server (server.js)
    ↓ Python subprocess
Python Memory Operations (memory_operations.py)
    ↓ mem0 with Apple Intelligence
Apple Intelligence Foundation Models (macOS)
    ↓ Neural Engine
Local Infrastructure (Qdrant + PostgreSQL + Redis)
```

## Components and Interfaces

### 1. Apple Intelligence LLM Provider

**File**: `mem0/llms/apple_intelligence.py`

```python
class AppleIntelligenceLLM(LLMBase):
    """Apple Intelligence LLM provider using Foundation Models framework"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model = "apple-intelligence-foundation"
        self.max_tokens = config.get("max_tokens", 500)
        self.temperature = config.get("temperature", 0.3)
        self._initialize_foundation_models()
    
    def _initialize_foundation_models(self):
        """Initialize connection to macOS Foundation Models"""
        # Use PyObjC to interface with Foundation Models framework
        pass
    
    def generate_response(self, messages: List[Dict], **kwargs) -> str:
        """Generate response using Apple Intelligence"""
        # Call Foundation Models API for text generation
        pass
```

**Integration Points**:
- Uses PyObjC to interface with macOS Foundation Models framework
- Implements LLMBase interface for seamless mem0 integration
- Handles memory extraction, fact retrieval, and memory updates
- Provides fallback error handling when Apple Intelligence unavailable

### 2. Apple Intelligence Embedding Provider

**File**: `mem0/embeddings/apple_intelligence.py`

```python
class AppleIntelligenceEmbedder(EmbeddingBase):
    """Apple Intelligence embedder using Foundation Models"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model = "apple-intelligence-embeddings"
        self.dimensions = config.get("dimensions", 1536)
        self._initialize_foundation_models()
    
    def embed(self, text: str, **kwargs) -> List[float]:
        """Generate embeddings using Apple Intelligence"""
        # Call Foundation Models API for embedding generation
        pass
```

**Integration Points**:
- Uses PyObjC to interface with macOS Foundation Models framework
- Implements EmbeddingBase interface for seamless mem0 integration
- Generates embeddings for memory storage and semantic search
- Optimized for Apple Silicon Neural Engine processing

### 3. Foundation Models Interface Layer

**File**: `mem0/utils/apple_intelligence.py`

```python
class FoundationModelsInterface:
    """Interface layer for macOS Foundation Models framework"""
    
    def __init__(self):
        self._check_availability()
        self._initialize_framework()
    
    def _check_availability(self):
        """Check if Foundation Models framework is available"""
        # Verify macOS version and Apple Intelligence availability
        pass
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Foundation Models"""
        pass
    
    def generate_embeddings(self, text: str, **kwargs) -> List[float]:
        """Generate embeddings using Foundation Models"""
        pass
```

**Key Features**:
- Detects macOS version and Apple Intelligence availability
- Provides unified interface to Foundation Models framework
- Handles Neural Engine optimization
- Manages privacy-first processing

### 4. Updated MCP Configuration

**File**: `integrations/mcp/memory_operations.py`

```python
def initialize_memory():
    """Initialize Mem0 memory with Apple Intelligence configuration"""
    config = {
        "llm": {
            "provider": "apple_intelligence",
            "config": {
                "model": "apple-intelligence-foundation",
                "max_tokens": 500,
                "temperature": 0.3
            }
        },
        "embedder": {
            "provider": "apple_intelligence", 
            "config": {
                "model": "apple-intelligence-embeddings",
                "dimensions": 1536
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "url": os.getenv("QDRANT_URL"),
                "collection_name": os.getenv("QDRANT_COLLECTION", "gabriel_apple_intelligence_memories")
            }
        }
    }
    
    return Memory.from_config(config)
```

### 5. Multi-Agent Memory Sharing

**Enhancement to existing MCP servers**:

```python
def add_memory_with_agent_context(params: Dict[str, Any]) -> Dict[str, Any]:
    """Add memory with multi-agent context tracking"""
    
    # Extract agent information
    agent_id = params.get("agent_id", "default")
    run_id = params.get("run_id")
    
    # Enhanced metadata for multi-agent scenarios
    metadata = {
        "agent_id": agent_id,
        "run_id": run_id,
        "conversation_context": "multi_agent",
        "processed_by": "apple_intelligence",
        "timestamp": datetime.now().isoformat()
    }
    
    # Add memory with Apple Intelligence processing
    result = memory.add(
        messages=params.get("messages"),
        user_id=params.get("user_id", "gabriel"),
        metadata=metadata
    )
    
    return result
```

## Data Models

### Memory Item with Apple Intelligence Metadata

```python
class AppleIntelligenceMemoryItem(MemoryItem):
    """Extended memory item with Apple Intelligence metadata"""
    
    apple_intelligence_processed: bool = True
    neural_engine_optimized: bool = True
    foundation_model_version: Optional[str] = None
    semantic_tags: List[str] = []
    relevance_score: Optional[float] = None
    agent_context: Optional[Dict[str, Any]] = None
```

### Configuration Schema

```python
class AppleIntelligenceConfig:
    """Configuration for Apple Intelligence integration"""
    
    foundation_models_enabled: bool = True
    neural_engine_optimization: bool = True
    privacy_mode: str = "strict"  # strict, moderate, open
    fallback_provider: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.3
    embedding_dimensions: int = 1536
```

## Error Handling

### Apple Intelligence Availability Check

```python
def check_apple_intelligence_availability() -> bool:
    """Check if Apple Intelligence is available on the system"""
    try:
        # Check macOS version (requires macOS 15.1+)
        import platform
        version = platform.mac_ver()[0]
        major, minor = map(int, version.split('.')[:2])
        
        if major < 15 or (major == 15 and minor < 1):
            return False
        
        # Check if Foundation Models framework is available
        import objc
        foundation_models = objc.lookUpClass('MLModel')  # Simplified check
        return foundation_models is not None
        
    except Exception:
        return False
```

### Graceful Fallback Strategy

```python
class AppleIntelligenceFallback:
    """Fallback strategy when Apple Intelligence is unavailable"""
    
    def __init__(self, fallback_provider: str = "ollama"):
        self.fallback_provider = fallback_provider
        self.apple_intelligence_available = check_apple_intelligence_availability()
    
    def get_llm_provider(self):
        if self.apple_intelligence_available:
            return "apple_intelligence"
        else:
            logger.warning("Apple Intelligence unavailable, falling back to Ollama")
            return self.fallback_provider
```

## Testing Strategy

### Unit Tests

1. **Apple Intelligence Provider Tests**
   - Test LLM provider initialization
   - Test embedding provider initialization
   - Test Foundation Models interface
   - Mock Apple Intelligence responses for CI/CD

2. **Integration Tests**
   - Test mem0 with Apple Intelligence providers
   - Test MCP server with Apple Intelligence
   - Test multi-agent memory sharing
   - Test fallback scenarios

3. **System Tests**
   - End-to-end memory operations through MCP
   - Claude Desktop integration testing
   - Kiro IDE integration testing
   - Performance testing with Neural Engine

### Test Configuration

```python
# Test configuration for Apple Intelligence
APPLE_INTELLIGENCE_TEST_CONFIG = {
    "llm": {
        "provider": "apple_intelligence",
        "config": {
            "model": "apple-intelligence-foundation",
            "test_mode": True  # Use mock responses in tests
        }
    },
    "embedder": {
        "provider": "apple_intelligence",
        "config": {
            "model": "apple-intelligence-embeddings",
            "test_mode": True
        }
    }
}
```

### Mock Apple Intelligence for Testing

```python
class MockAppleIntelligence:
    """Mock Apple Intelligence for testing environments"""
    
    def generate_text(self, prompt: str) -> str:
        return f"Mock Apple Intelligence response for: {prompt[:50]}..."
    
    def generate_embeddings(self, text: str) -> List[float]:
        # Generate deterministic embeddings for testing
        return [0.1] * 1536
```

## Migration Strategy

### Phase 1: Implement Apple Intelligence Providers
1. Create `mem0/llms/apple_intelligence.py`
2. Create `mem0/embeddings/apple_intelligence.py`
3. Create `mem0/utils/apple_intelligence.py`
4. Update factory classes to register new providers

### Phase 2: Update MCP Servers
1. Update `integrations/mcp/memory_operations.py` to use Apple Intelligence
2. Add multi-agent memory sharing capabilities
3. Update configuration handling

### Phase 3: Chrome Extension Integration
1. Update Chrome extension to connect to local MCP server
2. Implement memory migration from managed service
3. Test web memory operations with Apple Intelligence

### Phase 4: Testing and Optimization
1. Comprehensive testing on macOS with Apple Intelligence
2. Performance optimization for Neural Engine
3. Documentation and user guides

## Performance Considerations

### Neural Engine Optimization
- Batch embedding generation when possible
- Optimize prompt sizes for Foundation Models
- Cache frequently accessed memories
- Use Apple Intelligence's built-in optimization features

### Memory Management
- Efficient handling of large conversation contexts
- Streaming responses for long text generation
- Proper cleanup of Foundation Models resources

### Concurrency
- Thread-safe access to Foundation Models
- Proper resource sharing between MCP requests
- Efficient handling of multiple agent contexts

## Security and Privacy

### On-Device Processing
- All Apple Intelligence operations occur locally
- No external API calls for LLM or embedding operations
- Data never leaves the device during processing

### Privacy Compliance
- Follows Apple's privacy-first approach
- Transparent logging of all operations
- User control over data processing and storage

### Access Control
- Secure access to Foundation Models framework
- Proper sandboxing of memory operations
- Audit trail for all memory modifications