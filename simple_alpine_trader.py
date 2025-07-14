#!/usr/bin/env python3
"""
🌿 Simple Alpine Trader - REAL TRADING VERSION
Executes actual trades on Bitget Futures
"""

import time
import threading
import ccxt
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from rich import box
import signal
import sys
import pandas as pd

# Import local modules
from config import get_exchange_config, TradingConfig, TRADING_PAIRS
from strategy import VolumeAnomalyStrategy

class SimpleAlpineTrader:
    def __init__(self):
        self.console = Console(width=120, height=40, force_terminal=True)
        self.config = TradingConfig()
        self.exchange_config = get_exchange_config()
        self.strategy = VolumeAnomalyStrategy()
        
        self.running = False
        self.exchange = None
        self.account_data = {'balance': 0.0, 'equity': 0.0, 'free_margin': 0.0}
        self.positions = []
        self.signals = []
        self.logs = []
        
        # Initialize exchange
        self.initialize_exchange()
        
    def initialize_exchange(self):
        """Initialize Bitget exchange connection"""
        try:
            # Unpack config properly for ccxt
            self.exchange = ccxt.bitget({
                'apiKey': self.exchange_config['apiKey'],
                'secret': self.exchange_config['secret'], 
                'password': self.exchange_config['password'],
                'sandbox': self.exchange_config.get('sandbox', False),
                'enableRateLimit': True,
                'options': self.exchange_config.get('options', {})
            })
            
            # Test connection with futures balance
            balance = self.exchange.fetch_balance({'type': 'swap'})
            usdt_info = balance.get('USDT', {})
            total_balance = float(usdt_info.get('total', 0) or 0)
            
            self.log(f"✅ Connected to Bitget - Futures Balance: ${total_balance:.2f}")
            return True
            
        except Exception as e:
            self.log(f"❌ Exchange connection failed: {str(e)}")
            return False
    
    def log(self, message: str):
        """Add log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        if len(self.logs) > 15:
            self.logs.pop(0)
        print(log_entry)  # Also print to console
    
    def update_account_data(self):
        """Update account data from futures balance"""
        try:
            if self.exchange:
                balance = self.exchange.fetch_balance({'type': 'swap'})
                usdt_info = balance.get('USDT', {})
                
                self.account_data = {
                    'balance': float(usdt_info.get('total', 0) or 0),
                    'equity': float(usdt_info.get('total', 0) or 0),
                    'free_margin': float(usdt_info.get('free', 0) or 0),
                }
        except Exception as e:
            self.log(f"❌ Account update error: {str(e)}")
    
    def update_positions(self):
        """Update positions from futures"""
        try:
            if self.exchange:
                positions = self.exchange.fetch_positions(None, {'type': 'swap'})
                self.positions = []
                
                for pos in positions:
                    contracts = pos.get('contracts', 0)
                    if contracts and float(contracts) > 0:
                        self.positions.append({
                            'symbol': pos['symbol'],
                            'side': pos['side'],
                            'size': float(contracts),
                            'entry': pos.get('entryPrice', 0),
                            'current': pos.get('markPrice', 0),
                            'pnl': pos.get('unrealizedPnl', 0),
                            'pnl_pct': pos.get('percentage', 0)
                        })
                        
        except Exception as e:
            self.log(f"❌ Positions update error: {str(e)}")
    
    def scan_and_execute(self):
        """Scan for signals and execute trades immediately"""
        try:
            if not self.exchange:
                return
                
            # Use the same trading pairs from config.py (first 5 for demo)
            pairs_to_scan = TRADING_PAIRS[:5]
            
            self.signals = []
            
            for symbol in pairs_to_scan:
                try:
                    # Get current ticker - CCXT format
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    
                    # Get 24h change
                    price_change_24h = ticker.get('percentage', 0) or 0
                    price_change_24h = float(price_change_24h)
                    
                    # Simple signal: if price is up > 2% in 24h, it's a buy signal
                    if price_change_24h > 2.0:
                        confidence = min(50.0 + price_change_24h * 10.0, 95.0)  # Scale confidence
                        
                        signal = {
                            'symbol': symbol.split('/')[0],  # Extract base symbol (e.g., DOGE from DOGE/USDT:USDT)
                            'action': 'BUY',
                            'price': current_price,
                            'confidence': confidence,
                            'timeframe': '1d',
                            'change_24h': price_change_24h
                        }
                        
                        self.signals.append(signal)
                        
                        # Execute if confidence > 80% and above 75% threshold [[memory:3208189]]
                        if confidence > 80:
                            self.execute_trade(symbol, 'BUY', current_price, confidence)
                    
                except Exception as e:
                    self.log(f"⚠️ Error scanning {symbol}: {str(e)}")
                    continue
            
            if self.signals:
                self.log(f"📊 Found {len(self.signals)} signals")
            
        except Exception as e:
            self.log(f"❌ Signal scan error: {str(e)}")
    
    def execute_trade(self, symbol, action, price, confidence):
        """Execute a simple trade"""
        try:
            if not self.exchange:
                self.log("❌ Exchange not connected")
                return False
                
            account_balance = self.account_data.get('balance', 0)
            
            if account_balance < 10:
                self.log(f"⚠️ Insufficient balance: ${account_balance:.2f}")
                return False
            
            # Use 2% of balance for trade (matching memory:3191609)
            position_value = account_balance * 0.02
            quantity = position_value / price
            
            # Round quantity appropriately for different price ranges
            if price > 100:
                quantity = round(quantity, 4)
            elif price > 1:
                quantity = round(quantity, 6)
            else:
                quantity = round(quantity, 0)
            
            if quantity <= 0:  # Minimum quantity check
                self.log(f"⚠️ Quantity too small: {quantity}")
                return False
            
            side = action.lower()
            
            self.log(f"🎯 EXECUTING: {side.upper()} {quantity} {symbol}")
            self.log(f"💰 Value: ${position_value:.2f} | Price: ${price:.4f}")
            self.log(f"📈 Confidence: {confidence:.1f}%")
            
            # Execute the trade with proper CCXT parameters for Bitget swap
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=quantity,
                params={
                    'type': 'swap',  # Use 'swap' instead of 'future' for CCXT Bitget
                    'timeInForce': 'IOC'  # Immediate or Cancel
                }
            )
            
            self.log(f"✅ TRADE EXECUTED! Order ID: {order['id']}")
            self.log(f"🚀 {side.upper()} {quantity} {symbol} @ ${price:.4f}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ Trade execution failed: {error_msg}")
            
            # Check for specific errors and provide solutions
            if "order validity period" in error_msg.lower():
                self.log("💡 Retrying with different order parameters...")
                # Retry with limit order close to market price
                try:
                    order_price = price * 1.001 if side == 'buy' else price * 0.999
                    order = self.exchange.create_limit_order(
                        symbol=symbol,
                        side=side,
                        amount=quantity,
                        price=order_price,
                        params={
                            'type': 'swap',
                            'timeInForce': 'IOC'
                        }
                    )
                    self.log(f"✅ LIMIT ORDER PLACED! Order ID: {order['id']}")
                    return True
                except Exception as retry_error:
                    self.log(f"❌ Retry failed: {str(retry_error)}")
            
            return False
    
    def create_display(self) -> Layout:
        """Create trading display"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="account", size=8),
            Layout(name="positions")
        )
        
        layout["right"].split_column(
            Layout(name="signals"),
            Layout(name="logs")
        )
        
        # Header
        header_text = Text("🚀 SIMPLE ALPINE TRADER | LIVE TRADING | AUTO-EXECUTION", style="bold green")
        balance_text = Text(f"💰 Balance: ${self.account_data['balance']:.2f}", style="cyan")
        
        header_table = Table.grid()
        header_table.add_column()
        header_table.add_column(justify="right")
        header_table.add_row(header_text, balance_text)
        
        layout["header"].update(Panel(header_table, box=box.DOUBLE, style="green"))
        
        # Account Panel
        account_table = Table(show_header=True, header_style="bold green")
        account_table.add_column("Account", style="cyan")
        account_table.add_column("Value", style="white")
        
        account_table.add_row("💰 Balance", f"${self.account_data['balance']:.2f}")
        account_table.add_row("📊 Equity", f"${self.account_data['equity']:.2f}")
        account_table.add_row("🎯 Free Margin", f"${self.account_data['free_margin']:.2f}")
        
        layout["account"].update(Panel(account_table, title="💰 ACCOUNT", border_style="green"))
        
        # Positions Panel
        if self.positions:
            pos_table = Table(show_header=True, header_style="bold green")
            pos_table.add_column("Symbol", style="cyan")
            pos_table.add_column("Side", style="white")
            pos_table.add_column("Size", style="white")
            pos_table.add_column("PnL", style="white")
            
            for pos in self.positions:
                pnl = pos['pnl']
                pnl_style = "green" if pnl >= 0 else "red"
                pnl_text = f"[{pnl_style}]${pnl:.2f}[/{pnl_style}]"
                
                pos_table.add_row(
                    pos['symbol'].replace('/USDT:USDT', ''),
                    pos['side'].upper(),
                    f"{pos['size']:.4f}",
                    pnl_text
                )
            
            layout["positions"].update(Panel(pos_table, title="📈 ACTIVE TRADES", border_style="green"))
        else:
            layout["positions"].update(Panel(Text("No active positions", style="yellow", justify="center"), 
                                           title="📈 ACTIVE TRADES", border_style="green"))
        
        # Signals Panel
        if self.signals:
            signals_text = Text()
            for signal in self.signals:
                action_color = "green" if signal['action'] == 'BUY' else "red"
                confidence = signal['confidence']
                change_24h = signal.get('change_24h', 0)
                
                signals_text.append(f"🟢 {signal['symbol']} ", style="white")
                signals_text.append(f"{signal['action']}", style=action_color)
                signals_text.append(f" @ ${signal['price']:.4f}\n", style="white")
                signals_text.append(f"📈 24h: +{change_24h:.1f}% | Confidence: {confidence:.1f}%\n", style="cyan")
                
                if confidence > 80:
                    signals_text.append("🚀 AUTO-EXECUTING!\n\n", style="bright_green")
                else:
                    signals_text.append("⏳ Monitoring...\n\n", style="yellow")
            
            layout["signals"].update(Panel(signals_text, title="🎯 LIVE SIGNALS", border_style="green"))
        else:
            layout["signals"].update(Panel(Text("Scanning markets...", style="yellow", justify="center"),
                                         title="🎯 LIVE SIGNALS", border_style="green"))
        
        # Logs Panel
        if self.logs:
            logs_text = Text()
            for log in self.logs[-6:]:
                logs_text.append(f"{log}\n", style="white")
            
            layout["logs"].update(Panel(logs_text, title="📜 TRADE LOG", border_style="green"))
        else:
            layout["logs"].update(Panel(Text("Starting...", style="yellow", justify="center"),
                                       title="📜 TRADE LOG", border_style="green"))
        
        # Footer
        status_text = Text(f"🔥 AUTO-TRADER ACTIVE | Scanning every 15s | Last: {datetime.now().strftime('%H:%M:%S')}", style="green")
        layout["footer"].update(Panel(status_text, box=box.SIMPLE, style="green"))
        
        return layout
    
    def trading_loop(self):
        """Main trading loop - LIVE TRADING"""
        counter = 0
        while self.running:
            try:
                # Update account data
                if counter % 5 == 0:
                    self.update_account_data()
                    
                # Update positions  
                if counter % 10 == 0:
                    self.update_positions()
                    
                # Scan and execute trades every 15 seconds
                if counter % 15 == 0:
                    self.log("🔍 Scanning markets for opportunities...")
                    self.scan_and_execute()
                
                counter += 1
                time.sleep(1)
                
            except Exception as e:
                self.log(f"❌ Trading error: {str(e)}")
                time.sleep(5)
    
    def run(self):
        """Run the live trader"""
        self.log("🚀 Starting Alpine Live Trader...")
        self.log("⚠️ WARNING: LIVE TRADING MODE - REAL MONEY!")
        self.running = True
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            self.log("⏹️ Shutdown signal received")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start trading thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        self.log("🔄 Live trading loop started")
        
        # Main display loop
        try:
            with Live(self.create_display(), console=self.console, refresh_per_second=1, screen=True) as live:
                self.log("✅ Alpine Live Trader ready!")
                
                while self.running:
                    live.update(self.create_display())
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.log("⏹️ Trader stopped by user")
            self.running = False
            
        except Exception as e:
            self.log(f"❌ Display error: {str(e)}")
            # Fallback mode
            while self.running:
                time.sleep(1)
        
        finally:
            self.log("👋 Alpine Live Trader stopped")

def main():
    print("🚨 WARNING: This is LIVE TRADING mode!")
    print("🚨 This bot will execute REAL trades with REAL money!")
    print("🚨 Press Ctrl+C at any time to stop")
    print()
    
    response = input("Type 'YES' to start live trading: ")
    if response.upper() != 'YES':
        print("❌ Live trading cancelled")
        return
    
    trader = SimpleAlpineTrader()
    trader.run()

if __name__ == "__main__":
    main() 