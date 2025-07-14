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
        """Force connection with exponential backoff retry"""
        logger.info("🔌 Forcing Bitget connection...")
        
        for attempt in range(self.max_retries):
            try:
                # Create sync exchange
                self.exchange = ccxt.bitget({
                    'apiKey': self.config['apiKey'],
                    'secret': self.config['secret'],
                    'password': self.config['password'],
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                
                # Test connection
                balance = self.exchange.fetch_balance()
                self.connected = True
                self.retry_count = 0
                logger.info("✅ Bitget connection established!")
                return True
                
            except Exception as e:
                self.retry_count = attempt + 1
                wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                logger.warning(f"❌ Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        logger.error("❌ Failed to connect to Bitget after maximum retries")
        return False
    
    def keep_alive(self):
        """Keep connection alive with periodic pings"""
        now = datetime.now()
        if (now - self.last_ping).seconds > 30:  # Ping every 30 seconds
            try:
                if self.exchange:
                    self.exchange.fetch_balance()
                self.last_ping = now
            except Exception as e:
                logger.warning(f"❌ Keep alive failed: {str(e)}")
                self.connected = False

class MintGreenDisplay:
    """🌿 Beautiful Mint Green & Black Terminal Display"""
    
    # Mint Green & Black Color Scheme
    COLORS = {
        'primary': 'bright_green',
        'secondary': 'green',
        'accent': 'cyan',
        'background': 'black',
        'text': 'white',
        'success': 'bright_green',
        'warning': 'yellow',
        'danger': 'red',
        'profit': 'bright_green',
        'loss': 'bright_red'
    }
    
    def __init__(self):
        self.console = Console(width=140, height=50, force_terminal=True)
        self.last_layout = None
        self.last_update = datetime.now()
        self.update_throttle = 0.5  # Minimum time between layout updates
        
    def create_header(self, account_data: Dict) -> Panel:
        """Create dashboard header"""
        balance = account_data.get('balance', 0)
        equity = account_data.get('equity', 0)
        free_margin = account_data.get('free_margin', 0)
        
        header_text = Text()
        header_text.append("🌿 ALPINE TRADING SYSTEM | BITGET PERPETUAL | v2.0", style="bold bright_green")
        
        balance_info = Text()
        balance_info.append(f"💰 Balance:     ${balance:.2f}", style="bright_green")
        balance_info.append("  ")
        balance_info.append(f"📊 Equity:      ${equity:.2f}", style="bright_cyan")
        balance_info.append("  ")
        balance_info.append(f"🎯 Free Margin: ${free_margin:.2f}", style="bright_yellow")
        
        # Create table for header
        table = Table.grid(padding=1)
        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_row(header_text, balance_info)
        
        return Panel(
            table,
            box=box.DOUBLE,
            style="bright_green",
            border_style="bright_green"
        )
    
    def create_pnl_panel(self, pnl_data: Dict) -> Panel:
        """Create PnL performance panel"""
        table = Table(show_header=True, header_style="bold bright_green", box=box.SIMPLE)
        table.add_column("Metric", style="bright_cyan", width=12)
        table.add_column("Today", justify="center", width=8)
        table.add_column("Week", justify="center", width=8)
        table.add_column("Month", justify="center", width=8)
        table.add_column("All Time", justify="center", width=10)
        
        def format_pnl(value):
            if value > 0:
                return f"[bright_green]+${value:.2f}[/bright_green]"
            elif value < 0:
                return f"[bright_red]-${abs(value):.2f}[/bright_red]"
            else:
                return f"[white]+${value:.2f}[/white]"
        
        def format_percentage(value):
            if value > 0:
                return f"[bright_green]{value:.1f}%[/bright_green]"
            elif value < 0:
                return f"[bright_red]{value:.1f}%[/bright_red]"
            else:
                return f"[white]{value:.1f}%[/white]"
        
        # PnL row
        table.add_row(
            "💵 PnL",
            format_pnl(pnl_data.get('daily_pnl', 0)),
            format_pnl(pnl_data.get('weekly_pnl', 0)),
            format_pnl(pnl_data.get('monthly_pnl', 0)),
            format_pnl(pnl_data.get('total_pnl', 0))
        )
        
        # Win Rate row
        table.add_row(
            "📈 Win Rate",
            format_percentage(pnl_data.get('daily_winrate', 0)),
            format_percentage(pnl_data.get('weekly_winrate', 0)),
            format_percentage(pnl_data.get('monthly_winrate', 0)),
            format_percentage(pnl_data.get('total_winrate', 0))
        )
        
        # Trades row
        table.add_row(
            "🎯 Trades",
            str(pnl_data.get('daily_trades', 0)),
            str(pnl_data.get('weekly_trades', 0)),
            str(pnl_data.get('monthly_trades', 0)),
            str(pnl_data.get('total_trades', 0))
        )
        
        return Panel(
            table,
            title="📊 PERFORMANCE METRICS",
            title_align="left",
            border_style="bright_green",
            padding=(1, 1)
        )
    
    def create_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create active positions panel"""
        if not positions:
            content = Text("No active positions", style="bright_yellow", justify="center")
            content.append("\n\n")
            content.append("  Symbol                Side   Size   Entry   Current   PnL   PnL %   Duration            ")
            content.append("\n  ──────────────────────────────────────────────────────────────────────────────           ")
            content.append("\n  No active positions   -      -      -       -         -     -       -                   ")
            
            return Panel(
                content,
                title="📈 ACTIVE POSITIONS",
                title_align="left",
                border_style="bright_green",
                padding=(1, 1)
            )
        
        table = Table(show_header=True, header_style="bold bright_green", box=box.SIMPLE)
        table.add_column("Symbol", style="bright_cyan", width=15)
        table.add_column("Side", justify="center", width=6)
        table.add_column("Size", justify="right", width=8)
        table.add_column("Entry", justify="right", width=8)
        table.add_column("Current", justify="right", width=8)
        table.add_column("PnL", justify="right", width=8)
        table.add_column("PnL %", justify="right", width=8)
        table.add_column("Duration", justify="center", width=12)
        
        for position in positions:
            side_style = "bright_green" if position['side'] == 'long' else "bright_red"
            pnl = position.get('unrealized_pnl', 0)
            pnl_pct = position.get('percentage', 0)
            
            pnl_style = "bright_green" if pnl >= 0 else "bright_red"
            pnl_text = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
            pnl_pct_text = f"+{pnl_pct:.2f}%" if pnl_pct >= 0 else f"{pnl_pct:.2f}%"
            
            table.add_row(
                position['symbol'],
                f"[{side_style}]{position['side'].upper()}[/{side_style}]",
                f"{position.get('contracts', 0):.4f}",
                f"{position.get('entry_price', 0):.4f}",
                f"{position.get('mark_price', 0):.4f}",
                f"[{pnl_style}]{pnl_text}[/{pnl_style}]",
                f"[{pnl_style}]{pnl_pct_text}[/{pnl_style}]",
                position.get('duration', '-')
            )
        
        return Panel(
            table,
            title="📈 ACTIVE POSITIONS",
            title_align="left",
            border_style="bright_green",
            padding=(1, 1)
        )
    
    def create_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create trading signals panel"""
        if not signals:
            content = Text("🔍 Scanning for signals...", style="bright_yellow", justify="center")
            return Panel(
                content,
                title="🎯 TRADING SIGNALS",
                title_align="left",
                border_style="bright_green",
                padding=(1, 1)
            )
        
        signal_lines = []
        for signal in signals[:6]:  # Show top 6 signals
            symbol = signal.get('symbol', 'Unknown')
            timeframe = signal.get('timeframe', '1m')
            action = signal.get('action', 'HOLD').upper()
            price = signal.get('current_price', 0)
            confidence = signal.get('confidence', 0)
            
            # Color based on action
            if action == 'BUY':
                action_color = "bright_green"
                emoji = "🟢"
            elif action == 'SELL':
                action_color = "bright_red"
                emoji = "🔴"
            else:
                action_color = "yellow"
                emoji = "🟡"
            
            # Confidence bar
            bar_length = 10
            filled_length = int(confidence / 100 * bar_length)
            confidence_bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            signal_text = f"{emoji} {symbol} [{timeframe}] [{action_color}]{action}[/{action_color}] @ ${price:.4f} [{confidence_bar}]"
            confidence_text = f"{confidence:.1f}%"
            
            signal_line = Text(signal_text)
            signal_line.append("\n")
            signal_line.append(confidence_text, style="bright_cyan")
            signal_lines.append(signal_line)
        
        content = Text()
        for i, signal_line in enumerate(signal_lines):
            content.append(signal_line)
            if i < len(signal_lines) - 1:
                content.append("\n")
        
        return Panel(
            content,
            title="🎯 TRADING SIGNALS",
            title_align="left",
            border_style="bright_green",
            padding=(1, 1)
        )
    
    def create_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create status bar"""
        now = datetime.now()
        uptime = now - last_update if last_update else timedelta(0)
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        status_text = Text()
        status_text.append("⚡ Status: ", style="bright_cyan")
        status_text.append(status, style="bright_green" if "Running" in status else "yellow")
        status_text.append("  📅 Last Update: ", style="bright_cyan")
        status_text.append(last_update.strftime("%H:%M:%S") if last_update else "Never", style="white")
        status_text.append("  ⏱️ Uptime: ", style="bright_cyan")
        status_text.append(uptime_str, style="white")
        
        return Panel(
            Align.center(status_text),
            box=box.SIMPLE,
            style="bright_green"
        )
    
    def create_logs_panel(self, logs: List[str]) -> Panel:
        """Create activity logs panel"""
        if not logs:
            content = Text("No recent activity", style="bright_yellow", justify="center")
        else:
            content = Text()
            for log in logs[-8:]:  # Show last 8 logs
                timestamp = datetime.now().strftime("[%H:%M:%S]")
                content.append(f"{timestamp} ", style="bright_cyan")
                content.append(log)
                content.append("\n")
        
        return Panel(
            content,
            title="📜 ACTIVITY LOG",
            title_align="left",
            border_style="bright_green",
            padding=(1, 1)
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
            'balance': 0.0,
            'equity': 0.0,
            'free_margin': 0.0,
            'margin_level': 100.0
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
        self.last_update = datetime.now()
        
        # Display optimization
        self.layout_cache = None
        self.data_changed = True
        
        # Initialize strategies
        from strategy import VolumeAnomalyStrategy
        from volume_anom_bot import VolumeAnomBot
        self.strategy1 = VolumeAnomalyStrategy()
        self.strategy2 = None  # Will initialize volume anomaly bot
        
        # Trading executor (will be set by orchestrator)
        self.executor = None
        
    def add_log(self, message: str):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 50:  # Keep last 50 logs
            self.logs.pop(0)
        logger.info(message)
        self.data_changed = True
        
    def force_connection(self) -> bool:
        """Force connection to Bitget"""
        self.add_log("🔌 Forcing Bitget connection...")
        success = self.connection.force_connect()
        if success:
            self.add_log("✅ Bitget connection established!")
        else:
            self.add_log("❌ Failed to connect to Bitget")
        return success
    
    def update_account_data(self):
        """Update account data from exchange - FUTURES BALANCE"""
        try:
            if self.connection.exchange:
                            # Fetch futures balance specifically
            balance = self.connection.exchange.fetch_balance({'type': 'swap'})
                
                # Get futures balance info from the response
                usdt_info = balance.get('USDT', {})
                total_balance = float(usdt_info.get('total', 0) or 0)
                free_balance = float(usdt_info.get('free', 0) or 0)
                used_balance = float(usdt_info.get('used', 0) or 0)
                
                # Calculate margin level
                margin_level = 100.0
                if used_balance > 0 and total_balance > 0:
                    margin_level = (total_balance / used_balance) * 100
                
                # Update account data
                old_balance = float(self.account_data.get('balance', 0))
                self.account_data['balance'] = total_balance
                self.account_data['equity'] = total_balance
                self.account_data['free_margin'] = free_balance
                self.account_data['margin_level'] = margin_level
                
                # Mark data as changed if balance changed significantly
                if abs(old_balance - total_balance) > 0.01:
                    self.data_changed = True
                    self.add_log(f"💰 Balance updated: ${total_balance:.2f} (Free: ${free_balance:.2f})")
                    
        except Exception as e:
            self.add_log(f"❌ Account data error: {str(e)}")
    
    def update_positions(self):
        """Update positions from exchange - FUTURES POSITIONS"""
        try:
            if self.connection.exchange:
                            # Fetch futures positions specifically
            positions = self.connection.exchange.fetch_positions(None, {'type': 'swap'})
                active_positions = []
                
                for pos in positions:
                    contracts = pos.get('contracts', 0)
                    if contracts and isinstance(contracts, (int, float)) and contracts > 0:
                        duration = "Unknown"
                        try:
                            datetime_str = pos.get('datetime')
                            if datetime_str and isinstance(datetime_str, str):
                                entry_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                                duration = str(datetime.now(entry_time.tzinfo) - entry_time).split('.')[0]
                        except:
                            pass
                        
                        active_positions.append({
                            'symbol': pos['symbol'],
                            'side': pos['side'],
                            'contracts': contracts,
                            'entry_price': pos['entryPrice'] or 0,
                            'mark_price': pos['markPrice'] or 0,
                            'unrealized_pnl': pos['unrealizedPnl'] or 0,
                            'percentage': pos['percentage'] or 0,
                            'duration': duration
                        })
                
                # Update positions if changed
                if len(active_positions) != len(self.positions):
                    self.positions = active_positions
                    self.data_changed = True
                    if active_positions:
                        self.add_log(f"📊 {len(active_positions)} active positions")
                    
        except Exception as e:
            self.add_log(f"❌ Positions error: {str(e)}")
    
    def scan_for_signals(self):
        """Scan for trading signals"""
        try:
            # Simple signal generation for dashboard
            from config import TRADING_PAIRS
            import random
            
            new_signals = []
            for symbol in TRADING_PAIRS[:6]:  # Check first 6 pairs
                if random.random() > 0.7:  # 30% chance of signal
                    signal = {
                        'symbol': symbol.replace('/USDT', ''),
                        'timeframe': '1m',
                        'action': random.choice(['BUY', 'SELL']),
                        'current_price': random.uniform(0.0001, 2.0),
                        'confidence': random.uniform(50, 100),
                        'timestamp': datetime.now()
                    }
                    new_signals.append(signal)
            
            # Update signals if changed
            if len(new_signals) != len(self.signals):
                self.signals = new_signals
                self.data_changed = True
                
        except Exception as e:
            self.add_log(f"❌ Signal scanning error: {str(e)}")
    
    def create_layout(self) -> Layout:
        """Create main dashboard layout with caching"""
        # Return cached layout if data hasn't changed
        if not self.data_changed and self.layout_cache:
            return self.layout_cache
        
        # Create main layout
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=15)
        )
        
        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left into metrics and positions
        layout["left"].split_column(
            Layout(name="metrics", size=8),
            Layout(name="positions")
        )
        
        # Split right into signals and logs
        layout["right"].split_column(
            Layout(name="signals"),
            Layout(name="logs")
        )
        
        # Populate layout
        layout["header"].update(self.display.create_header(self.account_data))
        layout["metrics"].update(self.display.create_pnl_panel(self.pnl_data))
        layout["positions"].update(self.display.create_positions_panel(self.positions))
        layout["signals"].update(self.display.create_signals_panel(self.signals))
        layout["logs"].update(self.display.create_logs_panel(self.logs))
        layout["footer"].update(self.display.create_status_bar("🟢 Running", self.last_update))
        
        # Cache layout and reset change flag
        self.layout_cache = layout
        self.data_changed = False
        
        return layout
    
    def trading_loop(self):
        """Main trading loop with proper timing"""
        self.running = True
        update_counter = 0
        
        while self.running:
            try:
                # Keep connection alive
                self.connection.keep_alive()
                
                # Update data with proper intervals
                if update_counter % 3 == 0:  # Every 3 seconds
                    self.update_account_data()
                    
                if update_counter % 5 == 0:  # Every 5 seconds
                    self.update_positions()
                    
                if update_counter % 10 == 0:  # Every 10 seconds
                    self.scan_for_signals()
                
                # Update timestamp
                self.last_update = datetime.now()
                
                update_counter += 1
                time.sleep(1)  # Consistent 1-second intervals
                
            except Exception as e:
                self.add_log(f"❌ Trading loop error: {str(e)}")
                time.sleep(5)  # Wait longer on error
    
    def run(self):
        """Run the trading dashboard with stable display"""
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
        
        # Main display loop with stable refresh
        with Live(
            self.create_layout(), 
            console=self.display.console, 
            refresh_per_second=1,  # Stable 1 FPS
            screen=True
        ) as live:
            while self.running:
                # Only update if data has changed or every 5 seconds minimum
                now = time.time()
                if self.data_changed or (now - getattr(self, '_last_display_update', 0)) > 5:
                    live.update(self.create_layout())
                    self._last_display_update = now
                
                time.sleep(1)  # Consistent 1-second sleep

def main():
    """Main entry point"""
    dashboard = AlpineTradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()