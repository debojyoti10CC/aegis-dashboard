#!/bin/bash

echo "🚀 Vercel Deployment for Disaster Management System"
echo "==================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Vercel CLI"
        exit 1
    fi
fi

echo "✅ Vercel CLI is ready"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit for Vercel deployment"
fi

echo "🚀 Starting Vercel deployment..."
echo ""
echo "📋 Follow these prompts:"
echo "   - Set up and deploy? [Y/n] → Press Y"
echo "   - Which scope? → Select your account"
echo "   - Link to existing project? [y/N] → Press N"
echo "   - Project name? → disaster-management-system (or your choice)"
echo "   - Directory? → Press Enter (use current directory)"
echo ""

vercel

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "🌐 Your Disaster Management System is now live!"
    echo "   Check the URL provided above"
    echo ""
    echo "📊 Features available:"
    echo "   ✅ Beautiful brutalist UI"
    echo "   ✅ Interactive disaster simulation"
    echo "   ✅ Demo blockchain transactions"
    echo "   ✅ Real-time logging"
    echo "   ✅ Mobile responsive design"
    echo ""
    echo "🔄 To update your deployment:"
    echo "   1. Make changes to your code"
    echo "   2. Run: vercel --prod"
    echo ""
    echo "🌍 To add a custom domain:"
    echo "   1. Go to vercel.com dashboard"
    echo "   2. Select your project"
    echo "   3. Go to Settings → Domains"
    echo ""
else
    echo "❌ Deployment failed"
    echo "📋 Check the error messages above"
fi