#!/usr/bin/env python3
"""
🌿 Alpine Trading Dashboard - Mint Green & Black Terminal Display
Optimized Trade Execution with Forced Bitget Connection
Real-time PnL, Account Stats, and Beautiful Visualizations
"""

import asyncio
import time
import threading
import ccxt
import ccxt.pro as ccxtpro
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt
import signal
import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add("alpine_trading.log", rotation="1 day", retention="7 days", level="INFO")
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

class BitgetConnection:
    """🔌 Forced Bitget Connection Manager with Auto-Retry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.exchange = None
        self.exchange_async = None
        self.connected = False
        self.last_ping = datetime.now()
        self.retry_count = 0
        self.max_retries = 10
        
    def force_connect(self) -> bool:
        """Force connection to Bitget with aggressive retry mechanism"""
        logger.info("🔌 Forcing Bitget connection...")
        
        while self.retry_count < self.max_retries:
            try:
                # Try synchronous connection first
                self.exchange = ccxt.bitget(self.config)
                self.exchange.load_markets()
                
                # Test authentication
                balance = self.exchange.fetch_balance()
                
                self.connected = True
                logger.success(f"✅ Bitget connected successfully! (Attempt {self.retry_count + 1})")
                return True
                
            except Exception as e:
                self.retry_count += 1
                logger.warning(f"⚠️ Connection attempt {self.retry_count} failed: {str(e)}")
                
                if self.retry_count < self.max_retries:
                    wait_time = min(2 ** self.retry_count, 30)  # Exponential backoff
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("❌ Max retries reached. Connection failed!")
                    return False
        
        return False
    
    def keep_alive(self):
        """Keep connection alive with periodic pings"""
        if self.connected and (datetime.now() - self.last_ping).seconds > 30:
            try:
                self.exchange.fetch_ticker('BTC/USDT:USDT')
                self.last_ping = datetime.now()
            except:
                self.connected = False
                self.force_connect()

class MintGreenDisplay:
    """🌿 Beautiful Mint Green & Black Terminal Display"""
    
    # Mint Green & Black Color Scheme
    COLORS = {
        'mint': '#00FFB3',          # Primary mint green
        'mint_bright': '#00FF7F',   # Bright mint
        'mint_dark': '#00CC8F',     # Dark mint
        'black': '#000000',         # Pure black
        'dark_gray': '#0D0D0D',     # Dark gray
        'gray': '#1A1A1A',          # Gray
        'white': '#FFFFFF',         # White text
        'green': '#00FF00',         # Profit green
        'red': '#FF0044',           # Loss red
        'yellow': '#FFD700',        # Warning yellow
        'blue': '#00BFFF',          # Info blue
        'purple': '#9D4EDD',        # Accent purple
    }
    
    def __init__(self):
        self.console = Console(width=140, height=50)
        self.animation_frame = 0
        
    def create_header(self, account_data: Dict) -> Panel:
        """Create beautiful header with account info"""
        balance = account_data.get('balance', 0)
        equity = account_data.get('equity', balance)
        free_margin = account_data.get('free_margin', balance)
        margin_level = account_data.get('margin_level', 100)
        
        header_text = Text()
        header_text.append("🌿 ", style=f"color({self.COLORS['mint']})")
        header_text.append("ALPINE TRADING SYSTEM", style=f"bold color({self.COLORS['mint']})")
        header_text.append(" | ", style=f"color({self.COLORS['gray']})")
        header_text.append("BITGET PERPETUAL", style=f"color({self.COLORS['white']})")
        header_text.append(" | ", style=f"color({self.COLORS['gray']})")
        header_text.append(f"v2.0", style=f"color({self.COLORS['mint_dark']})")
        
        account_info = Table(show_header=False, box=None, padding=0)
        account_info.add_column(style=f"color({self.COLORS['mint']})")
        account_info.add_column(style=f"bold color({self.COLORS['white']})")
        
        account_info.add_row("💰 Balance:", f"${balance:,.2f}")
        account_info.add_row("📊 Equity:", f"${equity:,.2f}")
        account_info.add_row("🎯 Free Margin:", f"${free_margin:,.2f}")
        account_info.add_row("⚡ Margin Level:", f"{margin_level:.1f}%")
        
        header_content = Columns([
            Align(header_text, align="left"),
            Align(account_info, align="right")
        ], expand=True)
        
        return Panel(
            header_content,
            box=box.DOUBLE,
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['black']}"
        )
    
    def create_pnl_panel(self, pnl_data: Dict) -> Panel:
        """Create PnL statistics panel"""
        table = Table(
            show_header=True,
            header_style=f"bold color({self.COLORS['mint']})",
            box=box.ROUNDED,
            border_style=f"color({self.COLORS['mint_dark']})"
        )
        
        table.add_column("Metric", style=f"color({self.COLORS['mint']})")
        table.add_column("Today", style=f"color({self.COLORS['white']})")
        table.add_column("Week", style=f"color({self.COLORS['white']})")
        table.add_column("Month", style=f"color({self.COLORS['white']})")
        table.add_column("All Time", style=f"color({self.COLORS['white']})")
        
        # Add PnL rows with color coding
        def format_pnl(value):
            color = self.COLORS['green'] if value >= 0 else self.COLORS['red']
            prefix = "+" if value >= 0 else ""
            return f"[color({color})]{prefix}${value:,.2f}[/color({color})]"
        
        table.add_row(
            "💵 PnL",
            format_pnl(pnl_data.get('daily_pnl', 0)),
            format_pnl(pnl_data.get('weekly_pnl', 0)),
            format_pnl(pnl_data.get('monthly_pnl', 0)),
            format_pnl(pnl_data.get('total_pnl', 0))
        )
        
        table.add_row(
            "📈 Win Rate",
            f"{pnl_data.get('daily_winrate', 0):.1f}%",
            f"{pnl_data.get('weekly_winrate', 0):.1f}%",
            f"{pnl_data.get('monthly_winrate', 0):.1f}%",
            f"{pnl_data.get('total_winrate', 0):.1f}%"
        )
        
        table.add_row(
            "🎯 Trades",
            str(pnl_data.get('daily_trades', 0)),
            str(pnl_data.get('weekly_trades', 0)),
            str(pnl_data.get('monthly_trades', 0)),
            str(pnl_data.get('total_trades', 0))
        )
        
        return Panel(
            table,
            title="[bold]📊 PERFORMANCE METRICS[/bold]",
            title_align="left",
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['dark_gray']}"
        )
    
    def create_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create active positions panel"""
        table = Table(
            show_header=True,
            header_style=f"bold color({self.COLORS['mint']})",
            box=box.SIMPLE,
            border_style=f"color({self.COLORS['mint_dark']})"
        )
        
        table.add_column("Symbol", style=f"color({self.COLORS['mint']})")
        table.add_column("Side", style=f"color({self.COLORS['white']})")
        table.add_column("Size", style=f"color({self.COLORS['white']})")
        table.add_column("Entry", style=f"color({self.COLORS['white']})")
        table.add_column("Current", style=f"color({self.COLORS['white']})")
        table.add_column("PnL", style=f"color({self.COLORS['white']})")
        table.add_column("PnL %", style=f"color({self.COLORS['white']})")
        table.add_column("Duration", style=f"color({self.COLORS['gray']})")
        
        if not positions:
            table.add_row("No active positions", "-", "-", "-", "-", "-", "-", "-")
        else:
            for pos in positions:
                pnl = pos.get('unrealized_pnl', 0)
                pnl_pct = pos.get('pnl_percentage', 0)
                
                # Color coding for PnL
                pnl_color = self.COLORS['green'] if pnl >= 0 else self.COLORS['red']
                side_color = self.COLORS['green'] if pos['side'] == 'long' else self.COLORS['red']
                
                table.add_row(
                    pos['symbol'].replace('/USDT:USDT', ''),
                    f"[color({side_color})]{pos['side'].upper()}[/color({side_color})]",
                    f"{pos['contracts']:.4f}",
                    f"${pos['entry_price']:.4f}",
                    f"${pos['current_price']:.4f}",
                    f"[color({pnl_color})]${pnl:.2f}[/color({pnl_color})]",
                    f"[color({pnl_color})]{pnl_pct:.2f}%[/color({pnl_color})]",
                    pos['duration']
                )
        
        return Panel(
            table,
            title="[bold]📈 ACTIVE POSITIONS[/bold]",
            title_align="left",
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['dark_gray']}"
        )
    
    def create_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create trading signals panel"""
        content = []
        
        if not signals:
            content.append(Text("⏳ Scanning for trading opportunities...", 
                              style=f"color({self.COLORS['gray']})"))
        else:
            for signal in signals[:8]:  # Show top 8 signals
                symbol = signal['symbol'].replace('/USDT:USDT', '')
                confidence = signal.get('confidence', 0)
                timeframe = signal.get('timeframe', '1m')
                
                # Confidence bar
                bar_length = int(confidence / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                
                # Signal color based on type
                signal_color = self.COLORS['green'] if signal['action'] == 'BUY' else self.COLORS['red']
                
                signal_text = Text()
                signal_text.append(f"{'🟢' if signal['action'] == 'BUY' else '🔴'} ", 
                                 style=f"color({signal_color})")
                signal_text.append(f"{symbol} ", style=f"bold color({self.COLORS['white']})")
                signal_text.append(f"[{timeframe}] ", style=f"color({self.COLORS['gray']})")
                signal_text.append(f"{signal['action']} ", style=f"bold color({signal_color})")
                signal_text.append(f"@ ${signal.get('price', 0):.4f} ", 
                                 style=f"color({self.COLORS['white']})")
                signal_text.append(f"[{bar}] ", style=f"color({self.COLORS['mint']})")
                signal_text.append(f"{confidence:.1f}%", style=f"color({self.COLORS['mint_bright']})")
                
                content.append(signal_text)
        
        signals_panel = Panel(
            Align("\n".join(str(c) for c in content), align="left"),
            title="[bold]🎯 TRADING SIGNALS[/bold]",
            title_align="left",
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['dark_gray']}"
        )
        
        return signals_panel
    
    def create_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create status bar with system info"""
        uptime = datetime.now() - last_update
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        status_text = Text()
        status_text.append("⚡ Status: ", style=f"color({self.COLORS['mint']})")
        status_text.append(status, style=f"bold color({self.COLORS['green']})")
        status_text.append(" | ", style=f"color({self.COLORS['gray']})")
        status_text.append("⏱️ Uptime: ", style=f"color({self.COLORS['mint']})")
        status_text.append(f"{hours}h {minutes}m", style=f"color({self.COLORS['white']})")
        status_text.append(" | ", style=f"color({self.COLORS['gray']})")
        status_text.append("🔄 Last Update: ", style=f"color({self.COLORS['mint']})")
        status_text.append(datetime.now().strftime("%H:%M:%S"), style=f"color({self.COLORS['white']})")
        
        return Panel(
            Align(status_text, align="center"),
            box=box.SIMPLE,
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['black']}"
        )
    
    def create_logs_panel(self, logs: List[str]) -> Panel:
        """Create activity logs panel"""
        log_content = []
        
        for log in logs[-10:]:  # Show last 10 logs
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Color code based on log type
            if "ERROR" in log or "❌" in log:
                style = f"color({self.COLORS['red']})"
            elif "SUCCESS" in log or "✅" in log:
                style = f"color({self.COLORS['green']})"
            elif "WARNING" in log or "⚠️" in log:
                style = f"color({self.COLORS['yellow']})"
            else:
                style = f"color({self.COLORS['white']})"
            
            log_text = Text()
            log_text.append(f"[{timestamp}] ", style=f"color({self.COLORS['gray']})")
            log_text.append(log, style=style)
            log_content.append(log_text)
        
        return Panel(
            Align("\n".join(str(l) for l in log_content), align="left"),
            title="[bold]📜 ACTIVITY LOG[/bold]",
            title_align="left",
            border_style=f"color({self.COLORS['mint']})",
            style=f"on {self.COLORS['dark_gray']}"
        )

class AlpineTradingDashboard:
    """🌿 Main Trading Dashboard with Optimized Execution"""
    
    def __init__(self):
        # Load configuration
        from config import get_exchange_config, TradingConfig
        self.config = TradingConfig()
        self.exchange_config = get_exchange_config()
        
        # Initialize components
        self.display = MintGreenDisplay()
        self.connection = BitgetConnection(self.exchange_config)
        
        # Trading state
        self.running = False
        self.account_data = {
            'balance': 0,
            'equity': 0,
            'free_margin': 0,
            'margin_level': 100
        }
        self.positions = []
        self.signals = []
        self.logs = []
        self.pnl_data = {
            'daily_pnl': 0,
            'weekly_pnl': 0,
            'monthly_pnl': 0,
            'total_pnl': 0,
            'daily_winrate': 0,
            'weekly_winrate': 0,
            'monthly_winrate': 0,
            'total_winrate': 0,
            'daily_trades': 0,
            'weekly_trades': 0,
            'monthly_trades': 0,
            'total_trades': 0
        }
        self.start_time = datetime.now()
        
        # Initialize strategies
        from strategy import VolumeAnomalyStrategy
        from volume_anom_bot import VolumeAnomalyBot
        self.strategy1 = VolumeAnomalyStrategy()
        self.strategy2 = None  # Will initialize volume anomaly bot
        
    def add_log(self, message: str):
        """Add log message"""
        self.logs.append(message)
        if len(self.logs) > 100:
            self.logs.pop(0)
        logger.info(message)
    
    def force_connection(self) -> bool:
        """Force Bitget connection"""
        self.add_log("🔌 Forcing Bitget connection...")
        
        if self.connection.force_connect():
            self.add_log("✅ Bitget connection established!")
            self.update_account_data()
            return True
        else:
            self.add_log("❌ Failed to connect to Bitget after multiple attempts!")
            return False
    
    def update_account_data(self):
        """Update account data from exchange"""
        try:
            if not self.connection.connected:
                return
                
            balance = self.connection.exchange.fetch_balance()
            usdt = balance.get('USDT', {})
            
            self.account_data = {
                'balance': usdt.get('total', 0),
                'equity': usdt.get('total', 0),  # Update with proper equity calculation
                'free_margin': usdt.get('free', 0),
                'margin_level': 100 if usdt.get('used', 0) == 0 else (usdt.get('total', 0) / usdt.get('used', 1)) * 100
            }
            
        except Exception as e:
            self.add_log(f"⚠️ Error updating account data: {str(e)}")
    
    def update_positions(self):
        """Update active positions"""
        try:
            if not self.connection.connected:
                return
                
            positions = self.connection.exchange.fetch_positions()
            self.positions = []
            
            for pos in positions:
                if pos['contracts'] > 0:
                    entry_time = datetime.fromtimestamp(pos['timestamp'] / 1000)
                    duration = datetime.now() - entry_time
                    
                    self.positions.append({
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'contracts': pos['contracts'],
                        'entry_price': pos['entryPrice'] or 0,
                        'current_price': pos['markPrice'] or 0,
                        'unrealized_pnl': pos['unrealizedPnl'] or 0,
                        'pnl_percentage': pos['percentage'] or 0,
                        'duration': f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
                    })
                    
        except Exception as e:
            self.add_log(f"⚠️ Error updating positions: {str(e)}")
    
    def scan_for_signals(self):
        """Scan for trading signals"""
        try:
            from config import TRADING_PAIRS
            
            self.signals = []
            
            for symbol in TRADING_PAIRS[:10]:  # Scan first 10 pairs
                try:
                    # Get market data
                    ticker = self.connection.exchange.fetch_ticker(symbol)
                    
                    # Simple momentum signal (for demo)
                    price_change = ticker.get('percentage', 0)
                    volume_ratio = ticker.get('quoteVolume', 0) / 1000000  # Volume in millions
                    
                    if abs(price_change) > 2 and volume_ratio > 10:
                        signal = {
                            'symbol': symbol,
                            'action': 'BUY' if price_change > 0 else 'SELL',
                            'price': ticker['last'],
                            'confidence': min(abs(price_change) * 10 + volume_ratio, 100),
                            'timeframe': '1m'
                        }
                        self.signals.append(signal)
                        
                except:
                    pass
            
            # Sort by confidence
            self.signals.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            self.add_log(f"⚠️ Error scanning signals: {str(e)}")
    
    def create_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", size=30),
            Layout(name="footer", size=15),
            Layout(name="status", size=3)
        )
        
        # Split main section
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Split left section
        layout["left"].split_column(
            Layout(name="pnl", size=10),
            Layout(name="positions", size=20)
        )
        
        # Split right section
        layout["right"].split_column(
            Layout(name="signals", size=20),
            Layout(name="logs", size=10)
        )
        
        # Update content
        layout["header"].update(self.display.create_header(self.account_data))
        layout["pnl"].update(self.display.create_pnl_panel(self.pnl_data))
        layout["positions"].update(self.display.create_positions_panel(self.positions))
        layout["signals"].update(self.display.create_signals_panel(self.signals))
        layout["logs"].update(self.display.create_logs_panel(self.logs))
        layout["status"].update(self.display.create_status_bar("TRADING ACTIVE", self.start_time))
        
        return layout
    
    def trading_loop(self):
        """Main trading loop"""
        self.running = True
        update_counter = 0
        
        while self.running:
            try:
                # Keep connection alive
                self.connection.keep_alive()
                
                # Update data every 2 seconds
                if update_counter % 2 == 0:
                    self.update_account_data()
                    self.update_positions()
                
                # Scan for signals every 5 seconds
                if update_counter % 5 == 0:
                    self.scan_for_signals()
                
                update_counter += 1
                time.sleep(1)
                
            except Exception as e:
                self.add_log(f"❌ Trading loop error: {str(e)}")
                time.sleep(5)
    
    def run(self):
        """Run the trading dashboard"""
        # Force connection
        if not self.force_connection():
            print("Failed to connect to Bitget. Please check your credentials.")
            return
        
        # Start trading thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            self.running = False
            self.display.console.print("\n[bold red]Shutting down Alpine Trading Dashboard...[/bold red]")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Main display loop
        with Live(self.create_layout(), console=self.display.console, refresh_per_second=2) as live:
            while self.running:
                live.update(self.create_layout())
                time.sleep(0.5)

def main():
    """Main entry point"""
    dashboard = AlpineTradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()