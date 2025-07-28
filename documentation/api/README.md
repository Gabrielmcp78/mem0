# Mem0 API Reference

Complete API reference for the Mem0 memory layer.

## 🚀 Quick Start

```python
from mem0 import Memory

# Initialize memory
memory = Memory()

# Basic operations
memory.add("User prefers dark mode", user_id="user123")
results = memory.search("preferences", user_id="user123")
all_memories = memory.get_all(user_id="user123")
```

## 📚 Core API

### Memory Class

The main interface for all memory operations.

#### Constructor

```python
Memory(config: Optional[Config] = None)
```

**Parameters:**
- `config` (Optional[Config]): Configuration object. If not provided, uses default configuration.

**Example:**
```python
from mem0 import Memory, Config

# Default configuration
memory = Memory()

# Custom configuration
config = Config(
    vector_store={"provider": "qdrant", "config": {"url": "http://localhost:6333"}},
    llm={"provider": "openai", "config": {"model": "gpt-4o-mini"}}
)
memory = Memory(config=config)
```

#### add()

Add new memories from conversation messages.

```python
add(
    messages: Union[str, List[Dict[str, str]]], 
    user_id: str = "default",
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Parameters:**
- `messages`: String or list of message dictionaries with 'role' and 'content' keys
- `user_id`: Unique identifier for the user
- `agent_id`: Optional agent identifier
- `run_id`: Optional run identifier for session tracking
- `metadata`: Optional metadata dictionary

**Returns:**
- Dictionary with operation result and message

**Example:**
```python
# String input
result = memory.add("I love pizza", user_id="user123")

# Message format
messages = [
    {"role": "user", "content": "I love pizza"},
    {"role": "assistant", "content": "Great! I'll remember that."}
]
result = memory.add(messages, user_id="user123")

# With metadata
result = memory.add(
    messages, 
    user_id="user123",
    metadata={"source": "chat", "timestamp": "2024-01-01T00:00:00Z"}
)
```

#### search()

Search for relevant memories based on a query.

```python
search(
    query: str,
    user_id: str = "default",
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `query`: Search query string
- `user_id`: User identifier to search within
- `agent_id`: Optional agent identifier filter
- `run_id`: Optional run identifier filter
- `limit`: Maximum number of results to return
- `filters`: Optional filters dictionary

**Returns:**
- List of memory dictionaries with relevance scores

**Example:**
```python
# Basic search
results = memory.search("food preferences", user_id="user123")

# Limited results
results = memory.search("food", user_id="user123", limit=5)

# With filters
results = memory.search(
    "preferences", 
    user_id="user123",
    filters={"category": "food"}
)
```

#### get_all()

Retrieve all memories for a user.

```python
get_all(
    user_id: str = "default",
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `user_id`: User identifier
- `agent_id`: Optional agent identifier filter
- `run_id`: Optional run identifier filter
- `limit`: Optional limit on number of results

**Returns:**
- List of all memory dictionaries

**Example:**
```python
# All memories for user
all_memories = memory.get_all(user_id="user123")

# Limited results
recent_memories = memory.get_all(user_id="user123", limit=10)
```

#### update()

Update an existing memory.

```python
update(
    memory_id: str,
    data: str,
    user_id: str = "default"
) -> Dict[str, Any]
```

**Parameters:**
- `memory_id`: Unique identifier of the memory to update
- `data`: New memory content
- `user_id`: User identifier

**Returns:**
- Dictionary with update result

**Example:**
```python
result = memory.update(
    memory_id="mem_123",
    data="I love both pizza and pasta",
    user_id="user123"
)
```

#### delete()

Delete a specific memory.

```python
delete(memory_id: str, user_id: str = "default") -> Dict[str, Any]
```

**Parameters:**
- `memory_id`: Unique identifier of the memory to delete
- `user_id`: User identifier

**Returns:**
- Dictionary with deletion result

**Example:**
```python
result = memory.delete(memory_id="mem_123", user_id="user123")
```

#### delete_all()

Delete all memories for a user.

```python
delete_all(user_id: str = "default") -> Dict[str, Any]
```

**Parameters:**
- `user_id`: User identifier

**Returns:**
- Dictionary with deletion result

**Example:**
```python
result = memory.delete_all(user_id="user123")
```

#### history()

Get the history of memory operations.

```python
history(
    user_id: str = "default",
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]
```

**Parameters:**
- `user_id`: User identifier
- `agent_id`: Optional agent identifier filter
- `run_id`: Optional run identifier filter
- `limit`: Maximum number of history entries

**Returns:**
- List of history entries

**Example:**
```python
history = memory.history(user_id="user123", limit=50)
```

## 🔧 Configuration API

### Config Class

Configuration management for Mem0.

```python
from mem0 import Config

config = Config(
    vector_store={
        "provider": "qdrant",
        "config": {
            "url": "http://localhost:6333",
            "api_key": "your-api-key"
        }
    },
    llm={
        "provider": "openai",
        "config": {
            "api_key": "your-openai-key",
            "model": "gpt-4o-mini"
        }
    },
    embeddings={
        "provider": "openai",
        "config": {
            "api_key": "your-openai-key",
            "model": "text-embedding-3-small"
        }
    }
)
```

### Environment Configuration

Configure Mem0 using environment variables:

```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Vector Store Configuration
VECTOR_STORE_PROVIDER=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Embeddings Configuration
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small
```

## 🌐 REST API

### Base URL
```
http://localhost:8000/v1
```

### Authentication
Include your API key in the Authorization header:
```
Authorization: Bearer your_api_key
```

### Endpoints

#### POST /memories/
Add new memories.

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "I love pizza"},
    {"role": "assistant", "content": "Great! I'll remember that."}
  ],
  "user_id": "user123",
  "agent_id": "agent456",
  "metadata": {"source": "chat"}
}
```

**Response:**
```json
{
  "message": "Memories added successfully",
  "results": [
    {
      "id": "mem_123",
      "memory": "User loves pizza",
      "user_id": "user123",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /memories/search/
Search memories.

**Request Body:**
```json
{
  "query": "food preferences",
  "user_id": "user123",
  "limit": 10,
  "filters": {"category": "food"}
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "mem_123",
      "memory": "User loves pizza",
      "score": 0.95,
      "user_id": "user123",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /memories/
Get all memories for a user.

**Query Parameters:**
- `user_id`: User identifier
- `agent_id`: Optional agent filter
- `limit`: Optional result limit

**Response:**
```json
{
  "results": [
    {
      "id": "mem_123",
      "memory": "User loves pizza",
      "user_id": "user123",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### PUT /memories/{memory_id}/
Update a specific memory.

**Request Body:**
```json
{
  "data": "User loves both pizza and pasta",
  "user_id": "user123"
}
```

#### DELETE /memories/{memory_id}/
Delete a specific memory.

**Query Parameters:**
- `user_id`: User identifier

#### DELETE /memories/
Delete all memories for a user.

**Query Parameters:**
- `user_id`: User identifier

#### GET /memories/history/
Get memory operation history.

**Query Parameters:**
- `user_id`: User identifier
- `agent_id`: Optional agent filter
- `limit`: Optional result limit

## 📊 Response Formats

### Memory Object
```json
{
  "id": "mem_123",
  "memory": "Extracted memory content",
  "user_id": "user123",
  "agent_id": "agent456",
  "run_id": "run789",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "metadata": {
    "source": "chat",
    "category": "preference"
  }
}
```

### Search Result
```json
{
  "id": "mem_123",
  "memory": "Extracted memory content",
  "score": 0.95,
  "user_id": "user123",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Operation Result
```json
{
  "message": "Operation completed successfully",
  "results": [...],
  "metadata": {
    "operation": "add",
    "count": 1,
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## ❌ Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request format",
    "details": "Missing required field: user_id"
  }
}
```

### Common Error Codes
- `INVALID_REQUEST`: Malformed request
- `UNAUTHORIZED`: Invalid or missing API key
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

## 🔍 Advanced Usage

### Batch Operations
```python
# Add multiple memories at once
memories = [
    {"role": "user", "content": "I like coffee"},
    {"role": "user", "content": "I work remotely"},
    {"role": "user", "content": "I have a cat named Whiskers"}
]

for msg in memories:
    memory.add([msg], user_id="user123")
```

### Custom Filters
```python
# Search with custom filters
results = memory.search(
    "preferences",
    user_id="user123",
    filters={
        "category": "food",
        "created_after": "2024-01-01T00:00:00Z",
        "metadata.source": "chat"
    }
)
```

### Memory Analytics
```python
# Get memory statistics
all_memories = memory.get_all(user_id="user123")
memory_count = len(all_memories)
recent_memories = [m for m in all_memories if m['created_at'] > '2024-01-01']
```

## 📝 Best Practices

1. **Use descriptive user_ids**: Make them meaningful for your application
2. **Include metadata**: Add context that helps with filtering and organization
3. **Regular cleanup**: Periodically review and clean up old memories
4. **Error handling**: Always handle potential errors in your application
5. **Rate limiting**: Respect API rate limits in production applications

## 🔗 Related Documentation

- [Integration Guide](../INTEGRATIONS.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Configuration Guide](guides/configuration.md)
- [Best Practices](guides/best-practices.md)