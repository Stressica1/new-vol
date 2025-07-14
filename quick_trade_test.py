#!/usr/bin/env python3
"""
🚀 Quick Trade Test - Alpine Trading Bot
======================================

Immediately executes a small test trade to verify functionality.
Uses minimal position size for safety.
"""

import sys
import time
from datetime import datetime

try:
    from alpine_bot import AlpineBot
    from config import TradingConfig
    import ccxt
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def execute_quick_test_trade():
    """Execute a quick test trade"""
    
    print("🏔️ ALPINE TRADING BOT - QUICK TRADE TEST")
    print("=" * 50)
    print("🚀 Executing small test trade to verify functionality...")
    
    try:
        # Initialize bot
        print("🔧 Initializing bot...")
        bot = AlpineBot()
        
        # Connect to exchange
        print("🔌 Connecting to Bitget...")
        if not bot.initialize_exchange():
            print("❌ Failed to connect to exchange")
            return False
        
        # Get account data
        print("💰 Fetching account balance...")
        bot.fetch_account_data()
        balance = bot.account_data.get('balance', 0)
        print(f"💰 Available balance: ${balance:.2f}")
        
        if balance < 5:
            print("❌ Insufficient balance for test trade (need $5+)")
            return False
        
        # Load markets to find tradeable symbol
        print("🔍 Finding tradeable symbol...")
        markets = bot.exchange.load_markets()
        
        # Find BTC futures (most liquid)
        test_symbol = None
        for symbol in ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']:
            if symbol in markets and markets[symbol].get('active', False):
                test_symbol = symbol
                break
        
        if not test_symbol:
            print("❌ No suitable trading symbol found")
            return False
        
        print(f"✅ Using symbol: {test_symbol}")
        
        # Get current price
        print("📊 Getting current price...")
        ticker = bot.exchange.fetch_ticker(test_symbol)
        current_price = ticker['last']
        print(f"💱 Current price: ${current_price:.2f}")
        
        # Create minimal test signal
        test_signal = {
            'symbol': test_symbol,
            'type': 'LONG',
            'entry_price': current_price,
            'price': current_price,
            'confidence': 75.0,
            'volume_ratio': 3.0,
            'timeframe': '3m',
            'timestamp': time.time(),
            'time': datetime.now(),
            'action': 'EXECUTE',
            'reason': 'QUICK_TEST_TRADE',
            'is_confluence': False,
            'strength': 75.0
        }
        
        # Use very small position size for safety
        original_size = bot.config.position_size_pct
        bot.config.position_size_pct = 0.5  # Use only 0.5% of balance
        
        print("\n🚀 EXECUTING TEST TRADE...")
        print(f"   Symbol: {test_symbol}")
        print(f"   Type: LONG")
        print(f"   Price: ${current_price:.4f}")
        print(f"   Size: ~${balance * 0.005:.2f} (0.5% of balance)")
        print("   This is a REAL trade with REAL money!")
        
        try:
            # Execute the trade
            success = bot.execute_trade(test_signal)
            
            if success:
                print("\n🎉 SUCCESS! Test trade executed!")
                print("✅ Trade placed successfully")
                print("📱 Check your Bitget account for the new position")
                print("🔄 The bot's trading functionality is confirmed working!")
                
                # Show active positions
                print("\n📊 Checking positions...")
                bot.fetch_account_data()
                positions = bot.get_positions() if hasattr(bot, 'get_positions') else []
                if positions:
                    print(f"✅ Found {len(positions)} active position(s)")
                else:
                    print("ℹ️ Position may still be opening...")
                
                return True
            else:
                print("\n❌ FAILED! Test trade execution failed")
                print("🔧 Check error messages above for details")
                return False
                
        finally:
            # Restore original position size
            bot.config.position_size_pct = original_size
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    try:
        success = execute_quick_test_trade()
        
        if success:
            print("\n🎉 QUICK TRADE TEST COMPLETED SUCCESSFULLY!")
            print("✅ Your Alpine Trading Bot is working and can execute trades")
            print("💰 A small test position has been opened")
            print("📱 Check your Bitget account to see the position")
            print("🔄 You can now run the full bot: python3 alpine_bot.py")
        else:
            print("\n❌ QUICK TRADE TEST FAILED")
            print("🔧 Check the error messages above")
            print("💡 Common issues: insufficient balance, API permissions, network")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)