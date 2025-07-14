"""
🏔️ Alpine Trading Bot - Next-Generation Terminal UI
Ultra-modern design with neon gradients, real-time analytics, and professional trading interface
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.padding import Padding
from rich.style import Style
from rich.tree import Tree
from rich.rule import Rule
from rich.markdown import Markdown
from rich.syntax import Syntax
from config import TradingConfig, BOT_NAME, VERSION
import numpy as np

class AlpineDisplayV2:
    """🏔️ Next-Generation Alpine Trading Interface - 200x Better Design"""
    
    def __init__(self):
        self.console = Console(width=120, height=40)
        self.config = TradingConfig()
        self.start_time = datetime.now()
        
        # 📊 Enhanced Trading Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.best_trade = 0.0
        self.worst_trade = 0.0
        self.current_streak = 0
        self.max_streak = 0
        
        # 🎨 Next-Generation Color Palette
        self.colors = self.config.COLORS
        
        # 📱 Enhanced Display Optimization
        self.last_refresh = time.time()
        self.refresh_throttle = 0.2  # Ultra-fast refresh for scalping
        self.animation_frame = 0
        
        # 🚀 Performance Metrics
        self.signals_per_minute = 0
        self.execution_latency = 0.0
        self.api_response_time = 0.0
        
        self.console.print(self._create_startup_banner(), style="bold cyan")
    
    def _create_startup_banner(self) -> Panel:
        """🎆 Epic startup banner with ASCII art"""
        banner_text = f"""
[bold cyan]╔═══════════════════════════════════════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]                          [bold gradient(#00FFB3,#7C3AED)]🏔️  ALPINE TRADING BOT V2.0  🏔️[/]                            [bold cyan]║[/]
[bold cyan]║[/]                      [italic]Next-Generation AI-Powered Trading Interface[/]                       [bold cyan]║[/]
[bold cyan]╚═══════════════════════════════════════════════════════════════════════════════════════════════╝[/]

[bold green]🚀 INITIALIZED FEATURES:[/]
├─ [cyan]⚡ 1m/3m Confluence Signal Detection[/]
├─ [cyan]🎯 Dynamic ATR-Based Stop Loss[/]
├─ [cyan]📈 +15% Position Size Boost on Confluence[/]
├─ [cyan]🔥 Real-time Volume Anomaly Analysis[/]
├─ [cyan]💎 Enhanced Risk Management[/]
└─ [cyan]🌈 Ultra-Modern UI Design[/]

[bold yellow]⚡ SYSTEM STATUS: [bold green]OPERATIONAL[/][/]
"""
        return Panel(
            banner_text,
            box=box.DOUBLE,
            style=f"bold {self.colors['gradient_start']}",
            padding=(1, 2)
        )
    
    def create_enhanced_header(self) -> Panel:
        """🎆 Ultra-modern animated header with gradients"""
        uptime = datetime.now() - self.start_time
        uptime_str = f"{int(uptime.total_seconds() // 3600):02d}:{int((uptime.total_seconds() % 3600) // 60):02d}:{int(uptime.total_seconds() % 60):02d}"
        
        # Animated indicators
        self.animation_frame = (self.animation_frame + 1) % 8
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧"
        spinner = spinner_chars[self.animation_frame]
        
        # Win rate calculation
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        
        # Status indicator based on performance
        if win_rate >= 80:
            status_indicator = "🔥 CRUSHING IT"
            status_color = "bold green"
        elif win_rate >= 60:
            status_indicator = "📈 PROFITABLE"
            status_color = "green"
        elif win_rate >= 40:
            status_indicator = "⚖️ BALANCED"
            status_color = "yellow"
        else:
            status_indicator = "🎯 OPTIMIZING"
            status_color = "cyan"
        
        header_content = f"""[bold cyan]{spinner}[/] [{self.colors['gradient_start']}]ALPINE BOT V2.0[/] │ 
[bold]Status:[/] [{status_color}]{status_indicator}[/] │ 
[bold]Uptime:[/] [cyan]{uptime_str}[/] │ 
[bold]Win Rate:[/] [{'green' if win_rate >= 70 else 'yellow' if win_rate >= 50 else 'red'}]{win_rate:.1f}%[/] │ 
[bold]Signals/Min:[/] [bright_blue]{self.signals_per_minute:.1f}[/]"""
        
        return Panel(
            header_content,
            box=box.HEAVY,
            style=f"bold {self.colors['primary']}",
            height=3
        )
    
    def create_advanced_portfolio_panel(self, balance: float, equity: float, margin: float, free_margin: float) -> Panel:
        """💰 Advanced portfolio dashboard with enhanced metrics"""
        
        # Calculate additional metrics
        margin_ratio = (margin / equity * 100) if equity > 0 else 0
        buying_power = free_margin * 10  # Assuming 10x leverage available
        portfolio_health = "EXCELLENT" if margin_ratio < 30 else "GOOD" if margin_ratio < 50 else "CAUTION" if margin_ratio < 70 else "DANGER"
        health_color = "bright_green" if margin_ratio < 30 else "green" if margin_ratio < 50 else "yellow" if margin_ratio < 70 else "red"
        
        # Daily P&L percentage
        daily_pnl_pct = (self.daily_pnl / balance * 100) if balance > 0 else 0
        
        portfolio_table = Table.grid(padding=1)
        portfolio_table.add_column(style="bold cyan", width=15)
        portfolio_table.add_column(style="bold white", width=12, justify="right")
        portfolio_table.add_column(style="cyan", width=8)
        portfolio_table.add_column(style="bold white", width=12, justify="right")
        
        # Portfolio metrics with visual indicators
        portfolio_table.add_row(
            "💎 Balance:", f"${balance:,.2f}", "📊 Equity:", f"${equity:,.2f}"
        )
        portfolio_table.add_row(
            "🔒 Margin:", f"${margin:,.2f}", "💰 Free:", f"${free_margin:,.2f}"
        )
        portfolio_table.add_row(
            "⚡ Power:", f"${buying_power:,.0f}", "🎯 Health:", f"[{health_color}]{portfolio_health}[/]"
        )
        portfolio_table.add_row(
            "📈 Daily P&L:", f"[{'green' if self.daily_pnl >= 0 else 'red'}]${self.daily_pnl:+,.2f}[/]", 
            "📊 Daily %:", f"[{'green' if daily_pnl_pct >= 0 else 'red'}]{daily_pnl_pct:+.2f}%[/]"
        )
        
        # Add margin usage bar
        margin_bar = self._create_progress_bar(margin_ratio, 100, "Margin Usage", health_color)
        
        content = Align.center(portfolio_table) + "\n" + margin_bar
        
        return Panel(
            content,
            title="[bold cyan]💰 PORTFOLIO DASHBOARD[/]",
            box=box.ROUNDED,
            style=f"bold {self.colors['primary']}",
            padding=(1, 2)
        )
    
    def create_performance_dashboard(self) -> Panel:
        """📊 Ultra-detailed performance analytics"""
        
        # Calculate advanced metrics
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        avg_win = (sum([t for t in [self.best_trade] if t > 0]) / max(self.winning_trades, 1)) if self.winning_trades > 0 else 0
        avg_loss = (sum([t for t in [self.worst_trade] if t < 0]) / max(self.losing_trades, 1)) if self.losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        sharpe_ratio = 1.5  # Placeholder - would calculate from actual returns
        
        perf_table = Table.grid(padding=1)
        perf_table.add_column(style="bold yellow", width=16)
        perf_table.add_column(style="bold white", width=10, justify="right")
        perf_table.add_column(style="bold yellow", width=16)
        perf_table.add_column(style="bold white", width=10, justify="right")
        
        perf_table.add_row(
            "🎯 Total Trades:", f"{self.total_trades}", 
            "📈 Win Rate:", f"[{'green' if win_rate >= 70 else 'yellow' if win_rate >= 50 else 'red'}]{win_rate:.1f}%[/]"
        )
        perf_table.add_row(
            "✅ Winners:", f"[green]{self.winning_trades}[/]", 
            "❌ Losers:", f"[red]{self.losing_trades}[/]"
        )
        perf_table.add_row(
            "🚀 Best Trade:", f"[bright_green]${self.best_trade:+.2f}[/]", 
            "📉 Worst Trade:", f"[red]${self.worst_trade:+.2f}[/]"
        )
        perf_table.add_row(
            "🔥 Current Streak:", f"[{'green' if self.current_streak >= 0 else 'red'}]{self.current_streak:+d}[/]", 
            "⭐ Max Streak:", f"[bright_green]{self.max_streak}[/]"
        )
        perf_table.add_row(
            "💎 Profit Factor:", f"[{'bright_green' if profit_factor >= 2 else 'green' if profit_factor >= 1.5 else 'yellow'}]{profit_factor:.2f}[/]", 
            "📊 Sharpe Ratio:", f"[bright_blue]{sharpe_ratio:.2f}[/]"
        )
        
        # Add performance bars
        win_rate_bar = self._create_progress_bar(win_rate, 100, "Win Rate", "green" if win_rate >= 70 else "yellow")
        profit_bar = self._create_progress_bar(min(profit_factor * 33.33, 100), 100, "Profit Factor", "green")
        
        content = Align.center(perf_table) + "\n" + win_rate_bar + "\n" + profit_bar
        
        return Panel(
            content,
            title="[bold yellow]📊 PERFORMANCE ANALYTICS[/]",
            box=box.ROUNDED,
            style=f"bold {self.colors['accent']}",
            padding=(1, 2)
        )
    
    def create_next_gen_positions_panel(self, positions: List[Dict]) -> Panel:
        """🚀 Next-generation positions display with advanced metrics"""
        
        if not positions:
            empty_content = Align.center(
                Text("🌟 No Active Positions\nReady for Next Signal!", style="bold cyan"),
                vertical="middle"
            )
            return Panel(
                empty_content,
                title="[bold green]🎯 ACTIVE POSITIONS[/]",
                box=box.ROUNDED,
                style=f"bold {self.colors['success']}",
                height=8
            )
        
        # Create advanced positions table
        positions_table = Table(box=box.MINIMAL_HEAVY_HEAD)
        positions_table.add_column("Symbol", style="bold cyan", width=12)
        positions_table.add_column("Side", style="bold", width=6)
        positions_table.add_column("Size", style="bold white", width=10, justify="right")
        positions_table.add_column("Entry", style="bold blue", width=10, justify="right")
        positions_table.add_column("Current", style="bold white", width=10, justify="right")
        positions_table.add_column("P&L", style="bold", width=12, justify="right")
        positions_table.add_column("P&L%", style="bold", width=8, justify="right")
        positions_table.add_column("Risk", style="bold", width=8)
        
        total_pnl = 0.0
        
        for position in positions[:8]:  # Show max 8 positions
            symbol = position.get('symbol', 'N/A')
            side = position.get('side', 'N/A')
            size = position.get('size', 0.0)
            entry_price = position.get('entry_price', 0.0)
            current_price = position.get('current_price', 0.0)
            unrealized_pnl = position.get('unrealized_pnl', 0.0)
            
            # Calculate P&L percentage
            pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            if side.upper() == 'SHORT':
                pnl_pct = -pnl_pct
            
            total_pnl += unrealized_pnl
            
            # Risk assessment
            risk_level = "🟢 LOW" if abs(pnl_pct) < 1 else "🟡 MED" if abs(pnl_pct) < 2 else "🔴 HIGH"
            
            # Color coding for P&L
            pnl_color = "bright_green" if unrealized_pnl > 0 else "red" if unrealized_pnl < 0 else "white"
            side_color = "green" if side.upper() == 'LONG' else "red"
            
            positions_table.add_row(
                f"[bold]{symbol}[/]",
                f"[{side_color}]{side.upper()}[/]",
                f"{size:.4f}",
                f"${entry_price:.4f}",
                f"${current_price:.4f}",
                f"[{pnl_color}]${unrealized_pnl:+.2f}[/]",
                f"[{pnl_color}]{pnl_pct:+.2f}%[/]",
                risk_level
            )
        
        # Add total P&L summary
        total_pnl_color = "bright_green" if total_pnl > 0 else "red" if total_pnl < 0 else "white"
        
        footer = f"\n[bold]Total Unrealized P&L: [{total_pnl_color}]${total_pnl:+,.2f}[/] │ Active Positions: [cyan]{len(positions)}[/]"
        
        content = positions_table.render() + footer
        
        return Panel(
            content,
            title="[bold green]🎯 ACTIVE POSITIONS[/]",
            box=box.ROUNDED,
            style=f"bold {self.colors['success']}",
            padding=(0, 1)
        )
    
    def create_advanced_signals_panel(self, signals: List[Dict]) -> Panel:
        """🔍 Advanced signal analysis with confluence detection"""
        
        if not signals:
            empty_content = Align.center(
                Text("🔍 Scanning Markets...\nWaiting for High-Quality Signals", style="bold yellow"),
                vertical="middle"
            )
            return Panel(
                empty_content,
                title="[bold blue]🔍 SIGNAL RADAR[/]",
                box=box.ROUNDED,
                style=f"bold {self.colors['info']}",
                height=12
            )
        
        # Create signals table with enhanced information
        signals_table = Table(box=box.MINIMAL_HEAVY_HEAD)
        signals_table.add_column("Time", style="bold white", width=8)
        signals_table.add_column("Symbol", style="bold cyan", width=12)
        signals_table.add_column("Type", style="bold", width=8)
        signals_table.add_column("Signal", style="bold", width=12)
        signals_table.add_column("Confidence", style="bold", width=10, justify="center")
        signals_table.add_column("Volume", style="bold blue", width=8, justify="right")
        signals_table.add_column("TF", style="bold yellow", width=6)
        signals_table.add_column("Status", style="bold", width=10)
        
        recent_signals = signals[-10:]  # Show last 10 signals
        
        for signal in recent_signals:
            timestamp = signal.get('timestamp', datetime.now())
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp)
            time_str = timestamp.strftime("%H:%M:%S")
            
            symbol = signal.get('symbol', 'N/A')
            signal_type = signal.get('type', 'N/A')
            timeframe = signal.get('timeframe', '1m')
            confidence = signal.get('confidence', 0)
            volume_ratio = signal.get('volume_ratio', 0)
            is_confluence = signal.get('is_confluence', False)
            
            # Enhanced signal classification
            if is_confluence:
                signal_class = "🚀 CONFLUENCE"
                signal_color = "bright_magenta"
            elif confidence >= 90:
                signal_class = "💎 PREMIUM"
                signal_color = "bright_green"
            elif confidence >= 80:
                signal_class = "⭐ STRONG"
                signal_color = "green"
            elif confidence >= 70:
                signal_class = "📈 GOOD"
                signal_color = "yellow"
            else:
                signal_class = "⚠️ WEAK"
                signal_color = "red"
            
            # Color coding
            type_color = "green" if signal_type.upper() == 'LONG' else "red"
            confidence_color = "bright_green" if confidence >= 80 else "green" if confidence >= 70 else "yellow"
            volume_color = "bright_blue" if volume_ratio >= 3 else "blue" if volume_ratio >= 2 else "white"
            
            # Status based on signal quality
            if is_confluence and confidence >= 80:
                status = "🎯 EXECUTE"
                status_color = "bright_green"
            elif confidence >= 85:
                status = "✅ READY"
                status_color = "green"
            elif confidence >= 75:
                status = "⏳ WATCH"
                status_color = "yellow"
            else:
                status = "❌ SKIP"
                status_color = "red"
            
            signals_table.add_row(
                time_str,
                f"[bold]{symbol}[/]",
                f"[{type_color}]{signal_type}[/]",
                f"[{signal_color}]{signal_class}[/]",
                f"[{confidence_color}]{confidence:.0f}%[/]",
                f"[{volume_color}]{volume_ratio:.1f}x[/]",
                f"[yellow]{timeframe}[/]",
                f"[{status_color}]{status}[/]"
            )
        
        # Add signal summary
        confluence_count = sum(1 for s in recent_signals if s.get('is_confluence', False))
        avg_confidence = np.mean([s.get('confidence', 0) for s in recent_signals]) if recent_signals else 0
        
        footer = f"\n[bold]Recent Signals: [cyan]{len(recent_signals)}[/] │ Confluence: [magenta]{confluence_count}[/] │ Avg Confidence: [green]{avg_confidence:.1f}%[/]"
        
        content = signals_table.render() + footer
        
        return Panel(
            content,
            title="[bold blue]🔍 SIGNAL RADAR[/]",
            box=box.ROUNDED,
            style=f"bold {self.colors['info']}",
            padding=(0, 1)
        )
    
    def create_enhanced_log_panel(self, logs: List[str]) -> Panel:
        """📜 Enhanced log display with syntax highlighting"""
        
        if not logs:
            content = "[dim]System ready - waiting for activity...[/]"
        else:
            # Process and colorize logs
            colored_logs = []
            for log in logs[-15:]:  # Show last 15 logs
                if "SUCCESS" in log or "✅" in log:
                    colored_logs.append(f"[green]{log}[/]")
                elif "ERROR" in log or "❌" in log:
                    colored_logs.append(f"[red]{log}[/]")
                elif "WARNING" in log or "⚠️" in log:
                    colored_logs.append(f"[yellow]{log}[/]")
                elif "CONFLUENCE" in log or "🚀" in log:
                    colored_logs.append(f"[magenta]{log}[/]")
                elif "INFO" in log:
                    colored_logs.append(f"[cyan]{log}[/]")
                else:
                    colored_logs.append(f"[white]{log}[/]")
            
            content = "\n".join(colored_logs)
        
        return Panel(
            content,
            title="[bold white]📜 SYSTEM LOG[/]",
            box=box.ROUNDED,
            style=f"bold {self.colors['text']}",
            height=10,
            padding=(0, 1)
        )
    
    def create_cyber_status_bar(self, status: str, last_update: datetime) -> Panel:
        """🌈 Cyber-themed status bar with real-time metrics"""
        
        current_time = datetime.now()
        update_age = (current_time - last_update).total_seconds()
        
        # Animated status indicator
        if update_age < 1:
            status_indicator = "🟢 LIVE"
            status_color = "bright_green"
        elif update_age < 5:
            status_indicator = "🟡 ACTIVE"
            status_color = "yellow"
        else:
            status_indicator = "🔴 STALE"
            status_color = "red"
        
        # System metrics
        execution_speed = f"{self.execution_latency:.2f}ms" if self.execution_latency > 0 else "⚡ Instant"
        api_speed = f"{self.api_response_time:.0f}ms" if self.api_response_time > 0 else "⚡ Fast"
        
        status_content = f"""[{status_color}]{status_indicator}[/] │ 
Status: [bold cyan]{status}[/] │ 
Execution: [bright_blue]{execution_speed}[/] │ 
API: [green]{api_speed}[/] │ 
Updated: [white]{last_update.strftime('%H:%M:%S')}[/] │ 
[bold magenta]⚡ ALPINE V2.0 - NEXT-GEN TRADING[/]"""
        
        return Panel(
            status_content,
            box=box.HEAVY,
            style=f"bold {self.colors['neon_cyan']}",
            height=3
        )
    
    def _create_progress_bar(self, value: float, max_value: float, label: str, color: str = "green") -> str:
        """📊 Create a visual progress bar"""
        percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
        filled_length = int(percentage // 4)  # 25 chars max
        bar = "█" * filled_length + "░" * (25 - filled_length)
        return f"[bold]{label}:[/] [{color}]{bar}[/] [bold white]{percentage:.1f}%[/]"
    
    def create_master_layout(self, account_data: Dict, positions: List[Dict], 
                           signals: List[Dict], logs: List[str], status: str) -> Layout:
        """🎨 Master layout orchestration for next-gen interface"""
        
        # Extract account data safely
        balance = account_data.get('balance', 0.0)
        equity = account_data.get('equity', balance)
        margin = account_data.get('margin_used', 0.0)
        free_margin = account_data.get('free_margin', balance)
        
        # Create the main layout
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(self.create_enhanced_header())
        
        # Body - split into main and sidebar
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        # Main area - split into top and bottom
        layout["main"].split_column(
            Layout(name="top_main"),
            Layout(name="bottom_main")
        )
        
        # Top main - portfolio and performance
        layout["top_main"].split_row(
            Layout(name="portfolio"),
            Layout(name="performance")
        )
        
        layout["portfolio"].update(self.create_advanced_portfolio_panel(balance, equity, margin, free_margin))
        layout["performance"].update(self.create_performance_dashboard())
        
        # Bottom main - positions
        layout["bottom_main"].update(self.create_next_gen_positions_panel(positions))
        
        # Sidebar - split for signals and logs
        layout["sidebar"].split_column(
            Layout(name="signals", ratio=2),
            Layout(name="logs", ratio=1)
        )
        
        layout["signals"].update(self.create_advanced_signals_panel(signals))
        layout["logs"].update(self.create_enhanced_log_panel(logs))
        
        # Footer
        layout["footer"].update(self.create_cyber_status_bar(status, datetime.now()))
        
        return layout
    
    def update_trading_stats(self, trade_result: Dict):
        """📊 Update trading statistics with enhanced metrics"""
        if trade_result.get('status') == 'completed':
            self.total_trades += 1
            pnl = trade_result.get('pnl', 0)
            
            if pnl > 0:
                self.winning_trades += 1
                self.current_streak = max(self.current_streak + 1, 1)
                self.max_streak = max(self.max_streak, self.current_streak)
                self.best_trade = max(self.best_trade, pnl)
            else:
                self.losing_trades += 1
                self.current_streak = min(self.current_streak - 1, -1)
                self.worst_trade = min(self.worst_trade, pnl)
            
            self.total_pnl += pnl
            self.daily_pnl += pnl
    
    def update_performance_metrics(self, signals_count: int = 0, exec_latency: float = 0, api_time: float = 0):
        """⚡ Update real-time performance metrics"""
        self.signals_per_minute = signals_count
        self.execution_latency = exec_latency
        self.api_response_time = api_time
        self.animation_frame = (self.animation_frame + 1) % 8
    
    def should_refresh(self) -> bool:
        """⚡ Ultra-fast refresh control for scalping"""
        current_time = time.time()
        if current_time - self.last_refresh >= self.refresh_throttle:
            self.last_refresh = current_time
            return True
        return False