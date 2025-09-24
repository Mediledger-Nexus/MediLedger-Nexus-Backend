# MediLedger Nexus Backend Deployment Guide

This guide provides step-by-step instructions for deploying the MediLedger Nexus backend to various platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Render.com Deployment](#rendercom-deployment)
6. [AWS Deployment](#aws-deployment)
7. [Environment Variables](#environment-variables)
8. [Database Setup](#database-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.11+
- Node.js 18+ (for frontend assets)
- PostgreSQL 14+ or SQLite (for development)
- Redis 6+ (for caching and task queues)
- Git

### Accounts & Services
- Hedera Testnet/Mainnet account
- Groq AI API key
- IPFS/Arweave account (optional)
- Render.com account (for cloud deployment)
- AWS account (for AWS deployment)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/mediledger-nexus.git
cd mediledger-nexus
```

### 2. Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the backend directory:

```bash
# Hedera Configuration
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here
HEDERA_OPERATOR_ID=0.0.123456
HEDERA_OPERATOR_KEY=your_operator_key_here

# Database Configuration
DATABASE_URL=sqlite:///./mediledger.db
# For PostgreSQL: postgresql://user:password@localhost/mediledger

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Groq AI Configuration
GROQ_API_KEY=your_groq_api_key_here

# Smart Contract Addresses
HEALTH_VAULT_CONTRACT=0.0.1001
CONSENT_CONTRACT=0.0.1002
RESEARCH_CONTRACT=0.0.1003
EMERGENCY_CONTRACT=0.0.1004

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Local Development

### 1. Start Database
```bash
# For SQLite (default)
# No additional setup needed

# For PostgreSQL
sudo systemctl start postgresql
createdb mediledger
```

### 2. Start Redis
```bash
# macOS with Homebrew
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. Run Database Migrations
```bash
cd backend
python -m alembic upgrade head
```

### 4. Start the Application
```bash
# Development mode
uvicorn src.mediledger_nexus.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.mediledger_nexus.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Start Celery Workers (Optional)
```bash
# In a separate terminal
celery -A src.mediledger_nexus.main:celery worker --loglevel=info
```

### 6. Verify Deployment
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
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

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.mediledger_nexus.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mediledger
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=mediledger
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A src.mediledger_nexus.main:celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mediledger
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Render.com Deployment

### 1. Connect Repository
1. Go to [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `mediledger-nexus` repository

### 2. Configure Service
- **Name**: `mediledger-nexus-backend`
- **Environment**: `Python 3`
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn src.mediledger_nexus.main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables
Add the following environment variables in Render dashboard:

```bash
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://user:password@host:port
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Database Setup
1. Create a PostgreSQL database in Render
2. Update the `DATABASE_URL` environment variable
3. The application will automatically run migrations on startup

### 5. Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Access your API at the provided URL

## AWS Deployment

### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y
```

### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/your-org/mediledger-nexus.git
cd mediledger-nexus/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your environment variables

# Run migrations
python -m alembic upgrade head
```

### 3. Systemd Service
Create `/etc/systemd/system/mediledger.service`:

```ini
[Unit]
Description=MediLedger Nexus API
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/mediledger-nexus/backend
Environment=PATH=/home/ubuntu/mediledger-nexus/backend/venv/bin
ExecStart=/home/ubuntu/mediledger-nexus/backend/venv/bin/uvicorn src.mediledger_nexus.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration
Create `/etc/nginx/sites-available/mediledger`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Start Services
```bash
# Enable and start services
sudo systemctl enable mediledger
sudo systemctl start mediledger
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status mediledger
```

## Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `HEDERA_ACCOUNT_ID` | Your Hedera account ID | `0.0.123456` |
| `HEDERA_PRIVATE_KEY` | Your Hedera private key | `302e020100300506032b657004220420...` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | Application secret key | `your-secret-key-here` |
| `JWT_SECRET_KEY` | JWT signing key | `your-jwt-secret-here` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `HEDERA_NETWORK` | Hedera network (testnet/mainnet) | `testnet` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## Database Setup

### PostgreSQL Setup
```bash
# Create database
sudo -u postgres createdb mediledger

# Create user
sudo -u postgres createuser mediledger_user

# Set password
sudo -u postgres psql -c "ALTER USER mediledger_user PASSWORD 'your_password';"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mediledger TO mediledger_user;"
```

### Run Migrations
```bash
cd backend
python -m alembic upgrade head
```

## Monitoring & Logging

### Health Checks
The application provides health check endpoints:

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health information
- `GET /metrics` - Application metrics

### Logging Configuration
Logs are written to:
- Console (stdout)
- Files in `logs/` directory
- JSON format for structured logging

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client

# Configure Prometheus (optional)
# Add to your monitoring stack
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U mediledger_user -d mediledger
```

#### 2. Hedera Connection Issues
```bash
# Verify Hedera credentials
python -c "
from src.mediledger_nexus.blockchain.hedera_client import HederaClient
client = HederaClient()
print(client.get_account_balance())
"
```

#### 3. Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Log Analysis
```bash
# View application logs
tail -f logs/mediledger.log

# View system logs
sudo journalctl -u mediledger -f
```

### Performance Optimization
```bash
# Increase worker processes
uvicorn src.mediledger_nexus.main:app --workers 4

# Enable gzip compression
# Add to nginx config: gzip on;

# Use connection pooling
# Configure in database settings
```

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secrets
- Rotate keys regularly

### 2. Database Security
- Use strong passwords
- Enable SSL connections
- Restrict network access

### 3. API Security
- Enable HTTPS in production
- Use proper CORS configuration
- Implement rate limiting

### 4. Hedera Security
- Store private keys securely
- Use environment variables for credentials
- Monitor account activity

## Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test database connections
4. Check Hedera network status
5. Contact support team

## Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure automated backups
3. Implement CI/CD pipeline
4. Set up staging environment
5. Plan for scaling
