#!/bin/bash
# Setup script for Disaster Management System

set -e

echo "🚀 Setting up Disaster Management System..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker check passed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p test_images
mkdir -p data

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your blockchain credentials"
else
    echo "✅ .env file already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make run script executable
chmod +x run.py

# Test Redis connection with Docker
echo "🧪 Testing Redis with Docker..."
docker run --rm -d --name test-redis -p 6380:6379 redis:7-alpine
sleep 2

if docker exec test-redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis test passed"
else
    echo "❌ Redis test failed"
fi

docker stop test-redis

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your blockchain credentials:"
echo "   nano .env"
echo ""
echo "2. Start the system:"
echo "   docker-compose up -d"
echo "   # OR"
echo "   python run.py start"
echo ""
echo "3. Check system status:"
echo "   python run.py status"
echo ""
echo "4. Test with sample image:"
echo "   python run.py test test_images/your_image.jpg"
echo ""
echo "📚 Read README.md for detailed instructions"