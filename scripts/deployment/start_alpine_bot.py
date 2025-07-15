#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Simple Startup Script
This script provides a reliable way to start the Alpine bot with proper error handling.
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'ccxt', 'pandas', 'numpy', 'ta', 'rich', 'loguru', 
        'watchdog', 'psutil', 'scipy'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"  ❌ {module} - MISSING")
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Installing missing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--break-system-packages', *missing_modules
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_files():
    """Check if all required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        'alpine_bot.py',
        'config.py', 
        'strategy.py',
        'risk_manager.py',
        'ui_display.py',
        'working_trading_system.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            missing_files.append(file)
            print(f"  ❌ {file} - MISSING")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_imports():
    """Test if all core modules can be imported"""
    print("\n🔍 Testing module imports...")
    
    try:
        from working_alpine_bot import WorkingAlpineBot
        print("  ✅ WorkingAlpineBot")
        
        from config import TradingConfig
        print("  ✅ TradingConfig")
        
        from strategy import VolumeAnomalyStrategy
        print("  ✅ VolumeAnomalyStrategy")
        
        from risk_manager import AlpineRiskManager
        print("  ✅ AlpineRiskManager")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def kill_existing_bots():
    """Kill any existing Alpine bot processes"""
    print("\n🔄 Checking for existing bot processes...")
    
    try:
        # Try to import psutil, install if not available
        try:
            import psutil
        except ImportError:
            print("  📦 Installing psutil for process management...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--break-system-packages', 'psutil'
            ])
            import psutil
        
        alpine_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(keyword in cmdline.lower() for keyword in ['alpine_bot', 'alpine', 'trading']):
                    if proc.info['pid'] != os.getpid():  # Don't kill ourselves
                        alpine_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if alpine_processes:
            print(f"  🛑 Found {len(alpine_processes)} existing bot processes")
            for proc in alpine_processes:
                try:
                    proc.terminate()
                    print(f"  ✅ Terminated process {proc.pid}")
                except:
                    try:
                        proc.kill()
                        print(f"  ✅ Killed process {proc.pid}")
                    except:
                        pass
            time.sleep(2)  # Give processes time to terminate
        else:
            print("  ✅ No existing bot processes found")
            
    except Exception as e:
        print(f"  ⚠️  Error checking processes: {e}")
        print("  ⚠️  Continuing without process cleanup...")

def display_config_info():
    """Display current configuration"""
    print("\n⚙️  Configuration:")
    
    try:
        from config import TradingConfig
        config = TradingConfig()
        
        print(f"  📊 Timeframes: {getattr(config, 'timeframes', ['3m'])}")
        print(f"  🎯 Min Signal Confidence: {getattr(config, 'min_signal_confidence', 60)}%")
        print(f"  💰 Position Size: {getattr(config, 'position_size_pct', 20)}%")
        print(f"  ⚡ Leverage: {getattr(config, 'leverage', 35)}x")
        print(f"  🛡️  Risk Per Trade: {getattr(config, 'risk_per_trade', 2)}%")
        print(f"  📏 Min Order Size: {getattr(config, 'min_order_size', 10)} USDT")
        
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")

def start_bot():
    """Start the Alpine bot"""
    print("\n🚀 Starting Alpine Trading Bot...")
    
    try:
        from working_alpine_bot import WorkingAlpineBot
        
        # Create and run the bot
        bot = WorkingAlpineBot()
        print("  ✅ Bot instance created")
        
        print("  🔄 Starting bot...")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    print("🏔️  ALPINE TRADING BOT STARTUP")
    print("=" * 50)
    
    # Change to the workspace root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.join(script_dir, '..', '..')
    workspace_root = os.path.abspath(workspace_root)
    
    print(f"📁 Changing to workspace directory: {workspace_root}")
    os.chdir(workspace_root)
    
    # Add workspace to Python path
    sys.path.insert(0, workspace_root)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Step 2: Check required files
    if not check_files():
        print("\n❌ Required files missing. Please ensure all files are present.")
        return False
    
    # Step 3: Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check for syntax errors.")
        return False
    
    # Step 4: Kill existing processes
    kill_existing_bots()
    
    # Step 5: Display configuration
    display_config_info()
    
    # Step 6: Start the bot
    print("\n" + "=" * 50)
    print("🎯 All checks passed! Starting bot...")
    print("=" * 50)
    
    return start_bot()

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Bot session completed successfully")
        else:
            print("\n❌ Bot session failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 