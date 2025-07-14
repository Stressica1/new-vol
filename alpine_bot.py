"""
🏔️ Alpine Trading Bot - Main Engine
Beautiful mint green terminal displays with immediate trading capabilities
Volume Anomaly Strategy with 90% success rate from PineScript
"""

import threading
import time
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Optional, Tuple
from rich.live import Live
from rich.console import Console

# Import our components
from config import TradingConfig, get_exchange_config, TRADING_PAIRS, BOT_NAME, VERSION
from ui_display import AlpineDisplay
from strategy import VolumeAnomalyStrategy
from risk_manager import AlpineRiskManager

class AlpineBot:
    """🏔️ Alpine Trading Bot - Volume Anomaly Master"""
    
    def __init__(self):
        self.console = Console()
        self.config = TradingConfig()
        
        # Initialize components
        self.display = AlpineDisplay()
        self.strategy = VolumeAnomalyStrategy()
        self.risk_manager = AlpineRiskManager()
        
        # Exchange connection
        self.exchange = None
        self.connected = False
        
        # Trading state
        self.running = False
        self.last_update = datetime.now()
        
        # Data storage
        self.market_data = {}
        self.account_data = {}
        self.positions = []
        self.activity_logs = []
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_signals = 0
        self.total_trades = 0
        
    def log_activity(self, message: str, level: str = "INFO"):
        """Add activity log with emoji and timestamp 📝"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji_map = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TRADE": "💰",
            "SIGNAL": "🎯"
        }
        
        emoji = emoji_map.get(level, "📝")
        log_entry = f"{timestamp} {emoji} {message}"
        self.activity_logs.append(log_entry)
        
        # Keep only last 100 logs
        if len(self.activity_logs) > 100:
            self.activity_logs = self.activity_logs[-100:]
    
    def initialize_exchange(self) -> bool:
        """Initialize Bitget exchange connection 🔌"""
        
        try:
            self.log_activity("🔌 Connecting to Bitget exchange...", "INFO")
            
            # Initialize exchange
            exchange_config = get_exchange_config()
            self.log_activity(f"🔧 Exchange config loaded: {list(exchange_config.keys())}", "INFO")
            
            self.exchange = ccxt.bitget(exchange_config)
            
            # Test connection
            self.log_activity("📡 Testing connection with load_markets()...", "INFO")
            self.exchange.load_markets()
            
            self.log_activity("💰 Fetching account balance...", "INFO")
            balance = self.exchange.fetch_balance()
            
            self.connected = True
            self.log_activity("✅ Successfully connected to Bitget!", "SUCCESS")
            self.log_activity(f"💰 Account balance loaded: ${balance.get('USDT', {}).get('total', 0):,.2f}", "INFO")
            
            return True
            
        except ccxt.AuthenticationError as e:
            self.log_activity(f"🔐 Authentication Error: {str(e)}", "ERROR")
            self.log_activity("❌ Check your API credentials (Key, Secret, Passphrase)", "ERROR")
            self.connected = False
            return False
            
        except ccxt.NetworkError as e:
            self.log_activity(f"🌐 Network Error: {str(e)}", "ERROR")
            self.log_activity("❌ Check your internet connection", "ERROR")
            self.connected = False
            return False
            
        except ccxt.ExchangeError as e:
            self.log_activity(f"🏦 Exchange Error: {str(e)}", "ERROR")
            self.log_activity("❌ Bitget API issue or invalid settings", "ERROR")
            self.connected = False
            return False
            
        except Exception as e:
            self.log_activity(f"❌ Unexpected error connecting to Bitget: {str(e)}", "ERROR")
            self.log_activity(f"🔍 Error type: {type(e).__name__}", "ERROR")
            import traceback
            self.log_activity(f"📋 Full traceback: {traceback.format_exc()}", "ERROR")
            self.connected = False
            return False
    
    def fetch_account_data(self):
        """Fetch account balance and positions 💰"""
        
        try:
            if not self.connected:
                return
            
            # Fetch balance
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {})
            
            self.account_data = {
                'balance': usdt_balance.get('total', 0),
                'equity': usdt_balance.get('total', 0),  # For futures, equity = total
                'margin': usdt_balance.get('used', 0),
                'free_margin': usdt_balance.get('free', 0)
            }
            
            # Initialize risk manager with current balance
            self.risk_manager.initialize_session(self.account_data['balance'])
            
            # Fetch positions
            positions = self.exchange.fetch_positions()
            self.positions = [pos for pos in positions if pos['contracts'] > 0]
            
            # Update risk manager positions
            for pos in self.positions:
                self.risk_manager.update_position(
                    pos['symbol'], 
                    pos['markPrice'], 
                    pos.get('unrealizedPnl', 0)
                )
            
        except Exception as e:
            self.log_activity(f"❌ Error fetching account data: {str(e)}", "ERROR")
    
    def fetch_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for analysis 📊"""
        
        try:
            if not self.connected:
                return None
            
            # Fetch candle data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Store in market data
            self.market_data[symbol] = df
            
            return df
            
        except Exception as e:
            self.log_activity(f"❌ Error fetching market data for {symbol}: {str(e)}", "ERROR")
            return None
    
    def analyze_signals(self):
        """Analyze all trading pairs for volume anomaly signals 🎯"""
        
        all_signals = []
        
        for symbol in TRADING_PAIRS:
            try:
                # Fetch fresh market data
                df = self.fetch_market_data(symbol)
                
                if df is None or len(df) < 50:
                    continue
                
                # Generate signals using our strategy
                signals = self.strategy.generate_signals(df, symbol)
                
                if signals:
                    self.total_signals += len(signals)
                    all_signals.extend(signals)
                    
                    for signal in signals:
                        self.log_activity(
                            f"🎯 {signal['type']} signal for {symbol.replace('/USDT:USDT', '')} "
                            f"| Vol: {signal['volume_ratio']:.1f}x | Conf: {signal['confidence']:.1f}%",
                            "SIGNAL"
                        )
                
            except Exception as e:
                self.log_activity(f"❌ Error analyzing {symbol}: {str(e)}", "ERROR")
        
        return all_signals
    
    def execute_trade(self, signal: Dict) -> bool:
        """Execute a trade based on signal 💰"""
        
        try:
            symbol = signal['symbol']
            signal_type = signal['type']
            current_price = signal['price']
            
            # Check if we can open position
            can_open, reason = self.risk_manager.can_open_position(signal, self.account_data['balance'])
            
            if not can_open:
                self.log_activity(f"🚫 Trade rejected: {reason}", "WARNING")
                return False
            
            # Calculate position size
            position_size, risk_info = self.risk_manager.calculate_position_size(
                signal, self.account_data['balance'], current_price
            )
            
            # Calculate stop loss and take profit
            risk_levels = self.risk_manager.calculate_stop_loss_take_profit(
                signal, current_price, position_size
            )
            
            # Determine order side
            side = 'buy' if signal_type == 'LONG' else 'sell'
            
            # Place market order
            order = self.exchange.create_market_order(
                symbol, side, position_size, current_price
            )
            
            if order and order.get('id'):
                # Create position record
                position = {
                    'symbol': symbol,
                    'side': signal_type.lower(),
                    'entry_price': current_price,
                    'position_size': position_size,
                    'position_value': risk_info['adjusted_value'],
                    'stop_loss': risk_levels['stop_loss'],
                    'take_profit': risk_levels['take_profit'],
                    'trailing_stop_distance': risk_levels.get('trailing_stop_distance'),
                    'order_id': order['id'],
                    'signal': signal
                }
                
                # Add to risk manager
                self.risk_manager.add_position(position)
                
                self.total_trades += 1
                self.log_activity(
                    f"💰 {signal_type} trade executed for {symbol.replace('/USDT:USDT', '')} "
                    f"| Size: {position_size:.4f} | Entry: ${current_price:.4f}",
                    "TRADE"
                )
                
                # Update display stats
                self.display.update_stats({'pnl': 0})  # Will be updated when closed
                
                return True
            
        except Exception as e:
            self.log_activity(f"❌ Trade execution failed: {str(e)}", "ERROR")
            return False
        
        return False
    
    def monitor_positions(self):
        """Monitor open positions for stop loss, take profit, and trailing stops 👀"""
        
        if not self.risk_manager.active_positions:
            return
        
        for position in self.risk_manager.active_positions[:]:  # Copy list to avoid modification during iteration
            try:
                symbol = position['symbol']
                side = position['side']
                
                # Fetch current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate unrealized P&L
                entry_price = position['entry_price']
                position_size = position['position_size']
                
                if side == 'long':
                    unrealized_pnl = (current_price - entry_price) * position_size
                else:
                    unrealized_pnl = (entry_price - current_price) * position_size
                
                # Update position
                self.risk_manager.update_position(symbol, current_price, unrealized_pnl)
                
                # Check exit conditions
                should_close = False
                close_reason = ""
                
                # Check stop loss
                if side == 'long' and current_price <= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop Loss"
                elif side == 'short' and current_price >= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop Loss"
                
                # Check take profit
                elif side == 'long' and current_price >= position['take_profit']:
                    should_close = True
                    close_reason = "Take Profit"
                elif side == 'short' and current_price <= position['take_profit']:
                    should_close = True
                    close_reason = "Take Profit"
                
                # Execute close if needed
                if should_close:
                    self.close_position(position, current_price, close_reason)
                
            except Exception as e:
                self.log_activity(f"❌ Error monitoring position {position.get('symbol', 'Unknown')}: {str(e)}", "ERROR")
    
    def close_position(self, position: Dict, close_price: float, reason: str):
        """Close a position 🔄"""
        
        try:
            symbol = position['symbol']
            side = 'sell' if position['side'] == 'long' else 'buy'
            size = position['position_size']
            
            # Place closing order
            order = self.exchange.create_market_order(symbol, side, size, close_price)
            
            if order and order.get('id'):
                # Calculate realized P&L
                entry_price = position['entry_price']
                if position['side'] == 'long':
                    realized_pnl = (close_price - entry_price) * size
                else:
                    realized_pnl = (entry_price - close_price) * size
                
                # Update risk manager
                closed_pos = self.risk_manager.close_position(symbol, close_price, realized_pnl, reason)
                
                if closed_pos:
                    pnl_emoji = "💚" if realized_pnl > 0 else "❤️"
                    self.log_activity(
                        f"{pnl_emoji} Position closed: {symbol.replace('/USDT:USDT', '')} "
                        f"| {reason} | P&L: ${realized_pnl:.2f}",
                        "TRADE"
                    )
                    
                    # Update display stats
                    self.display.update_stats({'pnl': realized_pnl})
                
        except Exception as e:
            self.log_activity(f"❌ Error closing position: {str(e)}", "ERROR")
    
    def trading_loop(self):
        """Main trading loop 🔄"""
        
        while self.running:
            try:
                # Fetch account data
                self.fetch_account_data()
                
                # Check risk limits
                self.risk_manager.check_risk_limits(self.account_data.get('balance', 0))
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Look for new signals if trading is allowed
                if not self.risk_manager.trading_halted:
                    signals = self.analyze_signals()
                    
                    # Execute trades on valid signals
                    for signal in signals:
                        if self.strategy.should_enter_trade(signal, self.account_data.get('balance', 0), self.positions):
                            self.execute_trade(signal)
                
                self.last_update = datetime.now()
                
                # Wait before next iteration
                time.sleep(self.config.refresh_rate)
                
            except Exception as e:
                self.log_activity(f"❌ Error in trading loop: {str(e)}", "ERROR")
                time.sleep(5)  # Wait longer on error
    
    def get_display_data(self) -> Dict:
        """Get data for terminal display 📊"""
        
        # Get recent signals
        recent_signals = self.strategy.get_recent_signals(10)
        
        # Get status
        if not self.connected:
            status = "❌ DISCONNECTED"
        elif self.risk_manager.trading_halted:
            status = "🛑 TRADING HALTED"
        elif self.running:
            status = "🟢 ACTIVE TRADING"
        else:
            status = "⏸️ PAUSED"
        
        return {
            'account_data': self.account_data,
            'positions': self.positions,
            'signals': recent_signals,
            'logs': self.activity_logs,
            'status': status
        }
    
    def run(self):
        """Start the Alpine bot 🚀"""
        
        # Initialize exchange
        if not self.initialize_exchange():
            self.console.print("❌ Failed to initialize exchange. Exiting...", style="red")
            return
        
        self.log_activity(f"🚀 {BOT_NAME} {VERSION} starting up!", "SUCCESS")
        self.log_activity("🎯 Volume Anomaly Strategy loaded with 90% success rate", "INFO")
        self.log_activity(f"💰 Risk Management: {self.config.max_daily_loss_pct}% daily loss limit", "INFO")
        self.log_activity(f"📊 Monitoring {len(TRADING_PAIRS)} trading pairs", "INFO")
        
        self.running = True
        
        # Start trading loop in background thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        
        try:
            # Run live display
            with Live(
                self.display.create_layout(**self.get_display_data()),
                refresh_per_second=1,
                screen=True
            ) as live:
                
                while self.running:
                    # Update display
                    display_data = self.get_display_data()
                    live.update(self.display.create_layout(**display_data))
                    
                    time.sleep(self.config.refresh_rate)
                    
        except KeyboardInterrupt:
            self.log_activity("⏹️ Shutdown signal received", "WARNING")
            self.running = False
            
        except Exception as e:
            self.log_activity(f"❌ Display error: {str(e)}", "ERROR")
            
        finally:
            self.log_activity("👋 Alpine bot shutdown complete", "INFO")

def main():
    """Main entry point 🏔️"""
    
    # Create and run Alpine bot
    bot = AlpineBot()
    bot.run()

if __name__ == "__main__":
    # Display startup banner
    console = Console()
    console.print("\n" + "="*60, style="bold cyan")
    console.print("🏔️  ALPINE TRADING BOT", style="bold green", justify="center")
    console.print("Volume Anomaly Strategy | 90% Success Rate", style="cyan", justify="center") 
    console.print("Beautiful Mint Green Terminal Interface", style="green", justify="center")
    console.print("="*60 + "\n", style="bold cyan")
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n👋 Alpine bot terminated by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Fatal error: {str(e)}", style="red")
        sys.exit(1)