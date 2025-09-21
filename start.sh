#!/bin/bash

echo "🚀 Starting deployment process..."

echo "📦 Installing system dependencies and Google Chrome..."
apt-get update

apt-get install -y wget gnupg unzip curl

wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

apt-get update
apt-get install -y google-chrome-stable

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
    xdg-utils

rm -rf /var/lib/apt/lists/*

echo "✅ Chrome installation completed"

echo "🐍 Installing Python dependencies..."
pip3 install --no-cache-dir -r requirements.txt

echo "✅ Python dependencies installed"

echo "🚀 Starting Python server..."
python3 server.py
