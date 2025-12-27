@echo off
REM Setup script for Disaster Management System (Windows)

echo 🚀 Setting up Disaster Management System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    exit /b 1
)

echo ✅ Python check passed

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo ✅ Docker check passed

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✅ Docker Compose check passed

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist test_images mkdir test_images
if not exist data mkdir data

REM Copy environment template if .env doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your blockchain credentials
) else (
    echo ✅ .env file already exists
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your blockchain credentials
echo.
echo 2. Start the system:
echo    docker-compose up -d
echo    # OR
echo    python run.py start
echo.
echo 3. Check system status:
echo    python run.py status
echo.
echo 4. Test with sample image:
echo    python run.py test test_images/your_image.jpg
echo.
echo 📚 Read README.md for detailed instructions