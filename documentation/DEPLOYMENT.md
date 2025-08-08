# Mem0 Deployment Guide

Complete guide for deploying Mem0 in production environments.

## 🚀 Production Setup

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL or compatible database
- Redis (for caching)
- Vector database (Qdrant, Pinecone, or Chroma)

### Environment Configuration

```bash
# .env.production
OPENAI_API_KEY=your_openai_api_key
POSTGRES_URL=postgresql://user:pass@localhost:5432/mem0
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Production Installation

```bash
# Clone repository
git clone https://github.com/mem0ai/mem0.git
cd mem0

# Install production dependencies
pip install -e ".[production]"

# Set up database
python -m mem0.setup.database

# Run migrations
python -m mem0.setup.migrate

# Start production server
gunicorn --config gunicorn.conf.py mem0.server:app
```

## 🐳 Docker Deployment

### Single Container

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install mem0
RUN pip install -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "mem0.server:app"]
```

### Docker Compose Production Stack

```yaml
# docker-compose.production.yml
version: "3.8"

services:
  mem0-api:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URL=postgresql://mem0:password@postgres:5432/mem0
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - postgres
      - redis
      - qdrant
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mem0
      POSTGRES_USER: mem0
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mem0"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deployment/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - mem0-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

### Nginx Configuration

```nginx
# deployment/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream mem0_backend {
        server mem0-api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://mem0_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://mem0_backend/health;
            access_log off;
        }
    }
}
```

## ☸️ Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mem0
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mem0-config
  namespace: mem0
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  POSTGRES_URL: "postgresql://mem0:password@postgres:5432/mem0"
  REDIS_URL: "redis://redis:6379"
  QDRANT_URL: "http://qdrant:6333"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mem0-secrets
  namespace: mem0
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  POSTGRES_PASSWORD: <base64-encoded-password>
```

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mem0-api
  namespace: mem0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mem0-api
  template:
    metadata:
      labels:
        app: mem0-api
    spec:
      containers:
        - name: mem0-api
          image: mem0/mem0:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: mem0-config
            - secretRef:
                name: mem0-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mem0-api-service
  namespace: mem0
spec:
  selector:
    app: mem0-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mem0-ingress
  namespace: mem0
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.mem0.yourdomain.com
      secretName: mem0-tls
  rules:
    - host: api.mem0.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mem0-api-service
                port:
                  number: 80
```

## 📊 Scaling Considerations

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mem0-api-hpa
  namespace: mem0
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mem0-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Database Scaling

```yaml
# k8s/postgres-cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: mem0
spec:
  instances: 3

  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"

  bootstrap:
    initdb:
      database: mem0
      owner: mem0
      secret:
        name: postgres-credentials

  storage:
    size: 100Gi
    storageClass: fast-ssd

  monitoring:
    enabled: true
```

## 🔧 Configuration Management

### Production Configuration

```python
# config/production.py
import os
from mem0.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    # Database
    POSTGRES_URL = os.getenv('POSTGRES_URL')
    REDIS_URL = os.getenv('REDIS_URL')

    # Vector Store
    VECTOR_STORE = {
        'provider': 'qdrant',
        'config': {
            'url': os.getenv('QDRANT_URL'),
            'api_key': os.getenv('QDRANT_API_KEY'),
            'collection_name': 'mem0_vectors'
        }
    }

    # LLM
    LLM = {
        'provider': 'openai',
        'config': {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4o-mini'
        }
    }

    # Embeddings
    EMBEDDINGS = {
        'provider': 'openai',
        'config': {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'text-embedding-3-small'
        }
    }

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET = os.getenv('JWT_SECRET')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = 'json'

    # Performance
    CACHE_TTL = 3600
    MAX_MEMORY_SIZE = 1000000
    BATCH_SIZE = 100

    # Rate Limiting
    RATE_LIMIT = {
        'requests_per_minute': 1000,
        'requests_per_hour': 10000
    }
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "mem0-api"

# Server mechanics
daemon = False
pidfile = "/tmp/mem0.pid"
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Performance
preload_app = True
keepalive = 5
timeout = 120
graceful_timeout = 30
```

## 📈 Monitoring & Observability

### Prometheus Metrics

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
memory_operations = Counter('mem0_memory_operations_total', 'Total memory operations', ['operation', 'status'])
memory_search_duration = Histogram('mem0_memory_search_duration_seconds', 'Memory search duration')
active_users = Gauge('mem0_active_users', 'Number of active users')
memory_count = Gauge('mem0_memory_count_total', 'Total number of memories')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Process request
            await self.app(scope, receive, send)

            # Record metrics
            duration = time.time() - start_time
            memory_search_duration.observe(duration)

        else:
            await self.app(scope, receive, send)
```

### Health Checks

```python
# health/checks.py
from mem0 import Memory
import asyncio

class HealthChecker:
    def __init__(self):
        self.memory = Memory()

    async def check_database(self):
        try:
            # Test database connection
            await self.memory.health_check()
            return {"status": "healthy", "latency": "< 10ms"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_vector_store(self):
        try:
            # Test vector store connection
            result = await self.memory.vector_store.health_check()
            return {"status": "healthy", "collections": result}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_llm(self):
        try:
            # Test LLM connection
            response = await self.memory.llm.generate("test")
            return {"status": "healthy", "model": self.memory.llm.model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def full_health_check(self):
        checks = await asyncio.gather(
            self.check_database(),
            self.check_vector_store(),
            self.check_llm(),
            return_exceptions=True
        )

        return {
            "database": checks[0],
            "vector_store": checks[1],
            "llm": checks[2],
            "overall": "healthy" if all(c.get("status") == "healthy" for c in checks) else "unhealthy"
        }
```

## 🔒 Security Best Practices

### API Security

```python
# security/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.state.limiter = limiter
@app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/memories/")
@limiter.limit("100/minute")
async def add_memory(request: Request, memory_data: dict, user=Depends(verify_token)):
    # Implementation
    pass
```

### Data Encryption

```python
# security/encryption.py
from cryptography.fernet import Fernet
import os

class DataEncryption:
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## 🚨 Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump $POSTGRES_URL > backups/postgres_$(date +%Y%m%d_%H%M%S).sql

# Vector store backup
curl -X POST "$QDRANT_URL/collections/mem0_vectors/snapshots" > backups/qdrant_$(date +%Y%m%d_%H%M%S).snapshot

# Upload to S3
aws s3 sync backups/ s3://mem0-backups/$(date +%Y%m%d)/
```

### Recovery Procedures

```bash
#!/bin/bash
# restore.sh

# Restore database
psql $POSTGRES_URL < backups/postgres_backup.sql

# Restore vector store
curl -X PUT "$QDRANT_URL/collections/mem0_vectors/snapshots/recover" \
  -H "Content-Type: application/json" \
  -d '{"location": "backups/qdrant_backup.snapshot"}'
```

## 📋 Deployment Checklist

### Pre-deployment

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring setup
- [ ] Backup procedures tested
- [ ] Load testing completed
- [ ] Security audit passed

### Post-deployment

- [ ] Health checks passing
- [ ] Metrics collecting
- [ ] Logs aggregating
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Team notified

### Rollback Plan

- [ ] Previous version tagged
- [ ] Database rollback scripts ready
- [ ] Traffic routing plan
- [ ] Monitoring for issues
- [ ] Communication plan
