"""
🏔️ Alpine Trading Bot - Connection Test
Quick test to verify Bitget API connectivity and credentials
"""

import asyncio
import ccxt.pro as ccxt_async
import ccxt
from config import get_exchange_config

async def test_bitget_connection():
    """Test Bitget API connection step by step"""
    
    print("🏔️ Alpine Trading Bot - Connection Test")
    print("=" * 50)
    
    try:
        # Get configuration
        print("1️⃣ Loading configuration...")
        config = get_exchange_config()
        print(f"   ✅ Config keys: {list(config.keys())}")
        
        # Create exchange instance (async version)
        print("2️⃣ Creating Bitget exchange instance...")
        exchange = ccxt_async.bitget(config)
        print(f"   ✅ Exchange created: {exchange.id}")
        
        # Test basic connection
        print("3️⃣ Testing basic connection...")
        markets = await exchange.load_markets()
        print(f"   ✅ Markets loaded: {len(markets)} pairs available")
        
        # Test authentication
        print("4️⃣ Testing authentication...")
        balance = await exchange.fetch_balance()
        print(f"   ✅ Authentication successful!")
        
        # Show account info
        print("5️⃣ Account Information:")
        usdt_balance = balance.get('USDT', {})
        print(f"   💰 Total Balance: ${usdt_balance.get('total', 0):,.2f} USDT")
        print(f"   💰 Free Balance: ${usdt_balance.get('free', 0):,.2f} USDT")
        print(f"   💰 Used Balance: ${usdt_balance.get('used', 0):,.2f} USDT")
        
        # Test market data
        print("6️⃣ Testing market data...")
        ticker = await exchange.fetch_ticker('BTC/USDT:USDT')
        print(f"   📊 BTC/USDT Price: ${ticker['last']:,.2f}")
        
        print("\n✅ All tests passed! Alpine bot is ready to trade! 🚀")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error with async version: {e}")
        print("🔄 Trying synchronous version...")
        
        # Fallback to synchronous version
        try:
            exchange = ccxt.bitget(config)
            print(f"   ✅ Sync Exchange created: {exchange.id}")
            
            markets = exchange.load_markets()
            print(f"   ✅ Markets loaded: {len(markets)} pairs available")
            
            balance = exchange.fetch_balance()
            print(f"   ✅ Authentication successful!")
            
            usdt_balance = balance.get('USDT', {})
            print(f"   💰 Total Balance: ${usdt_balance.get('total', 0):,.2f} USDT")
            
            ticker = exchange.fetch_ticker('BTC/USDT:USDT')
            print(f"   📊 BTC/USDT Price: ${ticker['last']:,.2f}")
            
            print("\n✅ Synchronous connection successful! 🚀")
            return True
            
        except ccxt.AuthenticationError as e:
            print(f"\n❌ Authentication Error: {e}")
            print("🔧 Check your API credentials:")
            print("   - API Key is correct")
            print("   - Secret Key is correct") 
            print("   - Passphrase is correct")
            print("   - API permissions include trading")
            return False
            
        except ccxt.NetworkError as e:
            print(f"\n❌ Network Error: {e}")
            print("🌐 Check your internet connection")
            return False
            
        except ccxt.ExchangeError as e:
            print(f"\n❌ Exchange Error: {e}")
            print("🏦 Check Bitget API status and settings")
            return False
            
        except Exception as e:
            print(f"\n❌ Final Error: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    print("Starting Alpine connection test...\n")
    success = asyncio.run(test_bitget_connection())
    
    if success:
        print("\n🏔️ Ready to launch Alpine trading bot!")
    else:
        print("\n🛠️ Please fix the issues above before running the bot.")