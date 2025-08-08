#!/bin/bash

# Mem0 MCP Server Installation Script for Claude Desktop
# This script sets up the Mem0 MCP server for use with Claude Desktop

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the absolute path to the mem0 project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MCP_SERVER_PATH="$PROJECT_ROOT/integrations/mcp/server.py"

log_info "Setting up Mem0 MCP Server for Claude Desktop..."
log_info "Project root: $PROJECT_ROOT"

# Check if Claude Desktop is installed
CLAUDE_CONFIG_DIR=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
else
    log_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

log_info "Claude Desktop config location: $CLAUDE_CONFIG_FILE"

# Check if Claude Desktop is installed
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    log_error "Claude Desktop not found. Please install Claude Desktop first."
    log_info "Download from: https://claude.ai/download"
    exit 1
fi

# Install required Python packages
log_info "Installing required Python packages..."
python3 -m pip install mcp mem0ai psycopg2-binary redis requests

# Make server script executable
chmod +x "$MCP_SERVER_PATH"

# Create backup of existing config
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    log_info "Backing up existing Claude Desktop config..."
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Prompt for API keys
log_info "Please provide your API keys (press Enter to skip):"

read -p "OpenAI API Key: " OPENAI_API_KEY
read -p "Qdrant API Key (optional): " QDRANT_API_KEY

# Set default values if not provided
OPENAI_API_KEY=${OPENAI_API_KEY:-"your-openai-api-key-here"}
QDRANT_API_KEY=${QDRANT_API_KEY:-""}

# Create the MCP configuration
log_info "Creating MCP server configuration..."

# Create config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Generate the configuration
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "mem0-memory": {
      "command": "python3",
      "args": [
        "$MCP_SERVER_PATH"
      ],
      "env": {
        "OPENAI_API_KEY": "$OPENAI_API_KEY",
        "QDRANT_URL": "http://localhost:26333",
        "QDRANT_API_KEY": "$QDRANT_API_KEY",
        "QDRANT_COLLECTION": "mem0_memories",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2:3b",
        "OPENAI_MODEL": "gpt-4o-mini",
        "EMBEDDINGS_MODEL": "text-embedding-3-small",
        "REDIS_URL": "redis://localhost:26379",
        "POSTGRES_URL": "postgresql://mem0:mem0_secure_password_2024@localhost:25432/mem0",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "$PROJECT_ROOT"
      },
      "disabled": false,
      "alwaysAllow": [
        "add_memory",
        "search_memories",
        "get_all_memories"
      ],
      "timeout": 30000
    }
  }
}
EOF

log_success "MCP server configuration created successfully!"

# Test the server
log_info "Testing MCP server..."
if python3 "$MCP_SERVER_PATH" --help > /dev/null 2>&1; then
    log_success "MCP server script is executable"
else
    log_warning "MCP server test failed - this is normal if dependencies are missing"
fi

# Check if infrastructure is running
log_info "Checking infrastructure services..."

# Check Qdrant
if curl -s http://localhost:26333/ > /dev/null 2>&1; then
    log_success "Qdrant is running on port 26333"
else
    log_warning "Qdrant not detected on port 26333"
    log_info "Start infrastructure with: ./deployment/scripts/start-infrastructure.sh"
fi

# Check Ollama
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    log_success "Ollama is running on port 11434"
else
    log_warning "Ollama not detected on port 11434"
fi

# Check Redis
if redis-cli -p 26379 ping > /dev/null 2>&1; then
    log_success "Redis is running on port 26379"
else
    log_warning "Redis not detected on port 26379"
fi

# Check PostgreSQL
if pg_isready -h localhost -p 25432 -U mem0 > /dev/null 2>&1; then
    log_success "PostgreSQL is running on port 25432"
else
    log_warning "PostgreSQL not detected on port 25432"
fi

echo ""
log_success "Mem0 MCP Server installation complete!"
echo ""
log_info "📋 Next steps:"
echo "   1. Start infrastructure services (if not running):"
echo "      ./deployment/scripts/start-infrastructure.sh"
echo ""
echo "   2. Update your API keys in the config file:"
echo "      $CLAUDE_CONFIG_FILE"
echo ""
echo "   3. Restart Claude Desktop to load the new MCP server"
echo ""
echo "   4. Test the integration by asking Claude:"
echo "      'Add this to memory: I love pizza'"
echo "      'Search my memories for food preferences'"
echo ""
log_info "📚 Documentation:"
echo "   - MCP Server Guide: $PROJECT_ROOT/integrations/mcp/README.md"
echo "   - API Reference: $PROJECT_ROOT/documentation/api/README.md"
echo ""
log_info "🔧 Configuration file location:"
echo "   $CLAUDE_CONFIG_FILE"
echo ""
log_info "🚨 Troubleshooting:"
echo "   - Check Claude Desktop logs for MCP server errors"
echo "   - Verify infrastructure services are running"
echo "   - Ensure API keys are correctly set"