#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Simple Bitget Futures Test
Direct test of Bitget futures connection without complex imports
"""

import ccxt
import asyncio

def test_bitget_futures_simple():
    """Simple test of Bitget futures connection"""
    print("🏔️ Alpine Trading Bot - Simple Bitget Futures Test")
    print("=" * 55)
    
    # Direct configuration for Bitget futures
    config = {
        'apiKey': 'bg_5400882ef43c5596ffcf4af0c697b250',
        'secret': '60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45',
        'password': '22672267',
        'sandbox': False,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # This is key for futures trading
            'marginMode': 'cross'
        }
    }
    
    try:
        print("1️⃣ Creating Bitget futures exchange...")
        exchange = ccxt.bitget(config)
        print(f"   ✅ Exchange: {exchange.name}")
        print(f"   ✅ Default type: {exchange.options.get('defaultType', 'spot')}")
        
        print("\n2️⃣ Loading markets...")
        markets = exchange.load_markets()
        
        # Count different market types
        spot_markets = sum(1 for m in markets.values() if m.get('type') == 'spot')
        swap_markets = sum(1 for m in markets.values() if m.get('type') == 'swap')
        
        print(f"   ✅ Total markets: {len(markets)}")
        print(f"   ✅ Spot markets: {spot_markets}")
        print(f"   ✅ Futures/Swap markets: {swap_markets}")
        
        print("\n3️⃣ Testing futures market data...")
        # Test BTC futures
        btc_symbol = 'BTC/USDT:USDT'
        if btc_symbol in markets:
            print(f"   ✅ {btc_symbol} found in markets")
            
            # Get ticker
            ticker = exchange.fetch_ticker(btc_symbol)
            print(f"   📊 BTC futures price: ${ticker['last']:,.2f}")
            print(f"   📊 24h volume: ${ticker['quoteVolume']:,.0f}")
            print(f"   📊 24h change: {ticker['percentage']:.2f}%")
        else:
            print(f"   ❌ {btc_symbol} not found")
        
        print("\n4️⃣ Testing authentication...")
        try:
            balance = exchange.fetch_balance()
            print("   ✅ Authentication successful!")
            
            # Show balance
            usdt_balance = balance.get('USDT', {})
            print(f"   💰 USDT Balance: ${usdt_balance.get('total', 0):,.2f}")
            
            # Test positions
            print("\n5️⃣ Testing positions...")
            positions = exchange.fetch_positions()
            open_positions = [p for p in positions if p['size'] > 0]
            
            print(f"   📊 Total positions: {len(positions)}")
            print(f"   📊 Open positions: {len(open_positions)}")
            
            if open_positions:
                print("   📊 Open positions:")
                for pos in open_positions[:5]:
                    print(f"      {pos['symbol']}: Size {pos['size']} @ ${pos['markPrice']:,.2f}")
            
        except Exception as auth_error:
            print(f"   ❌ Authentication failed: {auth_error}")
            return False
        
        print("\n6️⃣ Testing some trading pairs from config...")
        test_pairs = [
            'BTC/USDT:USDT',
            'ETH/USDT:USDT', 
            'SOL/USDT:USDT',
            'DOGE/USDT:USDT',
            'ADA/USDT:USDT'
        ]
        
        working_pairs = []
        for pair in test_pairs:
            try:
                if pair in markets:
                    ticker = exchange.fetch_ticker(pair)
                    print(f"   ✅ {pair}: ${ticker['last']:,.4f}")
                    working_pairs.append(pair)
                else:
                    print(f"   ❌ {pair}: Not available")
            except Exception as e:
                print(f"   ❌ {pair}: Error - {e}")
        
        print(f"\n✅ Working pairs: {len(working_pairs)}")
        print("✅ Bitget futures connection is working!")
        
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("🔧 Check your API credentials:")
        print("   - API Key is correct")
        print("   - Secret Key is correct")
        print("   - Passphrase is correct")
        print("   - API has futures trading permissions")
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
    success = test_bitget_futures_simple()
    
    if success:
        print("\n🎉 SUCCESS! Bitget futures connection is working!")
        print("🚀 The trading system is ready for futures trading")
        print("\n📋 Configuration confirmed:")
        print("   ✅ Exchange: Bitget")
        print("   ✅ Market type: Futures/Swaps")
        print("   ✅ Default type: swap")
        print("   ✅ Authentication: Working")
        print("   ✅ Market data: Available")
        print("   ✅ Positions: Accessible")
        
        print("\n🚀 Ready to launch Alpine Trading Bot!")
    else:
        print("\n⚠️  Please fix the connection issues before proceeding")
        
    print("\n📋 Next steps:")
    print("   1. Run: python scripts/deployment/launch_alpine.py")
    print("   2. Choose option 2 to test connection")
    print("   3. Choose option 1 for full trading system")
