# 🌐 Heroku Deployment Guide

Deploy your disaster management system to Heroku in minutes!

## 🚀 Quick Heroku Deployment

### Step 1: Install Heroku CLI
```bash
# Windows (using chocolatey)
choco install heroku-cli

# macOS (using homebrew)
brew tap heroku/brew && brew install heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login to Heroku
```bash
heroku login
```

### Step 3: Create Heroku App
```bash
# Create app with unique name
heroku create your-disaster-system-123

# Or let Heroku generate a name
heroku create
```

### Step 4: Set Environment Variables
```bash
# Set your blockchain credentials
heroku config:set BLOCKCHAIN_NETWORK_URL="https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832"
heroku config:set BLOCKCHAIN_PRIVATE_KEY="0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c"

# Set recipient addresses
heroku config:set EMERGENCY_NGO_ADDRESS="0x5D3f355f0EA186896802878E7Aa0b184469c3033"
heroku config:set LOCAL_GOVERNMENT_ADDRESS="0x5D3f355f0EA186896802878E7Aa0b184469c3033"
heroku config:set DISASTER_RELIEF_ADDRESS="0x5D3f355f0EA186896802878E7Aa0b184469c3033"

# Set Flask environment
heroku config:set FLASK_ENV=production
```

### Step 5: Deploy
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial deployment to Heroku"

# Add Heroku remote
heroku git:remote -a your-disaster-system-123

# Deploy
git push heroku main
```

### Step 6: Open Your App
```bash
heroku open
```

## 🔧 Heroku Configuration

### Buildpacks
Heroku will automatically detect Python and install dependencies from `requirements.txt`.

### Scaling
```bash
# Scale web dynos
heroku ps:scale web=1

# Check status
heroku ps
```

### Logs
```bash
# View logs
heroku logs --tail

# View specific logs
heroku logs --source app --tail
```

## 💰 Heroku Pricing

- **Free Tier**: Discontinued (as of November 2022)
- **Eco Dynos**: $5/month (sleeps after 30 minutes of inactivity)
- **Basic Dynos**: $7/month (never sleeps)
- **Standard Dynos**: $25/month (auto-scaling, metrics)

## 🔄 Updates

To update your deployed app:
```bash
git add .
git commit -m "Update application"
git push heroku main
```

## 🌍 Custom Domain

```bash
# Add custom domain
heroku domains:add your-domain.com

# Configure DNS
# Point your domain's CNAME to: your-app-name.herokuapp.com
```

## 🔒 SSL Certificate

Heroku provides free SSL certificates for all apps:
- Automatic SSL for *.herokuapp.com domains
- Free SSL for custom domains (Automated Certificate Management)

## 📊 Monitoring

```bash
# View app metrics
heroku logs --tail

# Monitor performance
heroku ps:exec
```

## 🆘 Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Check build logs
   heroku logs --tail
   
   # Ensure requirements.txt is correct
   pip freeze > requirements.txt
   ```

2. **App Crashes**
   ```bash
   # Check error logs
   heroku logs --tail
   
   # Restart app
   heroku restart
   ```

3. **Environment Variables**
   ```bash
   # List all config vars
   heroku config
   
   # Set missing variables
   heroku config:set VARIABLE_NAME=value
   ```

## 🎉 Success!

Your disaster management system is now live on Heroku! 

- **URL**: https://your-app-name.herokuapp.com
- **Real Blockchain Transactions**: ✅ Enabled
- **Brutalist UI**: ✅ Live
- **Global Access**: ✅ Available worldwide

Share your live disaster management system with the world! 🌍