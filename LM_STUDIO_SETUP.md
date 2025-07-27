# OpenMemory MCP with LM Studio Integration

This setup allows you to run OpenMemory MCP with a local LM Studio instance running Gemma 3.

## Prerequisites

1. [LM Studio](https://lmstudio.ai/) installed and running
2. Docker and Docker Compose installed
3. Make utility installed

## Setup Instructions

### 1. Start LM Studio

1. Open LM Studio
2. Load the Gemma 3 model (`gemma-3-4b-it@q4_k_m`)
3. Start the local server by going to the "Local Server" tab and clicking "Start Server"
4. Make sure the server is running on `http://localhost:1234`

### 2. Test LM Studio API

You can test if LM Studio is properly set up with these commands:

```bash
# Test embeddings
curl http://127.0.0.1:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-nomic-embed-text-v1.5",
    "input": "Some text to embed"
  }'

# Test chat completions
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-3-4b-it@q4_k_m",
    "messages": [
      { "role": "system", "content": "Always answer in rhymes. Today is Thursday" },
      { "role": "user", "content": "What day is it today?" }
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": false
}'
```

### 3. Start OpenMemory MCP

Run the provided start script:

```bash
./start-with-lmstudio.sh
```

This script will:
1. Check if LM Studio is running
2. Build and start the OpenMemory MCP Docker containers
3. Configure the system to use your local LM Studio instance

### 4. Configure your MCP Clients

To connect tools like Claude Desktop, Cursor, or other MCP clients:

Add this configuration to your MCP client's settings:

```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8765/mcp/<mcp-client>/sse/<your-username>"
    }
  }
}
```

Replace `<mcp-client>` with your client name (e.g., "claude", "cursor") and `<your-username>` with your desired username.

For Windsurf users, use `serverUrl` instead of `url`.

### 5. Access the UI

The OpenMemory dashboard is available at: http://localhost:3000

## Troubleshooting

- If you encounter errors, check the Docker logs with `docker-compose logs`
- Make sure LM Studio is running before starting OpenMemory MCP
- Check that the correct models are loaded in LM Studio
