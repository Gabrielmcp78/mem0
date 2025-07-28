# Mem0 Integrations Guide

This guide covers all available integrations for Mem0, from agent frameworks to UI components.

## 🤖 Agent Frameworks

### AutoGen Integration
```python
from mem0 import Memory
from autogen import ConversableAgent

memory = Memory()

class MemoryAgent(ConversableAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = memory
    
    def generate_reply(self, messages, sender, config):
        # Retrieve relevant memories
        context = self.memory.search(messages[-1]["content"], user_id=sender.name)
        
        # Generate response with memory context
        response = super().generate_reply(messages, sender, config)
        
        # Store conversation in memory
        self.memory.add(messages + [{"role": "assistant", "content": response}], 
                       user_id=sender.name)
        
        return response
```

### CrewAI Integration
```python
from mem0 import Memory
from crewai import Agent, Task, Crew

memory = Memory()

def create_memory_agent(role, goal, backstory):
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        memory=True,
        tools=[memory_tool]
    )

def memory_tool(query: str, user_id: str = "default"):
    """Search and retrieve relevant memories"""
    return memory.search(query, user_id=user_id)
```

### LangChain Integration
```python
from mem0 import Memory
from langchain.memory import BaseMemory

class Mem0Memory(BaseMemory):
    def __init__(self, user_id: str = "default"):
        self.memory = Memory()
        self.user_id = user_id
    
    def save_context(self, inputs, outputs):
        conversation = [
            {"role": "user", "content": inputs["input"]},
            {"role": "assistant", "content": outputs["output"]}
        ]
        self.memory.add(conversation, user_id=self.user_id)
    
    def load_memory_variables(self, inputs):
        memories = self.memory.search(inputs["input"], user_id=self.user_id)
        return {"memory": memories}
```

## 🔌 MCP Server Integration

### Server Setup
```python
from mem0 import Memory
from mcp import Server
import asyncio

memory = Memory()
server = Server("mem0-mcp")

@server.tool()
async def add_memory(content: str, user_id: str = "default"):
    """Add a new memory"""
    return memory.add(content, user_id=user_id)

@server.tool()
async def search_memories(query: str, user_id: str = "default", limit: int = 5):
    """Search memories"""
    return memory.search(query, user_id=user_id, limit=limit)

@server.tool()
async def get_all_memories(user_id: str = "default"):
    """Get all memories for a user"""
    return memory.get_all(user_id=user_id)

if __name__ == "__main__":
    asyncio.run(server.run())
```

### Client Configuration
```json
{
  "mcpServers": {
    "mem0": {
      "command": "python",
      "args": ["integrations/mcp/server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

## 🎨 UI Components

### React Dashboard
```tsx
import React, { useState, useEffect } from 'react';
import { Memory } from 'mem0ai';

const MemoryDashboard: React.FC = () => {
  const [memories, setMemories] = useState([]);
  const [query, setQuery] = useState('');
  const memory = new Memory();

  const searchMemories = async () => {
    const results = await memory.search(query);
    setMemories(results);
  };

  return (
    <div className="memory-dashboard">
      <div className="search-section">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search memories..."
        />
        <button onClick={searchMemories}>Search</button>
      </div>
      
      <div className="memories-list">
        {memories.map((memory, index) => (
          <div key={index} className="memory-item">
            <p>{memory.content}</p>
            <small>{new Date(memory.created_at).toLocaleString()}</small>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MemoryDashboard;
```

### Vue.js Component
```vue
<template>
  <div class="memory-interface">
    <div class="input-section">
      <textarea
        v-model="newMemory"
        placeholder="Add a new memory..."
        rows="3"
      ></textarea>
      <button @click="addMemory">Add Memory</button>
    </div>
    
    <div class="memories-grid">
      <div
        v-for="memory in memories"
        :key="memory.id"
        class="memory-card"
      >
        {{ memory.content }}
      </div>
    </div>
  </div>
</template>

<script>
import { Memory } from 'mem0ai';

export default {
  data() {
    return {
      memory: new Memory(),
      memories: [],
      newMemory: ''
    };
  },
  methods: {
    async addMemory() {
      await this.memory.add(this.newMemory);
      this.newMemory = '';
      this.loadMemories();
    },
    async loadMemories() {
      this.memories = await this.memory.getAll();
    }
  },
  mounted() {
    this.loadMemories();
  }
};
</script>
```

## 🔧 Custom Implementations

### Custom Vector Store
```python
from mem0.vector_stores.base import VectorStoreBase
import numpy as np

class CustomVectorStore(VectorStoreBase):
    def __init__(self, config):
        self.config = config
        self.vectors = {}
    
    def create_col(self, name, vector_size, distance):
        self.vectors[name] = {
            'size': vector_size,
            'distance': distance,
            'data': []
        }
    
    def insert(self, name, vectors, payloads=None):
        collection = self.vectors[name]
        for i, vector in enumerate(vectors):
            collection['data'].append({
                'vector': vector,
                'payload': payloads[i] if payloads else {}
            })
    
    def search(self, name, query_vector, limit=5, filters=None):
        collection = self.vectors[name]
        results = []
        
        for item in collection['data']:
            similarity = np.dot(query_vector, item['vector'])
            results.append({
                'id': len(results),
                'score': similarity,
                'payload': item['payload']
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
```

### Custom LLM Provider
```python
from mem0.llms.base import LLMBase

class CustomLLM(LLMBase):
    def __init__(self, config):
        self.config = config
        # Initialize your custom LLM client
    
    def generate_response(self, messages, **kwargs):
        # Implement your custom generation logic
        response = self.client.generate(messages)
        return {
            'content': response.text,
            'usage': {
                'prompt_tokens': response.prompt_tokens,
                'completion_tokens': response.completion_tokens
            }
        }
```

## 📱 Mobile Integration

### React Native
```javascript
import { Memory } from 'mem0ai';

const MemoryService = {
  memory: new Memory(),
  
  async addMemory(content, userId = 'default') {
    return await this.memory.add(content, { user_id: userId });
  },
  
  async searchMemories(query, userId = 'default') {
    return await this.memory.search(query, { user_id: userId });
  }
};

export default MemoryService;
```

### Flutter/Dart
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class MemoryService {
  final String baseUrl = 'https://api.mem0.ai';
  final String apiKey;
  
  MemoryService(this.apiKey);
  
  Future<Map<String, dynamic>> addMemory(String content, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/memories/'),
      headers: {
        'Authorization': 'Bearer $apiKey',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'messages': [{'role': 'user', 'content': content}],
        'user_id': userId,
      }),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<List<dynamic>> searchMemories(String query, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/memories/search/'),
      headers: {
        'Authorization': 'Bearer $apiKey',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'query': query,
        'user_id': userId,
      }),
    );
    
    return jsonDecode(response.body)['results'];
  }
}
```

## 🔗 Webhook Integration

### Setting up Webhooks
```python
from mem0 import Memory
from flask import Flask, request, jsonify

app = Flask(__name__)
memory = Memory()

@app.route('/webhook/memory', methods=['POST'])
def memory_webhook():
    data = request.json
    
    if data['event'] == 'memory.created':
        # Handle new memory creation
        memory_data = data['memory']
        # Process the memory data
        
    elif data['event'] == 'memory.updated':
        # Handle memory updates
        memory_data = data['memory']
        # Process the update
        
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
```

## 📊 Analytics Integration

### Google Analytics
```javascript
import { Memory } from 'mem0ai';
import { gtag } from 'gtag';

class AnalyticsMemory extends Memory {
  async add(content, options = {}) {
    const result = await super.add(content, options);
    
    // Track memory addition
    gtag('event', 'memory_added', {
      'event_category': 'memory',
      'event_label': options.user_id || 'default'
    });
    
    return result;
  }
  
  async search(query, options = {}) {
    const result = await super.search(query, options);
    
    // Track memory search
    gtag('event', 'memory_searched', {
      'event_category': 'memory',
      'event_label': query,
      'value': result.length
    });
    
    return result;
  }
}
```

## 🔐 Security Considerations

### Authentication
```python
from mem0 import Memory
import jwt

class SecureMemory:
    def __init__(self, secret_key):
        self.memory = Memory()
        self.secret_key = secret_key
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def add_memory(self, content, token):
        user_id = self.verify_token(token)
        return self.memory.add(content, user_id=user_id)
    
    def search_memories(self, query, token):
        user_id = self.verify_token(token)
        return self.memory.search(query, user_id=user_id)
```

### Data Encryption
```python
from cryptography.fernet import Fernet
from mem0 import Memory

class EncryptedMemory:
    def __init__(self, encryption_key):
        self.memory = Memory()
        self.cipher = Fernet(encryption_key)
    
    def add_encrypted_memory(self, content, user_id):
        encrypted_content = self.cipher.encrypt(content.encode())
        return self.memory.add(encrypted_content.decode(), user_id=user_id)
    
    def search_encrypted_memories(self, query, user_id):
        results = self.memory.search(query, user_id=user_id)
        
        for result in results:
            try:
                decrypted = self.cipher.decrypt(result['content'].encode())
                result['content'] = decrypted.decode()
            except:
                pass  # Handle decryption errors
        
        return results
```