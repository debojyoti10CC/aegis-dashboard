#!/bin/bash

# Disaster Management System Deployment Script

echo "🚨 Disaster Management System Deployment"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting application..."
docker-compose up -d

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if application is healthy
echo "🔍 Checking application health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
    echo ""
    echo "🌐 Your Disaster Management System is now running at:"
    echo "   http://localhost:5000"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop the application:"
    echo "   docker-compose down"
    echo ""
    echo "🎉 Deployment successful!"
else
    echo "❌ Application health check failed"
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi