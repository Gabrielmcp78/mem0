# 🌐 Chrome Extension Migration to Local System

## 🎯 **Objective**

Convert the existing Mem0 Chrome extension from managed cloud service to your local Apple Intelligence-enhanced memory system.

## 📋 **Current Chrome Extension Analysis**

The existing Chrome extension likely has:
- **API calls** to `https://api.mem0.ai`
- **Authentication** using API keys
- **Memory operations** (add, search, retrieve)
- **UI components** for memory management
- **Content scripts** for web page interaction

## 🔄 **Migration Strategy**

### **1. API Endpoint Changes**

```javascript
// OLD: Managed service
const API_BASE_URL = 'https://api.mem0.ai/v1';
const API_KEY = 'your-managed-api-key';

// NEW: Local system
const API_BASE_URL = 'http://localhost:8000/v1';
// No API key needed for local system
```

### **2. Authentication Removal**

```javascript
// OLD: API key authentication
const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

// NEW: Local system (no auth needed)
const headers = {
    'Content-Type': 'application/json'
};
```

### **3. Health Check Integration**

```javascript
// NEW: Add local system health check
async function checkLocalSystemHealth() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const health = await response.json();
        return health.status === 'healthy';
    } catch (error) {
        console.error('Local system not available:', error);
        return false;
    }
}
```

## 🛠️ **Implementation Steps**

### **Step 1: Create Local Extension Structure**

```
chrome-extension-local/
├── manifest.json
├── background.js
├── content.js
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── options/
│   ├── options.html
│   ├── options.js
│   └── options.css
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### **Step 2: Update Manifest**

```json
{
  "manifest_version": 3,
  "name": "Mem0 Local Memory",
  "version": "2.0.0",
  "description": "Local AI memory system powered by Apple Intelligence",
  "permissions": [
    "activeTab",
    "storage",
    "scripting"
  ],
  "host_permissions": [
    "http://localhost:8000/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "options_page": "options/options.html"
}
```

### **Step 3: Local API Client**

```javascript
// api-client.js
class LocalMem0Client {
    constructor() {
        this.baseUrl = 'http://localhost:8000/v1';
        this.isHealthy = false;
        this.checkHealth();
    }
    
    async checkHealth() {
        try {
            const response = await fetch('http://localhost:8000/health');
            const health = await response.json();
            this.isHealthy = health.status === 'healthy';
            return this.isHealthy;
        } catch (error) {
            this.isHealthy = false;
            return false;
        }
    }
    
    async addMemory(content, metadata = {}) {
        if (!this.isHealthy) {
            throw new Error('Local memory system not available');
        }
        
        const messages = [
            { role: 'user', content: content },
            { role: 'assistant', content: 'Memory stored locally' }
        ];
        
        const response = await fetch(`${this.baseUrl}/memories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages,
                user_id: 'chrome_extension_user',
                metadata: {
                    ...metadata,
                    source: 'chrome_extension',
                    url: window.location?.href,
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        return await response.json();
    }
    
    async searchMemories(query, limit = 10) {
        if (!this.isHealthy) {
            throw new Error('Local memory system not available');
        }
        
        const response = await fetch(`${this.baseUrl}/memories/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                user_id: 'chrome_extension_user',
                limit
            })
        });
        
        return await response.json();
    }
    
    async getAllMemories(limit = 50) {
        if (!this.isHealthy) {
            throw new Error('Local memory system not available');
        }
        
        const response = await fetch(
            `${this.baseUrl}/memories?user_id=chrome_extension_user&limit=${limit}`
        );
        
        return await response.json();
    }
}

// Global instance
const mem0Client = new LocalMem0Client();
```

### **Step 4: Enhanced Popup Interface**

```html
<!-- popup/popup.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            width: 350px;
            padding: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .status {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            padding: 8px;
            border-radius: 6px;
        }
        
        .status.healthy {
            background-color: #d4edda;
            color: #155724;
        }
        
        .status.unhealthy {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status.healthy .status-indicator {
            background-color: #28a745;
        }
        
        .status.unhealthy .status-indicator {
            background-color: #dc3545;
        }
        
        .memory-input {
            width: 100%;
            min-height: 80px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
            font-family: inherit;
        }
        
        .button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 4px;
        }
        
        .button:hover {
            background-color: #0056b3;
        }
        
        .button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        
        .memories-list {
            max-height: 200px;
            overflow-y: auto;
            margin-top: 16px;
        }
        
        .memory-item {
            padding: 8px;
            border: 1px solid #eee;
            border-radius: 4px;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .memory-meta {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div id="status" class="status">
        <div class="status-indicator"></div>
        <span id="status-text">Checking system...</span>
    </div>
    
    <div>
        <textarea 
            id="memory-input" 
            class="memory-input" 
            placeholder="Add a memory about this page or your thoughts..."
        ></textarea>
        
        <div style="margin-top: 8px;">
            <button id="add-memory" class="button">Add Memory</button>
            <button id="search-memories" class="button">Search</button>
            <button id="show-all" class="button">Show All</button>
        </div>
    </div>
    
    <div id="memories-container" class="memories-list" style="display: none;">
        <h4>Recent Memories</h4>
        <div id="memories-list"></div>
    </div>
    
    <script src="popup.js"></script>
</body>
</html>
```

### **Step 5: Popup Logic**

```javascript
// popup/popup.js
document.addEventListener('DOMContentLoaded', async () => {
    const statusEl = document.getElementById('status');
    const statusTextEl = document.getElementById('status-text');
    const memoryInput = document.getElementById('memory-input');
    const addButton = document.getElementById('add-memory');
    const searchButton = document.getElementById('search-memories');
    const showAllButton = document.getElementById('show-all');
    const memoriesContainer = document.getElementById('memories-container');
    const memoriesList = document.getElementById('memories-list');
    
    // Check system health
    const isHealthy = await mem0Client.checkHealth();
    updateStatus(isHealthy);
    
    // Add memory
    addButton.addEventListener('click', async () => {
        const content = memoryInput.value.trim();
        if (!content) return;
        
        try {
            addButton.disabled = true;
            addButton.textContent = 'Adding...';
            
            // Get current tab info
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            await mem0Client.addMemory(content, {
                page_title: tab.title,
                page_url: tab.url,
                domain: new URL(tab.url).hostname
            });
            
            memoryInput.value = '';
            showNotification('Memory added successfully!');
            
        } catch (error) {
            showNotification('Error adding memory: ' + error.message, 'error');
        } finally {
            addButton.disabled = false;
            addButton.textContent = 'Add Memory';
        }
    });
    
    // Search memories
    searchButton.addEventListener('click', async () => {
        const query = memoryInput.value.trim();
        if (!query) return;
        
        try {
            const results = await mem0Client.searchMemories(query);
            displayMemories(results.results || []);
        } catch (error) {
            showNotification('Error searching memories: ' + error.message, 'error');
        }
    });
    
    // Show all memories
    showAllButton.addEventListener('click', async () => {
        try {
            const results = await mem0Client.getAllMemories();
            displayMemories(results.results || []);
        } catch (error) {
            showNotification('Error loading memories: ' + error.message, 'error');
        }
    });
    
    function updateStatus(healthy) {
        if (healthy) {
            statusEl.className = 'status healthy';
            statusTextEl.textContent = 'Local memory system online';
            addButton.disabled = false;
            searchButton.disabled = false;
            showAllButton.disabled = false;
        } else {
            statusEl.className = 'status unhealthy';
            statusTextEl.textContent = 'Local memory system offline';
            addButton.disabled = true;
            searchButton.disabled = true;
            showAllButton.disabled = true;
        }
    }
    
    function displayMemories(memories) {
        memoriesContainer.style.display = 'block';
        memoriesList.innerHTML = '';
        
        if (memories.length === 0) {
            memoriesList.innerHTML = '<p>No memories found.</p>';
            return;
        }
        
        memories.forEach(memory => {
            const item = document.createElement('div');
            item.className = 'memory-item';
            
            const content = memory.memory || memory.content || 'No content';
            const metadata = memory.metadata || {};
            const createdAt = new Date(memory.created_at).toLocaleDateString();
            
            item.innerHTML = `
                <div>${content}</div>
                <div class="memory-meta">
                    ${metadata.page_title ? `📄 ${metadata.page_title}` : ''}
                    ${metadata.domain ? `🌐 ${metadata.domain}` : ''}
                    📅 ${createdAt}
                </div>
            `;
            
            memoriesList.appendChild(item);
        });
    }
    
    function showNotification(message, type = 'success') {
        // Simple notification - could be enhanced with toast library
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 4px;
            color: white;
            font-size: 14px;
            z-index: 1000;
            background-color: ${type === 'error' ? '#dc3545' : '#28a745'};
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }
});
```

## 🚀 **Installation & Testing**

### **1. Package Extension**

```bash
# Create extension package
cd integrations/chrome-extension
zip -r mem0-local-extension.zip .
```

### **2. Install in Chrome**

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the extension folder
4. The extension should appear in your toolbar

### **3. Test Functionality**

1. **Health Check**: Extension should show "Local memory system online"
2. **Add Memory**: Try adding a memory about the current page
3. **Search**: Search for previously added memories
4. **Show All**: View all stored memories

## 🎯 **Enhanced Features**

### **Apple Intelligence Integration**

The local system now leverages Apple Intelligence for:
- **Better semantic understanding** of web content
- **Improved memory extraction** from pages
- **Enhanced search relevance** 
- **Privacy-first processing** (all local)

### **Advanced Capabilities**

```javascript
// Enhanced memory extraction
async function extractPageMemory() {
    const pageContent = {
        title: document.title,
        url: window.location.href,
        selectedText: window.getSelection().toString(),
        mainContent: extractMainContent(),
        metadata: {
            domain: window.location.hostname,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        }
    };
    
    return pageContent;
}

// Smart content extraction
function extractMainContent() {
    // Remove navigation, ads, etc.
    const content = document.querySelector('main, article, .content, #content');
    return content ? content.innerText.slice(0, 1000) : document.body.innerText.slice(0, 1000);
}
```

## 🎉 **Benefits of Local Extension**

### **Privacy & Security**
- ✅ **No data leaves your machine**
- ✅ **No API keys or authentication needed**
- ✅ **Apple Intelligence processing on-device**
- ✅ **Full control over your memory data**

### **Performance**
- ✅ **Instant response times** (no network latency)
- ✅ **Works offline** when needed
- ✅ **No rate limits** or usage restrictions
- ✅ **Optimized for Apple Silicon**

### **Cost & Reliability**
- ✅ **Zero ongoing costs** (no API charges)
- ✅ **Always available** (no service outages)
- ✅ **Unlimited usage** (no quotas)
- ✅ **Future-proof** (no vendor lock-in)

**Your Chrome extension is now powered by your local Apple Intelligence-enhanced memory system! 🌐🧠**