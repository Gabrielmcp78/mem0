#!/bin/bash

# Apple Intelligence Local Memory System Startup Script
# This script starts the complete Apple Intelligence memory system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
QDRANT_PORT=6333
QDRANT_CONTAINER_NAME="qdrant-apple-intelligence"

echo -e "${PURPLE}🍎 Apple Intelligence Local Memory System Startup${NC}"
echo -e "${PURPLE}=================================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check macOS version
    if [[ "$OSTYPE" == "darwin"* ]]; then
        macos_version=$(sw_vers -productVersion)
        major_version=$(echo $macos_version | cut -d. -f1)
        minor_version=$(echo $macos_version | cut -d. -f2)
        
        if [[ $major_version -ge 15 ]] && [[ $minor_version -ge 1 ]] || [[ $major_version -gt 15 ]]; then
            print_success "macOS version: $macos_version (Apple Intelligence compatible)"
        else
            print_warning "macOS version: $macos_version (Apple Intelligence requires 15.1+)"
        fi
    else
        print_warning "Not running on macOS - Apple Intelligence will not be available"
    fi
    
    # Check architecture
    arch=$(uname -m)
    if [[ "$arch" == "arm64" ]]; then
        print_success "Architecture: $arch (Apple Silicon - Apple Intelligence compatible)"
    else
        print_warning "Architecture: $arch (Apple Intelligence requires Apple Silicon)"
    fi
    
    # Check Python
    if command_exists python3; then
        python_version=$(python3 --version)
        print_success "Python: $python_version"
    elif command_exists python; then
        python_version=$(python --version)
        print_success "Python: $python_version"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check Docker
    if command_exists docker; then
        if docker info >/dev/null 2>&1; then
            print_success "Docker is running"
        else
            print_error "Docker is installed but not running. Please start Docker."
            exit 1
        fi
    else
        print_error "Docker not found. Please install Docker for Qdrant support."
        exit 1
    fi
    
    echo ""
}

# Setup Python virtual environment and install dependencies
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Check if we're already in a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_success "Already using virtual environment: $VIRTUAL_ENV"
    else
        # Create virtual environment if it doesn't exist
        if [[ ! -d "venv" ]]; then
            print_status "Creating Python virtual environment..."
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        # Activate virtual environment
        print_status "Activating virtual environment..."
        source venv/bin/activate
        print_success "Virtual environment activated: $(which python)"
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip -q
    
    # Install required packages
    print_status "Installing Python dependencies..."
    pip install -q mem0ai mcp pyobjc qdrant-client
    
    print_success "Python dependencies installed"
    echo ""
}

# Test Apple Intelligence availability
test_apple_intelligence() {
    print_status "Testing Apple Intelligence availability..."
    
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT')

try:
    from mem0.utils.apple_intelligence import check_apple_intelligence_availability, get_apple_intelligence_status
    
    available = check_apple_intelligence_availability()
    status = get_apple_intelligence_status()
    
    if available:
        print('✅ Apple Intelligence: Available')
        print(f'   macOS Version: {status.get(\"macos_version\", \"unknown\")}')
        print(f'   Platform: {status.get(\"platform\", \"unknown\")}')
        print(f'   Machine: {status.get(\"machine\", \"unknown\")}')
    else:
        print('⚠️  Apple Intelligence: Not Available')
        print(f'   Reason: {status.get(\"error_message\", \"Unknown\")}')
        print('   System will use fallback providers')
    
    # Test providers
    from mem0.llms.apple_intelligence import AppleIntelligenceLLM
    from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder
    from mem0.configs.llms.apple_intelligence import AppleIntelligenceLlmConfig
    from mem0.configs.embeddings.base import BaseEmbedderConfig
    
    llm = AppleIntelligenceLLM(AppleIntelligenceLlmConfig())
    embedder = AppleIntelligenceEmbedder(BaseEmbedderConfig())
    
    print(f'✅ LLM Provider: {llm.__class__.__name__} (Available: {llm.is_available})')
    print(f'✅ Embedder Provider: {embedder.__class__.__name__} (Available: {embedder.is_available()})')
    
except Exception as e:
    print(f'❌ Error testing Apple Intelligence: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Apple Intelligence test completed"
    else
        print_error "Apple Intelligence test failed"
        exit 1
    fi
    
    echo ""
}

# Start Qdrant
start_qdrant() {
    print_status "Starting Qdrant vector database..."
    
    # Check if Qdrant is already running
    if port_in_use $QDRANT_PORT; then
        print_warning "Port $QDRANT_PORT is already in use. Checking if it's Qdrant..."
        
        if curl -s "http://localhost:$QDRANT_PORT/" | grep -q "qdrant"; then
            print_success "Qdrant is already running on port $QDRANT_PORT"
            return 0
        else
            print_error "Port $QDRANT_PORT is in use by another service"
            exit 1
        fi
    fi
    
    # Stop existing container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER_NAME}$"; then
        print_status "Stopping existing Qdrant container..."
        docker stop $QDRANT_CONTAINER_NAME >/dev/null 2>&1 || true
        docker rm $QDRANT_CONTAINER_NAME >/dev/null 2>&1 || true
    fi
    
    # Start Qdrant container with persistence and restart policy
    print_status "Starting new Qdrant container..."
    docker run -d \
        --name $QDRANT_CONTAINER_NAME \
        --restart unless-stopped \
        -p $QDRANT_PORT:6333 \
        -v qdrant_storage:/qdrant/storage \
        qdrant/qdrant:latest >/dev/null
    
    # Wait for Qdrant to be ready
    wait_for_service "http://localhost:$QDRANT_PORT/" "Qdrant"
    
    print_success "Qdrant started successfully on port $QDRANT_PORT"
    echo ""
}

# Test MCP server
test_mcp_server() {
    print_status "Testing MCP server initialization..."
    
    python3 -c "
import sys
import asyncio
sys.path.append('$PROJECT_ROOT')
sys.path.append('$PROJECT_ROOT/integrations/mcp')

try:
    from server import Mem0MCPServer
    
    async def test_server():
        server = Mem0MCPServer()
        
        if server.memory is None:
            print('❌ Memory initialization failed')
            return False
        
        # Check providers
        llm_class = server.memory.llm.__class__.__name__ if hasattr(server.memory, 'llm') else 'Unknown'
        embedder_class = server.memory.embedding_model.__class__.__name__ if hasattr(server.memory, 'embedding_model') else 'Unknown'
        
        apple_intelligence_active = 'AppleIntelligence' in llm_class and 'AppleIntelligence' in embedder_class
        
        print(f'✅ MCP Server initialized successfully')
        print(f'   LLM Provider: {llm_class}')
        print(f'   Embedder Provider: {embedder_class}')
        print(f'   Apple Intelligence Active: {apple_intelligence_active}')
        
        return True
    
    result = asyncio.run(test_server())
    if not result:
        sys.exit(1)
        
except Exception as e:
    print(f'❌ MCP server test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "MCP server test completed"
    else
        print_error "MCP server test failed"
        exit 1
    fi
    
    echo ""
}

# Update Claude Desktop configuration
update_claude_config() {
    print_status "Updating Claude Desktop configuration..."
    
    claude_config_dir="$HOME/Library/Application Support/Claude"
    claude_config_file="$claude_config_dir/claude_desktop_config.json"
    
    # Create directory if it doesn't exist
    mkdir -p "$claude_config_dir"
    
    # Backup existing config
    if [ -f "$claude_config_file" ]; then
        cp "$claude_config_file" "$claude_config_file.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Backed up existing Claude Desktop config"
    fi
    
    # Create config with persistence settings
    cat > "$claude_config_file" << EOF
{
  "mcpServers": {
    "gabriel-apple-intelligence-memory": {
      "command": "python",
      "args": ["$PROJECT_ROOT/integrations/mcp/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:10333",
        "QDRANT_COLLECTION": "gabriel_apple_intelligence_memories",
        "APPLE_INTELLIGENCE_ENABLED": "true",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "$PROJECT_ROOT"
      },
      "disabled": false,
      "persistent": true,
      "autoRestart": true,
      "maxRestarts": 5,
      "restartDelay": 2000,
      "alwaysAllow": [
        "test_connection",
        "add_memory",
        "search_memories",
        "get_all_memories",
        "update_memory",
        "delete_memory",
        "get_memory_history"
      ],
      "timeout": 30000,
      "initTimeout": 10000,
      "healthCheck": {
        "enabled": true,
        "interval": 30000,
        "timeout": 5000
      }
    }
  }
}
EOF
    
    print_success "Claude Desktop configuration updated"
    print_status "Config location: $claude_config_file"
    echo ""
}

# Display system status
display_status() {
    print_status "System Status Summary:"
    echo ""
    
    # Qdrant status
    if curl -s "http://localhost:$QDRANT_PORT/" >/dev/null 2>&1; then
        echo -e "  🟢 Qdrant Vector Database: ${GREEN}Running${NC} (http://localhost:$QDRANT_PORT)"
    else
        echo -e "  🔴 Qdrant Vector Database: ${RED}Not Running${NC}"
    fi
    
    # Apple Intelligence status
    apple_status=$(python3 -c "
import sys
sys.path.append('$PROJECT_ROOT')
from mem0.utils.apple_intelligence import check_apple_intelligence_availability
print('Available' if check_apple_intelligence_availability() else 'Not Available')
" 2>/dev/null)
    
    if [[ "$apple_status" == "Available" ]]; then
        echo -e "  🍎 Apple Intelligence: ${GREEN}Available${NC}"
    else
        echo -e "  🍎 Apple Intelligence: ${YELLOW}Not Available${NC} (using fallback)"
    fi
    
    # MCP Server status
    echo -e "  🐍 Python MCP Server: ${GREEN}Ready${NC} ($PROJECT_ROOT/integrations/mcp/server.py)"
    echo -e "  📋 Claude Desktop Config: ${GREEN}Updated${NC}"
    
    echo ""
    print_success "🎉 Apple Intelligence Local Memory System is ready!"
    echo ""
    
    echo -e "${CYAN}Next Steps:${NC}"
    echo "1. Restart Claude Desktop to load the new MCP configuration"
    echo "2. Test the connection with: 'Test connection to my memory system'"
    echo "3. Add your first memory: 'Remember that I prefer concise explanations'"
    echo "4. Search memories: 'What do you remember about my preferences?'"
    echo ""
    
    echo -e "${CYAN}Available Commands:${NC}"
    echo "• test_connection - Test system connectivity and Apple Intelligence status"
    echo "• add_memory - Store new memories with Apple Intelligence processing"
    echo "• search_memories - Search memories using Apple Intelligence embeddings"
    echo "• get_all_memories - Retrieve all stored memories"
    echo "• update_memory - Update existing memories"
    echo "• delete_memory - Delete specific memories"
    echo "• get_memory_history - View memory operation history"
    echo ""
    
    echo -e "${CYAN}Monitoring:${NC}"
    echo "• Qdrant UI: http://localhost:$QDRANT_PORT/dashboard"
    echo "• Logs: Check Claude Desktop logs for MCP server output"
    echo "• Test script: python test_complete_integration.py"
    echo ""
}

# Main execution
main() {
    echo -e "${PURPLE}Starting Apple Intelligence Local Memory System...${NC}"
    echo ""
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Run all setup steps
    check_system_requirements
    setup_python_environment
    test_apple_intelligence
    start_qdrant
    test_mcp_server
    update_claude_config
    display_status
    
    print_success "🚀 System startup completed successfully!"
}

# Handle script interruption
trap 'echo -e "\n${RED}Script interrupted. Cleaning up...${NC}"; exit 1' INT TERM

# Run main function
main "$@"