#!/bin/bash
# Local Persistence Manager for Mem0 Apple Intelligence Server
# Pure local, no external dependencies, self-contained

set -e

# Configuration
SERVER_NAME="mem0-apple-intelligence"
SERVER_PATH="/Volumes/Ready500/DEVELOPMENT/mem0/integrations/mcp/native_node_server.js"
PID_FILE="/tmp/${SERVER_NAME}.pid"
LOG_FILE="/tmp/${SERVER_NAME}.log"
ERROR_LOG="/tmp/${SERVER_NAME}-error.log"
HEALTH_CHECK_INTERVAL=30
MAX_RESTART_ATTEMPTS=5
RESTART_DELAY=10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }# Check if server is running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Start the server
start_server() {
    if is_server_running; then
        print_warning "Server is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    print_info "Starting $SERVER_NAME server..."
    
    # Set environment variables
    export QDRANT_URL="http://localhost:6333"
    export QDRANT_COLLECTION="gabriel_apple_intelligence_memories"
    export APPLE_INTELLIGENCE_ENABLED="true"
    export LOG_LEVEL="INFO"
    
    # Start server in background
    nohup node "$SERVER_PATH" > "$LOG_FILE" 2> "$ERROR_LOG" &
    local pid=$!    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if is_server_running; then
        print_status "Server started successfully (PID: $pid)"
        return 0
    else
        print_error "Server failed to start"
        return 1
    fi
}

# Stop the server
stop_server() {
    if ! is_server_running; then
        print_warning "Server is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    print_info "Stopping server (PID: $pid)..."
    
    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        count=$((count + 1))
    done    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Forcing server shutdown..."
        kill -KILL "$pid" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    print_status "Server stopped"
}

# Health check
health_check() {
    if ! is_server_running; then
        print_error "Server is not running"
        return 1
    fi
    
    # Simple health check - check if process is responsive
    local pid=$(cat "$PID_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        print_status "Server is healthy (PID: $pid, uptime: $(ps -o etime= -p $pid | tr -d ' '))"
        return 0
    else
        print_error "Server process is not responsive"
        return 1
    fi
}

# Restart server
restart_server() {
    print_info "Restarting server..."
    stop_server
    sleep 2
    start_server
}# Monitor and auto-restart
monitor() {
    print_info "Starting monitoring mode (health checks every ${HEALTH_CHECK_INTERVAL}s)"
    local restart_count=0
    
    while true; do
        if ! health_check > /dev/null 2>&1; then
            if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                restart_count=$((restart_count + 1))
                print_warning "Health check failed, attempting restart ($restart_count/$MAX_RESTART_ATTEMPTS)"
                
                stop_server
                sleep $RESTART_DELAY
                
                if start_server; then
                    print_status "Server restarted successfully"
                    restart_count=0  # Reset counter on successful restart
                else
                    print_error "Failed to restart server"
                fi
            else
                print_error "Max restart attempts reached ($MAX_RESTART_ATTEMPTS), giving up"
                exit 1
            fi
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Show status
status() {
    echo "=== $SERVER_NAME Status ==="
    if is_server_running; then
        local pid=$(cat "$PID_FILE")
        echo "Status: Running (PID: $pid)"
        echo "Uptime: $(ps -o etime= -p $pid | tr -d ' ')"
        echo "Memory: $(ps -o rss= -p $pid | tr -d ' ') KB"
        echo "Log file: $LOG_FILE"
        echo "Error log: $ERROR_LOG"
    else
        echo "Status: Not running"
    fi
}# Show logs
logs() {
    local lines=${1:-50}
    if [ -f "$LOG_FILE" ]; then
        echo "=== Last $lines lines of $LOG_FILE ==="
        tail -n "$lines" "$LOG_FILE"
    fi
    
    if [ -f "$ERROR_LOG" ]; then
        echo "=== Last $lines lines of $ERROR_LOG ==="
        tail -n "$lines" "$ERROR_LOG"
    fi
}

# Main command handler
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status
        ;;
    health)
        health_check
        ;;
    monitor)
        monitor
        ;;
    logs)
        logs "${2:-50}"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health|monitor|logs [lines]}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the server"
        echo "  stop     - Stop the server"
        echo "  restart  - Restart the server"
        echo "  status   - Show server status"
        echo "  health   - Check server health"
        echo "  monitor  - Start monitoring mode with auto-restart"
        echo "  logs     - Show server logs (default: 50 lines)"
        exit 1
        ;;
esac