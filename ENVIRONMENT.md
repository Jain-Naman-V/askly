# 🔧 Environment Configuration Guide

This document explains how to properly configure environment variables for the AI Data Agent project across different environments and deployment scenarios.

## 📁 Environment File Structure

```
ai-data-agent/
├── .env                           # Main environment file (not in git)
├── .env.development.example       # Development template
├── .env.production.example        # Production template
├── backend/
│   ├── .env                      # Backend-specific config (not in git)
│   └── .env.example              # Backend template
└── frontend/
    ├── .env.local                # Frontend environment (not in git)
    └── .env.example              # Frontend template
```

## 🔄 Configuration Priority

Environment variables are loaded in this priority order:

1. **System environment variables** (highest priority)
2. **Root-level `.env`** (shared configuration)
3. **Service-specific `.env`** (backend/.env or frontend/.env.local)
4. **Default values** in code (lowest priority)

## 🛠️ Setup Instructions

### 1. Development Environment

```bash
# Copy development templates
cp .env.development.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Update with your actual values
nano .env                    # Update GROQ_API_KEY
nano backend/.env           # Update backend-specific settings
nano frontend/.env.local    # Update frontend settings
```

### 2. Production Environment

```bash
# Copy production templates
cp .env.production.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Update with production values
nano .env                    # Set production API keys, domains
nano backend/.env           # Set production database URLs
nano frontend/.env.local    # Set production API endpoints
```

## 📝 Environment Variables Reference

### 🔧 Root Level Configuration (/.env)

#### Database Configuration
```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/ai_data_agent
MONGODB_DB_NAME=ai_data_agent
MONGODB_COLLECTION_NAME=structured_data

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
CACHE_TTL=3600
```

#### AI Service Configuration
```bash
# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
AI_MODEL=llama-3.1-8b-instant

# Vector Search
VECTOR_DIMENSION=1536
SEARCH_LIMIT=50
SIMILARITY_THRESHOLD=0.7
```

#### Security Configuration
```bash
SECRET_KEY=your_super_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SECURE_COOKIES=true
HTTPS_ONLY=true
```

### 🚀 Backend Configuration (/backend/.env)

#### API Configuration
```bash
API_V1_STR=/api/v1
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# CORS
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

#### Logging & Monitoring
```bash
LOG_LEVEL=INFO
LOG_FILE=app.log
SENTRY_DSN=your_sentry_dsn_here
ENABLE_METRICS=true
```

#### Rate Limiting
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 🌐 Frontend Configuration (/frontend/.env.local)

#### API Endpoints
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

#### Application Settings
```bash
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
```

#### Feature Flags
```bash
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_CHAT=true
REACT_APP_ENABLE_EXPORT=true
REACT_APP_DEBUG=false
```

## 🌍 Environment-Specific Configurations

### Development Environment
```bash
# Database
MONGODB_URI=mongodb://localhost:27017/ai_data_agent
REDIS_URL=redis://localhost:6379

# API
API_RELOAD=True
LOG_LEVEL=DEBUG
SECURE_COOKIES=false
HTTPS_ONLY=false

# Frontend
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENV=development
REACT_APP_DEBUG=true
```

### Production Environment
```bash
# Database (use managed services)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ai_data_agent_prod
REDIS_URL=redis://user:pass@redis-server:6379

# API
API_RELOAD=False
LOG_LEVEL=INFO
SECURE_COOKIES=true
HTTPS_ONLY=true

# Frontend
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENV=production
REACT_APP_DEBUG=false
```

### Docker Environment
```bash
# Use Docker service names
MONGODB_URI=mongodb://admin:password123@mongodb:27017/ai_data_agent?authSource=admin
REDIS_URL=redis://:redis123@redis:6379

# Docker-specific
API_HOST=0.0.0.0
CORS_ORIGINS=["http://frontend","https://yourdomain.com"]
```

## 🔐 Security Best Practices

### 1. API Keys and Secrets
```bash
# ✅ Use strong, unique keys
SECRET_KEY=$(openssl rand -hex 32)
GROQ_API_KEY=gsk_your_actual_key_here

# ❌ Never commit real keys
# GROQ_API_KEY=gsk_E3dlsnMw8TSM8HvtIiFPWGdyb3FY...
```

### 2. Database Security
```bash
# ✅ Use authentication
MONGODB_URI=mongodb://username:password@host:port/database

# ✅ Use SSL/TLS in production
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db?ssl=true

# ❌ Avoid default credentials
# MONGODB_URI=mongodb://admin:password123@localhost:27017
```

### 3. CORS Configuration
```bash
# ✅ Specific origins in production
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# ❌ Avoid wildcards in production
# CORS_ORIGINS=["*"]
```

## 🚀 Cloud Platform Configurations

### Heroku
```bash
# Set via Heroku CLI
heroku config:set GROQ_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set MONGODB_URI=mongodb+srv://...

# Or via .env for staging
# (Heroku automatically loads environment variables)
```

### AWS/Docker
```bash
# Use AWS Parameter Store or Secrets Manager
GROQ_API_KEY={{resolve:secretsmanager:ai-data-agent:SecretString:GROQ_API_KEY}}

# Or Docker secrets
GROQ_API_KEY_FILE=/run/secrets/groq_api_key
```

### Kubernetes
```yaml
# ConfigMap for non-sensitive data
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-data-agent-config
data:
  MONGODB_DB_NAME: ai_data_agent
  LOG_LEVEL: INFO

# Secret for sensitive data
apiVersion: v1
kind: Secret
metadata:
  name: ai-data-agent-secrets
type: Opaque
data:
  GROQ_API_KEY: <base64-encoded-key>
  SECRET_KEY: <base64-encoded-secret>
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
```bash
# Check if file exists
ls -la .env

# Check file format (no spaces around =)
cat .env | grep -E "^\w+\s*=.*"

# Check file permissions
chmod 644 .env
```

#### 2. Frontend Environment Variables
```bash
# ✅ Must start with REACT_APP_
REACT_APP_API_URL=http://localhost:8000

# ❌ Won't work
API_URL=http://localhost:8000
```

#### 3. Docker Environment Issues
```bash
# Check if variables are passed to container
docker exec container_name env | grep GROQ_API_KEY

# Check docker-compose environment section
docker-compose config
```

### Validation Commands

```bash
# Check backend configuration
cd backend && python -c "from app.utils.config import settings; print(settings.dict())"

# Check if API key is set
echo $GROQ_API_KEY

# Test database connection
mongosh "$MONGODB_URI" --eval "db.runCommand({ping: 1})"

# Test Redis connection
redis-cli -u "$REDIS_URL" ping
```

## 📋 Deployment Checklist

### Before Deployment
- [ ] Copy appropriate .env.example files
- [ ] Update all API keys and secrets
- [ ] Set correct database URLs
- [ ] Configure CORS origins
- [ ] Set production logging levels
- [ ] Enable security features
- [ ] Test all environment variables

### After Deployment
- [ ] Verify environment variables are loaded
- [ ] Test API connectivity
- [ ] Check database connections
- [ ] Verify logging output
- [ ] Test application functionality

## 🔄 Environment Migration

### From Development to Production
```bash
# 1. Copy production template
cp .env.production.example .env

# 2. Update critical variables
sed -i 's/localhost/your-domain.com/g' .env
sed -i 's/development/production/g' .env
sed -i 's/DEBUG/INFO/g' .env

# 3. Set real API keys
echo "GROQ_API_KEY=your_real_key" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### Environment Sync Script
```bash
#!/bin/bash
# sync-env.sh - Sync environment variables across services

# Copy shared variables to service-specific files
grep -v '^REACT_APP_' .env > backend/.env.temp
grep '^REACT_APP_' .env > frontend/.env.local.temp

# Merge with existing service-specific variables
cat backend/.env.example backend/.env.temp > backend/.env
cat frontend/.env.example frontend/.env.local.temp > frontend/.env.local

# Cleanup
rm *.temp
```

---

## 📞 Support

For environment configuration issues:
1. Check this guide for common patterns
2. Validate environment files with provided commands
3. Test configurations in development before production
4. Use example files as templates

Remember: **Never commit actual API keys or secrets to version control!**