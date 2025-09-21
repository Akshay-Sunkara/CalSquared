#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting deployment process..."

# Render-optimized Chrome installation with caching
STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
    echo "📦 Downloading Chrome..."
    mkdir -p $STORAGE_DIR/chrome
    
    # Save current directory
    ORIGINAL_DIR=$(pwd)
    
    cd $STORAGE_DIR/chrome
    wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
    rm ./google-chrome-stable_current_amd64.deb
    
    # Return to original directory
    cd $ORIGINAL_DIR
    echo "✅ Chrome downloaded and extracted"
else
    echo "✅ Using Chrome from cache"
fi

export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

echo "🌐 Installing Chrome dependencies..."
apt-get update
apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    wget \
    gnupg \
    unzip \
    curl

# Clean up apt cache
rm -rf /var/lib/apt/lists/*

echo "✅ Chrome dependencies installed"

echo "🐍 Installing Python dependencies..."
pip3 install --no-cache-dir -r requirements.txt
echo "✅ Python dependencies installed"

echo "🚀 Starting Python server..."
python3 server.py
