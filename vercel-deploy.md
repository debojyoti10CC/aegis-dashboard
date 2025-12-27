# 🚀 Vercel Deployment Guide

Deploy your disaster management system to Vercel for free with global CDN!

## ⚡ Why Vercel?

- **Free hosting** with generous limits
- **Global CDN** for fast loading worldwide
- **Automatic HTTPS** and custom domains
- **Git integration** for automatic deployments
- **Serverless functions** for backend API

## 🎯 Vercel Limitations & Solutions

### Limitations:
- **50MB deployment size limit** (our full system is larger)
- **No persistent storage** (serverless functions)
- **10-second function timeout** (for free tier)

### Our Solution:
- **Demo mode** with simulated blockchain transactions
- **Lightweight version** without heavy AI libraries
- **Mock data** for disaster detection
- **Beautiful UI** with full functionality

## 🚀 Quick Vercel Deployment

### Method 1: Vercel CLI (Recommended)

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Login to Vercel
```bash
vercel login
```

#### Step 3: Deploy
```bash
# From your project root
vercel

# Follow the prompts:
# ? Set up and deploy "~/disaster-management-system"? [Y/n] y
# ? Which scope do you want to deploy to? [Your Account]
# ? Link to existing project? [y/N] n
# ? What's your project's name? disaster-management-system
# ? In which directory is your code located? ./
```

#### Step 4: Set Environment Variables (Optional)
```bash
vercel env add BLOCKCHAIN_NETWORK_URL
# Enter: https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832

vercel env add BLOCKCHAIN_PRIVATE_KEY
# Enter: 0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c
```

### Method 2: GitHub Integration

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

#### Step 2: Import on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure build settings:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty)
   - **Output Directory**: `frontend`

#### Step 3: Deploy
Click "Deploy" and wait for deployment to complete!

## 🔧 Vercel Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/vercel_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*\\.(css|js|html|ico|png|jpg))",
      "dest": "/frontend/$1"
    },
    {
      "src": "/api/(.*)",
      "dest": "/frontend/vercel_app.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/vercel_app.py"
    }
  ]
}
```

### requirements.txt (Vercel-optimized)
```txt
Flask==2.3.3
web3==6.11.0
Pillow==10.0.1
numpy==1.24.3
python-dotenv==1.0.0
eth-account==0.9.0
flask-limiter==3.5.0
```

## 🌍 Custom Domain

### Step 1: Add Domain in Vercel Dashboard
1. Go to your project dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain

### Step 2: Configure DNS
Point your domain to Vercel:
```
Type: CNAME
Name: www (or @)
Value: cname.vercel-dns.com
```

### Step 3: SSL Certificate
Vercel automatically provides SSL certificates for all domains!

## 📊 Vercel Features

### Automatic Deployments
- **Git Integration**: Every push to main branch deploys automatically
- **Preview Deployments**: Every pull request gets a preview URL
- **Rollback**: Easy rollback to previous deployments

### Analytics
- **Web Analytics**: Built-in analytics dashboard
- **Performance Monitoring**: Core Web Vitals tracking
- **Function Logs**: Serverless function execution logs

### Environment Variables
```bash
# Production environment
vercel env add BLOCKCHAIN_NETWORK_URL production

# Preview environment  
vercel env add BLOCKCHAIN_NETWORK_URL preview

# Development environment
vercel env add BLOCKCHAIN_NETWORK_URL development
```

## 🎨 Vercel Demo Features

Your Vercel deployment will have:

### ✅ Working Features:
- **Beautiful brutalist UI** - Full visual experience
- **Interactive buttons** - All UI interactions work
- **Simulated disaster detection** - Mock AI responses
- **Fake blockchain transactions** - Demo transaction hashes
- **Real-time logs** - Terminal-style output
- **Statistics dashboard** - Mock performance metrics
- **Mobile responsive** - Works on all devices

### ⚠️ Demo Limitations:
- **No real AI processing** - Uses mock disaster detection
- **No real blockchain transactions** - Simulated for demo
- **No persistent data** - Resets on each deployment

## 💰 Vercel Pricing

### Hobby (Free)
- **100GB bandwidth** per month
- **100 serverless function executions** per day
- **Custom domains** included
- **Automatic HTTPS**

### Pro ($20/month)
- **1TB bandwidth** per month
- **1000 serverless function executions** per day
- **Advanced analytics**
- **Password protection**

## 🔄 Updates & Maintenance

### Automatic Updates
```bash
# Push changes to trigger deployment
git add .
git commit -m "Update disaster system"
git push origin main
```

### Manual Deployment
```bash
# Deploy specific branch
vercel --prod

# Deploy with custom name
vercel --name my-disaster-system
```

## 🆘 Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Check build logs in Vercel dashboard
   # Ensure requirements.txt is correct
   ```

2. **Function Timeout**
   ```bash
   # Upgrade to Pro plan for longer timeouts
   # Or optimize function performance
   ```

3. **Import Errors**
   ```bash
   # Check Python path in vercel.json
   # Ensure all dependencies are in requirements.txt
   ```

### Debug Commands
```bash
# Local development
vercel dev

# Check deployment logs
vercel logs

# List deployments
vercel ls
```

## 🎉 Success!

Your disaster management system is now live on Vercel!

### Example URLs:
- **Production**: https://disaster-management-system.vercel.app
- **Custom Domain**: https://your-domain.com
- **Preview**: https://disaster-management-system-git-feature.vercel.app

### What You Get:
- ✅ **Global CDN** - Fast loading worldwide
- ✅ **Automatic HTTPS** - Secure by default
- ✅ **Beautiful UI** - Full brutalist design
- ✅ **Demo Functionality** - Interactive experience
- ✅ **Mobile Responsive** - Works everywhere
- ✅ **Free Hosting** - No cost to run

## 🔗 Next Steps

1. **Share your demo** - Show the world your brutalist UI
2. **Custom domain** - Add your own domain name
3. **Real deployment** - Use Docker/Heroku for real transactions
4. **Analytics** - Monitor usage with Vercel Analytics

---

**🌍 Your disaster management system is now live on the global web!**

Perfect for demos, portfolios, and showcasing your brutalist design skills!