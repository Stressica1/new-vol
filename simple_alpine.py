#!/usr/bin/env python3
"""
🌿 Simple Alpine Trading Bot - Stable Version
Real-time trading with futures balance and stable display
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

# Import local modules
from config import get_exchange_config, TradingConfig
from strategy import VolumeAnomalyStrategy
from bot_manager import AlpineBotManager

class SimpleAlpineBot:
    def __init__(self):
        self.console = Console(width=140, height=50, force_terminal=True)
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
        if len(self.logs) > 20:
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
    
    def scan_signals(self):
        """Real signal scanning using VolumeAnomalyStrategy"""
        try:
            if not self.exchange:
                return
                
            # Trading pairs to scan
            from config import TRADING_PAIRS
            pairs_to_scan = TRADING_PAIRS[:6]  # Scan top 6 pairs
            
            real_signals = []
            
            for symbol in pairs_to_scan:
                try:
                    # Fetch market data for 3m timeframe
                    ohlcv = self.exchange.fetch_ohlcv(symbol, '3m', limit=100)
                    
                    if len(ohlcv) < 50:  # Need enough data
                        continue
                        
                    # Convert to pandas DataFrame
                    import pandas as pd
                    df = pd.DataFrame(ohlcv)
                    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Generate signals using the Volume Anomaly Strategy
                    signals = []
                    try:
                        # Use the proper Volume Anomaly Strategy method
                        signals = self.strategy.generate_single_timeframe_signals(df, symbol, '3m')
                        
                        # Convert signal format if needed (from 'type' to 'action')
                        for signal in signals:
                            if 'type' in signal and 'action' not in signal:
                                signal['action'] = 'BUY' if signal['type'] == 'LONG' else 'SELL'
                                
                    except Exception as e:
                        self.log(f"⚠️ Volume Anomaly Strategy error for {symbol}: {str(e)}")
                        continue
                    
                    # Filter for high-confidence signals
                    for signal in signals:
                        if signal.get('confidence', 0) >= 75.0:  # 75% minimum confidence
                            
                            # Get current price
                            ticker = self.exchange.fetch_ticker(symbol)
                            current_price = ticker['last']
                            
                            real_signals.append({
                                'symbol': symbol.replace('/USDT:USDT', '').replace('/USDT', ''),
                                'action': signal['action'],
                                'price': current_price,
                                'confidence': signal['confidence'],
                                'timeframe': '3m',
                                'raw_signal': signal  # Keep original signal for execution
                            })
                            
                            # Execute trade if confidence is high enough
                            if signal['confidence'] >= 80.0:  # Execute at 80%+ confidence
                                self.execute_signal(signal, symbol, current_price)
                    
                except Exception as e:
                    self.log(f"⚠️ Error scanning {symbol}: {str(e)}")
                    continue
            
            # Update signals list
            self.signals = real_signals
            if real_signals:
                self.log(f"📊 Found {len(real_signals)} signals")
            
        except Exception as e:
            self.log(f"❌ Signal scan error: {str(e)}")
    
    def execute_signal(self, signal, symbol, current_price):
        """Execute a trading signal"""
        try:
            # Calculate position size (2% of account balance)
            account_balance = self.account_data.get('balance', 0)
            if account_balance < 10:  # Minimum $10 to trade
                self.log(f"⚠️ Insufficient balance for trading: ${account_balance:.2f}")
                return
                
            risk_amount = account_balance * 0.02  # 2% risk
            stop_loss_pct = 0.015  # 1.5% stop loss
            position_size = risk_amount / stop_loss_pct  # Position size based on risk
            
            # Minimum position size check
            if position_size < 5:  # Minimum $5 position
                position_size = 5
                
            # Get market info for minimum order size
            try:
                markets = self.exchange.load_markets()
                market = markets.get(symbol)
                if market:
                    min_cost = market.get('limits', {}).get('cost', {}).get('min', 5)
                    if position_size < min_cost:
                        position_size = min_cost
            except:
                pass
            
            # Calculate quantity
            quantity = position_size / current_price
            
            # Round to appropriate precision
            quantity = round(quantity, 6)
            
            side = 'buy' if signal['action'] == 'BUY' else 'sell'
            
            self.log(f"🎯 Executing {side.upper()} for {symbol}")
            self.log(f"💰 Position size: ${position_size:.2f} | Quantity: {quantity}")
            
            # Place market order
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=quantity,
                                            params={'type': 'swap'}  # Futures trading
            )
            
            self.log(f"✅ Order placed: {order['id']} | {side.upper()} {quantity} {symbol}")
            self.log(f"📈 Confidence: {signal['confidence']:.1f}% | Price: ${current_price:.4f}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Trade execution failed: {str(e)}")
            return False
    
    def create_display(self) -> Layout:
        """Create simple display layout"""
        layout = Layout()
        
        # Main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Body sections
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
        header_text = Text("🌿 SIMPLE ALPINE BOT | FUTURES TRADING | STABLE VERSION", style="bold green")
        balance_text = Text(f"💰 Balance: ${self.account_data['balance']:.2f} | Equity: ${self.account_data['equity']:.2f}", style="cyan")
        
        header_table = Table.grid()
        header_table.add_column()
        header_table.add_column(justify="right")
        header_table.add_row(header_text, balance_text)
        
        layout["header"].update(Panel(header_table, box=box.DOUBLE, style="green"))
        
        # Account Panel
        account_table = Table(show_header=True, header_style="bold green")
        account_table.add_column("Account Info", style="cyan")
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
            
            layout["positions"].update(Panel(pos_table, title="📈 POSITIONS", border_style="green"))
        else:
            layout["positions"].update(Panel(Text("No active positions", style="yellow", justify="center"), 
                                           title="📈 POSITIONS", border_style="green"))
        
        # Signals Panel
        if self.signals:
            signals_text = Text()
            for signal in self.signals:
                action_color = "green" if signal['action'] == 'BUY' else "red"
                signals_text.append(f"🟢 {signal['symbol']} [{signal['timeframe']}] ", style="white")
                signals_text.append(f"{signal['action']}", style=action_color)
                signals_text.append(f" @ ${signal['price']:.4f}\n", style="white")
                signals_text.append(f"Confidence: {signal['confidence']:.1f}%\n\n", style="cyan")
            
            layout["signals"].update(Panel(signals_text, title="🎯 SIGNALS", border_style="green"))
        else:
            layout["signals"].update(Panel(Text("Scanning for signals...", style="yellow", justify="center"),
                                         title="🎯 SIGNALS", border_style="green"))
        
        # Logs Panel
        if self.logs:
            logs_text = Text()
            for log in self.logs[-8:]:
                logs_text.append(f"{log}\n", style="white")
            
            layout["logs"].update(Panel(logs_text, title="📜 LOGS", border_style="green"))
        else:
            layout["logs"].update(Panel(Text("No logs yet", style="yellow", justify="center"),
                                       title="📜 LOGS", border_style="green"))
        
        # Footer
        status_text = Text(f"⚡ Status: Running | Last Update: {datetime.now().strftime('%H:%M:%S')}", style="green")
        layout["footer"].update(Panel(status_text, box=box.SIMPLE, style="green"))
        
        return layout
    
    def trading_loop(self):
        """Background trading loop with real signal scanning"""
        counter = 0
        while self.running:
            try:
                # Update data every few cycles
                if counter % 5 == 0:
                    self.update_account_data()
                    
                if counter % 8 == 0:
                    self.update_positions()
                    
                # Scan for signals more frequently (every 10 seconds)
                if counter % 10 == 0:
                    self.log("🔍 Scanning for trading signals...")
                    self.scan_signals()
                
                counter += 1
                time.sleep(1)
                
            except Exception as e:
                self.log(f"❌ Trading loop error: {str(e)}")
                time.sleep(5)
    
    def run(self):
        """Run the simple Alpine bot"""
        self.log("🚀 Starting Simple Alpine Bot...")
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
        self.log("🔄 Trading loop started")
        
        # Main display loop
        try:
            with Live(self.create_display(), console=self.console, refresh_per_second=1, screen=True) as live:
                self.log("✅ Display ready - Simple Alpine Bot running!")
                
                while self.running:
                    live.update(self.create_display())
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.log("⏹️ Keyboard interrupt received")
            self.running = False
            
        except Exception as e:
            self.log(f"❌ Display error: {str(e)}")
            # Fallback mode
            while self.running:
                time.sleep(1)
        
        finally:
            self.log("👋 Simple Alpine Bot shutdown complete")

def main():
    """Main entry point with process management"""
    try:
        # Kill all other Alpine bot processes first
        manager = AlpineBotManager()
        console = Console()
        
        console.print("🤖 [bold green]SIMPLE ALPINE BOT STARTING[/bold green]")
        manager.kill_alpine_processes(exclude_current=True)
        
        bot = SimpleAlpineBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Simple Alpine Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 