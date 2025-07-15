#!/usr/bin/env python3
"""
🚀 Force Test Trade - Alpine Trading Bot
=======================================

This script forces a small test trade to verify the trading execution works.
Uses a small position size for safety testing.
"""

import sys
import time
from datetime import datetime
from typing import Dict, Optional

try:
    from alpine_bot import AlpineBot
    from config import TradingConfig
    import ccxt
    from rich.console import Console
    from rich.panel import Panel
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TradeForcer:
    """Force a test trade execution"""
    
    def __init__(self):
        self.console = Console()
        self.bot = None
        
    def initialize_bot(self) -> bool:
        """Initialize the Alpine bot"""
        try:
            self.console.print("🏔️ Initializing Alpine Trading Bot...")
            self.bot = AlpineBot()
            
            # Initialize exchange connection
            if not self.bot.initialize_exchange():
                self.console.print("❌ Failed to connect to exchange")
                return False
                
            self.console.print("✅ Bot initialized and connected to Bitget")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Bot initialization failed: {str(e)}")
            return False
    
    def get_account_status(self) -> Dict:
        """Get current account status"""
        try:
            self.bot.fetch_account_data()
            return self.bot.account_data
        except Exception as e:
            self.console.print(f"❌ Failed to get account data: {str(e)}")
            return {}
    
    def find_tradeable_symbol(self) -> Optional[str]:
        """Find a symbol that exists on Bitget for trading"""
        try:
            self.console.print("🔍 Finding tradeable symbols on Bitget...")
            
            # Load markets
            markets = self.bot.exchange.load_markets()
            
            # Look for common symbols that should exist
            preferred_symbols = [
                'BTC/USDT:USDT',   # Bitcoin
                'ETH/USDT:USDT',   # Ethereum  
                'SOL/USDT:USDT',   # Solana
                'ADA/USDT:USDT',   # Cardano
                'DOT/USDT:USDT',   # Polkadot
                'MATIC/USDT:USDT', # Polygon
                'LINK/USDT:USDT',  # Chainlink
                'UNI/USDT:USDT',   # Uniswap
            ]
            
            for symbol in preferred_symbols:
                if symbol in markets:
                    market = markets[symbol]
                    if market.get('active', False) and market.get('type') == 'swap':
                        self.console.print(f"✅ Found tradeable symbol: {symbol}")
                        return symbol
            
            # If none of the preferred symbols work, find any active futures market
            for symbol, market in markets.items():
                if (market.get('active', False) and 
                    market.get('type') == 'swap' and 
                    'USDT' in symbol and 
                    symbol.endswith(':USDT')):
                    self.console.print(f"✅ Found alternative symbol: {symbol}")
                    return symbol
            
            return None
            
        except Exception as e:
            self.console.print(f"❌ Error finding tradeable symbol: {str(e)}")
            return None
    
    def create_test_signal(self, symbol: str) -> Dict:
        """Create a test signal for forced trade execution"""
        try:
            # Get current price
            ticker = self.bot.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Create a realistic test signal
            test_signal = {
                'symbol': symbol,
                'type': 'LONG',  # Long position
                'entry_price': current_price,
                'price': current_price,
                'confidence': 75.0,  # 75% confidence
                'volume_ratio': 3.0,  # 3x volume ratio
                'timeframe': '3m',
                'timestamp': time.time(),
                'time': datetime.now(),
                'action': 'EXECUTE',
                'reason': 'FORCED_TEST_TRADE',
                'is_confluence': False,
                'strength': 75.0
            }
            
            self.console.print(f"📊 Created test signal for {symbol} at ${current_price:.4f}")
            return test_signal
            
        except Exception as e:
            self.console.print(f"❌ Error creating test signal: {str(e)}")
            return {}
    
    def execute_forced_trade(self) -> bool:
        """Execute a forced test trade"""
        try:
            self.console.print(Panel.fit(
                "🚀 FORCING TEST TRADE EXECUTION\n"
                "This will place a small test trade to verify functionality",
                title="⚠️ TEST TRADE WARNING",
                border_style="yellow"
            ))
            
            # Confirm with user
            self.console.print("\n⚠️ This will place a REAL trade with REAL money!")
            self.console.print("💰 Position size will be minimized for safety")
            
            response = input("\nContinue with test trade? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                self.console.print("❌ Test trade cancelled by user")
                return False
            
            # Get account status
            account_data = self.get_account_status()
            if not account_data:
                self.console.print("❌ Cannot get account data")
                return False
                
            balance = account_data.get('balance', 0)
            self.console.print(f"💰 Current balance: ${balance:.2f}")
            
            if balance < 10:  # Need at least $10 for a test trade
                self.console.print("❌ Insufficient balance for test trade (need $10+)")
                return False
            
            # Find a tradeable symbol
            symbol = self.find_tradeable_symbol()
            if not symbol:
                self.console.print("❌ No tradeable symbols found")
                return False
            
            # Create test signal
            signal = self.create_test_signal(symbol)
            if not signal:
                self.console.print("❌ Failed to create test signal")
                return False
            
            # Override position size for safety - use minimum possible
            original_position_size_pct = self.bot.config.position_size_pct
            self.bot.config.position_size_pct = 1.0  # Use only 1% for test
            
            try:
                self.console.print("\n🚀 Executing test trade...")
                success = self.bot.execute_trade(signal)
                
                if success:
                    self.console.print(Panel.fit(
                        "✅ TEST TRADE EXECUTED SUCCESSFULLY!\n\n"
                        f"Symbol: {symbol}\n"
                        f"Type: {signal['type']}\n"
                        f"Price: ${signal['entry_price']:.4f}\n"
                        f"Size: ~{balance * 0.01:.2f} USDT (1% of balance)\n\n"
                        "Check your Bitget account to see the position!",
                        title="🎉 TRADE SUCCESS",
                        border_style="green"
                    ))
                    return True
                else:
                    self.console.print(Panel.fit(
                        "❌ TEST TRADE FAILED\n\n"
                        "Check the logs above for error details.\n"
                        "Common issues:\n"
                        "• Insufficient balance\n"
                        "• API permissions\n"
                        "• Market not available\n"
                        "• Position size too small",
                        title="❌ TRADE FAILED", 
                        border_style="red"
                    ))
                    return False
                    
            finally:
                # Restore original position size
                self.bot.config.position_size_pct = original_position_size_pct
                
        except Exception as e:
            self.console.print(f"❌ Trade execution error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_forced_trade_test(self):
        """Run the complete forced trade test"""
        self.console.print("🏔️ ALPINE TRADING BOT - FORCED TRADE TEST")
        self.console.print("=" * 50)
        
        try:
            # Initialize bot
            if not self.initialize_bot():
                return False
            
            # Execute forced trade
            success = self.execute_forced_trade()
            
            if success:
                self.console.print("\n🎉 Forced trade test completed successfully!")
                self.console.print("📱 Check your Bitget account to see the new position")
                self.console.print("🔄 You can now run the regular bot to continue trading")
            else:
                self.console.print("\n❌ Forced trade test failed")
                self.console.print("🔧 Check the error messages above for troubleshooting")
            
            return success
            
        except KeyboardInterrupt:
            self.console.print("\n⏹️ Test interrupted by user")
            return False
        except Exception as e:
            self.console.print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main execution"""
    forcer = TradeForcer()
    
    try:
        success = forcer.run_forced_trade_test()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()