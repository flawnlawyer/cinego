@echo off
echo ========================================
echo     CINEGO - Movie Streaming Platform
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Run the application
echo ========================================
echo Starting CINEGO...
echo.
echo Access the application at:
echo    http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
