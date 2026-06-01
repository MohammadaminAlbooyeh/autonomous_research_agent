# Production Setup Guide

This document outlines all the production-ready features added to the Autonomous Research Agent.

## 1. Fixed Pydantic Deprecation Warnings

All Pydantic models have been updated to use `ConfigDict` instead of deprecated class-based `Config`.

**Files Updated:**
- `backend/api/schemas.py`

**Before:**
```python
class ResearchTaskResponse(BaseModel):
    id: str
    # ...
    class Config:
        from_attributes = True
```

**After:**
```python
class ResearchTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    # ...
```

## 2. API Authentication & Authorization

### JWT Token-Based Authentication

All API endpoints (except `/health`) now require authentication via JWT tokens.

**Key Files:**
- `backend/auth.py` - Authentication logic
- `backend/api/auth_routes.py` - Login endpoint
- `backend/api/routes.py` - Protected endpoints

### Getting Started with Authentication

1. **Login to get a token:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "demo"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. **Use token in subsequent requests:**
```bash
curl -X GET "http://localhost:8000/api/research" \
  -H "Authorization: bearer YOUR_TOKEN_HERE"
```

### Configuration

- Set `SECRET_KEY` in `.env` for production (change from default)
- Token expiration: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

## 3. Rate Limiting

Request rate limiting has been implemented using `slowapi` to protect the API from abuse.

### Rate Limits by Endpoint

| Endpoint | Limit | Period |
|----------|-------|--------|
| `POST /api/research` | 5 | per minute |
| `GET /api/research` | 10 | per minute |
| `GET /api/research/{id}` | 10 | per minute |
| `DELETE /api/research/{id}` | 5 | per minute |
| `GET /api/research/stats` | 10 | per minute |
| `GET /api/research/{id}/report` | 10 | per minute |
| `GET /api/research/{id}/report/export` | 5 | per minute |

### Rate Limit Response

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded"
}
```
HTTP Status: 429

## 4. Comprehensive Logging

All API requests and responses are logged with:
- Request method and path
- Response status code
- Processing time
- User information (via authentication)

### Log Configuration

**Log Files:**
- Location: `logs/` directory
- Format: `research_agent_YYYYMMDD.log`
- Rotation: 10MB per file with 5 backup files

**Log Level:** INFO (configurable in `backend/logging_config.py`)

### Sample Log Output

```
[2025-05-31 15:30:45] INFO - backend.api.routes - User testuser starting research on topic: AI
[2025-05-31 15:30:45] INFO - backend.api.routes - Research task created: 550e8400-e29b-41d4-a716-446655440000
[2025-05-31 15:30:45] INFO - backend.main - Completed POST /api/research - Status: 200 - Duration: 0.45s
```

## 5. CI/CD Pipeline

### GitHub Actions Workflows

Three automated workflows have been configured:

#### A. `ci.yml` - Main CI Pipeline
- **Trigger:** Push to main/develop, Pull Requests
- **Steps:**
  - Run tests on Python 3.11 & 3.12
  - Lint code with pylint
  - Security scans (bandit, safety)
  - Build Docker images (on push)
  - Deploy to Docker Hub (main branch only)

#### B. `code-quality.yml` - Code Quality Checks
- **Trigger:** Push to main/develop, Pull Requests
- **Steps:**
  - Code formatting check (black)
  - Import sorting check (isort)
  - Linting (flake8, pylint)
  - Type checking (mypy)
  - Frontend linting and build

#### C. `deploy.yml` - Production Deployment
- **Trigger:** Manual trigger or when new tags are pushed
- **Steps:**
  - Build and push Docker images with version tags
  - Supports semantic versioning (v1.0.0, v1.0.1, etc.)

### Setting Up GitHub Actions

1. **Create GitHub Secrets:**
   ```bash
   DOCKER_USERNAME=your_docker_username
   DOCKER_PASSWORD=your_docker_token
   ```

2. **Tag releases for deployment:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Monitor workflow runs:**
   - Go to Actions tab in GitHub
   - View logs for each workflow

## 6. Docker Deployment

### Building Images Locally

```bash
# Backend
docker build -f Dockerfile.backend -t research-agent-backend:latest .

# Frontend
docker build -f frontend/Dockerfile.frontend -t research-agent-frontend:latest frontend/
```

### Running with Docker Compose

```bash
# Create .env file with required variables
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Environment Variables for Production

```bash
SECRET_KEY=your-strong-random-secret-key-here
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
GOOGLE_CX=your_google_cx
DATABASE_URL=postgresql://user:pass@host/dbname
```

## 7. Security Considerations

### Implemented

✅ JWT token authentication
✅ Rate limiting
✅ Input validation with Pydantic
✅ Request/response logging
✅ CORS enabled (adjust as needed)

### Recommended for Production

- [ ] Enable HTTPS/TLS
- [ ] Implement role-based access control (RBAC)
- [ ] Add database encryption
- [ ] Configure IP whitelisting
- [ ] Set up Web Application Firewall (WAF)
- [ ] Implement API key management
- [ ] Add request signing/verification
- [ ] Configure secure password policies

## 8. Monitoring & Maintenance

### Key Metrics to Monitor

- Request latency
- Error rates
- Database query performance
- Token refresh rates
- Rate limit violations

### Health Check

```bash
curl http://localhost:8000/health
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=backend
```

## 9. Upgrading Dependencies

```bash
# Update requirements
pip install --upgrade -r requirements.txt

# Pin versions for reproducibility
pip freeze > requirements.lock
```

## 10. Troubleshooting

### Rate Limit Issues
- Check your request frequency
- Implement exponential backoff in client
- Contact admin for limit adjustment

### Authentication Failures
- Verify token format: `Authorization: bearer <token>`
- Check token expiration
- Regenerate token via login endpoint

### Logging Issues
- Check `logs/` directory exists
- Verify file permissions
- Check disk space availability

---

For more information, see `README.md` for API documentation and examples.
