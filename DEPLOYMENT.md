# 🚀 Disaster Management System - Deployment Guide

Complete guide to deploy your brutalist disaster management system with real blockchain transactions.

## 📋 Quick Deployment Options

### 1. 🏠 **Local Development** (Current Setup)
```bash
cd frontend
python app.py
# Open http://localhost:5000
```

### 2. 🌐 **Simple Cloud Deployment** (Heroku/Railway)
### 3. 🐳 **Docker Deployment** 
### 4. ☁️ **Production Cloud** (AWS/GCP/Azure)

---

## 🐳 Docker Deployment (Recommended)

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "frontend/app.py"]
```

### Step 2: Create requirements.txt
```txt
Flask==2.3.3
web3==6.11.0
opencv-python-headless==4.8.1.78
Pillow==10.0.1
numpy==1.24.3
python-dotenv==1.0.0
asyncio==3.4.3
eth-account==0.9.0
```

### Step 3: Create docker-compose.yml
```yaml
version: '3.8'
services:
  disaster-system:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - BLOCKCHAIN_NETWORK_URL=${BLOCKCHAIN_NETWORK_URL}
      - BLOCKCHAIN_PRIVATE_KEY=${BLOCKCHAIN_PRIVATE_KEY}
    volumes:
      - ./test_images:/app/test_images:ro
    restart: unless-stopped
```

### Step 4: Deploy with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🌐 Heroku Deployment

### Step 1: Prepare for Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python frontend/app.py" > Procfile

# Create runtime.txt
echo "python-3.9.18" > runtime.txt
```

### Step 2: Configure Environment
```bash
# Set environment variables
heroku config:set BLOCKCHAIN_NETWORK_URL="https://sepolia.infura.io/v3/YOUR_PROJECT_ID"
heroku config:set BLOCKCHAIN_PRIVATE_KEY="0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c"
heroku config:set FLASK_ENV=production
```

### Step 3: Deploy
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial deployment"

# Create Heroku app
heroku create your-disaster-system

# Deploy
git push heroku main

# Open app
heroku open
```

---

## ☁️ AWS Deployment (Production)

### Option A: AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init disaster-management-system

# Create environment
eb create production

# Deploy
eb deploy

# Open
eb open
```

### Option B: AWS ECS with Fargate
```yaml
# docker-compose.aws.yml
version: '3.8'
services:
  disaster-system:
    image: your-account.dkr.ecr.region.amazonaws.com/disaster-system:latest
    ports:
      - "80:5000"
    environment:
      - BLOCKCHAIN_NETWORK_URL=${BLOCKCHAIN_NETWORK_URL}
      - BLOCKCHAIN_PRIVATE_KEY=${BLOCKCHAIN_PRIVATE_KEY}
    logging:
      driver: awslogs
      options:
        awslogs-group: /ecs/disaster-system
        awslogs-region: us-east-1
        awslogs-stream-prefix: ecs
```

---

## 🔧 Production Configuration

### 1. Environment Variables
Create `.env.production`:
```env
FLASK_ENV=production
FLASK_DEBUG=False
BLOCKCHAIN_NETWORK_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
BLOCKCHAIN_PRIVATE_KEY=0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c
EMERGENCY_NGO_ADDRESS=0x742d35Cc6634C0532925a3b8D0C9e3e0C8b0e4c1
LOCAL_GOVERNMENT_ADDRESS=0x8ba1f109551bD432803012645Hac136c0c8b0e4c2
DISASTER_RELIEF_ADDRESS=0x9cb2f209661cE532925a3b8D0C9e3e0C8b0e4c3
```

### 2. Production Flask App
```python
# frontend/wsgi.py
from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 3. Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔒 Security Considerations

### 1. Environment Security
- ✅ Never commit private keys to git
- ✅ Use environment variables for secrets
- ✅ Use different keys for production
- ✅ Enable HTTPS in production

### 2. Blockchain Security
- ✅ Use testnet for development
- ✅ Limit transaction amounts
- ✅ Implement rate limiting
- ✅ Monitor wallet balance

### 3. Application Security
```python
# Add to app.py for production
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/full-test', methods=['POST'])
@limiter.limit("5 per minute")  # Limit expensive operations
def full_test():
    # ... existing code
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring
```python
# Add to app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/disaster_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Disaster Management System startup')
```

### 2. Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

---

## 🚀 Quick Deploy Commands

### Local Development
```bash
cd frontend && python app.py
```

### Docker
```bash
docker-compose up -d
```

### Heroku
```bash
git push heroku main
```

### AWS
```bash
eb deploy
```

---

## 🌍 Domain & SSL

### 1. Custom Domain
- Buy domain from Namecheap/GoDaddy
- Point DNS to your deployment
- Configure SSL certificate

### 2. Free SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 💰 Cost Estimates

### Development
- **Local**: Free
- **Heroku**: $7/month (Hobby tier)
- **Railway**: $5/month

### Production
- **AWS ECS**: $20-50/month
- **Digital Ocean**: $10-25/month
- **Google Cloud Run**: $10-30/month

### Blockchain Costs
- **Sepolia Testnet**: Free (test ETH)
- **Ethereum Mainnet**: $5-50 per transaction

---

## 🎯 Recommended Deployment Path

1. **Start**: Local development (current)
2. **Demo**: Heroku deployment
3. **Production**: Docker + AWS/GCP
4. **Scale**: Kubernetes cluster

---

## 🆘 Troubleshooting

### Common Issues
1. **Port already in use**: Change port in app.py
2. **Image processing fails**: Install opencv dependencies
3. **Blockchain connection fails**: Check network URL and private key
4. **Memory issues**: Increase container memory limits

### Debug Commands
```bash
# Check logs
docker-compose logs disaster-system

# Shell into container
docker-compose exec disaster-system bash

# Check processes
docker-compose ps

# Restart service
docker-compose restart disaster-system
```

---

**🎉 Your brutalist disaster management system is ready for the world!**

Choose your deployment method and launch your real blockchain-powered disaster response system!