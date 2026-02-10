#!/bin/bash

echo "🎬 CINEGO - Movie Streaming Platform"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ pip detected"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run the application
echo ""
echo "🚀 Starting CINEGO..."
echo ""
echo "=================================="
echo "Access the application at:"
echo "👉 http://localhost:5000"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
