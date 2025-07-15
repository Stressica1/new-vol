#!/usr/bin/env python3
"""
🏔️ Simple Alpine Trading Bot - Lightweight Version
"""

import sys
import os
import time
import threading
import ccxt
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from config import TradingConfig, get_exchange_config, TRADING_PAIRS
from strategy import VolumeAnomalyStrategy
from risk_manager import AlpineRiskManager
from bot_manager import AlpineBotManager

class SimpleAlpineBot:
    """Simple Alpine Trading Bot"""
    
    def __init__(self):
        self.console = Console(width=120, height=40)
        self.config = TradingConfig()
        self.exchange_config = get_exchange_config()
        self.strategy = VolumeAnomalyStrategy()
        self.risk_manager = AlpineRiskManager()
        self.bot_manager = AlpineBotManager()
        
        self.running = False
        self.exchange = None
        self.account_data = {'balance': 0.0, 'equity': 0.0, 'free_margin': 0.0}
        self.positions = []
        self.signals = []
        self.logs = []
        
        # Clean up existing processes
        self.bot_manager.kill_alpine_processes(exclude_current=True)
        
        # Initialize exchange
        self.initialize_exchange()
    
    def initialize_exchange(self):
        """Initialize Bitget exchange connection"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': self.exchange_config['apiKey'],
                'secret': self.exchange_config['secret'], 
                'password': self.exchange_config['password'],
                'sandbox': self.exchange_config.get('sandbox', False),
                'enableRateLimit': True,
                'options': self.exchange_config.get('options', {})
            })
            
            # Test connection
            balance = self.exchange.fetch_balance({'type': 'swap'})
            usdt_info = balance.get('USDT', {})
            total_balance = float(usdt_info.get('total', 0) or 0)
            
            self.log(f"✅ Connected to Bitget - Balance: ${total_balance:.2f}")
            self.account_data['balance'] = total_balance
            return True
            
        except Exception as e:
            self.log(f"❌ Exchange connection failed: {str(e)}")
            return False
    
    def log(self, message: str):
        """Add log message with timestamp"""
        log_entry = {
            'timestamp': datetime.now(),
            'message': message,
            'level': 'INFO'
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]
    
    def update_account_data(self):
        """Update account data"""
        try:
            if self.exchange:
                balance = self.exchange.fetch_balance({'type': 'swap'})
                usdt_info = balance.get('USDT', {})
                
                self.account_data.update({
                    'balance': float(usdt_info.get('total', 0) or 0),
                    'equity': float(usdt_info.get('total', 0) or 0),
                    'free_margin': float(usdt_info.get('free', 0) or 0)
                })
        except Exception as e:
            self.log(f"❌ Error updating account: {str(e)}")
    
    def create_display(self):
        """Create display layout"""
        # Header
        header = Panel(
            Align.center(Text("🏔️ SIMPLE ALPINE TRADING BOT", style="bold green")),
            style="green"
        )
        
        # Account info
        account_table = Table(show_header=False, expand=True)
        account_table.add_column("Label", style="bold")
        account_table.add_column("Value", justify="right")
        
        account_table.add_row("💰 Balance:", f"${self.account_data['balance']:.2f}")
        account_table.add_row("📊 Equity:", f"${self.account_data['equity']:.2f}")
        account_table.add_row("🆓 Free Margin:", f"${self.account_data['free_margin']:.2f}")
        account_table.add_row("🎯 Signals:", f"{len(self.signals)}")
        
        account_panel = Panel(account_table, title="Account", border_style="blue")
        
        # Recent signals
        signal_table = Table(show_header=True, expand=True)
        signal_table.add_column("Time", style="dim")
        signal_table.add_column("Symbol", style="bold")
        signal_table.add_column("Type", style="green")
        signal_table.add_column("Confidence", style="yellow")
        
        for signal in self.signals[-5:]:  # Show last 5 signals
            time_str = signal['timestamp'].strftime("%H:%M:%S")
            confidence_str = f"{signal['confidence']:.1f}%"
            signal_table.add_row(
                time_str,
                signal['symbol'].replace('/USDT:USDT', ''),
                signal['type'],
                confidence_str
            )
        
        if not self.signals:
            signal_table.add_row("--", "No signals yet", "--", "--")
        
        signal_panel = Panel(signal_table, title="Recent Signals", border_style="green")
        
        # Recent logs
        log_text = Text()
        for log in self.logs[-6:]:
            time_str = log['timestamp'].strftime("%H:%M:%S")
            log_text.append(f"[{time_str}] {log['message']}\n", style="cyan")
        
        log_panel = Panel(log_text, title="Activity Log", border_style="yellow")
        
        # Combine
        display = f"{header}\n\n{account_panel}\n\n{signal_panel}\n\n{log_panel}"
        return display
    
    def trading_loop(self):
        """Background trading loop"""
        while self.running:
            try:
                # Update account data
                self.update_account_data()
                
                # Scan for signals
                self.scan_for_signals()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.log(f"❌ Trading loop error: {str(e)}")
                time.sleep(5)
    
    def scan_for_signals(self):
        """Scan trading pairs for volume anomaly signals"""
        try:
            for pair in TRADING_PAIRS:
                try:
                    # Get market data
                    ohlcv = self.exchange.fetch_ohlcv(pair, '3m', limit=100)
                    
                    if len(ohlcv) < 20:
                        continue
                    
                    # Convert to DataFrame
                    import pandas as pd
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Generate signal
                    signal = self.strategy.analyze_symbol(pair, df)
                    
                    if signal and signal.get('confidence', 0) >= self.config.min_signal_confidence:
                        self.log(f"🎯 Signal: {pair} - {signal['type']} ({signal['confidence']:.1f}%)")
                        
                        # Add to signals list
                        self.signals.append({
                            'symbol': pair,
                            'type': signal['type'],
                            'confidence': signal['confidence'],
                            'price': signal.get('price', 0),
                            'timestamp': datetime.now()
                        })
                        
                        # Keep only last 10 signals
                        if len(self.signals) > 10:
                            self.signals = self.signals[-10:]
                    
                except Exception as e:
                    self.log(f"⚠️ Error scanning {pair}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.log(f"❌ Signal scan error: {str(e)}")
    
    def run(self):
        """Run the simple bot"""
        self.running = True
        self.log("🚀 Simple Alpine Bot started")
        
        # Start trading thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        
        try:
            # Use Rich Live for proper display
            with Live(self.create_display(), console=self.console, refresh_per_second=0.5) as live:
                while self.running:
                    live.update(self.create_display())
                    time.sleep(2)
                
        except KeyboardInterrupt:
            self.running = False
            self.log("⏹️ Bot stopped by user")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        finally:
            self.running = False

def main():
    """Main entry point"""
    try:
        bot = SimpleAlpineBot()
        bot.run()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
