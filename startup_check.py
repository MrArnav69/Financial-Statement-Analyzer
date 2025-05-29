import sys
import subprocess
import importlib

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas', 
        'openpyxl': 'openpyxl',
        'plotly': 'plotly',
        'requests': 'requests',
        'numpy': 'numpy'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ All packages installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages automatically")
            print("💡 Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    else:
        print("🎉 All dependencies are satisfied!")
        return True

def check_file_structure():
    """Check if all required files exist"""
    import os
    
    required_files = [
        'main_app.py',
        'ai_analyzer.py',
        'data_processor.py', 
        'visualizations.py',
        'config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files are present")
        return True

if __name__ == "__main__":
    print("🔍 Checking Financial Statement Analyzer setup...")
    print("=" * 50)
    
    deps_ok = check_dependencies()
    files_ok = check_file_structure()
    
    if deps_ok and files_ok:
        print("\n🚀 Everything looks good! You can now run:")
        print("   streamlit run main_app.py")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
