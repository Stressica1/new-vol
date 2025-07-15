#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Bitget Futures Connection Test
Specifically test Bitget futures/swaps connection
"""

import os
import sys
import asyncio
import ccxt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_bitget_futures():
    """Test Bitget futures connection"""
    print("🏔️ Alpine Trading Bot - Bitget Futures Connection Test")
    print("=" * 60)
    
    try:
        # Import config from new structure
        from src.core.config import get_exchange_config
        
        print("1️⃣ Loading Bitget futures configuration...")
        config = get_exchange_config()
        
        # Display configuration info (without sensitive data)
        print(f"   ✅ API Key: {config['apiKey'][:10]}...")
        print(f"   ✅ Default Type: {config['options']['defaultType']}")
        print(f"   ✅ Margin Mode: {config['options']['marginMode']}")
        print(f"   ✅ Sandbox Mode: {config['sandbox']}")
        
        # Create Bitget exchange instance
        print("\n2️⃣ Creating Bitget exchange instance...")
        exchange = ccxt.bitget(config)
        print(f"   ✅ Exchange: {exchange.name}")
        print(f"   ✅ ID: {exchange.id}")
        
        # Load markets
        print("\n3️⃣ Loading futures markets...")
        markets = exchange.load_markets()
        
        # Filter for futures markets
        futures_markets = {k: v for k, v in markets.items() if v.get('type') == 'swap'}
        print(f"   ✅ Total markets: {len(markets)}")
        print(f"   ✅ Futures markets: {len(futures_markets)}")
        
        # Test some common futures pairs
        print("\n4️⃣ Testing common futures pairs...")
        test_pairs = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
        
        for pair in test_pairs:
            if pair in futures_markets:
                print(f"   ✅ {pair} - Available")
            else:
                print(f"   ❌ {pair} - Not found")
        
        # Test authentication
        print("\n5️⃣ Testing authentication...")
        try:
            balance = exchange.fetch_balance()
            print("   ✅ Authentication successful!")
            
            # Show USDT balance
            usdt_balance = balance.get('USDT', {})
            total = usdt_balance.get('total', 0)
            free = usdt_balance.get('free', 0)
            used = usdt_balance.get('used', 0)
            
            print(f"   💰 USDT Balance:")
            print(f"      Total: ${total:,.2f}")
            print(f"      Free: ${free:,.2f}")
            print(f"      Used: ${used:,.2f}")
            
        except Exception as auth_error:
            print(f"   ❌ Authentication failed: {auth_error}")
            return False
        
        # Test fetching ticker for a futures pair
        print("\n6️⃣ Testing market data...")
        try:
            ticker = exchange.fetch_ticker('BTC/USDT:USDT')
            print(f"   📊 BTC/USDT:USDT Price: ${ticker['last']:,.2f}")
            print(f"   📊 24h Volume: ${ticker['quoteVolume']:,.0f}")
            print(f"   📊 24h Change: {ticker['percentage']:.2f}%")
            
        except Exception as ticker_error:
            print(f"   ❌ Ticker fetch failed: {ticker_error}")
        
        # Test position fetching
        print("\n7️⃣ Testing positions...")
        try:
            positions = exchange.fetch_positions()
            open_positions = [p for p in positions if p['size'] > 0]
            
            print(f"   📊 Total positions: {len(positions)}")
            print(f"   📊 Open positions: {len(open_positions)}")
            
            if open_positions:
                print("   📊 Open positions:")
                for pos in open_positions[:5]:  # Show first 5
                    print(f"      {pos['symbol']}: {pos['size']} @ ${pos['markPrice']:,.2f}")
            
        except Exception as pos_error:
            print(f"   ❌ Positions fetch failed: {pos_error}")
        
        print("\n✅ Bitget futures connection test completed successfully! 🚀")
        print("✅ Ready for futures trading!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure the project structure is correct")
        return False
        
    except ccxt.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("🔧 Check your API credentials:")
        print("   - API Key")
        print("   - Secret Key") 
        print("   - Passphrase")
        print("   - API permissions include futures trading")
        return False
        
    except ccxt.NetworkError as e:
        print(f"❌ Network Error: {e}")
        print("🌐 Check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_bitget_futures()
    
    if success:
        print("\n🎉 Bitget futures connection is working perfectly!")
        print("🚀 You can now run the full trading system")
    else:
        print("\n⚠️  Please fix the connection issues before proceeding")
        
    print("\n📋 Next steps:")
    print("   1. Run: python scripts/deployment/launch_alpine.py")
    print("   2. Choose option 1 for full trading system")
    print("   3. Monitor the beautiful terminal interface")
