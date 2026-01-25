#!/usr/bin/env bash
# Build script for Render deployment

set -e

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🌐 Installing Chrome and ChromeDriver..."

# Use Chrome for Testing (official builds)
CHROME_VERSION="131.0.6778.87"

# Download Chrome
wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip
unzip -q chrome-linux64.zip
chmod +x chrome-linux64/chrome
export CHROME_BIN=$(pwd)/chrome-linux64/chrome

# Download ChromeDriver  
wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip
unzip -q chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver
export PATH=$(pwd)/chromedriver-linux64:$PATH

echo "✅ Build completed successfully!"
echo "Chrome: $CHROME_BIN"
echo "ChromeDriver: $(pwd)/chromedriver-linux64/chromedriver"
