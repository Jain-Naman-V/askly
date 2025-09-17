# AI Data Agent - Deployment Guide

This guide covers deploying the AI Data Agent to various cloud platforms and production environments.

## 🏗️ Architecture Overview

The AI Data Agent consists of:
- **Frontend**: React application with Redux state management
- **Backend**: FastAPI with async MongoDB and Redis
- **Database**: MongoDB for structured data storage
- **Cache**: Redis for session management and caching
- **AI**: Groq LLM integration for natural language processing

## 📋 Prerequisites

Before deployment, ensure you have:
- [ ] MongoDB instance (local or cloud)
- [ ] Redis instance (local or cloud)
- [ ] Groq API key
- [ ] Domain name (for production)
- [ ] SSL certificates (for HTTPS)

## 🚀 Quick Start with Docker

### 1. Environment Setup

```bash
# Copy environment template
cp .env.production.example .env

# Edit environment variables
nano .env
```

### 2. Deploy with Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Development deployment
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## ☁️ Cloud Platform Deployments

### Heroku Deployment

#### Backend Setup

1. **Create Heroku App**
```bash
# Install Heroku CLI
# Create app
heroku create ai-data-agent-api

# Set environment variables
heroku config:set GROQ_API_KEY=your_groq_key
heroku config:set SECRET_KEY=your_secret_key
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set REDIS_URL=your_redis_url
```

2. **Deploy Backend**
```bash
cd backend
git init
heroku git:remote -a ai-data-agent-api
git add .
git commit -m "Initial backend deployment"
git push heroku main
```

3. **Add Database Add-ons**
```bash
# MongoDB Atlas
heroku addons:create mongolab:sandbox

# Redis
heroku addons:create heroku-redis:mini
```

#### Frontend Setup (Netlify/Vercel)

1. **Build Settings**
```bash
# Build command
npm run build

# Publish directory
build/

# Environment variables
REACT_APP_API_URL=https://ai-data-agent-api.herokuapp.com
```

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create Task Definition**
```json
{
  "family": "ai-data-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-data-agent-backend:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "environment": [
        {"name": "MONGODB_URI", "value": "your-mongodb-uri"},
        {"name": "GROQ_API_KEY", "value": "your-groq-key"}
      ]
    }
  ]
}
```

2. **Deploy with ECS CLI**
```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin account.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-data-agent-backend backend/
docker tag ai-data-agent-backend:latest account.dkr.ecr.us-east-1.amazonaws.com/ai-data-agent-backend:latest
docker push account.dkr.ecr.us-east-1.amazonaws.com/ai-data-agent-backend:latest

# Create service
aws ecs create-service --cluster ai-data-agent --service-name ai-data-agent-service --task-definition ai-data-agent --desired-count 2
```

### Google Cloud Platform

#### Using Cloud Run

1. **Prepare Application**
```bash
# Backend deployment
cd backend
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-data-agent-backend

# Deploy to Cloud Run
gcloud run deploy ai-data-agent-backend \
  --image gcr.io/PROJECT-ID/ai-data-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key,MONGODB_URI=your_uri
```

2. **Frontend (Firebase Hosting)**
```bash
cd frontend
npm run build

# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Deploy
firebase deploy
```

### Azure Deployment

#### Using Azure Container Instances

1. **Create Resource Group**
```bash
az group create --name ai-data-agent-rg --location eastus
```

2. **Deploy Containers**
```bash
# Backend
az container create \
  --resource-group ai-data-agent-rg \
  --name ai-data-agent-backend \
  --image your-registry/ai-data-agent-backend:latest \
  --dns-name-label ai-data-agent-api \
  --ports 8000 \
  --environment-variables GROQ_API_KEY=your_key MONGODB_URI=your_uri

# Frontend
az container create \
  --resource-group ai-data-agent-rg \
  --name ai-data-agent-frontend \
  --image your-registry/ai-data-agent-frontend:latest \
  --dns-name-label ai-data-agent-web \
  --ports 80
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Required for all deployments
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_super_secret_key_change_in_production
MONGODB_URI=mongodb://username:password@host:port/database
REDIS_URL=redis://username:password@host:port

# Production specific
NODE_ENV=production
ALLOWED_ORIGINS=["https://yourdomain.com"]
SECURE_COOKIES=true
HTTPS_ONLY=true

# Optional monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

### Database Setup

#### MongoDB Atlas (Recommended)
```bash
# 1. Create cluster at mongodb.com/atlas
# 2. Create database user
# 3. Whitelist IP addresses
# 4. Get connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_data_agent?retryWrites=true&w=majority
```

#### Redis Cloud
```bash
# 1. Create Redis instance at redislabs.com
# 2. Get connection details
REDIS_URL=redis://username:password@host:port
```

### SSL/HTTPS Setup

#### Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Load Balancing & Scaling

#### Nginx Configuration
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Health Checks
```python
# backend/app/routers/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Logging Configuration
```python
# backend/app/utils/logging.py
import logging
import structlog

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🔒 Security Best Practices

### API Security
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Authentication tokens secured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection headers

### Infrastructure Security
- [ ] Firewall rules configured
- [ ] VPC/Security groups set up
- [ ] SSL/TLS certificates installed
- [ ] Environment variables secured
- [ ] Container images scanned
- [ ] Regular security updates

## 🚨 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```bash
# Check connection string
echo $MONGODB_URI

# Test connection
mongosh "$MONGODB_URI"

# Check network access
telnet mongodb-host 27017
```

#### 2. Redis Connection Failed
```bash
# Check Redis URL
echo $REDIS_URL

# Test connection
redis-cli -u "$REDIS_URL" ping
```

#### 3. API Rate Limits
```bash
# Check API key
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models

# Monitor usage
tail -f logs/app.log | grep "rate_limit"
```

#### 4. Frontend Build Issues
```bash
# Clear cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check environment variables
echo $REACT_APP_API_URL
```

### Performance Optimization

#### Database Indexing
```javascript
// MongoDB indexes
db.structured_data.createIndex({ "title": "text", "description": "text" });
db.structured_data.createIndex({ "category": 1 });
db.structured_data.createIndex({ "tags": 1 });
db.structured_data.createIndex({ "created_at": -1 });
```

#### Caching Strategy
```python
# Redis caching
@cached(ttl=300)  # 5 minutes
async def get_search_results(query: str):
    return await search_service.search(query)
```

#### CDN Setup
```bash
# CloudFlare CDN
# 1. Add domain to CloudFlare
# 2. Update DNS settings
# 3. Enable CDN for static assets
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Database read replicas
- Redis clustering
- CDN for static assets

### Vertical Scaling
- Increase CPU/memory for containers
- Optimize database queries
- Implement connection pooling
- Use async processing for heavy tasks

### Auto-scaling
```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-data-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-data-agent-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connections
4. Review security group/firewall rules
5. Check resource limits and quotas

## 🎯 Next Steps

After successful deployment:
- [ ] Set up monitoring dashboards
- [ ] Configure automated backups
- [ ] Implement CI/CD pipeline
- [ ] Set up staging environment
- [ ] Configure automated testing
- [ ] Plan disaster recovery

---

For more information, see the [README.md](README.md) file or open an issue in the repository.