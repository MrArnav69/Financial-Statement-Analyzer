@echo off
echo 🚀 Setting up Financial Statement Analyzer on Windows
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo 💡 Please install Python from https://python.org
    echo 💡 Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install required packages
echo 📦 Installing required packages...
python -m pip install --upgrade pip
python -m pip install streamlit pandas openpyxl plotly requests numpy

if %errorlevel% equ 0 (
    echo ✅ All packages installed successfully!
    echo 🌟 Starting the application...
    python -m streamlit run main_app.py
) else (
    echo ❌ Failed to install some packages
    echo 💡 Try running: python -m pip install streamlit pandas openpyxl plotly requests numpy
    pause
)
