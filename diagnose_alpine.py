#!/usr/bin/env python3
"""
🔍 Alpine Bot Diagnostic Tool
Quick diagnosis of the Alpine trading bot system
"""

import sys
import os
import time
import subprocess
from datetime import datetime

def print_header():
    """Print diagnostic header"""
    print("🔍 ALPINE BOT DIAGNOSTIC TOOL")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("=" * 50)

def check_processes():
    """Check for running Alpine processes"""
    print("\n🔍 Checking Running Processes...")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        alpine_processes = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['alpine', 'trading', 'bot.py']):
                if 'grep' not in line.lower():
                    alpine_processes.append(line.strip())
        
        if alpine_processes:
            print(f"  ✅ Found {len(alpine_processes)} processes:")
            for proc in alpine_processes:
                print(f"    • {proc}")
        else:
            print("  ❌ No Alpine processes found")
            
    except Exception as e:
        print(f"  ❌ Error checking processes: {e}")

def check_files():
    """Check for required files"""
    print("\n📁 Checking Required Files...")
    
    required_files = [
        'working_trading_system.py',
        'config.py',
        'strategy.py',
        'risk_manager.py',
        'alpine_bot.py',
        'simple_alpine.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} - MISSING")

def check_logs():
    """Check log files"""
    print("\n📝 Checking Log Files...")
    
    log_dirs = ['logs', 'data/logs']
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            print(f"  📂 {log_dir}/")
            try:
                files = os.listdir(log_dir)
                log_files = [f for f in files if f.endswith('.log')]
                
                if log_files:
                    for log_file in log_files:
                        path = os.path.join(log_dir, log_file)
                        size = os.path.getsize(path)
                        mtime = datetime.fromtimestamp(os.path.getmtime(path))
                        print(f"    • {log_file} ({size} bytes, modified: {mtime.strftime('%H:%M:%S')})")
                else:
                    print("    ❌ No log files found")
                    
            except Exception as e:
                print(f"    ❌ Error reading directory: {e}")
        else:
            print(f"  ❌ {log_dir}/ - NOT FOUND")

def check_imports():
    """Check if core modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    
    modules_to_test = [
        ('working_trading_system', 'AlpineTradingSystem'),
        ('config', 'TradingConfig'),
        ('strategy', 'VolumeAnomalyStrategy'),
        ('risk_manager', 'AlpineRiskManager'),
        ('ccxt', None),
        ('pandas', None),
        ('numpy', None),
        ('rich', None)
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            if class_name:
                getattr(module, class_name)
                print(f"  ✅ {module_name}.{class_name}")
            else:
                print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} - ImportError: {e}")
        except AttributeError as e:
            print(f"  ❌ {module_name}.{class_name} - AttributeError: {e}")
        except Exception as e:
            print(f"  ❌ {module_name} - Error: {e}")

def check_config():
    """Check configuration"""
    print("\n⚙️  Checking Configuration...")
    
    try:
        from config import TradingConfig
        config = TradingConfig()
        
        print(f"  ✅ Trading pairs: {len(getattr(config, 'trading_pairs', []))}")
        print(f"  ✅ Timeframes: {getattr(config, 'timeframes', ['Unknown'])}")
        print(f"  ✅ Leverage: {getattr(config, 'leverage', 'Unknown')}")
        print(f"  ✅ Risk per trade: {getattr(config, 'risk_per_trade', 'Unknown')}%")
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")

def quick_test():
    """Quick functional test"""
    print("\n🧪 Quick Functional Test...")
    
    try:
        from working_trading_system import AlpineTradingSystem
        
        print("  🔄 Creating bot instance...")
        bot = AlpineTradingSystem()
        print("  ✅ Bot created successfully")
        
        # Test basic functionality
        if hasattr(bot, 'exchange'):
            print("  ✅ Exchange interface available")
        else:
            print("  ❌ No exchange interface")
            
        if hasattr(bot, 'strategy'):
            print("  ✅ Strategy available")
        else:
            print("  ❌ No strategy")
            
        print("  ✅ Quick test passed")
        
    except Exception as e:
        print(f"  ❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main diagnostic function"""
    print_header()
    check_processes()
    check_files()
    check_logs()
    check_imports()
    check_config()
    quick_test()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()
