#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Enhanced Logging Test
Test script to verify the enhanced logging and traceback system
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_logging():
    """Test the enhanced logging system"""
    
    print("🧪 Testing Enhanced Logging System...")
    print("=" * 80)
    
    try:
        # Import enhanced logging
        from enhanced_logging import (
            alpine_logger, 
            EnhancedErrorHandler, 
            log_function_calls,
            log_startup_banner,
            log_shutdown
        )
        from loguru import logger
        
        # Test startup banner
        log_startup_banner()
        
        # Test basic logging
        logger.info("🔧 Testing basic logging functionality")
        logger.debug("🐛 Debug message test")
        logger.warning("⚠️ Warning message test")
        logger.error("❌ Error message test")
        logger.success("✅ Success message test")
        
        # Test configuration logging
        test_config = {
            'api_key': 'test_key_123',
            'api_secret': 'secret_password',
            'leverage': 35,
            'max_positions': 20,
            'position_size': 2.0
        }
        alpine_logger.log_config(test_config)
        
        # Test exception logging
        try:
            raise ValueError("This is a test exception")
        except Exception as e:
            alpine_logger.log_exception(e, "Exception Logging Test")
        
        # Test error handler context manager
        with EnhancedErrorHandler("Test Operation"):
            logger.info("🔄 Testing error handler context manager")
            time.sleep(0.1)
        
        # Test function decorator
        @log_function_calls
        def test_function(param1, param2="default"):
            logger.info(f"📝 Function called with {param1}, {param2}")
            return "test_result"
        
        result = test_function("test_param", param2="custom")
        
        # Test trading activity logging
        alpine_logger.log_trade_activity("BUY", "BTC/USDT", {
            "price": 43000.0,
            "size": 0.1,
            "timestamp": time.time()
        })
        
        # Test signal logging
        alpine_logger.log_signal({
            "symbol": "ETH/USDT",
            "signal": "SELL",
            "confidence": 0.75,
            "type": "VOLUME_ANOMALY"
        })
        
        # Test performance logging
        alpine_logger.log_performance({
            "total_trades": 10,
            "winning_trades": 7,
            "total_pnl": 250.0,
            "win_rate": 70.0
        })
        
        print("✅ Enhanced logging test completed successfully!")
        
        # Test shutdown
        log_shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_with_logging():
    """Test the main.py with enhanced logging"""
    
    print("\n🧪 Testing Main Entry Point with Enhanced Logging...")
    print("=" * 80)
    
    try:
        # Test import
        from main import main
        
        print("✅ Main module imported successfully")
        
        # Note: We won't actually run main() as it would start the bot
        # Instead, we'll test the logging setup
        
        return True
        
    except Exception as e:
        print(f"❌ Main module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_logging():
    """Test the bot components with enhanced logging"""
    
    print("\n🧪 Testing Bot Components with Enhanced Logging...")
    print("=" * 80)
    
    try:
        # Test bot import
        from src.core.bot import AlpineBot
        
        print("✅ AlpineBot imported successfully")
        
        # Test bot initialization (but don't run it)
        # bot = AlpineBot()
        # print("✅ AlpineBot initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🏔️ ALPINE TRADING BOT - ENHANCED LOGGING TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Enhanced Logging System", test_enhanced_logging),
        ("Main Entry Point", test_main_with_logging),
        ("Bot Components", test_bot_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running test: {test_name}")
        print("-" * 50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"🏆 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced logging is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
