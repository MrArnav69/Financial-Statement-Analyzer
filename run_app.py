import subprocess
import sys
import os
import platform

def get_python_command():
    """Get the correct Python command for the current system"""
    system = platform.system().lower()
    
    # Try different Python commands
    python_commands = ['python3', 'python', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Found Python: {cmd} - {result.stdout.strip()}")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def install_requirements():
    """Install required packages"""
    python_cmd = get_python_command()
    if not python_cmd:
        print("❌ Python not found. Please install Python 3.7+ and try again.")
        return False
    
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        print("💡 Trying to install packages individually...")
        
        # Try installing packages individually
        packages = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0", 
            "openpyxl>=3.1.0",
            "plotly>=5.15.0",
            "requests>=2.31.0",
            "numpy>=1.24.0"
        ]
        
        for package in packages:
            try:
                subprocess.check_call([python_cmd, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def run_streamlit_app():
    """Run the Streamlit application"""
    python_cmd = get_python_command()
    if not python_cmd:
        print("❌ Python not found. Cannot run the application.")
        return
    
    try:
        print("🌟 Launching Streamlit application...")
        print("🌐 The app will open in your default web browser")
        print("🛑 Press Ctrl+C to stop the application")
        subprocess.run([python_cmd, "-m", "streamlit", "run", "main_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        print("💡 Try running manually: streamlit run main_app.py")

def check_files():
    """Check if required files exist"""
    required_files = ["main_app.py", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("📁 Please ensure all files are in the current directory:")
        print("   - main_app.py")
        print("   - ai_analyzer.py") 
        print("   - data_processor.py")
        print("   - visualizations.py")
        print("   - config.py")
        print("   - requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Financial Statement Analyzer Setup")
    print("=" * 50)
    
    # Check if files exist
    if not check_files():
        exit(1)
    
    # Check Python installation
    python_cmd = get_python_command()
    if not python_cmd:
        print("❌ Python not found!")
        print("💡 Please install Python 3.7+ from https://python.org")
        print("💡 On macOS, you can also install via Homebrew: brew install python3")
        exit(1)
    
    print("📦 Installing requirements...")
    if install_requirements():
        print("🌟 Setup complete! Launching application...")
        run_streamlit_app()
    else:
        print("❌ Failed to install requirements.")
        print("💡 Try installing manually:")
        print(f"   {python_cmd} -m pip install streamlit pandas openpyxl plotly requests numpy")



