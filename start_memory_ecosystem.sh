#!/bin/bash

# Local Memory Ecosystem Startup Script
# Starts all components for production-ready local memory system

set -e

echo "🌟 Starting Local Memory Ecosystem..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
    
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama is not installed. Please install from https://ollama.ai"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed."
        exit 1
    fi
    
    print_status "All dependencies found"
}

# Start Ollama and pull models
setup_ollama() {
    print_info "Setting up Ollama..."
    
    # Start Ollama service
    if ! pgrep -f "ollama serve" > /dev/null; then
        print_info "Starting Ollama service..."
        ollama serve &
        sleep 5
    else
        print_status "Ollama already running"
    fi
    
    # Pull required models
    models=("llama3.2:3b" "nomic-embed-text")
    for model in "${models[@]}"; do
        if ! ollama list | grep -q "$model"; then
            print_info "Pulling $model..."
            ollama pull "$model"
        else
            print_status "$model already available"
        fi
    done
    
    print_status "Ollama setup complete"
}

# Create data directories
create_directories() {
    print_info "Creating data directories..."
    
    mkdir -p data/{qdrant,neo4j/{data,logs,import,plugins},redis,postgres}
    
    print_status "Data directories created"
}

# Setup environment files
setup_environment() {
    print_info "Setting up environment..."
    
    # Create OpenMemory .env file
    if [ ! -f "openmemory/api/.env" ]; then
        cat > openmemory/api/.env << EOF
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0production
REDIS_URL=redis://:mem0redis@localhost:6379
POSTGRES_URL=postgresql://mem0user:mem0postgres@localhost:5432/mem0db
USER=${USER}
NEXT_PUBLIC_API_URL=http://localhost:8765
NEXT_PUBLIC_USER_ID=${USER}
EOF
        print_status "OpenMemory environment file created"
    else
        print_status "OpenMemory environment file already exists"
    fi
    
    # Export environment variables
    export OPENAI_API_KEY=ollama
    export OPENAI_BASE_URL=http://localhost:11434/v1
    export USER=${USER}
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install mem0 with all extras
    pip install -e ".[graph]"
    
    # Install additional dependencies for integrations
    pip install autogen-agentchat crewai langchain requests asyncio
    
    print_status "Python dependencies installed"
}

# Start Docker services
start_docker_services() {
    print_info "Starting Docker services..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.production.yml down 2>/dev/null || true
    
    # Start services
    docker-compose -f docker-compose.production.yml up -d
    
    # Wait for services to be healthy
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    services=("mem0-qdrant:6333" "mem0-neo4j:7474" "mem0-redis:6379" "mem0-postgres:5432")
    for service in "${services[@]}"; do
        container=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if docker ps | grep -q "$container"; then
            print_status "$container is running"
        else
            print_warning "$container may not be ready yet"
        fi
    done
}

# Start Mem0 server
start_mem0_server() {
    print_info "Starting Mem0 server..."
    
    source venv/bin/activate
    
    # Start Mem0 server in background
    nohup python -m mem0.server > mem0_server.log 2>&1 &
    echo $! > mem0_server.pid
    
    sleep 5
    
    if ps -p $(cat mem0_server.pid) > /dev/null; then
        print_status "Mem0 server started (PID: $(cat mem0_server.pid))"
    else
        print_error "Failed to start Mem0 server"
    fi
}

# Test the setup
test_setup() {
    print_info "Testing the setup..."
    
    source venv/bin/activate
    
    # Test Mem0 client
    python3 -c "
from mem0 import Memory
try:
    m = Memory()
    m.add('Test memory for ecosystem validation')
    results = m.search('test')
    print('✅ Mem0 client working')
except Exception as e:
    print(f'❌ Mem0 client error: {e}')
"
    
    # Test OpenMemory API
    sleep 5
    if curl -s http://localhost:8765/health > /dev/null; then
        print_status "OpenMemory API responding"
    else
        print_warning "OpenMemory API not responding yet"
    fi
    
    # Test Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        print_status "Ollama API responding"
    else
        print_warning "Ollama API not responding"
    fi
}

# Print final status
print_final_status() {
    echo ""
    echo "🎉 Local Memory Ecosystem Started!"
    echo "=================================="
    echo ""
    echo "📍 Access Points:"
    echo "  OpenMemory UI:      http://localhost:3000"
    echo "  OpenMemory API:     http://localhost:8765"
    echo "  Mem0 Server:        http://localhost:1987"
    echo "  Qdrant Dashboard:   http://localhost:6333/dashboard"
    echo "  Neo4j Browser:      http://localhost:7474 (neo4j/mem0production)"
    echo "  Ollama API:         http://localhost:11434"
    echo ""
    echo "🧪 Test Files:"
    echo "  test_mem0_client.py"
    echo "  test_openmemory_client.py"
    echo "  test_autogen_integration.py"
    echo "  agent_memory_integrations.py"
    echo ""
    echo "🔧 Management:"
    echo "  Stop all: docker-compose -f docker-compose.production.yml down"
    echo "  View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "  Restart: ./start_memory_ecosystem.sh"
    echo ""
    echo "🚀 Ready for any agent framework!"
}

# Main execution
main() {
    check_dependencies
    create_directories
    setup_environment
    setup_ollama
    install_python_deps
    start_docker_services
    start_mem0_server
    test_setup
    print_final_status
}

# Handle script interruption
cleanup() {
    print_info "Cleaning up..."
    docker-compose -f docker-compose.production.yml down 2>/dev/null || true
    if [ -f mem0_server.pid ]; then
        kill $(cat mem0_server.pid) 2>/dev/null || true
        rm mem0_server.pid
    fi
    exit 0
}

trap cleanup INT TERM

# Run main function
main "$@"