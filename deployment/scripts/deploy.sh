#!/bin/bash

# Mem0 Production Deployment Script
# Usage: ./deploy.sh [environment] [version]

set -e

# Configuration
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [[ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]]; then
        log_error "Environment file .env.$ENVIRONMENT not found"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build production image
    docker build -f deployment/docker/Dockerfile.production -t mem0/mem0:$VERSION .
    docker tag mem0/mem0:$VERSION mem0/mem0:latest
    
    log_success "Docker images built successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Start only the database for migrations
    docker compose -f deployment/docker/docker-compose.production.yml up -d postgres
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 30
    
    # Run migrations
    docker run --rm --network mem0_default \
        --env-file .env.$ENVIRONMENT \
        mem0/mem0:$VERSION \
        python -m mem0.setup.migrate
    
    log_success "Database migrations completed"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment file
    cp .env.$ENVIRONMENT .env
    
    # Deploy with Docker Compose
    docker compose -f deployment/docker/docker-compose.production.yml up -d
    
    log_success "Services deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old versions (keep last 3)
    docker images mem0/mem0 --format "table {{.Tag}}" | tail -n +4 | xargs -r docker rmi mem0/mem0: 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Backup before deployment
backup() {
    log_info "Creating backup before deployment..."
    
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Database backup
    docker exec mem0_postgres_1 pg_dump -U mem0 mem0 > "$backup_dir/postgres_backup.sql" 2>/dev/null || true
    
    # Qdrant backup
    curl -X POST "http://localhost:6333/collections/mem0_vectors/snapshots" > "$backup_dir/qdrant_backup.json" 2>/dev/null || true
    
    log_success "Backup created at $backup_dir"
}

# Rollback function
rollback() {
    log_warning "Rolling back to previous version..."
    
    # Stop current services
    docker compose -f deployment/docker/docker-compose.production.yml down
    
    # Use previous image
    docker tag mem0/mem0:previous mem0/mem0:latest
    
    # Restart services
    docker compose -f deployment/docker/docker-compose.production.yml up -d
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting Mem0 deployment to $ENVIRONMENT environment (version: $VERSION)"
    
    # Trap errors and rollback
    trap 'log_error "Deployment failed! Rolling back..."; rollback; exit 1' ERR
    
    check_prerequisites
    backup
    build_images
    run_migrations
    deploy_services
    
    # Wait a bit for services to start
    sleep 20
    
    if health_check; then
        cleanup
        log_success "Deployment completed successfully!"
        log_info "Services are available at:"
        log_info "  - API: http://localhost:8000"
        log_info "  - Grafana: http://localhost:3000"
        log_info "  - Prometheus: http://localhost:9090"
    else
        log_error "Deployment failed health check"
        rollback
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    "backup")
        backup
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        main
        ;;
esac