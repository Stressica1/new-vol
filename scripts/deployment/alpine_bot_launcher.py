#!/usr/bin/env python3
"""
Alpine Bot Launcher - Handles dependencies and starts the bot
"""

import sys
import subprocess
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing required dependencies...")
    
    # Try to install with pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install dependencies with pip")
        
        # Try alternative approach
        try:
            required_packages = [
                "ccxt",
                "pandas",
                "numpy",
                "ta",
                "rich",
                "loguru"
            ]
            
            for package in required_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
                    print(f"✅ Installed {package}")
                except:
                    print(f"❌ Failed to install {package}")
            
            return True
            
        except Exception as e:
            print(f"❌ Could not install dependencies: {e}")
            return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import ccxt
        import pandas
        import numpy
        import ta
        import rich
        import loguru
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    """Main launcher function"""
    print("🏔️ Alpine Bot Launcher")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("📦 Dependencies not found, attempting to install...")
        if not install_dependencies():
            print("\n❌ Failed to install dependencies")
            print("Please install manually:")
            print("  pip install ccxt pandas numpy ta rich loguru")
            sys.exit(1)
    
    # Import and run the bot
    try:
        print("\n🚀 Starting Alpine Bot...")
        from alpine_bot import main as alpine_main
        alpine_main()
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()