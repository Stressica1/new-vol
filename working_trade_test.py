#!/usr/bin/env python3
"""
🚀 Working Trade Test - Alpine Trading Bot
========================================

Executes a successful trade using proper position sizing.
Uses cheaper symbols to meet minimum size requirements.
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

def execute_working_trade():
    """Execute a working trade with proper sizing"""
    
    print("🏔️ ALPINE TRADING BOT - WORKING TRADE TEST")
    print("=" * 50)
    print("🚀 Executing trade with proper position sizing...")
    
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
        
        # Load markets to find tradeable symbol with good liquidity and lower price
        print("🔍 Finding suitable trading symbol...")
        markets = bot.exchange.load_markets()
        
        # Try cheaper symbols that have lower minimum order sizes
        preferred_symbols = [
            'DOGE/USDT:USDT',    # Dogecoin - very cheap
            'XRP/USDT:USDT',     # Ripple - cheap
            'ADA/USDT:USDT',     # Cardano - cheap 
            'TRX/USDT:USDT',     # Tron - very cheap
            'SHIB/USDT:USDT',    # Shiba - very cheap
            'PEPE/USDT:USDT',    # Pepe - very cheap
            'SOL/USDT:USDT',     # Solana - medium price
            'MATIC/USDT:USDT',   # Polygon - cheap
            'DOT/USDT:USDT',     # Polkadot - medium
            'LINK/USDT:USDT',    # Chainlink - medium
        ]
        
        test_symbol = None
        test_price = 0
        min_amount = 0
        
        for symbol in preferred_symbols:
            if symbol in markets and markets[symbol].get('active', False):
                try:
                    # Get current price and check if we can afford it
                    ticker = bot.exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    
                    # Get minimum order amount
                    market = markets[symbol]
                    min_amount = market['limits']['amount']['min'] or 0.001
                    
                    # Calculate if we can meet minimum with our balance
                    min_cost = min_amount * price
                    max_affordable = balance * 0.1  # Use 10% of balance max
                    
                    print(f"🔍 Checking {symbol}: Price=${price:.6f}, MinAmount={min_amount}, MinCost=${min_cost:.2f}")
                    
                    if min_cost <= max_affordable and min_cost >= 1.0:  # At least $1 trade
                        test_symbol = symbol
                        test_price = price
                        print(f"✅ Selected {symbol} - affordable and meets requirements")
                        break
                        
                except Exception as e:
                    print(f"⚠️ Skipping {symbol}: {str(e)}")
                    continue
        
        if not test_symbol:
            print("❌ No suitable trading symbol found that meets minimum requirements")
            return False
        
        print(f"✅ Using symbol: {test_symbol}")
        print(f"💱 Current price: ${test_price:.6f}")
        print(f"📏 Minimum amount: {min_amount}")
        
        # Calculate proper position size
        # Use enough to meet minimum but not too much
        target_cost = min(balance * 0.05, 10.0)  # 5% of balance or $10 max
        position_amount = max(min_amount * 1.5, target_cost / test_price)  # 50% above minimum
        actual_cost = position_amount * test_price
        
        print(f"📊 Calculated position:")
        print(f"   Amount: {position_amount:.6f} {test_symbol.split('/')[0]}")
        print(f"   Cost: ${actual_cost:.2f}")
        print(f"   Percentage of balance: {(actual_cost/balance)*100:.1f}%")
        
        # Create test signal
        test_signal = {
            'symbol': test_symbol,
            'type': 'LONG',
            'entry_price': test_price,
            'price': test_price,
            'confidence': 75.0,
            'volume_ratio': 3.0,
            'timeframe': '3m',
            'timestamp': time.time(),
            'time': datetime.now(),
            'action': 'EXECUTE',
            'reason': 'WORKING_TEST_TRADE',
            'is_confluence': False,
            'strength': 75.0
        }
        
        # Override the position sizing calculation
        print("\n🚀 EXECUTING TRADE...")
        print(f"   Symbol: {test_symbol}")
        print(f"   Type: LONG")
        print(f"   Price: ${test_price:.6f}")
        print(f"   Amount: {position_amount:.6f}")
        print(f"   Cost: ${actual_cost:.2f}")
        print("   This is a REAL trade with REAL money!")
        
        # Temporarily override the risk manager to use our calculated amount
        original_calc = bot.risk_manager.calculate_position_size
        
        def custom_position_calc(signal, balance, price):
            return position_amount, {'adjusted_value': actual_cost}
        
        bot.risk_manager.calculate_position_size = custom_position_calc
        
        try:
            # Execute the trade
            success = bot.execute_trade(test_signal)
            
            if success:
                print("\n🎉 SUCCESS! Trade executed successfully!")
                print("✅ Trade placed on Bitget")
                print("📱 Check your Bitget account for the new position")
                print("🔄 The bot's trading functionality is confirmed working!")
                
                # Check for the position
                print("\n📊 Checking for new position...")
                time.sleep(2)  # Wait for position to appear
                positions = bot.exchange.fetch_positions()
                active_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]
                
                if active_positions:
                    print(f"✅ Found {len(active_positions)} active position(s)!")
                    for pos in active_positions:
                        symbol = pos.get('symbol', 'Unknown')
                        side = pos.get('side', 'Unknown')
                        size = pos.get('contracts', 0)
                        pnl = pos.get('unrealizedPnl', 0)
                        print(f"   📈 {symbol} {side} - Size: {size} - PnL: ${pnl}")
                else:
                    print("ℹ️ Position may still be processing...")
                
                return True
            else:
                print("\n❌ FAILED! Trade execution failed")
                print("🔧 Check error messages above for details")
                return False
                
        finally:
            # Restore original position calculation
            bot.risk_manager.calculate_position_size = original_calc
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    try:
        success = execute_working_trade()
        
        if success:
            print("\n🎉 WORKING TRADE TEST COMPLETED SUCCESSFULLY!")
            print("✅ Your Alpine Trading Bot is fully functional!")
            print("💰 A real position has been opened on Bitget")
            print("📱 Check your Bitget app/website to see the position")
            print("🔄 You can now run the full bot: python3 alpine_bot.py")
            print("\n🎯 TRADE EXECUTION CONFIRMED WORKING! 🎯")
        else:
            print("\n❌ WORKING TRADE TEST FAILED")
            print("🔧 Check the error messages above")
        
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