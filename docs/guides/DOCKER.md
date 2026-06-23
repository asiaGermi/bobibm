# Docker Deployment Guide
Financial Risk Management API

## Quick Start

### 1. Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Dataset file: `data/raw/HI-Small_Trans.csv`

### 2. Configuration

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development).

### 3. Build and Run

**Using Docker Compose (Recommended):**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

**Using Docker directly:**
```bash
# Build image
docker build -t financial-risk-management:latest .

# Run container
docker run -d \
  --name financial-risk-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data:ro \
  -e FRM_DATA_PATH=/app/data/raw/HI-Small_Trans.csv \
  financial-risk-management:latest
```

### 4. Verify Deployment

Check health:
```bash
curl http://localhost:8000/api/v1/health
```

Access API documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### 5. Test API

```bash
# Analyze transaction
curl -X POST http://localhost:8000/api/v1/analyze/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "8000EBD30",
    "timestamp": "2022/09/01 00:20",
    "lookback_days": 30
  }'

# Assess risk
curl -X POST http://localhost:8000/api/v1/assess/risk \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "8000EBD30",
    "lookback_days": 90
  }'

# Detect fraud
curl -X POST http://localhost:8000/api/v1/detect/fraud \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "8000EBD30",
    "timestamp": "2022/09/15 14:30",
    "lookback_days": 30
  }'

# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommend/actions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "8000EBD30",
    "lookback_days": 90
  }'
```

## Docker Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build:

1. **Builder stage**: Installs build dependencies and Python packages
2. **Runtime stage**: Copies only necessary files, runs as non-root user

### Security Features

- ✅ Non-root user (appuser, UID 1000)
- ✅ Minimal base image (python:3.11-slim)
- ✅ Read-only data volume mount
- ✅ No unnecessary packages
- ✅ Health check endpoint

### Container Structure

```
/app/
├── src/              # Application code
│   ├── api/         # FastAPI application
│   ├── agents/      # Agent implementations
│   └── data/        # Data layer
├── data/            # Mounted volume (read-only)
│   └── raw/
│       └── HI-Small_Trans.csv
└── home/appuser/.local/  # Python packages
```

## Environment Variables

All environment variables are prefixed with `FRM_` and read by pydantic-settings.

### Required Variables

- `FRM_DATA_PATH`: Path to dataset CSV file

### Optional Variables

- `FRM_APP_NAME`: Application name (default: "Financial Risk Management API")
- `FRM_APP_VERSION`: Version (default: "1.0.0")
- `FRM_API_PREFIX`: API prefix (default: "/api/v1")
- `FRM_CORS_ORIGINS`: CORS origins (default: "*")
- `LOG_LEVEL`: Logging level (default: "info")

See `.env.example` for complete list.

## Docker Compose Services

### API Service

- **Image**: financial-risk-management:latest
- **Port**: 8000:8000
- **Volumes**: ./data:/app/data:ro (read-only)
- **Network**: financial-risk-network
- **Restart**: unless-stopped
- **Health Check**: Every 30s, checks /api/v1/health

## Management Commands

### View Logs
```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 api

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00 api
```

### Container Shell
```bash
# Interactive shell
docker-compose exec api /bin/bash

# Run Python command
docker-compose exec api python -c "from src.data.loader import get_dataset_info; print(get_dataset_info())"
```

### Restart Service
```bash
# Restart
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build
```

### Stop and Remove
```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v
```

## Health Check

The container includes a health check that:
- Runs every 30 seconds
- Checks `/api/v1/health` endpoint
- Allows 40 seconds for startup
- Retries 3 times before marking unhealthy
- Times out after 10 seconds

Check health status:
```bash
docker-compose ps
docker inspect financial-risk-api | jq '.[0].State.Health'
```

## Performance Tuning

### Production Settings

For production deployment, update `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
      replicas: 3
    environment:
      - SERVER_WORKERS=4
      - LOG_LEVEL=warning
```

### Scaling

Scale the API service:
```bash
docker-compose up -d --scale api=3
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs api
```

Common issues:
- Dataset file not found: Verify `data/raw/HI-Small_Trans.csv` exists
- Port already in use: Change port in `docker-compose.yml`
- Permission denied: Check file permissions on data directory

### Health Check Failing

Test health endpoint manually:
```bash
docker-compose exec api curl http://localhost:8000/api/v1/health
```

### High Memory Usage

Monitor resource usage:
```bash
docker stats financial-risk-api
```

Reduce memory:
- Decrease `SERVER_WORKERS`
- Implement pagination for large datasets
- Add Redis caching

### Slow Response Times

- Check dataset size
- Monitor container resources
- Enable caching
- Increase worker processes

## Development Workflow

### Local Development with Docker

1. Make code changes
2. Rebuild image: `docker-compose up -d --build`
3. Test changes
4. View logs: `docker-compose logs -f api`

### Hot Reload (Development)

For development with auto-reload:

```yaml
# docker-compose.override.yml
services:
  api:
    volumes:
      - ./src:/app/src
    environment:
      - SERVER_RELOAD=true
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Then run:
```bash
docker-compose up -d
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build image
        run: docker build -t financial-risk-management:${{ github.sha }} .
      - name: Test image
        run: |
          docker run -d --name test-api -p 8000:8000 financial-risk-management:${{ github.sha }}
          sleep 10
          curl -f http://localhost:8000/api/v1/health || exit 1
```

## Security Best Practices

1. **Never commit .env file**
2. **Use secrets management** for production
3. **Scan images** for vulnerabilities
4. **Update base image** regularly
5. **Limit container resources**
6. **Use read-only volumes** where possible
7. **Run as non-root user** (already configured)
8. **Enable TLS/SSL** in production

## Monitoring

### Prometheus Metrics (Future)

Add metrics endpoint:
```python
# In src/api/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Logging

Logs are written to stdout/stderr and can be collected by:
- Docker logging drivers
- ELK stack
- Splunk
- CloudWatch

Configure logging driver in `docker-compose.yml`:
```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Support

For issues:
1. Check logs: `docker-compose logs api`
2. Verify health: `curl http://localhost:8000/api/v1/health`
3. Test endpoints: See API documentation
4. Review environment variables: `docker-compose config`

---

Made with Bob