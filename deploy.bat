@echo off
echo.
echo 🚨 Disaster Management System Deployment
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Create logs directory
if not exist logs mkdir logs

REM Build and start the application
echo 🔨 Building Docker image...
docker-compose build

echo 🚀 Starting application...
docker-compose up -d

REM Wait for application to start
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if application is healthy
echo 🔍 Checking application health...
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is healthy!
    echo.
    echo 🌐 Your Disaster Management System is now running at:
    echo    http://localhost:5000
    echo.
    echo 📊 To view logs:
    echo    docker-compose logs -f
    echo.
    echo 🛑 To stop the application:
    echo    docker-compose down
    echo.
    echo 🎉 Deployment successful!
) else (
    echo ❌ Application health check failed
    echo 📋 Checking logs...
    docker-compose logs
)

pause