"""
🏔️ Alpine Trading Bot - Beautiful Terminal UI
Mint green displays with hunter green gradients and emojis
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
from config import TradingConfig, BOT_NAME, VERSION

class AlpineDisplay:
    """🏔️ Beautiful Alpine Terminal Display System"""
    
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
        
        # 🎨 Style constants
        self.mint_green = "#00FFB3"
        self.hunter_green = "#355E3B"
        self.spring_green = "#00FF7F"
        self.peach = "#FFB347"
        self.light_red = "#FF6B6B"
        
    def create_header(self) -> Panel:
        """Create beautiful header with Alpine branding 🏔️"""
        header_text = Text()
        header_text.append("🏔️ ", style="bold white")
        header_text.append("ALPINE", style=f"bold {self.mint_green}")
        header_text.append(" TRADING BOT ", style="bold white")
        header_text.append("🚀", style="bold white")
        header_text.append(f"\n{VERSION} | Volume Anomaly Strategy", style=f"italic {self.hunter_green}")
        
        return Panel(
            Align.center(header_text),
            style=f"bold {self.mint_green}",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
    
    def create_account_panel(self, balance: float, equity: float, margin: float, free_margin: float) -> Panel:
        """Create account information panel 💰"""
        
        # Calculate margin level
        margin_level = (equity / margin * 100) if margin > 0 else 0
        
        account_table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        account_table.add_column("💰 Account Info", style="white", width=15)
        account_table.add_column("Value", style=f"bold {self.spring_green}", width=15)
        account_table.add_column("Status", style="white", width=10)
        
        # Balance row
        balance_status = "🟢" if balance > 1000 else "🟡" if balance > 100 else "🔴"
        account_table.add_row("Balance", f"${balance:,.2f}", balance_status)
        
        # Equity row
        equity_status = "🟢" if equity >= balance else "🔴"
        account_table.add_row("Equity", f"${equity:,.2f}", equity_status)
        
        # Margin row
        margin_status = "🟢" if margin_level > 200 else "🟡" if margin_level > 100 else "🔴"
        account_table.add_row("Used Margin", f"${margin:,.2f}", margin_status)
        
        # Free margin row
        free_status = "🟢" if free_margin > margin else "🟡"
        account_table.add_row("Free Margin", f"${free_margin:,.2f}", free_status)
        
        # Margin level row
        account_table.add_row("Margin Level", f"{margin_level:.1f}%", margin_status)
        
        return Panel(
            account_table,
            title="[bold]💰 Account Status",
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}"
        )
    
    def create_performance_panel(self) -> Panel:
        """Create performance statistics panel 📈"""
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        perf_table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        perf_table.add_column("📈 Performance", style="white", width=15)
        perf_table.add_column("Value", style=f"bold {self.spring_green}", width=15)
        perf_table.add_column("Status", style="white", width=10)
        
        # Total P&L
        pnl_status = "🟢" if self.total_pnl > 0 else "🔴" if self.total_pnl < 0 else "🟡"
        pnl_color = self.spring_green if self.total_pnl > 0 else self.light_red
        perf_table.add_row("Total P&L", f"[{pnl_color}]${self.total_pnl:,.2f}[/]", pnl_status)
        
        # Daily P&L
        daily_status = "🟢" if self.daily_pnl > 0 else "🔴" if self.daily_pnl < 0 else "🟡"
        daily_color = self.spring_green if self.daily_pnl > 0 else self.light_red
        perf_table.add_row("Daily P&L", f"[{daily_color}]${self.daily_pnl:,.2f}[/]", daily_status)
        
        # Win Rate
        wr_status = "🟢" if win_rate > 60 else "🟡" if win_rate > 40 else "🔴"
        perf_table.add_row("Win Rate", f"{win_rate:.1f}%", wr_status)
        
        # Total Trades
        perf_table.add_row("Total Trades", str(self.total_trades), "📊")
        
        # Max Drawdown
        dd_status = "🟢" if abs(self.max_drawdown) < 5 else "🟡" if abs(self.max_drawdown) < 15 else "🔴"
        perf_table.add_row("Max Drawdown", f"{self.max_drawdown:.2f}%", dd_status)
        
        return Panel(
            perf_table,
            title="[bold]📈 Performance Metrics",
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}"
        )
    
    def create_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create active positions panel 📋"""
        
        if not positions:
            empty_text = Text("No active positions", style=f"italic {self.hunter_green}")
            return Panel(
                Align.center(empty_text),
                title="[bold]📋 Active Positions",
                style=f"{self.hunter_green}",
                border_style=f"{self.mint_green}"
            )
        
        pos_table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        pos_table.add_column("Symbol", style="white", width=12)
        pos_table.add_column("Side", style="white", width=6)
        pos_table.add_column("Size", style="white", width=10)
        pos_table.add_column("Entry", style="white", width=10)
        pos_table.add_column("Current", style="white", width=10)
        pos_table.add_column("P&L", style="white", width=12)
        pos_table.add_column("Status", style="white", width=8)
        
        for pos in positions[:10]:  # Show max 10 positions
            side_emoji = "🟢" if pos['side'] == 'long' else "🔴"
            side_text = f"{side_emoji} {pos['side'].upper()}"
            
            pnl = pos.get('unrealizedPnl', 0)
            pnl_color = self.spring_green if pnl > 0 else self.light_red if pnl < 0 else "white"
            pnl_status = "💚" if pnl > 0 else "❤️" if pnl < 0 else "💛"
            
            pos_table.add_row(
                pos['symbol'].replace('/USDT:USDT', ''),
                side_text,
                f"{pos['contracts']:.4f}",
                f"${pos['entryPrice']:.4f}",
                f"${pos['markPrice']:.4f}",
                f"[{pnl_color}]${pnl:.2f}[/]",
                pnl_status
            )
        
        return Panel(
            pos_table,
            title=f"[bold]📋 Active Positions ({len(positions)})",
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}"
        )
    
    def create_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create trading signals panel 🎯"""
        
        if not signals:
            empty_text = Text("No recent signals", style=f"italic {self.hunter_green}")
            return Panel(
                Align.center(empty_text),
                title="[bold]🎯 Volume Anomaly Signals",
                style=f"{self.hunter_green}",
                border_style=f"{self.mint_green}"
            )
        
        sig_table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        sig_table.add_column("Time", style="white", width=8)
        sig_table.add_column("Symbol", style="white", width=10)
        sig_table.add_column("Signal", style="white", width=8)
        sig_table.add_column("Volume", style="white", width=12)
        sig_table.add_column("Price", style="white", width=10)
        sig_table.add_column("Action", style="white", width=10)
        
        for signal in signals[-5:]:  # Show last 5 signals
            signal_emoji = "🟢" if signal['type'] == 'LONG' else "🔴"
            volume_emoji = "🟣" if signal.get('anomaly_strength', 1) > 2 else "💥"
            
            sig_table.add_row(
                signal['time'].strftime("%H:%M:%S"),
                signal['symbol'].replace('/USDT:USDT', ''),
                f"{signal_emoji} {signal['type']}",
                f"{volume_emoji} {signal['volume_ratio']:.1f}x",
                f"${signal['price']:.4f}",
                signal.get('action', 'WAITING')
            )
        
        return Panel(
            sig_table,
            title="[bold]🎯 Volume Anomaly Signals",
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}"
        )
    
    def create_log_panel(self, logs: List[str]) -> Panel:
        """Create activity log panel 📝"""
        
        log_text = Text()
        for log in logs[-15:]:  # Show last 15 logs
            log_text.append(f"{log}\n", style="white")
        
        return Panel(
            log_text,
            title="[bold]📝 Activity Log",
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}",
            height=8
        )
    
    def create_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create status bar 🔄"""
        
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        status_text = Text()
        status_text.append("🔄 Status: ", style="white")
        status_text.append(status, style=f"bold {self.spring_green}")
        status_text.append("  ⏱️ Uptime: ", style="white")
        status_text.append(uptime_str, style=f"bold {self.mint_green}")
        status_text.append("  🕐 Last Update: ", style="white")
        status_text.append(last_update.strftime("%H:%M:%S"), style=f"bold {self.peach}")
        
        return Panel(
            Align.center(status_text),
            style=f"{self.hunter_green}",
            border_style=f"{self.mint_green}"
        )
    
    def create_layout(self, account_data: Dict, positions: List[Dict], 
                     signals: List[Dict], logs: List[str], status: str) -> Layout:
        """Create the complete layout 🎨"""
        
        layout = Layout()
        layout.split_column(
            Layout(self.create_header(), size=5, name="header"),
            Layout(name="main", ratio=1),
            Layout(self.create_status_bar(status, datetime.now()), size=3, name="status")
        )
        
        # Split main area
        layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left column
        layout["left"].split_column(
            Layout(self.create_account_panel(
                account_data.get('balance', 0),
                account_data.get('equity', 0),
                account_data.get('margin', 0),
                account_data.get('free_margin', 0)
            ), size=9, name="account"),
            Layout(self.create_performance_panel(), size=9, name="performance"),
            Layout(self.create_log_panel(logs), name="logs")
        )
        
        # Right column
        layout["right"].split_column(
            Layout(self.create_positions_panel(positions), name="positions"),
            Layout(self.create_signals_panel(signals), size=12, name="signals")
        )
        
        return layout
    
    def update_stats(self, trade_result: Dict):
        """Update trading statistics 📊"""
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