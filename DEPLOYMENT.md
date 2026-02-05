"""
Production Deployment Guide

This guide covers deploying the search engine to production.
"""

# DEPLOYMENT GUIDE: Search Engine to Production

## 1. Pre-Deployment Checklist

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No type errors: `mypy crawler/ indexer/ ranking/ api/`
- [ ] Code formatted: `black .`
- [ ] Linting clean: `flake8 .`

### Security Review
- [ ] No hardcoded secrets in code
- [ ] Input validation on all API endpoints
- [ ] SQL injection prevention verified
- [ ] HTTPS/TLS configured
- [ ] CORS policy defined
- [ ] Rate limiting configured

### Performance
- [ ] Load tested with expected query volume
- [ ] Memory usage profiled and acceptable
- [ ] Index size verified
- [ ] Database queries optimized
- [ ] Cache strategy defined

## 2. Deployment Options

### Option A: Linux Server (Ubuntu 20.04+)

#### Setup
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.9+
sudo apt-get install python3.9 python3-pip python3-venv

# Create app user
sudo useradd -m -s /bin/bash searchengine

# Clone application
cd /opt
sudo git clone <repo-url> search-engine
cd search-engine
sudo chown -R searchengine:searchengine .

# Setup virtual environment
su - searchengine
cd /opt/search-engine
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Systemd Service
Create `/etc/systemd/system/search-engine-api.service`:

```ini
[Unit]
Description=Search Engine API
After=network.target

[Service]
Type=notify
User=searchengine
WorkingDirectory=/opt/search-engine
Environment="PATH=/opt/search-engine/venv/bin"
ExecStart=/opt/search-engine/venv/bin/python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable search-engine-api
sudo systemctl start search-engine-api
sudo systemctl status search-engine-api
```

#### Nginx Reverse Proxy
Create `/etc/nginx/sites-available/search-engine`:

```nginx
upstream search_engine {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.searchengine.com;

    location / {
        proxy_pass http://search_engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/search-engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.searchengine.com
sudo systemctl restart nginx
```

### Option B: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data logs

# Run API server
CMD ["python", "-m", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  search-engine:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - search-engine
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
docker-compose logs -f
```

### Option C: Kubernetes Deployment

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: search-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: search-engine
  template:
    metadata:
      labels:
        app: search-engine
    spec:
      containers:
      - name: search-engine
        image: search-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: search-engine-pvc
```

## 3. Database Management

### Backup Strategy
```bash
# Automated daily backup
0 2 * * * /opt/search-engine/backup.sh

# Backup script
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sqlite3 /opt/search-engine/data/search_engine.db ".backup /backups/search_engine_$TIMESTAMP.db"
```

### Index Updates
```bash
# Incremental crawl and reindex
0 0 * * * /opt/search-engine/reindex.py

# Or on-demand:
python main.py  # Use CLI to trigger crawl
```

## 4. Monitoring and Logging

### Prometheus Metrics
Add to `api/server.py`:
```python
from prometheus_client import Counter, Histogram
from fastapi_prometheus_instrumentation import Instrumentation

search_counter = Counter('searches_total', 'Total searches')
search_latency = Histogram('search_latency_seconds', 'Search latency')
```

### Log Aggregation
```bash
# Using ELK Stack
# Logs automatically sent via:
# - Logstash or Filebeat
# - Elasticsearch for storage
# - Kibana for visualization
```

### Health Monitoring
```bash
# Monitor endpoint
curl http://api.searchengine.com/health

# Expected response:
{
    "status": "healthy",
    "indexed_documents": 50000,
    "terms_indexed": 100000
}
```

## 5. Performance Optimization

### Caching Strategy
```python
# Redis caching for popular queries
from redis import Redis
cache = Redis(host='localhost', port=6379)

# Cache top 100 queries
cache.set(f"search:{query_hash}", results, ex=3600)
```

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_url ON documents(url);
CREATE INDEX idx_crawl_time ON documents(crawl_time);
```

### API Optimization
```python
# Enable gzip compression
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Add CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

## 6. Security Hardening

### API Security
- [ ] Rate limiting: 100 req/min per IP
- [ ] API key authentication for admin endpoints
- [ ] HTTPS/TLS only (HTTP redirect)
- [ ] HSTS headers
- [ ] CSRF protection if needed

### System Security
- [ ] Firewall rules (only necessary ports)
- [ ] SELinux/AppArmor enabled
- [ ] SSH key-based auth only
- [ ] Regular security updates
- [ ] Vulnerability scanning

### Secrets Management
```python
# Use environment variables
from dotenv import load_dotenv
import os

API_KEY = os.getenv("API_KEY")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
```

## 7. Scaling Strategy

### Horizontal Scaling
1. Load balancer (Nginx/HAProxy)
2. Multiple API server instances
3. Shared database
4. Distributed cache (Redis Cluster)

### Vertical Scaling
1. More CPU cores
2. More memory
3. Faster storage (SSD)
4. Network optimization

### Database Sharding
```
Shard by domain hash:
- search_engine_shard_0.db
- search_engine_shard_1.db
- search_engine_shard_2.db
```

## 8. Disaster Recovery

### Backup and Recovery
```bash
# Full backup
mysqldump search_engine > backup_$(date +%s).sql

# Incremental backup
rsync -av /opt/search-engine/data /backups/

# Recovery
sqlite3 search_engine.db < backup.sql
```

### Failover
- Master-replica database setup
- Automatic failover with Keepalived
- Health checks every 30 seconds
- Recovery time objective: <5 minutes

## 9. Maintenance

### Regular Tasks
- [ ] Check disk space weekly
- [ ] Review logs for errors daily
- [ ] Monitor API latency
- [ ] Update dependencies monthly
- [ ] Reindex stale content
- [ ] Rotate certificates before expiry

### Monitoring Dashboards
```
Key metrics to track:
- API response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Index staleness
- Database size
- Memory usage
- CPU usage
- Cache hit rate
```

## 10. Cost Estimation

### Single Server
- Virtual machine: $10-20/month
- Bandwidth: $5-10/month
- SSL certificate: Free (Let's Encrypt)
- **Total: ~$15-30/month**

### Medium Scale (100k-1M documents)
- 3x servers: $30-60/month
- Database cluster: $50-100/month
- Load balancer: $20-40/month
- Backup storage: $10-20/month
- Monitoring: $10-20/month
- **Total: ~$120-240/month**

### Large Scale (>1M documents)
- Use cloud provider (AWS, GCP, Azure)
- Elasticsearch managed service
- Auto-scaling groups
- CDN for static content
- **Total: $500-2000+/month (depends on traffic)**

---

For questions or issues, check the main README.md
