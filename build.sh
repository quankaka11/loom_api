#!/usr/bin/env bash
# Build script for Render deployment

set -e

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🌐 Installing Chromium browser..."
playwright install chromium

echo "📚 Installing Chromium dependencies..."
playwright install-deps chromium

echo "✅ Build completed successfully!"
