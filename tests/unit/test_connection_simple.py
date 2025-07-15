#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Simple Connection Test
Quick test to verify Bitget API connectivity without complex imports
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

async def test_bitget_simple():
    """Simple Bitget API connection test"""
    
    print("🏔️ Alpine Trading Bot - Simple Connection Test")
    print("=" * 55)
    
    try:
        # Import only what we need
        import ccxt
        import ccxt.pro as ccxt_async
        
        # Try to import config
        try:
            from src.core.config import get_exchange_config
            print("1️⃣ Loading configuration from src.core.config...")
            config = get_exchange_config()
        except ImportError as e:
            print(f"❌ Config import error: {e}")
            print("🔧 Using manual configuration...")
            
            # Manual config as fallback
            config = {
                'apiKey': os.getenv('BITGET_API_KEY', 'bg_5400882ef43c5596ffcf4af0c697b250'),
                'secret': os.getenv('BITGET_SECRET', '60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45'),
                'password': os.getenv('BITGET_PASSPHRASE', '22672267'),
                'sandbox': False,
                'enableRateLimit': True,
            }
        
        print(f"   ✅ Config loaded with keys: {list(config.keys())}")
        
        # Create exchange instance
        print("2️⃣ Creating Bitget exchange instance...")
        exchange = ccxt.bitget(config)
        print(f"   ✅ Exchange created: {exchange.id}")
        
        # Test basic connection
        print("3️⃣ Testing basic connection...")
        try:
            markets = exchange.load_markets()
            print(f"   ✅ Markets loaded: {len(markets)} pairs available")
        except Exception as e:
            print(f"   ❌ Markets loading failed: {e}")
            return False
        
        # Test authentication
        print("4️⃣ Testing authentication...")
        try:
            balance = exchange.fetch_balance()
            print(f"   ✅ Authentication successful!")
            
            # Show account info
            print("5️⃣ Account Information:")
            usdt_balance = balance.get('USDT', {})
            print(f"   💰 Total Balance: ${usdt_balance.get('total', 0):,.2f} USDT")
            print(f"   💰 Free Balance: ${usdt_balance.get('free', 0):,.2f} USDT")
            print(f"   💰 Used Balance: ${usdt_balance.get('used', 0):,.2f} USDT")
            
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return False
        
        # Test market data
        print("6️⃣ Testing market data...")
        try:
            ticker = exchange.fetch_ticker('BTC/USDT:USDT')
            print(f"   📊 BTC/USDT Price: ${ticker['last']:,.2f}")
        except Exception as e:
            print(f"   ❌ Market data failed: {e}")
            return False
        
        print("\n✅ All tests passed! Alpine bot is ready to trade! 🚀")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Please install required packages:")
        print("   pip install ccxt pandas")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("Starting Alpine connection test...\n")
    
    # Run the async test
    try:
        success = asyncio.run(test_bitget_simple())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        success = False
    
    if success:
        print("\n🏔️ Ready to launch Alpine trading bot!")
        return 0
    else:
        print("\n🛠️ Please fix the issues above before running the bot.")
        return 1

if __name__ == "__main__":
    exit(main())
