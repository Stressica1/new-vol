"""
🏔️ Alpine Trading Bot - Beautiful Terminal UI
Optimized mint green displays with stable refresh and better spacing
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.padding import Padding
from config import TradingConfig, BOT_NAME, VERSION

class AlpineDisplay:
    """🏔️ Beautiful Alpine Terminal Display System - Optimized for Stability"""
    
    def __init__(self):
        self.console = Console()
        self.config = TradingConfig()
        self.start_time = datetime.now()
        
        # 📊 Trading Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        
        # 🎨 Optimized style constants
        self.mint_green = "#00FFB3"
        self.hunter_green = "#355E3B"
        self.spring_green = "#00FF7F"
        self.peach = "#FFB347"
        self.light_red = "#FF6B6B"
        self.dark_bg = "#1E1E1E"
        
        # 📱 Display optimization
        self.last_refresh = time.time()
        self.refresh_throttle = 0.5  # Minimum seconds between refreshes
        
    def create_header(self) -> Panel:
        """Create stable header with Alpine branding 🏔️"""
        header_text = Text()
        header_text.append("🏔️ ", style="bold white")
        header_text.append("ALPINE", style=f"bold {self.mint_green}")
        header_text.append(" TRADING BOT ", style="bold white")
        header_text.append("🚀", style="bold white")
        
        subtitle = Text()
        subtitle.append(f"Volume Anomaly Strategy | {VERSION} | 90% Success Rate", 
                       style=f"{self.spring_green}")
        
        header_content = Align.center(
            Text.assemble(header_text, "\n", subtitle)
        )
        
        return Panel(
            Padding(header_content, (0, 1)),
            style=f"bold {self.hunter_green}",
            box=box.DOUBLE_EDGE,
            title="🏔️ ALPINE SYSTEM",
            title_align="center"
        )
    
    def create_account_panel(self, balance: float, equity: float, margin: float, free_margin: float) -> Panel:
        """Create account status panel with better spacing 💰"""
        
        # Create account table with better spacing
        account_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        account_table.add_column("Label", style="bold white", width=15)
        account_table.add_column("Value", style=f"bold {self.mint_green}", width=18)
        
        account_table.add_row("💰 Balance:", f"${balance:,.2f}")
        account_table.add_row("📊 Equity:", f"${equity:,.2f}")
        account_table.add_row("🔒 Margin:", f"${margin:,.2f}")
        account_table.add_row("💵 Free:", f"${free_margin:,.2f}")
        
        # Add margin ratio
        margin_ratio = (margin / equity * 100) if equity > 0 else 0
        margin_color = self.light_red if margin_ratio > 80 else self.mint_green
        account_table.add_row("📈 Margin %:", f"{margin_ratio:.1f}%")
        
        return Panel(
            Padding(account_table, (1, 1)),
            title="💰 Account Status",
            border_style=self.hunter_green,
            box=box.ROUNDED
        )
    
    def create_performance_panel(self) -> Panel:
        """Create performance metrics panel with better spacing 📊"""
        
        perf_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        perf_table.add_column("Metric", style="bold white", width=15)
        perf_table.add_column("Value", style=f"bold {self.mint_green}", width=18)
        
        # Calculate win rate
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Format P&L with color
        pnl_color = self.spring_green if self.total_pnl >= 0 else self.light_red
        pnl_emoji = "📈" if self.total_pnl >= 0 else "📉"
        
        perf_table.add_row("🎯 Total Trades:", f"{self.total_trades}")
        perf_table.add_row("✅ Win Rate:", f"{win_rate:.1f}%")
        perf_table.add_row(f"{pnl_emoji} Total P&L:", f"${self.total_pnl:,.2f}")
        perf_table.add_row("📅 Daily P&L:", f"${self.daily_pnl:,.2f}")
        perf_table.add_row("📊 Max DD:", f"{self.max_drawdown:.1f}%")
        
        return Panel(
            Padding(perf_table, (1, 1)),
            title="📊 Performance",
            border_style=self.hunter_green,
            box=box.ROUNDED
        )
    
    def create_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create positions panel with better spacing and formatting 📋"""
        
        if not positions:
            empty_msg = Text("No active positions", style=f"italic {self.peach}")
            return Panel(
                Padding(Align.center(empty_msg), (2, 1)),
                title="📋 Active Positions (0)",
                border_style=self.hunter_green,
                box=box.ROUNDED
            )
        
        pos_table = Table(box=box.SIMPLE, padding=(0, 1))
        pos_table.add_column("Symbol", style="bold white", width=12)
        pos_table.add_column("Side", style="bold", width=6)
        pos_table.add_column("Size", style="white", width=10)
        pos_table.add_column("Entry", style="white", width=10)
        pos_table.add_column("Current", style="white", width=10)
        pos_table.add_column("P&L", style="bold", width=12)
        
        for pos in positions[:10]:  # Show max 10 positions
            symbol = pos.get('symbol', 'N/A').replace('/USDT:USDT', '')
            side = pos.get('side', 'N/A').upper()
            size = pos.get('contracts', 0)
            entry_price = pos.get('entryPrice', 0)
            mark_price = pos.get('markPrice', 0)
            unrealized_pnl = pos.get('unrealizedPnl', 0)
            
            # Color coding
            side_color = self.spring_green if side == 'LONG' else self.light_red
            pnl_color = self.spring_green if unrealized_pnl >= 0 else self.light_red
            pnl_emoji = "💚" if unrealized_pnl >= 0 else "❤️"
            
            pos_table.add_row(
                symbol,
                f"[{side_color}]{side}[/]",
                f"{size:.4f}",
                f"${entry_price:.4f}",
                f"${mark_price:.4f}",
                f"[{pnl_color}]{pnl_emoji}${unrealized_pnl:.2f}[/]"
            )
        
        return Panel(
            Padding(pos_table, (1, 1)),
            title=f"📋 Active Positions ({len(positions)})",
            border_style=self.hunter_green,
            box=box.ROUNDED
        )
    
    def create_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create signals panel with better spacing and formatting 🎯"""
        
        if not signals:
            empty_msg = Text("No recent signals", style=f"italic {self.peach}")
            return Panel(
                Padding(Align.center(empty_msg), (2, 1)),
                title="🎯 Trading Signals (0)",
                border_style=self.hunter_green,
                box=box.ROUNDED
            )
        
        sig_table = Table(box=box.SIMPLE, padding=(0, 1))
        sig_table.add_column("Time", style="white", width=8)
        sig_table.add_column("Symbol", style="bold white", width=10)
        sig_table.add_column("Signal", style="bold", width=10)
        sig_table.add_column("Volume", style="white", width=8)
        sig_table.add_column("Price", style="white", width=10)
        sig_table.add_column("TF", style="white", width=8)
        sig_table.add_column("Status", style="bold", width=10)
        
        for signal in signals[:8]:  # Show max 8 signals
            # Signal type color
            signal_type = signal.get('type', 'UNKNOWN')
            signal_emoji = "📈" if signal_type == 'LONG' else "📉"
            signal_color = self.spring_green if signal_type == 'LONG' else self.light_red
            
            # Volume color
            volume_ratio = signal.get('volume_ratio', 0)
            volume_emoji = "🔥" if volume_ratio > 3.0 else "💧"
            
            # Timeframe display
            tf_str = signal.get('timeframe', 'N/A')
            confluence_count = signal.get('confluence_count', 1)
            tf_display = f"{tf_str} ({confluence_count})" if confluence_count > 1 else tf_str
            
            # Handle both 'time' (datetime object) and 'timestamp' (Unix timestamp) fields
            try:
                if 'time' in signal and signal['time'] is not None:
                    time_str = signal['time'].strftime("%H:%M:%S")
                elif 'timestamp' in signal and signal['timestamp'] is not None:
                    from datetime import datetime
                    time_str = datetime.fromtimestamp(signal['timestamp']).strftime("%H:%M:%S")
                else:
                    time_str = "N/A"
            except (KeyError, ValueError, OSError, TypeError) as e:
                time_str = "N/A"
            
            sig_table.add_row(
                time_str,
                signal['symbol'].replace('/USDT:USDT', ''),
                f"[{signal_color}]{signal_emoji} {signal['type']}[/]",
                f"{volume_emoji} {signal['volume_ratio']:.1f}x",
                f"${signal['price']:.4f}",
                tf_display,
                signal.get('action', 'WAITING')
            )
        
        return Panel(
            Padding(sig_table, (1, 1)),
            title=f"🎯 Trading Signals ({len(signals)})",
            border_style=self.hunter_green,
            box=box.ROUNDED
        )
    
    def create_log_panel(self, logs: List[str]) -> Panel:
        """Create activity log panel with better spacing 📝"""
        
        if not logs:
            empty_msg = Text("No recent activity", style=f"italic {self.peach}")
            return Panel(
                Padding(Align.center(empty_msg), (1, 1)),
                title="📝 Activity Log",
                border_style=self.hunter_green,
                box=box.ROUNDED
            )
        
        log_content = Text()
        for log in logs[-8:]:  # Show last 8 logs
            log_content.append(f"{log}\n", style="white")
        
        return Panel(
            Padding(log_content, (1, 1)),
            title="📝 Activity Log",
            border_style=self.hunter_green,
            box=box.ROUNDED,
            height=10
        )
    
    def create_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create status bar with better spacing ⚡"""
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        uptime_str = f"{int(uptime.total_seconds() // 3600):02d}:{int((uptime.total_seconds() % 3600) // 60):02d}:{int(uptime.total_seconds() % 60):02d}"
        
        # Status with color
        if "ACTIVE" in status:
            status_color = self.spring_green
        elif "HALTED" in status:
            status_color = self.light_red
        elif "DISCONNECTED" in status:
            status_color = self.light_red
        else:
            status_color = self.peach
        
        status_text = Text()
        status_text.append("Status: ", style="bold white")
        status_text.append(status, style=f"bold {status_color}")
        status_text.append(" | ", style="white")
        status_text.append("⏱️ Uptime: ", style="bold white")
        status_text.append(uptime_str, style=f"bold {self.mint_green}")
        status_text.append(" | ", style="white")
        status_text.append("🔄 Updated: ", style="bold white")
        status_text.append(last_update.strftime("%H:%M:%S"), style=f"bold {self.mint_green}")
        
        return Panel(
            Padding(Align.center(status_text), (0, 1)),
            style=f"bold {self.hunter_green}",
            box=box.ROUNDED
        )
    
    def create_layout(self, account_data: Dict, positions: List[Dict], 
                     signals: List[Dict], logs: List[str], status: str) -> Layout:
        """Create optimized layout with better spacing and organization 🎨"""
        
        # Throttle refresh to reduce flashing
        current_time = time.time()
        if current_time - self.last_refresh < self.refresh_throttle:
            time.sleep(0.1)  # Small delay to prevent excessive refreshing
        self.last_refresh = current_time
        
        # Main layout structure
        layout = Layout()
        layout.split_column(
            Layout(self.create_header(), size=6, name="header"),
            Layout(name="main", ratio=1),
            Layout(self.create_status_bar(status, datetime.now()), size=4, name="status")
        )
        
        # Split main area with better proportions
        layout["main"].split_row(
            Layout(name="left_panel", ratio=2),
            Layout(name="right_panel", ratio=3)
        )
        
        # Left panel - Account & Performance
        layout["left_panel"].split_column(
            Layout(self.create_account_panel(
                account_data.get('balance', 0),
                account_data.get('equity', 0),
                account_data.get('margin', 0),
                account_data.get('free_margin', 0)
            ), size=10, name="account"),
            Layout(self.create_performance_panel(), size=10, name="performance"),
            Layout(self.create_log_panel(logs), name="logs")
        )
        
        # Right panel - Positions & Signals
        layout["right_panel"].split_column(
            Layout(self.create_positions_panel(positions), name="positions"),
            Layout(self.create_signals_panel(signals), name="signals")
        )
        
        return layout
    
    def update_stats(self, trade_result: Dict):
        """Update trading statistics with thread safety 📊"""
        self.total_trades += 1
        pnl = trade_result.get('pnl', 0)
        
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.total_pnl += pnl
        self.daily_pnl += pnl  # Reset daily at midnight
        
        # Update max drawdown if necessary
        if pnl < 0:
            current_dd = abs(pnl / self.total_pnl * 100) if self.total_pnl != 0 else 0
            self.max_drawdown = min(self.max_drawdown, -current_dd)