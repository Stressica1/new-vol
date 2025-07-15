#!/usr/bin/env python3
"""
🔍 Comprehensive Alpine Bot System Diagnosis
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print diagnostic header"""
    print("🔍 COMPREHENSIVE ALPINE BOT SYSTEM DIAGNOSIS")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("=" * 80)

def test_core_imports():
    """Test core system imports"""
    print("\n🧪 TESTING CORE IMPORTS")
    print("-" * 40)
    
    tests = [
        ("src.core.bot", "AlpineBot"),
        ("src.core.config", "TradingConfig"),
        ("src.exchange.bitget_client", "BitgetClient"),
        ("src.trading.trading_engine", "TradingEngine"),
        ("src.trading.risk_management_v1", "RiskManager"),
        ("src.ui.display", "AlpineDisplay"),
        ("config", "TradingConfig"),
        ("strategy", "VolumeAnomalyStrategy"),
        ("risk_manager", "AlpineRiskManager"),
    ]
    
    results = []
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Import Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate >= 80

def test_bot_initialization():
    """Test bot initialization"""
    print("\n🚀 TESTING BOT INITIALIZATION")
    print("-" * 40)
    
    try:
        from src.core.bot import AlpineBot
        from src.core.config import TradingConfig
        
        config = TradingConfig()
        bot = AlpineBot(config)
        
        print("  ✅ AlpineBot instance created")
        print(f"  ✅ Bot configuration: {type(bot.config).__name__}")
        print(f"  ✅ Bot status: {'Running' if bot.running else 'Stopped'}")
        
        # Test components
        components = [
            ('exchange_client', 'Exchange Client'),
            ('strategy', 'Strategy'),
            ('risk_manager', 'Risk Manager'),
            ('display', 'Display'),
            ('bot_manager', 'Bot Manager')
        ]
        
        for attr, name in components:
            if hasattr(bot, attr):
                component = getattr(bot, attr)
                print(f"  ✅ {name}: {type(component).__name__}")
            else:
                print(f"  ❌ {name}: Not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Bot initialization failed: {e}")
        return False

def test_display_system():
    """Test display system"""
    print("\n🎨 TESTING DISPLAY SYSTEM")
    print("-" * 40)
    
    try:
        from src.ui.display import AlpineDisplay
        
        display = AlpineDisplay()
        print("  ✅ AlpineDisplay instance created")
        
        # Test display methods
        methods = [
            'create_ultra_modern_header',
            'create_premium_account_panel',
            'create_performance_dashboard',
            'create_elite_positions_panel',
            'create_neural_signals_panel',
            'create_cyber_log_panel',
            'create_revolutionary_layout'
        ]
        
        for method in methods:
            if hasattr(display, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method}: Not found")
        
        # Test layout creation
        test_data = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 0.0,
            'free_margin': 10000.0
        }
        
        layout = display.create_revolutionary_layout(test_data, [], [], [], "TESTING")
        print("  ✅ Revolutionary layout created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Display system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exchange_connection():
    """Test exchange connection"""
    print("\n💱 TESTING EXCHANGE CONNECTION")
    print("-" * 40)
    
    try:
        from src.exchange.bitget_client import BitgetClient
        from config import get_exchange_config
        
        client = BitgetClient()
        print("  ✅ BitgetClient instance created")
        
        # Test connection
        if client.test_connection():
            print("  ✅ Exchange connection successful")
            return True
        else:
            print("  ❌ Exchange connection failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Exchange connection test failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("\n⚙️  TESTING CONFIGURATION")
    print("-" * 40)
    
    try:
        from config import TradingConfig, get_exchange_config, TRADING_PAIRS
        
        config = TradingConfig()
        exchange_config = get_exchange_config()
        
        print(f"  ✅ Trading pairs: {len(TRADING_PAIRS)}")
        print(f"  ✅ Max positions: {config.max_positions}")
        print(f"  ✅ Position size: {config.position_size_pct}%")
        print(f"  ✅ Leverage: {config.leverage}x")
        print(f"  ✅ Primary timeframe: {config.primary_timeframe}")
        
        # Check API credentials
        if config.API_KEY and config.API_SECRET and config.PASSPHRASE:
            print("  ✅ API credentials configured")
        else:
            print("  ❌ API credentials missing")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_legacy_systems():
    """Test legacy systems"""
    print("\n🏛️  TESTING LEGACY SYSTEMS")
    print("-" * 40)
    
    legacy_files = [
        'alpine_bot.py',
        'working_trading_system.py',
        'simple_alpine.py',
        'ui_display.py'
    ]
    
    working_systems = []
    
    for file in legacy_files:
        if os.path.exists(file):
            try:
                # Try to import the main class
                if file == 'alpine_bot.py':
                    from alpine_bot import AlpineBot as LegacyBot
                    print(f"  ✅ {file}: AlpineBot")
                    working_systems.append(file)
                elif file == 'working_trading_system.py':
                    from working_trading_system import AlpineTradingSystem
                    print(f"  ✅ {file}: AlpineTradingSystem")
                    working_systems.append(file)
                elif file == 'simple_alpine.py':
                    from simple_alpine import SimpleAlpineBot
                    print(f"  ✅ {file}: SimpleAlpineBot")
                    working_systems.append(file)
                elif file == 'ui_display.py':
                    from ui_display import AlpineDisplayV2
                    print(f"  ✅ {file}: AlpineDisplayV2")
                    working_systems.append(file)
                    
            except Exception as e:
                print(f"  ❌ {file}: {e}")
        else:
            print(f"  ❌ {file}: Not found")
    
    print(f"\n📊 Working legacy systems: {len(working_systems)}/{len(legacy_files)}")
    return len(working_systems) > 0

def generate_summary():
    """Generate diagnosis summary"""
    print("\n🎯 RUNNING COMPREHENSIVE DIAGNOSIS")
    print("=" * 80)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Bot Initialization", test_bot_initialization),
        ("Display System", test_display_system),
        ("Exchange Connection", test_exchange_connection),
        ("Configuration", test_configuration),
        ("Legacy Systems", test_legacy_systems),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📋 DIAGNOSIS SUMMARY")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = passed / total * 100
    
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 SYSTEM STATUS: HEALTHY")
        print("✅ Alpine Trading Bot is ready for operation!")
    elif success_rate >= 60:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print("🔧 Some components need fixing but core functionality works")
    else:
        print("❌ SYSTEM STATUS: CRITICAL")
        print("🚨 Major issues detected, system needs repair")
    
    return success_rate

def main():
    """Main diagnosis function"""
    print_header()
    success_rate = generate_summary()
    
    print("\n🔧 RECOMMENDATIONS:")
    if success_rate >= 80:
        print("  • System is ready for trading")
        print("  • Run: python main.py")
        print("  • Monitor with enhanced display")
    else:
        print("  • Fix failing components")
        print("  • Check import paths")
        print("  • Verify API credentials")
        print("  • Test individual modules")

if __name__ == "__main__":
    main()
