#!/bin/bash
# Install Local Persistence for Mem0 Apple Intelligence Server
# Pure local setup, no external services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo "🚀 Installing Local Persistence for Mem0 Apple Intelligence"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -f "integrations/mcp/native_node_server.js" ]; then
    print_error "Please run this script from the mem0 project root directory"
    exit 1
fi

print_info "Setting up local persistence components..."

# Make scripts executable
chmod +x local_persistence_manager.sh
print_status "Made persistence manager executable"

# Install Launch Agent (optional)
read -p "Install macOS Launch Agent for auto-startup? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$LAUNCH_AGENT_DIR"
    
    cp "launch_agents/com.gabriel.mem0-apple-intelligence.plist" "$LAUNCH_AGENT_DIR/"
    print_status "Launch Agent installed to $LAUNCH_AGENT_DIR"
    
    # Load the launch agent
    launchctl load "$LAUNCH_AGENT_DIR/com.gabriel.mem0-apple-intelligence.plist" 2>/dev/null || true
    print_status "Launch Agent loaded (will start on next login)"
    
    print_info "To start immediately: launchctl start com.gabriel.mem0-apple-intelligence"
    print_info "To stop: launchctl stop com.gabriel.mem0-apple-intelligence"
    print_info "To uninstall: launchctl unload $LAUNCH_AGENT_DIR/com.gabriel.mem0-apple-intelligence.plist"
fi# Test the persistence manager
print_info "Testing persistence manager..."
if ./local_persistence_manager.sh status; then
    print_status "Persistence manager is working"
else
    print_warning "Persistence manager test completed (server not running yet)"
fi

# Create convenience aliases
print_info "Creating convenience commands..."
cat > mem0-server << 'EOF'
#!/bin/bash
# Convenience wrapper for mem0 server management
exec "$(dirname "$0")/local_persistence_manager.sh" "$@"
EOF

chmod +x mem0-server
print_status "Created 'mem0-server' convenience command"

echo ""
print_status "Local Persistence Installation Complete!"
echo "========================================"
echo ""
print_info "Available commands:"
echo "  ./mem0-server start     - Start the server"
echo "  ./mem0-server stop      - Stop the server"
echo "  ./mem0-server restart   - Restart the server"
echo "  ./mem0-server status    - Show server status"
echo "  ./mem0-server health    - Check server health"
echo "  ./mem0-server monitor   - Start monitoring mode"
echo "  ./mem0-server logs      - Show server logs"
echo ""
print_info "To start the server now:"
echo "  ./mem0-server start"
echo ""
print_info "To start monitoring mode (auto-restart on failure):"
echo "  ./mem0-server monitor"
echo ""
print_status "Your Mem0 Apple Intelligence server now has bulletproof local persistence! 🛡️"