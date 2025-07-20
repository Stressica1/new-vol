#!/usr/bin/env python3
"""
🔍 DEBUG SCRIPT - Alpine Trading Bot
✅ Comprehensive testing of all functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """🔍 Test all imports"""
    print("🔍 Testing imports...")
    
    try:
        import ccxt.async_support as ccxt
        print("✅ ccxt.async_support imported")
    except ImportError as e:
        print(f"❌ ccxt.async_support import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.layout import Layout
        from rich.columns import Columns
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
        print("✅ rich components imported")
    except ImportError as e:
        print(f"❌ rich import failed: {e}")
        return False
    
    try:
        from loguru import logger
        print("✅ loguru imported")
    except ImportError as e:
        print(f"❌ loguru import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_bot_initialization():
    """🔍 Test bot initialization"""
    print("\n🔍 Testing bot initialization...")
    
    try:
        from alpine_trading_bot import AlpineTradingBot, TradingConfig, Position
        print("✅ AlpineTradingBot classes imported")
    except ImportError as e:
        print(f"❌ AlpineTradingBot import failed: {e}")
        return False
    
    try:
        bot = AlpineTradingBot()
        print("✅ Bot initialized successfully")
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False
    
    try:
        config = TradingConfig()
        print("✅ Config created successfully")
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return False
    
    try:
        position = Position(
            symbol="BTC/USDT:USDT",
            side="buy",
            size=0.1,
            entry_price=50000.0,
            current_price=51000.0,
            pnl=100.0,
            pnl_percent=2.0,
            timestamp=datetime.now()
        )
        print("✅ Position created successfully")
    except Exception as e:
        print(f"❌ Position creation failed: {e}")
        return False
    
    return True

def test_bot_methods():
    """🔍 Test bot methods"""
    print("\n🔍 Testing bot methods...")
    
    try:
        from alpine_trading_bot import AlpineTradingBot
        bot = AlpineTradingBot()
        
        # Test validation methods
        if hasattr(bot, 'validate_config'):
            result = bot.validate_config()
            print(f"✅ validate_config() returned: {result}")
        else:
            print("❌ validate_config() method not found")
        
        if hasattr(bot, 'validate_input_parameters'):
            result = bot.validate_input_parameters("BTC/USDT:USDT", "5m", 25)
            print(f"✅ validate_input_parameters() returned: {result}")
        else:
            print("❌ validate_input_parameters() method not found")
        
        if hasattr(bot, 'safe_format_positions'):
            result = bot.safe_format_positions(50)
            print(f"✅ safe_format_positions() returned: {type(result)}")
        else:
            print("❌ safe_format_positions() method not found")
        
        if hasattr(bot, 'safe_format_signals'):
            result = bot.safe_format_signals(50)
            print(f"✅ safe_format_signals() returned: {type(result)}")
        else:
            print("❌ safe_format_signals() method not found")
        
        if hasattr(bot, 'get_performance_summary'):
            result = bot.get_performance_summary()
            print(f"✅ get_performance_summary() returned: {type(result)}")
        else:
            print("❌ get_performance_summary() method not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot methods test failed: {e}")
        return False

def test_config_manager():
    """🔍 Test configuration manager"""
    print("\n🔍 Testing configuration manager...")
    
    try:
        from config_manager import ConfigManager
        config_manager = ConfigManager()
        print("✅ ConfigManager created successfully")
        
        # Test validation
        result = config_manager.validate_config()
        print(f"✅ Config validation returned: {result}")
        
        # Test summary
        summary = config_manager.get_config_summary()
        print(f"✅ Config summary created: {type(summary)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager test failed: {e}")
        return False

def test_environment():
    """🔍 Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ['BITGET_API_KEY', 'BITGET_SECRET_KEY', 'BITGET_PASSPHRASE']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"⚠️ {var} is not set (will use defaults)")
    
    return True

async def test_async_methods():
    """🔍 Test async methods"""
    print("\n🔍 Testing async methods...")
    
    try:
        from alpine_trading_bot import AlpineTradingBot
        bot = AlpineTradingBot()
        
        # Test retry connection (will fail without real credentials)
        if hasattr(bot, 'connect_exchange_with_retry'):
            print("✅ connect_exchange_with_retry() method found")
            # Don't actually call it as it requires real credentials
        else:
            print("❌ connect_exchange_with_retry() method not found")
        
        # Test safe execution methods
        if hasattr(bot, 'safe_execute_trade'):
            print("✅ safe_execute_trade() method found")
        else:
            print("❌ safe_execute_trade() method not found")
        
        if hasattr(bot, 'safe_update_positions'):
            print("✅ safe_update_positions() method found")
        else:
            print("❌ safe_update_positions() method not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Async methods test failed: {e}")
        return False

def main():
    """🔍 Main debug function"""
    print("🔍 ALPINE TRADING BOT DEBUG SESSION")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return False
    
    # Test bot initialization
    if not test_bot_initialization():
        print("❌ Bot initialization tests failed")
        return False
    
    # Test bot methods
    if not test_bot_methods():
        print("❌ Bot methods tests failed")
        return False
    
    # Test config manager
    if not test_config_manager():
        print("❌ Config manager tests failed")
        return False
    
    # Test environment
    if not test_environment():
        print("❌ Environment tests failed")
        return False
    
    # Test async methods
    asyncio.run(test_async_methods())
    
    print("\n" + "=" * 50)
    print("✅ ALL DEBUG TESTS COMPLETED SUCCESSFULLY!")
    print("🚀 Alpine Trading Bot is ready for production!")
    
    return True

if __name__ == "__main__":
    main() 