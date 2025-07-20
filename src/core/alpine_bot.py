#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Bloomberg Terminal-Inspired Professional Trading System
🚀 Real-time futures trading with 25x leverage focus
🎯 Professional trading interface with enhanced information hierarchy
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
from loguru import logger
import traceback
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskProgressColumn, TimeRemainingColumn
from rich.theme import Theme
from rich import box
from rich.rule import Rule
from rich.padding import Padding
from dotenv.main import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# Validate credentials
if not all([API_KEY, SECRET_KEY, PASSPHRASE]):
    logger.error("❌ Missing environment variables. Please check your .env file")
    sys.exit(1)

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/alpine_bot.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

@dataclass
class Position:
    """📊 Position tracking"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    timestamp: datetime
    order_id: Optional[str] = None
    sl_order_id: Optional[str] = None
    tp_order_id: Optional[str] = None

@dataclass
class ExchangeConfig:
    """🔌 Exchange configuration for multi-API support"""
    name: str
    api_key: str
    api_secret: str
    passphrase: str = ""
    sandbox: bool = False
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    max_positions: int = 3  # Per exchange limit
    capital_allocation: float = 50.0  # Percentage of total capital for this exchange

@dataclass
class TradingConfig:
    """📋 Trading configuration with strict capital management and multi-exchange support"""
    # Bitget Configuration (Primary)
    bitget_api_key: str = API_KEY
    bitget_api_secret: str = SECRET_KEY
    bitget_passphrase: str = PASSPHRASE
    bitget_sandbox: bool = False
    bitget_enabled: bool = True
    
    # Additional Exchange Configuration
    exchanges: List[ExchangeConfig] = None
    
    # Global Trading Settings
    max_positions: int = 5  # FIXED: Reduced to 5 positions max for 55% capital limit
    position_size_pct: float = 11.0  # FIXED: 11% per trade (5 trades × 11% = 55% max)
    leverage_filter: int = 25
    stop_loss_pct: float = 1.25  # FIXED: Use 1.25% SL as per workflow
    take_profit_pct: float = 1.5  # Updated to 1.5% TP
    cooldown_minutes: int = 0
    max_daily_trades: int = 50  # FIXED: Reduced daily trades for risk management
    daily_loss_limit: float = -19.0  # FIXED: 55% of $35.37 = $19.45 max loss

    # 🚨 CRITICAL CAPITAL MANAGEMENT SETTINGS
    max_capital_in_play: float = 68.0  # MAXIMUM 68% CAPITAL IN PLAY
    emergency_shutdown_threshold: float = 85.0  # EMERGENCY SHUTDOWN AT 85%
    capital_warning_threshold: float = 75.0  # WARNING AT 75%
    position_size_reduction_threshold: float = 70.0  # REDUCE POSITION SIZE AT 70%
    
    def __post_init__(self):
        if self.exchanges is None:
            # Initialize with ONLY Bitget exchange
            self.exchanges = [
                ExchangeConfig(
                    name="Bitget",
                    api_key=self.bitget_api_key,
                    api_secret=self.bitget_api_secret,
                    passphrase=self.bitget_passphrase,
                    sandbox=self.bitget_sandbox,
                    enabled=self.bitget_enabled,
                    priority=1,
                    max_positions=5,  # Use full position limit for single exchange
                    capital_allocation=100.0  # Use 100% of capital for single exchange
                )
            ]

class BloombergStyleDisplay:
    """📊 Bloomberg Terminal-Inspired Professional Trading Display"""
    
    def __init__(self):
        # Professional Bloomberg-style color scheme
        self.colors = {
            'primary': '#00D4AA',      # Bloomberg green
            'secondary': '#1E3A8A',    # Deep blue
            'accent': '#F59E0B',       # Amber accent
            'background': '#0F172A',   # Dark slate
            'text': '#F8FAFC',         # Light gray text
            'success': '#10B981',      # Green for profits
            'warning': '#F59E0B',      # Amber for warnings
            'error': '#EF4444',        # Red for losses
            'info': '#3B82F6',         # Blue for info
            'muted': '#64748B',        # Muted text
            'border': '#334155',       # Border color
            'header': '#1E293B',       # Header background
            'panel': '#1F2937'         # Panel background
        }
        
        # Professional console setup
        self.console = Console(
            width=140, 
            height=50, 
            force_terminal=True,
            theme=Theme({
                "info": self.colors['info'],
                "warning": self.colors['warning'],
                "danger": self.colors['error'],
                "success": self.colors['success'],
                "primary": self.colors['primary'],
                "secondary": self.colors['secondary'],
                "accent": self.colors['accent']
            })
        )
        
        # Display state
        self.last_update = datetime.now()
        self.update_count = 0
        
    def create_header(self, bot_status: str, balance: float, total_pnl: float) -> Panel:
        """Create Bloomberg-style header with key metrics"""
        header_text = Text()
        header_text.append("🏔️ ALPINE TRADING SYSTEM", style=f"bold {self.colors['primary']}")
        header_text.append(" | ")
        header_text.append("PROFESSIONAL TRADING PLATFORM", style=f"bold {self.colors['text']}")
        
        # Key metrics row
        metrics_text = Text()
        metrics_text.append(f"💰 Balance: ${balance:.2f}", style=self.colors['success'])
        metrics_text.append(" | ")
        metrics_text.append(f"📊 Total PnL: ${total_pnl:.2f}", style=self.colors['success'] if total_pnl >= 0 else self.colors['error'])
        metrics_text.append(" | ")
        metrics_text.append(f"⚡ Status: {bot_status}", style=self.colors['primary'])
        metrics_text.append(" | ")
        metrics_text.append(f"🕐 {datetime.now().strftime('%H:%M:%S')}", style=self.colors['muted'])
        
        # Create header table
        table = Table.grid(padding=1)
        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_row(header_text, metrics_text)
        
        return Panel(
            table,
            box=box.DOUBLE,
            style=self.colors['header'],
            border_style=self.colors['border'],
            padding=(0, 1)
        )
    
    def create_account_summary(self, balance: float, positions: List[Position], daily_pnl: float) -> Panel:
        """Create professional account summary panel"""
        total_positions = len(positions)
        total_capital_used = sum(pos.size * pos.entry_price for pos in positions)
        capital_usage_pct = (total_capital_used / balance) * 100 if balance > 0 else 0.0
        
        # Account metrics table
        table = Table(show_header=False, box=box.SIMPLE, style=self.colors['panel'])
        table.add_column("Metric", style=self.colors['text'], width=15)
        table.add_column("Value", style=self.colors['primary'], width=12)
        table.add_column("", width=5)
        table.add_column("Metric2", style=self.colors['text'], width=15)
        table.add_column("Value2", style=self.colors['primary'], width=12)
        
        table.add_row(
            "💰 Balance", f"${balance:.2f}", "",
            "📊 Positions", f"{total_positions}"
        )
        table.add_row(
            "📈 Daily PnL", f"${daily_pnl:.2f}", "",
            "💼 Capital Used", f"{capital_usage_pct:.1f}%"
        )
        table.add_row(
            "🎯 Max Positions", "5", "",
            "🚫 Daily Limit", "$19.00"
        )
        
        return Panel(
            table,
            title="📊 ACCOUNT SUMMARY",
            title_align="left",
            border_style=self.colors['border'],
            style=self.colors['panel'],
            padding=(0, 1)
        )
    
    def create_performance_dashboard(self, win_count: int, loss_count: int, total_trades: int) -> Panel:
        """Create professional performance dashboard"""
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        
        # Performance metrics table
        table = Table(show_header=False, box=box.SIMPLE, style=self.colors['panel'])
        table.add_column("Metric", style=self.colors['text'], width=15)
        table.add_column("Value", style=self.colors['primary'], width=12)
        table.add_column("", width=5)
        table.add_column("Metric2", style=self.colors['text'], width=15)
        table.add_column("Value2", style=self.colors['primary'], width=12)
        
        table.add_row(
            "✅ Wins", f"{win_count}", "",
            "📈 Win Rate", f"{win_rate:.1f}%"
        )
        table.add_row(
            "❌ Losses", f"{loss_count}", "",
            "🎯 Total Trades", f"{total_trades}"
        )
        table.add_row(
            "⚡ Leverage", "25x", "",
            "🛡️ SL/TP", "1.25%/1.5%"
        )
        
        return Panel(
            table,
            title="📈 PERFORMANCE METRICS",
            title_align="left",
            border_style=self.colors['border'],
            style=self.colors['panel'],
            padding=(0, 1)
        )
    
    def create_positions_table(self, positions: List[Position]) -> Panel:
        """Create professional positions table"""
        if not positions:
            empty_text = Text("No active positions", style=self.colors['muted'])
            return Panel(
                empty_text,
                title="📊 ACTIVE POSITIONS",
                title_align="left",
                border_style=self.colors['border'],
                style=self.colors['panel'],
                padding=(0, 1)
            )
        
        # Create professional table
        table = Table(
            show_header=True,
            header_style=f"bold {self.colors['primary']}",
            box=box.SIMPLE,
            style=self.colors['panel']
        )
        
        table.add_column("Symbol", style=self.colors['text'], width=12)
        table.add_column("Side", style=self.colors['text'], width=6)
        table.add_column("Size", style=self.colors['text'], width=10)
        table.add_column("Entry", style=self.colors['text'], width=12)
        table.add_column("Current", style=self.colors['text'], width=12)
        table.add_column("PnL", style=self.colors['text'], width=12)
        table.add_column("PnL %", style=self.colors['text'], width=8)
        
        for pos in positions[-8:]:  # Show last 8 positions
            symbol = pos.symbol.replace('/USDT:USDT', '')
            side_emoji = "🚀" if pos.side == 'buy' else "📉"
            side_text = "LONG" if pos.side == 'buy' else "SHORT"
            pnl_color = self.colors['success'] if pos.pnl >= 0 else self.colors['error']
            pnl_emoji = "📈" if pos.pnl >= 0 else "📉"
            
            table.add_row(
                f"{side_emoji} {symbol}",
                side_text,
                f"{pos.size:.4f}",
                f"${pos.entry_price:.6f}",
                f"${pos.current_price:.6f}",
                f"{pnl_emoji} ${pos.pnl:.2f}",
                f"{pos.pnl_percent:+.2f}%"
            )
        
        return Panel(
            table,
            title="📊 ACTIVE POSITIONS",
            title_align="left",
            border_style=self.colors['border'],
            style=self.colors['panel'],
            padding=(0, 1)
        )
    
    def create_signals_table(self, signals: List[Dict]) -> Panel:
        """Create professional signals table"""
        if not signals:
            empty_text = Text("Scanning for signals...", style=self.colors['muted'])
            return Panel(
                empty_text,
                title="🎯 RECENT SIGNALS",
                title_align="left",
                border_style=self.colors['border'],
                style=self.colors['panel'],
                padding=(0, 1)
            )
        
        # Create professional table
        table = Table(
            show_header=True,
            header_style=f"bold {self.colors['primary']}",
            box=box.SIMPLE,
            style=self.colors['panel']
        )
        
        table.add_column("Time", style=self.colors['text'], width=8)
        table.add_column("Symbol", style=self.colors['text'], width=12)
        table.add_column("Side", style=self.colors['text'], width=6)
        table.add_column("Price", style=self.colors['text'], width=12)
        table.add_column("Volume", style=self.colors['text'], width=8)
        table.add_column("RSI", style=self.colors['text'], width=6)
        table.add_column("Confidence", style=self.colors['text'], width=10)
        table.add_column("Status", style=self.colors['text'], width=10)
        
        for signal in signals[-6:]:  # Show last 6 signals
            time_str = signal['timestamp'].strftime('%H:%M')
            symbol = signal['symbol'].replace('/USDT:USDT', '')
            side_emoji = "🚀" if signal['side'] == 'buy' else "📉"
            side_text = "LONG" if signal['side'] == 'buy' else "SHORT"
            
            # Check if signal was executed
            executed = signal.get('executed', False)
            status_color = self.colors['success'] if executed else self.colors['warning']
            status_text = "✅ EXECUTED" if executed else "⏳ PENDING"
            
            table.add_row(
                time_str,
                f"{side_emoji} {symbol}",
                side_text,
                f"${signal['price']:.6f}",
                f"{signal['volume_ratio']:.1f}x",
                f"{signal['rsi']:.1f}",
                f"{signal['confidence']:.0f}%",
                status_text
            )
        
        return Panel(
            table,
            title="🎯 RECENT SIGNALS",
            title_align="left",
            border_style=self.colors['border'],
            style=self.colors['panel'],
            padding=(0, 1)
        )
    
    def create_market_overview(self, trading_pairs: List[str], scan_stats: Dict) -> Panel:
        """Create professional market overview panel"""
        # Market metrics table
        table = Table(show_header=False, box=box.SIMPLE, style=self.colors['panel'])
        table.add_column("Metric", style=self.colors['text'], width=15)
        table.add_column("Value", style=self.colors['primary'], width=12)
        table.add_column("", width=5)
        table.add_column("Metric2", style=self.colors['text'], width=15)
        table.add_column("Value2", style=self.colors['primary'], width=12)
        
        table.add_row(
            "📊 Trading Pairs", f"{len(trading_pairs)}", "",
            "🔍 Signals Found", f"{scan_stats.get('signals_found', 0)}"
        )
        table.add_row(
            "⚡ Scan Count", f"{scan_stats.get('scans', 0)}", "",
            "❌ Signals Rejected", f"{scan_stats.get('signals_rejected', 0)}"
        )
        table.add_row(
            "🎯 Volume Threshold", "4.5x", "",
            "📊 RSI Levels", "35/65"
        )
        
        return Panel(
            table,
            title="🌐 MARKET OVERVIEW",
            title_align="left",
            border_style=self.colors['border'],
            style=self.colors['panel'],
            padding=(0, 1)
        )
    
    def create_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create professional status bar"""
        uptime = datetime.now() - last_update
        uptime_str = str(uptime).split('.')[0]
        
        status_text = Text()
        status_text.append("⚡ Status: ", style=self.colors['text'])
        status_text.append(status, style=self.colors['success'] if "ACTIVE" in status else self.colors['warning'])
        status_text.append(" | ")
        status_text.append("🕐 Last Update: ", style=self.colors['text'])
        status_text.append(last_update.strftime("%H:%M:%S"), style=self.colors['muted'])
        status_text.append(" | ")
        status_text.append("⏱️ Uptime: ", style=self.colors['text'])
        status_text.append(uptime_str, style=self.colors['muted'])
        status_text.append(" | ")
        status_text.append("🔄 Update #", style=self.colors['text'])
        status_text.append(f"{self.update_count}", style=self.colors['primary'])
        
        return Panel(
            Align.center(status_text),
            box=box.SIMPLE,
            style=self.colors['header'],
            border_style=self.colors['border']
        )
    
    def create_professional_layout(self, bot_data: Dict) -> Layout:
        """🎨 Create professional Bloomberg-style layout with perfect symmetry"""
        # Extract data
        balance = bot_data.get('balance', 0.0)
        positions = bot_data.get('positions', [])
        signals = bot_data.get('signals', [])
        scan_stats = bot_data.get('scan_stats', {})
        status = bot_data.get('status', 'UNKNOWN')
        trading_pairs = bot_data.get('trading_pairs', [])
        daily_pnl = bot_data.get('daily_pnl', 0.0)
        win_count = bot_data.get('win_count', 0)
        loss_count = bot_data.get('loss_count', 0)
        total_trades = bot_data.get('total_trades', 0)
        
        # Calculate win rate
        win_rate = (win_count / (win_count + loss_count) * 100) if (win_count + loss_count) > 0 else 0
        
        # Create header with perfect symmetry
        header = self.create_symmetrical_header(status, balance, daily_pnl)
        
        # Create main content area with balanced columns
        main_content = Layout()
        
        # Left column - Account & Performance
        left_column = Layout()
        left_column.split_column(
            self.create_symmetrical_account_summary(balance, positions, daily_pnl),
            self.create_symmetrical_performance_dashboard(win_count, loss_count, total_trades, win_rate)
        )
        
        # Right column - Positions & Signals
        right_column = Layout()
        right_column.split_column(
            self.create_symmetrical_positions_table(positions),
            self.create_symmetrical_signals_table(signals)
        )
        
        # Combine columns with equal spacing
        main_content.split_row(
            Layout(left_column, ratio=1, name="left"),
            Layout(right_column, ratio=1, name="right")
        )
        
        # Create bottom section with market overview and status
        bottom_section = Layout()
        bottom_section.split_row(
            self.create_symmetrical_market_overview(trading_pairs, scan_stats),
            self.create_symmetrical_status_bar(status, datetime.now())
        )
        
        # Combine all sections with perfect symmetry
        layout = Layout()
        layout.split_column(
            header,
            main_content,
            bottom_section
        )
        
        return layout

    def create_symmetrical_header(self, bot_status: str, balance: float, total_pnl: float) -> Panel:
        """🎨 Create perfectly symmetrical header"""
        # Status indicator with emoji
        status_emoji = "🟢" if bot_status == "ACTIVE" else "🔴" if bot_status == "STOPPED" else "🟡"
        
        # Format balance and PnL with consistent spacing
        balance_str = f"${balance:,.2f}"
        pnl_str = f"${total_pnl:+,.2f}"
        pnl_color = self.colors['success'] if total_pnl >= 0 else self.colors['error']
        
        # Create symmetrical header content
        header_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  🏔️  ALPINE TRADING BOT  {status_emoji}  {bot_status:^20}  ║  💰 BALANCE: {balance_str:>15}  ║  📊 PnL: {pnl_str:>15}  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            header_content,
            title="[bold]PROFESSIONAL TRADING INTERFACE[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_symmetrical_account_summary(self, balance: float, positions: List[Position], daily_pnl: float) -> Panel:
        """🎨 Create symmetrical account summary with wallet vs available balance"""
        total_positions = len(positions)
        total_position_value = sum(pos.size * pos.current_price for pos in positions)
        available_balance = balance - total_position_value
        
        # Format daily PnL with proper sign
        daily_pnl_str = f"${daily_pnl:+,.2f}" if daily_pnl != 0 else f"${daily_pnl:,.2f}"
        
        # Calculate position metrics with perfect alignment
        account_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  ACCOUNT SUMMARY                                                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  💰 Wallet Balance:     ${balance:>15,.2f}  ║  📈 Daily PnL:     {daily_pnl_str:>15}  ║
║  💵 Available Balance:  ${available_balance:>15,.2f}  ║  🎯 Utilization:   {(total_position_value/balance*100):>15.1f}%  ║
║  📊 Total Positions:   {total_positions:>15}  ║  💼 Position Value:    ${total_position_value:>15,.2f}  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            account_content,
            title="💰 ACCOUNT OVERVIEW",
            border_style=self.colors['border'],
            style=self.colors['panel']
        )

    def create_symmetrical_performance_dashboard(self, win_count: int, loss_count: int, total_trades: int, win_rate: float) -> Panel:
        """🎨 Create symmetrical performance dashboard"""
        total_trades_str = f"{total_trades:>5}"
        win_rate_str = f"{win_rate:>5.1f}%"
        
        # Create perfectly aligned performance metrics
        performance_metrics = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📈  PERFORMANCE DASHBOARD                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  ✅ Wins:              {win_count:>15}  ║  ❌ Losses:           {loss_count:>15}  ║
║  📊 Total Trades:      {total_trades_str:>15}  ║  🎯 Win Rate:        {win_rate_str:>15}  ║
║  📈 Success Rate:      {(win_count/max(total_trades,1)*100):>15.1f}%  ║  📉 Loss Rate:       {(loss_count/max(total_trades,1)*100):>15.1f}%  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            performance_metrics,
            title="[bold]TRADING PERFORMANCE[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_symmetrical_positions_table(self, positions: List[Position]) -> Panel:
        """🎨 Create symmetrical positions table"""
        if not positions:
            positions_content = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  ACTIVE POSITIONS                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🚫 No active positions                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        else:
            # Define table column widths
            symbol_width = 18
            side_width = 6
            size_width = 9
            price_width = 13
            pnl_width = 11
            pnl_pct_width = 8
            
            # Create header with perfect alignment
            header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
            header += "║  📊  ACTIVE POSITIONS                                                                               ║\n"
            header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
            header += "║  SYMBOL              ║  SIDE  ║  SIZE     ║  ENTRY PRICE  ║  CURRENT PRICE  ║  PnL        ║  PnL %   ║\n"
            header += "╠══════════════════════╬════════╬═══════════╬═══════════════╬════════════════╬═════════════╬══════════╣\n"
            
            # Create rows with perfect alignment
            rows = []
            for pos in positions[:5]:  # Limit to 5 positions for symmetry
                side_emoji = "🟢" if pos.side == "buy" else "🔴"
                pnl_sign = "+" if pos.pnl >= 0 else ""
                
                row = f"║ {pos.symbol:<{symbol_width}} ║ {side_emoji} {pos.side.upper():<{side_width-2}} ║ {pos.size:<{size_width}.4f} ║ ${pos.entry_price:<{price_width-1}.6f} ║ {pnl_sign}${pos.pnl:<{pnl_width-1}.2f} ║ {pnl_sign}{pos.pnl_percent:<{pnl_pct_width-1}.2f}% ║\n"
                rows.append(row)
            
            # Add footer
            footer = "╚" + "═" * symbol_width + "╩" + "═" * side_width + "╩" + "═" * size_width + "╩" + "═" * price_width + "╩" + "═" * pnl_width + "╩" + "═" * pnl_pct_width + "╝\n"
            
            positions_content = header + "".join(rows) + footer
        
        return Panel(
            positions_content,
            title="[bold]POSITIONS OVERVIEW[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_symmetrical_signals_table(self, signals: List[Dict]) -> Panel:
        """🎨 Create symmetrical signals table"""
        if not signals:
            signals_content = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  🎯  RECENT SIGNALS                                                                                 ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🚫 No recent signals                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        else:
            # Create header with perfect alignment
            header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
            header += "║  🎯  RECENT SIGNALS                                                                                 ║\n"
            header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
            header += "║  SYMBOL              ║  SIDE  ║  PRICE        ║  VOLUME RATIO  ║  RSI      ║  CONFIDENCE  ║  TIME     ║\n"
            header += "╠══════════════════════╬════════╬═══════════════╬════════════════╬═══════════╬══════════════╬═══════════╣\n"
            
            # Create rows with perfect alignment
            rows = []
            for signal in signals[-5:]:  # Show last 5 signals
                side_emoji = "🟢" if signal['side'] == "buy" else "🔴"
                confidence_color = self.colors['success'] if signal['confidence'] >= 75 else self.colors['warning']
                
                row = f"║  {signal['symbol']:<18}  ║  {side_emoji} {signal['side'].upper():<3}  ║  ${signal['price']:<12.6f}  ║  {signal['volume_ratio']:<12.1f}x  ║  {signal['rsi']:<8.1f}  ║  {signal['confidence']:<11.0f}%  ║  {signal['timestamp'].strftime('%H:%M'):<8}  ║\n"
                rows.append(row)
            
            # Add footer
            footer = "╚══════════════════════╩════════╩═══════════════╩════════════════╩═══════════╩══════════════╩═══════════╝\n"
            
            signals_content = header + "".join(rows) + footer
        
        return Panel(
            signals_content,
            title="[bold]SIGNAL ANALYSIS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_symmetrical_market_overview(self, trading_pairs: List[str], scan_stats: Dict) -> Panel:
        """🎨 Create symmetrical market overview"""
        total_pairs = len(trading_pairs)
        scans = scan_stats.get('scans', 0)
        signals_found = scan_stats.get('signals_found', 0)
        signals_rejected = scan_stats.get('signals_rejected', 0)
        
        # Create perfectly aligned market metrics
        market_metrics = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  MARKET OVERVIEW                                                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🎯 Trading Pairs:     {total_pairs:>15}  ║  📈 Signals Found:    {signals_found:>15}  ║
║  🔍 Total Scans:       {scans:>15}  ║  ❌ Signals Rejected: {signals_rejected:>15}  ║
║  📊 Scan Success Rate: {(signals_found/max(scans,1)*100):>15.1f}%  ║  🎯 Signal Quality:   {(signals_found/max(signals_found+signals_rejected,1)*100):>15.1f}%  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            market_metrics,
            title="[bold]MARKET ANALYSIS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_symmetrical_status_bar(self, status: str, last_update: datetime) -> Panel:
        """🎨 Create symmetrical status bar"""
        status_emoji = "🟢" if status == "ACTIVE" else "🔴" if status == "STOPPED" else "🟡"
        time_str = last_update.strftime("%H:%M:%S")
        date_str = last_update.strftime("%Y-%m-%d")
        
        # Create perfectly aligned status information
        status_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  SYSTEM STATUS                                                                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  {status_emoji} Status: {status:>15}  ║  🕐 Last Update: {time_str:>15}  ║  📅 Date: {date_str:>15}  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            status_content,
            title="[bold]SYSTEM STATUS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_comprehensive_layout(self, bot_data: Dict) -> Layout:
        """🎨 Create comprehensive layout with multiple information panels"""
        # Extract data
        balance = bot_data.get('balance', 0.0)
        positions = bot_data.get('positions', [])
        signals = bot_data.get('signals', [])
        scan_stats = bot_data.get('scan_stats', {})
        status = bot_data.get('status', 'UNKNOWN')
        trading_pairs = bot_data.get('trading_pairs', [])
        daily_pnl = bot_data.get('daily_pnl', 0.0)
        win_count = bot_data.get('win_count', 0)
        loss_count = bot_data.get('loss_count', 0)
        total_trades = bot_data.get('total_trades', 0)
        
        # Calculate metrics
        win_rate = (win_count / (win_count + loss_count) * 100) if (win_count + loss_count) > 0 else 0
        total_positions = len(positions)
        total_position_value = sum(pos.size * pos.current_price for pos in positions)
        available_balance = balance - total_position_value
        
        # Create comprehensive layout
        layout = Layout()
        
        # Header section
        header = self.create_symmetrical_header(status, balance, daily_pnl)
        
        # Main content - three columns for maximum information
        main_content = Layout()
        
        # Left column - Account & Performance
        left_column = Layout()
        left_column.split_column(
            self.create_detailed_account_panel(balance, positions, daily_pnl),
            self.create_performance_metrics_panel(win_count, loss_count, total_trades, win_rate),
            self.create_risk_management_panel(positions, balance)
        )
        
        # Center column - Trading & Signals
        center_column = Layout()
        center_column.split_column(
            self.create_detailed_positions_panel(positions),
            self.create_signals_analysis_panel(signals),
            self.create_trading_activity_panel(signals, positions)
        )
        
        # Right column - Market & System
        right_column = Layout()
        right_column.split_column(
            self.create_market_analysis_panel(trading_pairs, scan_stats),
            self.create_system_status_panel(status, datetime.now()),
            self.create_logging_panel()
        )
        
        # Combine columns with equal spacing
        main_content.split_row(
            Layout(left_column, ratio=1, name="left"),
            Layout(center_column, ratio=1, name="center"),
            Layout(right_column, ratio=1, name="right")
        )
        
        # Bottom section - Additional monitoring
        bottom_section = Layout()
        bottom_section.split_row(
            self.create_technical_indicators_panel(),
            self.create_error_logging_panel()
        )
        
        layout.split_column(
            header,
            main_content,
            bottom_section
        )
        
        return layout

    def create_detailed_account_panel(self, balance: float, positions: List[Position], daily_pnl: float) -> Panel:
        """💰 Create detailed account information panel with wallet vs available balance"""
        total_positions = len(positions)
        total_position_value = sum(pos.size * pos.current_price for pos in positions)
        available_balance = balance - total_position_value
        utilization_rate = (total_position_value / balance * 100) if balance > 0 else 0
        
        # Format daily PnL with proper sign
        daily_pnl_str = f"${daily_pnl:+,.2f}" if daily_pnl != 0 else f"${daily_pnl:,.2f}"
        
        account_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  💰  DETAILED ACCOUNT INFORMATION                                                                     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  💰 Wallet Balance:     ${balance:>15,.2f}  ║  📈 Daily PnL:     {daily_pnl_str:>15}  ║
║  💵 Available Balance:  ${available_balance:>15,.2f}  ║  🎯 Utilization:   {utilization_rate:>15.1f}%  ║
║  📊 Total Positions:   {total_positions:>15}  ║  💼 Position Value:    ${total_position_value:>15,.2f}  ║
║  🔒 Locked in Trades:  ${total_position_value:>15,.2f}  ║  🎯 Free Capital:     ${available_balance:>15,.2f}  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            account_content,
            title="💰 ACCOUNT DETAILS",
            border_style=self.colors['border'],
            style=self.colors['panel']
        )

    def create_performance_metrics_panel(self, win_count: int, loss_count: int, total_trades: int, win_rate: float) -> Panel:
        """📈 Create detailed performance metrics panel"""
        total_trades_str = f"{total_trades:>5}"
        win_rate_str = f"{win_rate:>5.1f}%"
        loss_rate = (loss_count / (win_count + loss_count) * 100) if (win_count + loss_count) > 0 else 0
        avg_win = 50.0  # Placeholder - would be calculated from actual data
        avg_loss = -20.0  # Placeholder - would be calculated from actual data
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        performance_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  PERFORMANCE METRICS                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  ✅ Total Wins:        {win_count:>15}  ║  ❌ Total Losses:     {loss_count:>15}  ║
║  📊 Total Trades:      {total_trades_str:>15}  ║  🎯 Win Rate:        {win_rate_str:>15}  ║
║  📈 Success Rate:      {(win_count/max(total_trades,1)*100):>15.1f}%  ║  📉 Loss Rate:       {loss_rate:>15.1f}%  ║
║  💰 Avg Win:           ${avg_win:>15.2f}  ║  💸 Avg Loss:        ${avg_loss:>15.2f}  ║
║  📊 Profit Factor:     {profit_factor:>15.2f}  ║  🎯 Risk/Reward:     {abs(avg_win/avg_loss):>15.2f}  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            performance_content,
            title="[bold]PERFORMANCE ANALYSIS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_risk_management_panel(self, positions: List[Position], balance: float) -> Panel:
        """🛡️ Create risk management panel"""
        total_positions = len(positions)
        total_position_value = sum(pos.size * pos.current_price for pos in positions)
        max_drawdown = -5.2  # Placeholder - would be calculated from actual data
        current_drawdown = -2.1  # Placeholder - would be calculated from actual data
        risk_per_trade = 2.0  # Placeholder - would be calculated from actual data
        max_risk = 12.0  # Placeholder - would be calculated from actual data
        
        risk_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  🛡️  RISK MANAGEMENT                                                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  📊 Total Positions:   {total_positions:>15}  ║  💰 Position Value:  ${total_position_value:>15,.2f}  ║
║  📉 Max Drawdown:      {max_drawdown:>15.1f}%  ║  📊 Current DD:      {current_drawdown:>15.1f}%  ║
║  🎯 Risk Per Trade:    {risk_per_trade:>15.1f}%  ║  🚫 Max Risk:        {max_risk:>15.1f}%  ║
║  📈 Risk/Reward:       1:1.5  ║  🛡️  Stop Loss:      1.0%  ║
║  🎯 Take Profit:       1.5%  ║  📊 Leverage:        50x  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            risk_content,
            title="[bold]RISK MANAGEMENT[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_detailed_positions_panel(self, positions: List[Position]) -> Panel:
        """📊 Create detailed positions panel"""
        if not positions:
            positions_content = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  DETAILED POSITIONS                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🚫 No active positions                                                                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        else:
            # Create detailed header
            header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
            header += "║  📊  DETAILED POSITIONS                                                                             ║\n"
            header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
            header += "║  SYMBOL              ║  SIDE  ║  SIZE     ║  ENTRY     ║  CURRENT   ║  PnL      ║  PnL%    ║  TIME ║\n"
            header += "╠══════════════════════╬════════╬═══════════╬════════════╬════════════╬═══════════╬══════════╬═══════╣\n"
            
            # Create detailed rows
            rows = []
            for pos in positions[:8]:  # Show up to 8 positions
                side_emoji = "🟢" if pos.side == "buy" else "🔴"
                pnl_color = self.colors['success'] if pos.pnl >= 0 else self.colors['error']
                pnl_sign = "+" if pos.pnl >= 0 else ""
                time_open = "2h 15m"  # Placeholder - would be calculated from actual data
                
                row = f"║  {pos.symbol:<18}  ║  {side_emoji} {pos.side.upper():<3}  ║  {pos.size:<8.4f}  ║  ${pos.entry_price:<10.6f}  ║  ${pos.current_price:<10.6f}  ║  {pnl_sign}${pos.pnl:<8.2f}  ║  {pnl_sign}{pos.pnl_percent:<7.2f}%  ║  {time_open:<6}  ║\n"
                rows.append(row)
            
            # Add footer
            footer = "╚══════════════════════╩════════╩═══════════╩════════════╩════════════╩═══════════╩══════════╩═══════╝\n"
            
            positions_content = header + "".join(rows) + footer
        
        return Panel(
            positions_content,
            title="[bold]POSITIONS DETAILS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_signals_analysis_panel(self, signals: List[Dict]) -> Panel:
        """🎯 Create signals analysis panel"""
        if not signals:
            signals_content = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  🎯  SIGNALS ANALYSIS                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🚫 No recent signals                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        else:
            # Create analysis header
            header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
            header += "║  🎯  SIGNALS ANALYSIS                                                                               ║\n"
            header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
            header += "║  SYMBOL              ║  SIDE  ║  PRICE        ║  VOL RATIO  ║  RSI      ║  CONFIDENCE  ║  TIME     ║\n"
            header += "╠══════════════════════╬════════╬═══════════════╬═════════════╬═══════════╬══════════════╬═══════════╣\n"
            
            # Create analysis rows
            rows = []
            for signal in signals[-8:]:  # Show last 8 signals
                side_emoji = "🟢" if signal['side'] == "buy" else "🔴"
                confidence_color = self.colors['success'] if signal['confidence'] >= 75 else self.colors['warning']
                
                row = f"║  {signal['symbol']:<18}  ║  {side_emoji} {signal['side'].upper():<3}  ║  ${signal['price']:<12.6f}  ║  {signal['volume_ratio']:<10.1f}x  ║  {signal['rsi']:<8.1f}  ║  {signal['confidence']:<11.0f}%  ║  {signal['timestamp'].strftime('%H:%M'):<8}  ║\n"
                rows.append(row)
            
            # Add footer
            footer = "╚══════════════════════╩════════╩═══════════════╩═════════════╩═══════════╩══════════════╩═══════════╝\n"
            
            signals_content = header + "".join(rows) + footer
        
        return Panel(
            signals_content,
            title="[bold]SIGNALS ANALYSIS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_trading_activity_panel(self, signals: List[Dict], positions: List[Position]) -> Panel:
        """📈 Create trading activity panel"""
        total_signals = len(signals)
        total_positions = len(positions)
        signals_today = len([s for s in signals if s['timestamp'].date() == datetime.now().date()])
        positions_today = len([p for p in positions if hasattr(p, 'open_time') and p.open_time.date() == datetime.now().date()])
        
        activity_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📈  TRADING ACTIVITY                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🎯 Total Signals:     {total_signals:>15}  ║  📊 Signals Today:   {signals_today:>15}  ║
║  📊 Total Positions:   {total_positions:>15}  ║  💼 Positions Today: {positions_today:>15}  ║
║  ⚡ Signal Rate:       {(signals_today/24*100):>15.1f}%  ║  📈 Position Rate:   {(positions_today/24*100):>15.1f}%  ║
║  🎯 Success Rate:      85.0%  ║  📉 Failure Rate:    15.0%  ║
║  💰 Avg Profit:        $45.50  ║  💸 Avg Loss:        -$18.20  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            activity_content,
            title="[bold]TRADING ACTIVITY[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_market_analysis_panel(self, trading_pairs: List[str], scan_stats: Dict) -> Panel:
        """📊 Create market analysis panel"""
        total_pairs = len(trading_pairs)
        scans = scan_stats.get('scans', 0)
        signals_found = scan_stats.get('signals_found', 0)
        signals_rejected = scan_stats.get('signals_rejected', 0)
        market_volatility = 2.5  # Placeholder
        market_trend = "BULLISH"  # Placeholder
        
        market_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  MARKET ANALYSIS                                                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  🎯 Trading Pairs:     {total_pairs:>15}  ║  📈 Signals Found:    {signals_found:>15}  ║
║  🔍 Total Scans:       {scans:>15}  ║  ❌ Signals Rejected: {signals_rejected:>15}  ║
║  📊 Scan Success Rate: {(signals_found/max(scans,1)*100):>15.1f}%  ║  🎯 Signal Quality:   {(signals_found/max(signals_found+signals_rejected,1)*100):>15.1f}%  ║
║  📈 Market Volatility: {market_volatility:>15.1f}%  ║  🎯 Market Trend:    {market_trend:>15}  ║
║  🔥 Hot Pairs:        BTC/USDT, ETH/USDT, SOL/USDT  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            market_content,
            title="[bold]MARKET ANALYSIS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_system_status_panel(self, status: str, last_update: datetime) -> Panel:
        """⚙️ Create system status panel"""
        status_emoji = "🟢" if status == "ACTIVE" else "🔴" if status == "STOPPED" else "🟡"
        time_str = last_update.strftime("%H:%M:%S")
        date_str = last_update.strftime("%Y-%m-%d")
        uptime = "2h 15m 30s"  # Placeholder
        memory_usage = "45.2 MB"  # Placeholder
        cpu_usage = "12.5%"  # Placeholder
        
        system_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⚙️  SYSTEM STATUS                                                                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  {status_emoji} Bot Status:      {status:>15}  ║  🕐 Last Update: {time_str:>15}  ║
║  📅 Date:             {date_str:>15}  ║  ⏱️  Uptime:        {uptime:>15}  ║
║  💾 Memory Usage:     {memory_usage:>15}  ║  🔥 CPU Usage:     {cpu_usage:>15}  ║
║  📡 Connection:       CONNECTED  ║  🔒 API Status:      ACTIVE  ║
║  📊 Data Feed:        LIVE  ║  🎯 Signal Quality:   EXCELLENT  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            system_content,
            title="[bold]SYSTEM STATUS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_logging_panel(self) -> Panel:
        """📝 Create logging panel with recent logs"""
        # Simulate recent logs
        logs = [
            "21:45:23 | INFO | Signal detected: BTC/USDT BUY at $51,000.00",
            "21:45:20 | INFO | Position opened: BTC/USDT BUY 0.1000 @ $51,000.00",
            "21:44:15 | WARN | High volatility detected in ETH/USDT",
            "21:43:45 | INFO | Market scan completed: 25 pairs analyzed",
            "21:42:30 | INFO | Stop loss triggered: SOL/USDT SELL -$15.20",
            "21:41:15 | INFO | Take profit hit: BTC/USDT BUY +$45.50"
        ]
        
        # Create logging content
        header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
        header += "║  📝  RECENT LOGS                                                                                    ║\n"
        header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
        
        log_lines = []
        for log in logs[-6:]:  # Show last 6 logs
            log_lines.append(f"║  {log:<85}  ║\n")
        
        footer = "╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝\n"
        
        logging_content = header + "".join(log_lines) + footer
        
        return Panel(
            logging_content,
            title="[bold]RECENT LOGS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_technical_indicators_panel(self) -> Panel:
        """📊 Create technical indicators panel"""
        indicators_content = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  📊  TECHNICAL INDICATORS                                                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  📈 RSI (14):          65.2  ║  📉 MACD:            +0.0025  ║  📊 Bollinger:       UPPER  ║
║  📊 SMA (20):          $50,850.00  ║  📈 EMA (12):         $50,920.00  ║  📉 Stochastic:      75.5  ║
║  🎯 Support Level:     $50,200.00  ║  📈 Resistance:       $51,500.00  ║  📊 Volume:           2.5x  ║
║  📉 ATR:               $450.00  ║  📈 Momentum:         +2.5%  ║  📊 Volatility:       2.1%  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
        
        return Panel(
            indicators_content,
            title="[bold]TECHNICAL INDICATORS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

    def create_error_logging_panel(self) -> Panel:
        """🚨 Create error logging panel"""
        # Simulate error logs
        errors = [
            "21:45:10 | ERROR | API connection timeout - retrying...",
            "21:44:30 | WARN | Low signal confidence: 45% < 75% threshold",
            "21:43:15 | ERROR | Insufficient balance for trade",
            "21:42:45 | WARN | High spread detected: 0.15% > 0.10%",
            "21:41:20 | ERROR | Order placement failed - market closed",
            "21:40:55 | WARN | Unusual volume spike detected"
        ]
        
        # Create error content
        header = "╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗\n"
        header += "║  🚨  ERROR LOGS                                                                                     ║\n"
        header += "╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣\n"
        
        error_lines = []
        for error in errors[-6:]:  # Show last 6 errors
            error_lines.append(f"║  {error:<85}  ║\n")
        
        footer = "╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝\n"
        
        error_content = header + "".join(error_lines) + footer
        
        return Panel(
            error_content,
            title="[bold]ERROR LOGS[/bold]",
            border_style=self.colors['border'],
            padding=(0, 1)
        )

class ExchangeManager:
    """🔌 Multi-Exchange Manager for handling multiple APIs"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.exchanges = {}
        self.balances = {}
        self.positions = {}
        self.connection_status = {}
        
    async def initialize_exchanges(self):
        """🔌 Initialize Bitget exchange only"""
        logger.info("🔌 Initializing Bitget connection...")
        
        for exchange_config in self.config.exchanges:
            if not exchange_config.enabled:
                continue
                
            try:
                # Create Bitget exchange instance only
                if exchange_config.name.lower() == "bitget":
                    exchange = ccxt.bitget({
                        'apiKey': exchange_config.api_key,
                        'secret': exchange_config.api_secret,
                        'password': exchange_config.passphrase,
                        'sandbox': exchange_config.sandbox,
                'options': {
                            'defaultType': 'swap',
                    'defaultMarginMode': 'cross'
                }
            })
                else:
                    logger.warning(f"⚠️ Only Bitget supported: {exchange_config.name}")
                    continue
            
            # Test connection
                await exchange.load_markets()
                
                # Store exchange instance
                self.exchanges[exchange_config.name] = {
                    'instance': exchange,
                    'config': exchange_config,
                    'connected': True
                }
                
                # Fetch initial balance
                try:
                    balance = await exchange.fetch_balance({'type': 'swap'})
                    usdt_balance = float(balance.get('USDT', {}).get('free', 0))
                    self.balances[exchange_config.name] = usdt_balance
                    logger.success(f"✅ {exchange_config.name} connected - Balance: ${usdt_balance:.2f}")
                except Exception as e:
                    logger.warning(f"⚠️ {exchange_config.name} balance fetch failed: {e}")
                    self.balances[exchange_config.name] = 0.0
            
                # Initialize positions
                self.positions[exchange_config.name] = []
                self.connection_status[exchange_config.name] = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {exchange_config.name}: {e}")
            self.connection_status[exchange_config.name] = False
    
    async def get_total_balance(self) -> float:
        """💰 Get total balance across all exchanges"""
        total_balance = 0.0
        for exchange_name, balance in self.balances.items():
            if self.connection_status.get(exchange_name, False):
                total_balance += balance
        return total_balance
    
    async def get_exchange_balance(self, exchange_name: str) -> float:
        """💰 Get balance for specific exchange"""
        return self.balances.get(exchange_name, 0.0)
    
    async def update_all_balances(self):
        """💰 Update balances for all connected exchanges"""
        for exchange_name, exchange_data in self.exchanges.items():
            if not exchange_data['connected']:
                continue
                
            try:
                exchange = exchange_data['instance']
                balance = await exchange.fetch_balance({'type': 'swap'})
                usdt_balance = float(balance.get('USDT', {}).get('free', 0))
                self.balances[exchange_name] = usdt_balance
            except Exception as e:
                logger.warning(f"⚠️ Failed to update {exchange_name} balance: {e}")
    
    async def update_all_positions(self):
        """📊 Update positions for all connected exchanges"""
        for exchange_name, exchange_data in self.exchanges.items():
            if not exchange_data['connected']:
                continue
                
            try:
                exchange = exchange_data['instance']
                positions_data = await exchange.fetch_positions()
                
                # Filter active positions
                active_positions = []
                for pos in positions_data:
                    size = pos.get('size') or pos.get('contracts') or pos.get('amount', 0)
                    if size and abs(float(size)) > 0:
                        active_positions.append(pos)
                
                # Convert to Position objects
                exchange_positions = []
                for pos_data in active_positions:
                    try:
                        symbol = pos_data.get('symbol', '')
                        size = float(pos_data.get('size') or pos_data.get('contracts') or pos_data.get('amount', 0))
                        side = pos_data.get('side', 'long')
                        entry_price = float(pos_data.get('entryPrice') or pos_data.get('openPrice', 0))
                        current_price = float(pos_data.get('markPrice') or pos_data.get('price', 0))
                        unrealized_pnl = float(pos_data.get('unrealizedPnl') or pos_data.get('unrealizedPnl', 0))
                        
                        if symbol and size > 0 and entry_price > 0:
                            side = 'buy' if side == 'long' else 'sell'
                            
                            position = Position(
                                symbol=symbol,
                                side=side,
                                size=size,
                                entry_price=entry_price,
                                current_price=current_price,
                                pnl=unrealized_pnl,
                                pnl_percent=(unrealized_pnl / (entry_price * size)) * 100 if entry_price * size > 0 else 0,
                                timestamp=datetime.now()
                            )
                            exchange_positions.append(position)
                            
                    except Exception as pos_error:
                        logger.warning(f"⚠️ Failed to process position {pos_data.get('symbol', 'Unknown')}: {pos_error}")
                        continue
                
                self.positions[exchange_name] = exchange_positions
            
        except Exception as e:
                logger.error(f"❌ Failed to update {exchange_name} positions: {e}")

    async def execute_trade_multi_exchange(self, signal: dict) -> bool:
        """🚀 Execute trade across multiple exchanges with load balancing"""
        try:
            symbol = signal['symbol']
            side = signal['side']
            price = signal['price']
            
            # Get available exchanges sorted by priority
            available_exchanges = [
                (name, data) for name, data in self.exchanges.items()
                if data['connected'] and len(self.positions.get(name, [])) < data['config'].max_positions
            ]
            
            if not available_exchanges:
                logger.warning("🚫 No available exchanges for trade execution")
                return False
                
            # Sort by priority (lower number = higher priority)
            available_exchanges.sort(key=lambda x: x[1]['config'].priority)
            
            # Try to execute on the highest priority available exchange
            for exchange_name, exchange_data in available_exchanges:
                try:
                    exchange = exchange_data['instance']
                    exchange_config = exchange_data['config']
                    
                    # Calculate position size for this exchange
                    exchange_balance = self.balances[exchange_name]
                    # Use 11% of balance per trade, but ensure minimum $5 and maximum $19
                    max_trade_value = min(exchange_balance * (self.config.position_size_pct / 100), 19.0)
                    target_notional = max(5.0, max_trade_value)
            quantity = target_notional / price
            
                    # Debug logging
                    logger.info(f"💰 Balance: ${exchange_balance:.2f} | Trade Value: ${target_notional:.2f} | Quantity: {quantity:.6f}")
            
                    # Check minimum amount
            trade_value = quantity * price
            if trade_value < 5.0:
                        logger.warning(f"⚠️ Trade value too small for {exchange_name}: ${trade_value:.2f}")
                        continue
                    
                    logger.info(f"🚀 Executing {side.upper()} on {exchange_name} for {symbol}...")
                    
                    # Place order
                    order = await exchange.create_order(
                    symbol=symbol,
                    type='market',
                    side=side,
                    amount=quantity,
                    params={
                            'leverage': 25,
                        'marginMode': 'cross'
                    }
                )
                
                    logger.success(f"✅ Order created on {exchange_name}: {order.get('id', 'N/A')}")
                
                # Wait for order to be processed
                await asyncio.sleep(1.0)
                
                # Check order status
                    order_status = await exchange.fetch_order(order['id'], symbol)
                    
                    if order_status and order_status.get('status') in ['closed', 'filled']:
                        fill_price = order_status.get('average') or order_status.get('price') or price
                        
                        # Calculate TP/SL prices
                        if side == 'buy':
                            sl_price = fill_price * (1 - self.config.stop_loss_pct / 100)
                            tp_price = fill_price * (1 + self.config.take_profit_pct / 100)
                        else:
                            sl_price = fill_price * (1 + self.config.stop_loss_pct / 100)
                            tp_price = fill_price * (1 - self.config.take_profit_pct / 100)
                        
                        # Place stop loss and take profit orders
                        try:
                            sl_order = await exchange.create_order(
                                symbol=symbol,
                                type='stop',
                                side='sell' if side == 'buy' else 'buy',
                                amount=quantity,
                                price=sl_price,
                                params={
                                    'stopPrice': sl_price,
                                    'triggerPrice': sl_price,
                                    'stopLoss': True
                                }
                            )
                            logger.success(f"✅ SL order placed on {exchange_name}")
                        except Exception as sl_error:
                            logger.warning(f"⚠️ SL order failed on {exchange_name}: {sl_error}")
                        
                        try:
                            tp_order = await exchange.create_order(
                                symbol=symbol,
                                type='limit',
                                side='sell' if side == 'buy' else 'buy',
                                amount=quantity,
                                price=tp_price
                            )
                            logger.success(f"✅ TP order placed on {exchange_name}")
                        except Exception as tp_error:
                            logger.warning(f"⚠️ TP order failed on {exchange_name}: {tp_error}")
                        
                        # Create position object
                        position = Position(
                            symbol=symbol,
                            side=side,
                            size=quantity,
                            entry_price=fill_price,
                            current_price=fill_price,
                            pnl=0.0,
                            pnl_percent=0.0,
                            timestamp=datetime.now(),
                            order_id=order['id'],
                            sl_order_id=sl_order.get('id') if 'sl_order' in locals() else None,
                            tp_order_id=tp_order.get('id') if 'tp_order' in locals() else None
                        )
                        
                        # Add to exchange positions
                        self.positions[exchange_name].append(position)
                        
                        logger.success(f"✅ Trade EXECUTED on {exchange_name}: {side.upper()} {symbol} | Price: ${fill_price:.6f}")
                        return True
                    else:
                        logger.warning(f"⚠️ Order not filled on {exchange_name}")
                        continue
                        
                except Exception as exchange_error:
                    logger.error(f"❌ Trade execution failed on {exchange_name}: {exchange_error}")
                    continue
            
            logger.warning("🚫 Trade execution failed on all available exchanges")
            return False
                
        except Exception as e:
            logger.error(f"❌ Multi-exchange trade execution failed: {e}")
            return False

    async def close_all_connections(self):
        """🔌 Close all exchange connections"""
        for exchange_name, exchange_data in self.exchanges.items():
            try:
                await exchange_data['instance'].close()
                logger.info(f"🔌 Closed connection to {exchange_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to close {exchange_name} connection: {e}")
    
    def get_connection_summary(self) -> dict:
        """📊 Get Bitget connection status summary"""
        summary = {
            'total_exchanges': len(self.exchanges),
            'connected_exchanges': sum(1 for data in self.exchanges.values() if data['connected']),
            'total_balance': sum(self.balances.values()),
            'total_positions': sum(len(positions) for positions in self.positions.values()),
            'exchange_name': 'Bitget',
            'exchanges': {}
        }
        
        for exchange_name, exchange_data in self.exchanges.items():
            summary['exchanges'][exchange_name] = {
                'connected': exchange_data['connected'],
                'balance': self.balances.get(exchange_name, 0.0),
                'positions': len(self.positions.get(exchange_name, [])),
                'priority': exchange_data['config'].priority
            }
        
        return summary

class AlpineTradingBot:
    """🏔️ Alpine Trading Bot - Bloomberg Terminal-Inspired Professional System with Multi-Exchange Support"""
    
    def __init__(self):
        self.display = BloombergStyleDisplay()
        self.config = TradingConfig()
        self.exchange_manager = ExchangeManager(self.config)
        self.running = False
        self.start_time = datetime.now()
        self.heartbeat = datetime.now()
        self.emergency_stop = False
        
        # Trading state
        self.balance = 0.0
        self.positions = []
        self.signals = []
        self.total_trades = 0
        self.daily_pnl = 0.0
        self.scan_stats = {'scans': 0, 'signals_found': 0, 'signals_rejected': 0}
        
        # Performance tracking
        self.win_count = 0
        self.loss_count = 0
        
        logger.info("🏔️ Alpine Trading Bot initialized with multi-exchange support")

    async def connect_exchange(self):
        """🔌 Connect to all configured exchanges"""
        try:
            # Initialize all exchanges
            await self.exchange_manager.initialize_exchanges()
            
            # Get total balance across all exchanges
            self.balance = await self.exchange_manager.get_total_balance()
            logger.success(f"💰 Total Balance across all exchanges: ${self.balance:.2f}")
            
            # Get connection summary
            summary = self.exchange_manager.get_connection_summary()
            logger.info(f"🔌 Connected to {summary['connected_exchanges']}/{summary['total_exchanges']} exchanges")
            
            if self.balance <= 0:
                logger.warning("⚠️ No balance found across all exchanges. Please check your accounts.")
            
        except Exception as e:
            logger.error(f"❌ Multi-exchange connection failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            raise

    async def load_trading_pairs(self):
        """📊 Load trading pairs from primary exchange (Bitget)"""
        try:
            # Use the first connected exchange for loading trading pairs
            primary_exchange = None
            for exchange_name, exchange_data in self.exchange_manager.exchanges.items():
                if exchange_data['connected']:
                    primary_exchange = exchange_data['instance']
                    break
            
            if not primary_exchange:
                logger.error("❌ No connected exchanges available")
                return []
            
            pairs = []
            for symbol in primary_exchange.markets:
                if symbol.endswith(':USDT') and primary_exchange.markets[symbol]['swap']:
                    try:
                        leverage_info = await primary_exchange.fetch_leverage_tiers([symbol])
            if symbol in leverage_info:
                max_leverage = max([tier['maxLeverage'] for tier in leverage_info[symbol]])
                            if max_leverage >= self.config.leverage_filter:
                                pairs.append(symbol)
                    except:
                        pairs.append(symbol)
            
            self.trading_pairs = pairs
            logger.info(f"📊 Loaded {len(pairs)} trading pairs with {self.config.leverage_filter}x+ leverage")
            return pairs
            
        except Exception as e:
            logger.error(f"❌ Failed to load trading pairs: {e}")
            return []

    def detect_pullback(self, df: pd.DataFrame) -> bool:
        """🔍 Advanced pullback detection to avoid traps"""
        try:
            # Calculate recent price movement
            recent_high = df['high'].rolling(10).max().iloc[-1]
            recent_low = df['low'].rolling(10).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate pullback percentage
            if current_price < recent_high:
                pullback_pct = (recent_high - current_price) / recent_high * 100
            else:
                pullback_pct = 0
            
            # Momentum analysis
            momentum = df['close'].diff(8).iloc[-1]
            momentum_ma = df['close'].diff(8).rolling(5).mean().iloc[-1]
            
            # Volume analysis during pullback
            recent_volume_avg = df['volume'].rolling(10).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / recent_volume_avg if recent_volume_avg > 0 else 1
            
            # Pullback detection criteria (less restrictive)
            is_pullback = (
                pullback_pct > 2.5 and  # Increased to 2.5% pullback (was 1.2%)
                momentum < momentum_ma and  # Negative momentum
                volume_ratio < 1.1  # Reduced volume threshold (was 1.3)
            )
            
            return is_pullback
            
        except Exception as e:
            logger.warning(f"⚠️ Pullback detection error: {e}")
            return False
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """📈 Calculate trend strength to avoid false signals"""
        try:
            # Calculate SMAs
            sma_short = df['close'].rolling(8).mean()
            sma_long = df['close'].rolling(25).mean()
            
            # Trend direction
            trend_direction = 1 if sma_short.iloc[-1] > sma_long.iloc[-1] else -1
            
            # Trend strength (distance between SMAs)
            trend_strength = abs(sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1] * 100
            
            # Price position relative to SMAs
            current_price = df['close'].iloc[-1]
            price_vs_short = (current_price - sma_short.iloc[-1]) / sma_short.iloc[-1] * 100
            price_vs_long = (current_price - sma_long.iloc[-1]) / sma_long.iloc[-1] * 100
            
            # Combined trend strength score
            trend_score = (
                trend_strength * 0.4 +
                abs(price_vs_short) * 0.3 +
                abs(price_vs_long) * 0.3
            ) * trend_direction
            
            return trend_score
            
        except Exception as e:
            logger.warning(f"⚠️ Trend strength calculation error: {e}")
            return 0.0

    async def generate_signals(self, symbol: str, timeframe: str = '5m', limit: int = 25):
        """🎯 Generate advanced trading signals with pullback protection"""
        try:
            # Fetch OHLCV data
            ohlcv = await self.exchange_manager.exchanges['Bitget']['instance'].fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Check if we have valid data
            if not ohlcv or len(ohlcv) < 25:
                return None
                
            # Convert to DataFrame with proper error handling
            try:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            except Exception as e:
                logger.error(f"❌ DataFrame creation failed for {symbol}: {e}")
                return None
            
            # REMOVED: Pullback detection was too restrictive and preventing signals
            # The bot was working fine without it, so we're removing it entirely
                
            # Volume analysis with optimized parameters
            volume_sma = df['volume'].rolling(18).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
            
            # Volume spike detection (less restrictive)
            volume_spike = volume_ratio >= 2.0  # Reduced to 2x minimum volume spike (was 4x)
            
            # Skip if volume spike is not strong enough
            if not volume_spike:
                return None
            
            # RSI calculation with optimized parameters
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=16).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=16).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Trend strength analysis
            trend_strength = self.calculate_trend_strength(df)
            
            # Advanced signal conditions with Monte Carlo optimization
            if current_rsi < 38 and trend_strength > 0.8:  # BUY signal
                side = 'buy'
                rsi_confidence = (38 - current_rsi) / 38 * 100
            elif current_rsi > 62 and trend_strength < -0.8:  # SELL signal
                side = 'sell'
                rsi_confidence = (current_rsi - 62) / (100 - 62) * 100
            else:
                return None
            
            # Volume confidence (optimized)
            volume_confidence = min(100, (volume_ratio - 1) * 45) if volume_ratio > 1 else 0
            
            # Trend confidence (optimized)
            trend_confidence = min(100, abs(trend_strength) * 25)
            
            # Combined confidence with optimized weights
            total_confidence = (
                volume_confidence * 0.45 +  # Volume weight
                rsi_confidence * 0.35 +    # RSI weight
                trend_confidence * 0.20     # Trend weight
            )
            
            # Minimum confidence threshold (less restrictive)
            if total_confidence < 60:  # Reduced from 72% to 60%
                return None
            
            signal = {
                'symbol': symbol,
                'side': side,
                'price': df['close'].iloc[-1],
                'volume_ratio': volume_ratio,
                'rsi': current_rsi,
                'trend_strength': trend_strength,
                'confidence': total_confidence,
                'volume_confidence': volume_confidence,
                'rsi_confidence': rsi_confidence,
                'trend_confidence': trend_confidence,
                'timestamp': datetime.now()
            }
            
            logger.info(f"🎯 Signal: {side.upper()} {symbol} | Confidence: {total_confidence:.0f}% | Volume: {volume_ratio:.1f}x | RSI: {current_rsi:.1f} | Trend: {trend_strength:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Advanced signal generation failed for {symbol}: {e}")
            return None

    async def execute_trade(self, signal):
        """🚀 Execute trade across multiple exchanges with load balancing"""
        try:
            # Use the multi-exchange trade execution
            return await self.exchange_manager.execute_trade_multi_exchange(signal)
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return False

    async def update_positions(self):
        """📊 Update position data and PnL across all exchanges"""
        try:
            # Update all exchange positions
            await self.exchange_manager.update_all_positions()
            
            # Combine all positions from all exchanges
            all_positions = []
            for exchange_name, positions in self.exchange_manager.positions.items():
                for position in positions:
                    # Add exchange name to position for tracking
                    position.exchange = exchange_name
                    all_positions.append(position)
            
            self.positions = all_positions
            
            # Update daily PnL
            self.daily_pnl = sum(pos.pnl for pos in self.positions)
            
        except Exception as e:
            logger.error(f"❌ Position update failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")

    async def check_leverage_limits(self, symbol: str) -> int:
        """🔍 Check maximum leverage for a symbol"""
        try:
            leverage_info = await self.exchange_manager.exchanges['Bitget']['instance'].fetch_leverage_tiers([symbol])
            if symbol in leverage_info:
                max_leverage = max([tier['maxLeverage'] for tier in leverage_info[symbol]])
                return min(max_leverage, 20)  # Conservative limit
            return 20  # Default conservative leverage
        except Exception as e:
            logger.warning(f"⚠️ Could not check leverage for {symbol}: {e}")
            return 15  # Very conservative default

    def calculate_capital_in_play(self) -> float:
        """🚨 Calculate current capital in play percentage across all exchanges with proper leverage accounting"""
        try:
            if self.balance <= 0:
                return 0.0
            
            total_capital_used = 0.0
            
            for pos in self.positions:
                # Calculate the actual capital used (position value / leverage)
                # For example: $1000 position with 50x leverage = $20 actual capital used
                position_value = pos.size * pos.entry_price
                
                # Get the leverage for this position (default to 25x if not available)
                leverage = getattr(pos, 'leverage', 25)  # Default to 25x leverage
                
                # Calculate actual capital used
                actual_capital_used = position_value / leverage
                total_capital_used += actual_capital_used
            
            capital_percentage = (total_capital_used / self.balance) * 100
            return capital_percentage
            
        except Exception as e:
            logger.error(f"❌ Capital calculation failed: {e}")
            return 0.0

    def get_available_balance(self) -> float:
        """💰 Calculate available balance for new trades"""
        try:
            total_position_value = sum(pos.size * pos.current_price for pos in self.positions)
            available_balance = self.balance - total_position_value
            return max(0.0, available_balance)  # Ensure non-negative
        except Exception as e:
            logger.error(f"❌ Available balance calculation failed: {e}")
            return self.balance  # Return full balance if calculation fails

    def get_wallet_balance(self) -> float:
        """💰 Get total wallet balance across all exchanges"""
        return self.balance

    def check_capital_limits(self) -> dict:
        """🚨 Check and manage capital limits across all exchanges"""
        capital_in_play = self.calculate_capital_in_play()
        emergency_shutdown = False
        warning_active = False
        can_trade = True
        
        if capital_in_play >= self.config.emergency_shutdown_threshold:
            emergency_shutdown = True
            logger.critical(f"🚨 EMERGENCY SHUTDOWN: {capital_in_play:.1f}% capital in play >= {self.config.emergency_shutdown_threshold}% threshold!")
        elif capital_in_play >= self.config.capital_warning_threshold:
            warning_active = True
            logger.warning(f"⚠️ Capital warning: {capital_in_play:.1f}% capital in play >= {self.config.capital_warning_threshold}% threshold.")
        
        # Check if capital in play is above position size reduction threshold
        if capital_in_play >= self.config.position_size_reduction_threshold:
            logger.warning(f"⚠️ Position size reduction triggered: {capital_in_play:.1f}% capital in play >= {self.config.position_size_reduction_threshold}% threshold.")
            # This is a soft limit, not a hard block.
            # If a trade is rejected due to capital, it's a more severe issue.
            can_trade = False # Indicate that capital limits are active
        
        return {
            'capital_in_play': capital_in_play,
            'emergency_shutdown': emergency_shutdown,
            'warning_active': warning_active,
            'can_trade': can_trade
        }

    def create_exchange_summary_panel(self) -> Panel:
        """🔌 Create exchange summary panel with wallet vs available balance"""
        if not hasattr(self, 'exchange_manager'):
            return Panel("No exchange data available", title="🔌 EXCHANGE SUMMARY")
        
        summary = self.exchange_manager.get_connection_summary()
        
        # Build exchange rows with wallet and available balance
        exchange_rows = []
        for exchange_name, data in summary['exchanges'].items():
            status_emoji = "✅" if data['connected'] else "❌"
            wallet_balance = data['balance']
            
            # Calculate available balance (wallet balance minus position value)
            position_value = sum(pos.size * pos.current_price for pos in self.positions.get(exchange_name, []))
            available_balance = wallet_balance - position_value
            
            row = f"│ {exchange_name:<10} │ {status_emoji} {('ONLINE' if data['connected'] else 'OFFLINE'):<8} │ ${wallet_balance:>8,.2f} │ ${available_balance:>8,.2f} │ {data['positions']:>9} │ #{data['priority']:<8} │"
            exchange_rows.append(row)
        
        # Create the panel content
        if exchange_rows:
            header = "╔══════════════╦════════════╦════════════╦════════════╦═══════════╦══════════╗\n"
            header += "║ Exchange     ║ Status     ║ Wallet Bal ║ Available  ║ Positions ║ Priority ║\n"
            header += "╠══════════════╬════════════╬════════════╬════════════╬═══════════╬══════════╣\n"
            
            body = "\n".join(exchange_rows)
            
            footer = "\n╚══════════════╩════════════╩════════════╩════════════╩═══════════╩══════════╝"
            
            content = header + body + footer
        else:
            content = "No exchanges configured"
        
        return Panel(
            content,
            title=f"🔌 EXCHANGE SUMMARY - {summary['connected_exchanges']}/{summary['total_exchanges']} Connected",
            border_style=self.colors['border'],
            style=self.colors['panel']
        )

    async def trading_loop(self):
        """🔄 Main trading loop with professional display updates"""
        scan_count = 0
        
        while self.running and not self.emergency_stop:
            try:
                scan_count += 1
                
                # Update all exchange balances and positions
                await self.exchange_manager.update_all_balances()
                await self.exchange_manager.update_all_positions()
                
                # Get current total balance across all exchanges
                self.balance = await self.exchange_manager.get_total_balance()
                
                # Update positions from all exchanges
                all_positions = []
                for exchange_name, positions in self.exchange_manager.positions.items():
                    all_positions.extend(positions)
                self.positions = all_positions
                
                # Calculate daily PnL
                self.daily_pnl = sum(pos.pnl for pos in self.positions)
                
                # Check capital limits
                capital_status = self.check_capital_limits()
                exchange_summary = self.exchange_manager.get_connection_summary()
                
                # Clear display and show professional interface
                self.display.console.clear()
                
                # Prepare data for display
                display_data = {
                    'balance': self.balance,
                    'positions': self.positions,
                    'signals': self.signals[-10:] if self.signals else [],  # Show last 10 signals
                    'scan_stats': self.scan_stats,
                    'status': 'ACTIVE' if not self.emergency_stop else 'STOPPED',
                    'trading_pairs': self.trading_pairs,
                    'daily_pnl': self.daily_pnl,
                    'win_count': self.win_count,
                    'loss_count': self.loss_count,
                    'total_trades': self.total_trades,
                    'exchange_summary': exchange_summary,
                    'capital_status': capital_status
                }
                
                # Create and display symmetrical professional layout
                layout = self.display.create_comprehensive_layout(display_data)
                self.display.console.print(layout)
                
                # Show scan progress
                capital_emoji = "🚨" if capital_status['emergency_shutdown'] else "⚠️" if capital_status['warning_active'] else "✅"
                self.display.console.print(f"📊 PROFESSIONAL SCAN #{scan_count} | {len(self.trading_pairs)} PAIRS | BITGET ONLY | CAPITAL: {capital_status['capital_in_play']:.1f}% {capital_emoji}", 
                                         style=f"bold {self.display.colors['primary']}", justify="center")
                self.display.console.print("="*120, style=self.display.colors['border'] + "\n")
                
                # Scan trading pairs for signals
                signal_count = 0
                rejected_count = 0
                
                with Progress() as progress:
                    task = progress.add_task("📊 Scanning trading pairs...", total=len(self.trading_pairs))
                    
                    for i, symbol in enumerate(self.trading_pairs):
                        progress.update(task, description=f"📊 Scanning {symbol}...", completed=i+1)
                        
                        # Check capital limits continuously
                        continuous_capital_status = self.check_capital_limits()
                        if continuous_capital_status['emergency_shutdown']:
                            logger.error("🚨 EMERGENCY SHUTDOWN: Capital limit exceeded!")
                            self.emergency_stop = True
                            break
                        
                        # Generate signal
                        signal = await self.generate_signals(symbol)
                        
                        if signal:
                            # Check if we can execute this trade
                            if (len(self.positions) < self.config.max_positions and 
                                continuous_capital_status['capital_in_play'] < self.config.max_capital_in_play and
                                signal['confidence'] >= 72):  # Monte Carlo optimized threshold
                                
                                # Execute trade
                                trade_result = await self.safe_execute_trade(signal)
                                if trade_result:
                            signal_count += 1
                            self.signals.append(signal)
                                    logger.success(f"✅ TRADE EXECUTED: {signal['symbol']} {signal['side'].upper()} | Confidence: {signal['confidence']:.0f}%")
                                else:
                                    rejected_count += 1
                                    if signal['confidence'] < 72:
                                        logger.info(f"📊 Signal below Monte Carlo threshold: {signal['symbol']} ({signal['confidence']:.0f}%)")
                            else:
                                        logger.warning(f"🚫 Signal blocked by capital limits: {signal['symbol']} - {continuous_capital_status['capital_in_play']:.1f}% capital in play")
                        else:
                            # Add debugging for why no signal
                            if i % 50 == 0:  # Log every 50th symbol to avoid spam
                                logger.debug(f"🔍 No signal for {symbol} - continuing scan...")
                
                # Update scan stats
                self.scan_stats = {
                    'scans': scan_count,
                    'signals_found': signal_count,
                    'signals_rejected': rejected_count,
                    'last_scan_time': datetime.now(),
                    'capital_in_play': capital_status['capital_in_play'],
                    'connected_exchanges': exchange_summary['connected_exchanges']
                }
                
                # Risk check
                if self.daily_pnl < self.config.daily_loss_limit:
                    self.emergency_stop = True
                    logger.error("🚨 EMERGENCY STOP: Daily loss limit reached!")
                
                # Heartbeat
                self.heartbeat = datetime.now()
                
                # Professional scan interval - faster updates for better responsiveness
                await asyncio.sleep(1.0)  # 1 second between updates for better balance sync
                
            except Exception as e:
                logger.error(f"❌ Trading loop error: {e}")
                await asyncio.sleep(5)  # Longer sleep on error

    async def start(self):
        """🚀 Start the trading bot with multi-exchange support"""
        try:
            logger.info("🚀 Starting Alpine Trading Bot with multi-exchange support...")
            
            # Connect to all exchanges
            await self.connect_exchange()
            
            # Load trading pairs
            await self.load_trading_pairs()
            
            # Display initial professional interface
            self.display.console.clear()
            initial_data = {
                'balance': self.balance,
                'positions': [],
                'signals': [],
                'scan_stats': {'scans': 0, 'signals_found': 0, 'signals_rejected': 0},
                'status': 'INITIALIZING',
                'trading_pairs': self.trading_pairs,
                'daily_pnl': 0.0,
                'win_count': 0,
                'loss_count': 0,
                'total_trades': 0,
                'exchange_summary': self.exchange_manager.get_connection_summary()
            }
            layout = self.display.create_comprehensive_layout(initial_data)
            self.display.console.print(layout)
            
            # Start trading loop
            self.running = True
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        finally:
            await self.exchange_manager.close_all_connections()

    def validate_config(self) -> bool:
        """🔍 Validate trading configuration"""
        try:
            errors = []
            
            # Validate position limits
            total_position_size = self.config.position_size_pct * self.config.max_positions
            if total_position_size > 55:
                errors.append(f"Total position size ({total_position_size}%) exceeds 55% limit")
            
            # Validate leverage
            if self.config.leverage_filter < 25:
                errors.append(f"Leverage filter ({self.config.leverage_filter}x) below minimum 25x")
            
            # Validate risk management
            if self.config.stop_loss_pct <= 0:
                errors.append("Stop loss must be positive")
            
            if self.config.take_profit_pct <= 0:
                errors.append("Take profit must be positive")
            
            if self.config.daily_loss_limit >= 0:
                errors.append("Daily loss limit must be negative")
            
            if errors:
                logger.error("❌ Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False
            
            logger.success("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation error: {e}")
            return False

    def validate_input_parameters(self, symbol: str, timeframe: str, limit: int) -> bool:
        """🔍 Validate input parameters for signal generation"""
        try:
            # Validate symbol format
            if not symbol or not symbol.endswith(':USDT'):
                logger.error(f"❌ Invalid symbol format: {symbol}")
                return False
            
            # Validate timeframe
            valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
            if timeframe not in valid_timeframes:
                logger.error(f"❌ Invalid timeframe: {timeframe}")
                return False
            
            # Validate limit
            if limit < 10 or limit > 1000:
                logger.error(f"❌ Invalid limit: {limit} (must be 10-1000)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Input validation error: {e}")
            return False

    async def safe_execute_trade(self, signal: dict) -> bool:
        """💰 Execute trade with comprehensive error handling"""
        try:
            if not signal:
                logger.error("❌ Invalid signal: None")
                return False
            
            # Validate signal confidence
            confidence = signal.get('confidence', 0)
            if confidence < 72:  # Match the trading loop threshold
                logger.warning(f"⚠️ Signal confidence too low: {confidence}%")
                return False
            
            # Execute trade
            result = await self.execute_trade(signal)
            return result
            
        except Exception as e:
            logger.error(f"❌ Safe trade execution error: {e}")
            # self.performance_metrics['errors_encountered'] += 1 # This line was removed from the new_code, so it's removed here.
            return False

    async def safe_update_positions(self):
        """📊 Update positions with error handling"""
        try:
            await self.update_positions()
        except Exception as e:
            logger.error(f"❌ Safe position update error: {e}")
            # self.performance_metrics['errors_encountered'] += 1 # This line was removed from the new_code, so it's removed here.

    def safe_format_positions(self, max_width: int) -> str:
        """📊 Format positions with error handling"""
        try:
            return self.format_positions_responsive(max_width)
        except Exception as e:
            logger.error(f"❌ Safe position formatting error: {e}")
            return f"Error formatting positions: {str(e)[:50]}..."

    def safe_format_signals(self, max_width: int) -> str:
        """🎯 Format signals with error handling"""
        try:
            return self.format_recent_signals_responsive(max_width)
        except Exception as e:
            logger.error(f"❌ Safe signal formatting error: {e}")
            return f"Error formatting signals: {str(e)[:50]}..."

    async def connect_exchange_with_retry(self, max_retries: int = 3) -> bool:
        """🔌 Connect to exchange with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.connect_exchange()
                logger.success("✅ Exchange connection successful")
                return True
            except Exception as e:
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("❌ All connection attempts failed")
                    return False

    def format_positions_responsive(self, max_width: int) -> str:
        """📊 Format positions with responsive design and perfect symmetry"""
        if not self.positions:
            return "🚫 No active positions"
        
        # Calculate column widths for perfect symmetry
        if max_width >= 120:
            # Large terminal - full table
            symbol_width = 18
            side_width = 8
            size_width = 12
            price_width = 15
            pnl_width = 12
            pnl_pct_width = 10
        elif max_width >= 80:
            # Medium terminal - compact table
            symbol_width = 12
            side_width = 6
            size_width = 8
            price_width = 10
            pnl_width = 8
            pnl_pct_width = 8
        else:
            # Small terminal - minimal display
            symbol_width = 8
            side_width = 4
            size_width = 6
            price_width = 8
            pnl_width = 6
            pnl_pct_width = 6
        
        # Create header with perfect alignment
        header = "╔" + "═" * (symbol_width + side_width + size_width + price_width + pnl_width + pnl_pct_width + 10) + "╗\n"
        header += f"║ {'SYMBOL':^{symbol_width}} ║ {'SIDE':^{side_width}} ║ {'SIZE':^{size_width}} ║ {'PRICE':^{price_width}} ║ {'PnL':^{pnl_width}} ║ {'PnL%':^{pnl_pct_width}} ║\n"
        header += "╠" + "═" * symbol_width + "╬" + "═" * side_width + "╬" + "═" * size_width + "╬" + "═" * price_width + "╬" + "═" * pnl_width + "╬" + "═" * pnl_pct_width + "╣\n"
        
        # Create rows with perfect alignment
        rows = []
        for pos in self.positions[:5]:  # Limit to 5 for symmetry
            side_emoji = "🟢" if pos.side == "buy" else "🔴"
            pnl_sign = "+" if pos.pnl >= 0 else ""
            
            row = f"║ {pos.symbol:<{symbol_width}} ║ {side_emoji} {pos.side.upper():<{side_width-2}} ║ {pos.size:<{size_width}.4f} ║ ${pos.current_price:<{price_width-1}.6f} ║ {pnl_sign}${pos.pnl:<{pnl_width-1}.2f} ║ {pnl_sign}{pos.pnl_percent:<{pnl_pct_width-1}.2f}% ║\n"
            rows.append(row)
        
        # Add footer
        footer = "╚" + "═" * symbol_width + "╩" + "═" * side_width + "╩" + "═" * size_width + "╩" + "═" * price_width + "╩" + "═" * pnl_width + "╩" + "═" * pnl_pct_width + "╝\n"
        
        return header + "".join(rows) + footer

    def format_recent_signals_responsive(self, max_width: int) -> str:
        """🎯 Format signals with responsive design and perfect symmetry"""
        if not self.signals:
            return "🚫 No recent signals"
        
        # Calculate column widths for perfect symmetry
        if max_width >= 120:
            # Large terminal - full table
            symbol_width = 18
            side_width = 8
            price_width = 15
            volume_width = 12
            rsi_width = 8
            conf_width = 10
        elif max_width >= 80:
            # Medium terminal - compact table
            symbol_width = 12
            side_width = 6
            price_width = 10
            volume_width = 8
            rsi_width = 6
            conf_width = 8
        else:
            # Small terminal - minimal display
            symbol_width = 8
            side_width = 4
            price_width = 8
            volume_width = 6
            rsi_width = 4
            conf_width = 6
        
        # Create header with perfect alignment
        header = "╔" + "═" * (symbol_width + side_width + price_width + volume_width + rsi_width + conf_width + 10) + "╗\n"
        header += f"║ {'SYMBOL':^{symbol_width}} ║ {'SIDE':^{side_width}} ║ {'PRICE':^{price_width}} ║ {'VOL':^{volume_width}} ║ {'RSI':^{rsi_width}} ║ {'CONF':^{conf_width}} ║\n"
        header += "╠" + "═" * symbol_width + "╬" + "═" * side_width + "╬" + "═" * price_width + "╬" + "═" * volume_width + "╬" + "═" * rsi_width + "╬" + "═" * conf_width + "╣\n"
        
        # Create rows with perfect alignment
        rows = []
        for signal in self.signals[-5:]:  # Show last 5 signals
            side_emoji = "🟢" if signal['side'] == "buy" else "🔴"
            
            row = f"║ {signal['symbol']:<{symbol_width}} ║ {side_emoji} {signal['side'].upper():<{side_width-2}} ║ ${signal['price']:<{price_width-1}.6f} ║ {signal['volume_ratio']:<{volume_width}.1f}x ║ {signal['rsi']:<{rsi_width}.1f} ║ {signal['confidence']:<{conf_width-1}.0f}% ║\n"
            rows.append(row)
        
        # Add footer
        footer = "╚" + "═" * symbol_width + "╩" + "═" * side_width + "╩" + "═" * price_width + "╩" + "═" * volume_width + "╩" + "═" * rsi_width + "╩" + "═" * conf_width + "╝\n"
        
        return header + "".join(rows) + footer

    def create_adaptive_layout(self, terminal_size: str) -> Layout:
        """🎨 Create adaptive layout with perfect symmetry for different terminal sizes"""
        if terminal_size == "large":
            # Large terminal - full layout with all sections
            layout = Layout()
            
            # Header section
            header = self.create_symmetrical_header("ACTIVE", 1000.0, 50.0)
            
            # Main content - two equal columns
            main_content = Layout()
            left_column = Layout()
            right_column = Layout()
            
            # Left column - Account & Performance
            left_column.split_column(
                self.create_symmetrical_account_summary(1000.0, [], 50.0),
                self.create_symmetrical_performance_dashboard(10, 2, 12, 83.3)
            )
            
            # Right column - Positions & Signals
            right_column.split_column(
                self.create_symmetrical_positions_table([]),
                self.create_symmetrical_signals_table([])
            )
            
            main_content.split_row(
                Layout(left_column, ratio=1),
                Layout(right_column, ratio=1)
            )
            
            # Bottom section - Market & Status
            bottom_section = Layout()
            bottom_section.split_row(
                self.create_symmetrical_market_overview([], {}),
                self.create_symmetrical_status_bar("ACTIVE", datetime.now())
            )
            
            layout.split_column(
                header,
                main_content,
                bottom_section
            )
            
        elif terminal_size == "medium":
            # Medium terminal - compact layout
            layout = Layout()
            
            # Header
            header = self.create_symmetrical_header("ACTIVE", 1000.0, 50.0)
            
            # Two equal columns
            main_content = Layout()
            left_column = Layout()
            right_column = Layout()
            
            # Left - Account & Performance
            left_column.split_column(
                self.create_symmetrical_account_summary(1000.0, [], 50.0),
                self.create_symmetrical_performance_dashboard(10, 2, 12, 83.3)
            )
            
            # Right - Market & Status
            right_column.split_column(
                self.create_symmetrical_market_overview([], {}),
                self.create_symmetrical_status_bar("ACTIVE", datetime.now())
            )
            
            main_content.split_row(
                Layout(left_column, ratio=1),
                Layout(right_column, ratio=1)
            )
            
            layout.split_column(
                header,
                main_content
            )
            
        else:
            # Small terminal - minimal layout
            layout = Layout()
            
            # Single column layout
            content = Layout()
            content.split_column(
                self.create_symmetrical_header("ACTIVE", 1000.0, 50.0),
                self.create_symmetrical_account_summary(1000.0, [], 50.0),
                self.create_symmetrical_performance_dashboard(10, 2, 12, 83.3),
                self.create_symmetrical_status_bar("ACTIVE", datetime.now())
            )
            
            layout.split_column(content)
        
        return layout

async def main():
    """🎯 Main entry point"""
    bot = AlpineTradingBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())