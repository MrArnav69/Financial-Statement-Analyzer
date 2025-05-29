#!/bin/bash

echo "🚀 Setting up Financial Statement Analyzer on macOS"
echo "=================================================="

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found!"
    echo "💡 Please install Python 3 from https://python.org"
    echo "💡 Or install via Homebrew: brew install python3"
    exit 1
fi

# Check if pip is available
if python3 -m pip --version &> /dev/null; then
    echo "✅ pip found"
else
    echo "❌ pip not found!"
    echo "💡 Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install required packages
echo "📦 Installing required packages..."
python3 -m pip install --upgrade pip
python3 -m pip install streamlit pandas openpyxl plotly requests numpy

if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully!"
    echo "🌟 Starting the application..."
    python3 -m streamlit run main_app.py
else
    echo "❌ Failed to install some packages"
    echo "💡 Try running: python3 -m pip install streamlit pandas openpyxl plotly requests numpy"
fi
