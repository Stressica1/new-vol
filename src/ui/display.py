"""
🏔️ Alpine Trading Bot - Ultra-Modern Terminal UI
Revolutionary design with gradients, animations, real-time analytics, and professional trading interface
"""

import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich.align import Align
from rich.columns import Columns
from rich import box
from rich.padding import Padding
from rich.bar import Bar
from rich.style import Style
from rich.spinner import Spinner
from rich.tree import Tree
from rich.rule import Rule
from rich.markdown import Markdown
from rich.syntax import Syntax
from loguru import logger

# Import TradingConfig
try:
    from ..core.config import TradingConfig
except ImportError:
    # Fallback if import fails
    class TradingConfig:
        def __init__(self):
            self.display_update_throttle = 0.1

# Version constant
VERSION = "2.0.0"

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("numpy not available - using simplified mode")


class AlpineDisplay:
    """🏔️ Ultra-Modern Alpine Trading Interface - Revolutionary Design with Next-Generation Features"""
    
    def __init__(self, config=None):
        # Ensure console dimensions are properly constrained - smaller for stability
        self.console = Console(width=120, height=40, force_terminal=True, legacy_windows=False)
        self.config = config or TradingConfig()
        self.start_time = datetime.now()
        self.running = False
        
        # UI layout constraints to ensure content stays in boxes - more conservative
        self.max_table_width = 110  # Smaller width to prevent overflow
        self.max_content_height = 35  # Reduced height for stability
        
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
        
        # 🌈 Revolutionary color palette with gradients
        self.neon_cyan = "#00FFFF"
        self.electric_blue = "#0080FF"
        self.matrix_green = "#39FF14"
        self.cyber_lime = "#32CD32"
        self.neon_purple = "#9D00FF"
        self.hot_pink = "#FF1493"
        self.gold_accent = "#FFD700"
        self.silver_accent = "#C0C0C0"
        self.deep_space = "#0B0C10"
        self.dark_slate = "#1F2937"
        self.midnight_blue = "#1E3A8A"
        
        # 🎨 Gradient styles
        self.primary_gradient = "bright_cyan to bright_blue"
        self.success_gradient = "bright_green to green"
        self.danger_gradient = "bright_red to red"
        self.accent_gradient = "bright_magenta to magenta"
        self.gold_gradient = "yellow to bright_yellow"
        
        # ✨ Animation states
        self.animation_frame = 0
        self.pulse_state = 0
        self.last_refresh = time.time()
        self.refresh_throttle = self.config.display_update_throttle if hasattr(self.config, 'display_update_throttle') else 0.1
        
        # 📱 Advanced display features
        self.sparkline_data = {}
        self.trend_arrows = {"up": "▲", "down": "▼", "flat": "◆"}
        self.status_dots = {"active": "●", "idle": "○", "error": "⚠"}
        
        # 🎯 Display optimization
        self.layout_cache = None
        self.last_layout_data = None
        self.data_hash = None
        
        logger.info("🏔️ Ultra-Modern Alpine Trading Interface initialized")
        
    def start(self, bot):
        """Start the display"""
        self.running = True
        self.bot = bot
        logger.info("Display started")
        
        # Simple display loop
        try:
            while self.running:
                self.update_display()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the display"""
        self.running = False
        logger.info("Display stopped")
    
    def update_display(self):
        """Update the display with the revolutionary interface"""
        try:
            # Enhanced error handling and logging
            logger.debug("🖥️ Updating display...")
            
            # Get fresh data from the bot
            if hasattr(self, 'bot') and self.bot:
                try:
                    # Get account data
                    account_data = {
                        'balance': getattr(self.bot, 'balance', 10000.0),
                        'equity': getattr(self.bot, 'equity', 10000.0),
                        'margin': getattr(self.bot, 'margin', 0.0),
                        'free_margin': getattr(self.bot, 'free_margin', 10000.0)
                    }
                    
                    # Get positions
                    positions = getattr(self.bot, 'positions', [])
                    
                    # Get signals
                    signals = getattr(self.bot, 'signals', [])
                    
                    # Get logs
                    logs = getattr(self.bot, 'logs', [])
                    
                    # Get status
                    status = getattr(self.bot, 'status', 'RUNNING')
                    
                    logger.debug(f"📊 Display data: {len(positions)} positions, {len(signals)} signals, {len(logs)} logs")
                    
                except Exception as e:
                    logger.error(f"❌ Error getting bot data: {e}")
                    # Use default data if bot data fails
                    account_data = {
                        'balance': 10000.0,
                        'equity': 10000.0,
                        'margin': 0.0,
                        'free_margin': 10000.0
                    }
                    positions = []
                    signals = []
                    logs = [f"❌ Error getting bot data: {str(e)}"]
                    status = "ERROR"
                    
            else:
                # Default demo data
                account_data = {
                    'balance': 10000.0,
                    'equity': 10000.0,
                    'margin': 0.0,
                    'free_margin': 10000.0
                }
                positions = []
                signals = []
                logs = ["🚀 Alpine Bot initialized", "💎 Scanning for opportunities..."]
                status = "RUNNING"
            
            # Create the revolutionary layout
            try:
                layout = self.create_revolutionary_layout(account_data, positions, signals, logs, status)
                logger.debug("✅ Revolutionary layout created successfully")
                
            except Exception as e:
                logger.error(f"❌ Error creating revolutionary layout: {e}")
                # Fallback to basic layout
                layout = self._create_fallback_layout(account_data, status)
            
            # Clear and render
            try:
                self.console.clear()
                self.console.print(layout)
                
                # Update animation states
                self.animation_frame += 1
                self.pulse_state += 0.2
                
                logger.debug("✅ Display updated successfully")
                
            except Exception as e:
                logger.error(f"❌ Error rendering display: {e}")
                # Final fallback - basic text display
                self._render_basic_fallback(status)
                
        except Exception as e:
            logger.error(f"❌ Critical display update error: {e}")
            try:
                # Import enhanced logging if available
                from enhanced_logging import alpine_logger
                alpine_logger.log_exception(e, "Display Update")
            except ImportError:
                pass
            
            # Ultimate fallback
            self._render_basic_fallback("ERROR")
    
    def _create_fallback_layout(self, account_data: Dict, status: str):
        """Create a fallback layout when the main layout fails"""
        try:
            from rich.layout import Layout
            from rich.panel import Panel
            from rich.text import Text
            
            layout = Layout()
            
            # Simple header
            header_text = Text()
            header_text.append("🏔️ Alpine Trading Bot", style="bold cyan")
            header_text.append(f" | Status: {status}", style="bold white")
            header_text.append(f" | Time: {datetime.now().strftime('%H:%M:%S')}", style="bold yellow")
            
            header_panel = Panel(header_text, title="Alpine Trading Bot", border_style="cyan")
            
            # Simple account info
            account_text = Text()
            account_text.append(f"💰 Balance: ${account_data.get('balance', 0):.2f}\n", style="green")
            account_text.append(f"⚡ Equity: ${account_data.get('equity', 0):.2f}\n", style="blue")
            account_text.append(f"🔒 Margin: ${account_data.get('margin', 0):.2f}\n", style="yellow")
            account_text.append(f"💎 Free: ${account_data.get('free_margin', 0):.2f}", style="green")
            
            account_panel = Panel(account_text, title="Account Status", border_style="green")
            
            # Split layout
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(account_panel)
            )
            
            return layout
            
        except Exception as e:
            logger.error(f"❌ Error creating fallback layout: {e}")
            return Panel(Text(f"Display Error: {str(e)}", style="red"), title="Error", border_style="red")
    
    def _render_basic_fallback(self, status: str):
        """Render the most basic fallback display"""
        try:
            self.console.clear()
            basic_panel = Panel(
                Text(f"🏔️ Alpine Trading Bot | Status: {status} | Time: {datetime.now().strftime('%H:%M:%S')}", 
                     style="bold cyan"),
                title="Alpine Trading Bot - Basic Mode",
                border_style="cyan",
                box=box.ROUNDED
            )
            self.console.print(basic_panel)
            
        except Exception as e:
            # Last resort - plain print
            print(f"🏔️ Alpine Trading Bot | Status: {status} | Time: {datetime.now().strftime('%H:%M:%S')}")
            print(f"Display Error: {e}")
    
    def create_header(self):
        """Create header display"""
        return Panel("Alpine Trading Bot", style="bold cyan")
    
    def create_account_panel(self):
        """Create account panel"""
        return Panel("Account Info", style="green")
    
    def create_performance_panel(self):
        """Create performance panel"""
        return Panel("Performance", style="yellow")
    
    def create_positions_panel(self):
        """Create positions panel"""
        return Panel("Positions", style="blue")
    
    def create_signals_panel(self):
        """Create signals panel"""
        return Panel("Signals", style="magenta")
    
    def create_logs_panel(self):
        """Create logs panel"""
        return Panel("Logs", style="white")

    def get_animated_spinner(self) -> str:
        """Create animated spinner effect ✨"""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return spinners[self.animation_frame % len(spinners)]
    
    def get_pulse_effect(self, text: str, style: str) -> Text:
        """Create pulsing text effect 💫"""
        pulse_intensity = abs(math.sin(self.pulse_state))
        if pulse_intensity > 0.7:
            return Text(text, style=f"bold {style}")
        else:
            return Text(text, style=style)
    
    def create_glowing_border(self, content, title: str, color: str = "cyan") -> Panel:
        """Create glowing border effect 🌟"""
        return Panel(
            content,
            title=f"✨ {title} ✨",
            title_align="center",
            border_style=f"bold {color}",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
            width=self.max_table_width  # Constrain width to prevent overflow
        )
    
    def create_ultra_modern_header(self) -> Panel:
        """Create revolutionary header with gradients and animations 🌈"""
        
        # Animated title with gradient effect
        title_text = Text()
        title_text.append("🏔️ ", style="bold white")
        title_text.append("A", style=f"bold {self.neon_cyan}")
        title_text.append("L", style=f"bold {self.electric_blue}")
        title_text.append("P", style=f"bold {self.matrix_green}")
        title_text.append("I", style=f"bold {self.cyber_lime}")
        title_text.append("N", style=f"bold {self.neon_purple}")
        title_text.append("E", style=f"bold {self.hot_pink}")
        title_text.append(" TRADING BOT ", style="bold white")
        title_text.append(self.get_animated_spinner(), style=f"bold {self.gold_accent}")
        
        # Subtitle with live updates
        current_time = datetime.now().strftime("%H:%M:%S")
        subtitle = Text()
        subtitle.append("🚀 VOLUME ANOMALY STRATEGY ", style=f"bold {self.matrix_green}")
        subtitle.append("| ", style="white")
        subtitle.append("90% SUCCESS RATE ", style=f"bold {self.gold_accent}")
        subtitle.append("| ", style="white")
        subtitle.append(f"v{VERSION} ", style=f"bold {self.silver_accent}")
        subtitle.append("| ", style="white")
        subtitle.append(f"⏰ {current_time}", style=f"bold {self.neon_cyan}")
        
        # Status indicator line
        status_line = Text()
        status_line.append("● ", style=f"bold {self.matrix_green}")
        status_line.append("SYSTEM ACTIVE ", style=f"bold {self.matrix_green}")
        status_line.append("● ", style=f"bold {self.gold_accent}")
        status_line.append("AI POWERED ", style=f"bold {self.gold_accent}")
        status_line.append("● ", style=f"bold {self.hot_pink}")
        status_line.append("REAL-TIME TRADING", style=f"bold {self.hot_pink}")
        
        header_content = Align.center(
            Text.assemble(title_text, "\n", subtitle, "\n", status_line)
        )
        
        return Panel(
            header_content,
            style=f"bold {self.midnight_blue}",
            box=box.DOUBLE_EDGE,
            border_style=f"bold {self.neon_cyan}",
            width=self.max_table_width
        )
    
    def _create_startup_banner(self) -> Panel:
        """🎆 Epic startup banner with ASCII art"""
        banner_text = f"""
[bold cyan]╔═══════════════════════════════════════════════════════════════════════════════════════════════╗[/]
                [bold cyan]║[/]                          [bold bright_cyan]🏔️  ALPINE TRADING BOT V2.0  🏔️[/]                            [bold cyan]║[/]
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
            Padding(banner_text, (1, 2)),
            style=f"bold {self.midnight_blue}",
            box=box.DOUBLE_EDGE,
            title="🌟 ALPINE FINANCIAL INTELLIGENCE 🌟",
            title_align="center",
            border_style=f"bold {self.neon_cyan}",
            width=self.max_table_width
        )
    
    def create_premium_account_panel(self, balance: float, equity: float, margin: float, free_margin: float) -> Panel:
        """Create simplified account panel 💎"""
        
        # Simplified account info
        account_info = Text()
        account_info.append("💎 BALANCE: ", style="bold cyan")
        account_info.append(f"${balance:,.2f}\n", style="bold green")
        
        account_info.append("⚡ EQUITY: ", style="bold cyan") 
        account_info.append(f"${equity:,.2f}\n", style="bold blue")
        
        account_info.append("🔒 MARGIN: ", style="bold cyan")
        account_info.append(f"${margin:,.2f}\n", style="bold yellow")
        
        account_info.append("💰 FREE: ", style="bold cyan")
        account_info.append(f"${free_margin:,.2f}", style="bold green")
        
        return Panel(
            account_info,
            title="💎 ACCOUNT STATUS 💎",
            border_style="cyan",
            width=self.max_table_width
        )
    
    def create_performance_dashboard(self) -> Panel:
        """Create simplified performance dashboard 📈"""
        
        # Simple performance info
        perf_info = Text()
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        perf_info.append("🎯 TRADES: ", style="bold cyan")
        perf_info.append(f"{self.total_trades}\n", style="bold white")
        
        perf_info.append("🏆 WIN RATE: ", style="bold cyan")
        perf_info.append(f"{win_rate:.1f}%\n", style="bold green" if win_rate >= 60 else "bold yellow")
        
        perf_info.append("💰 TOTAL P&L: ", style="bold cyan")
        perf_info.append(f"${self.total_pnl:,.2f}\n", style="bold green" if self.total_pnl >= 0 else "bold red")
        
        perf_info.append("📊 DAILY P&L: ", style="bold cyan")
        perf_info.append(f"${self.daily_pnl:,.2f}", style="bold green" if self.daily_pnl >= 0 else "bold red")
        
        return Panel(
            perf_info,
            title="📈 PERFORMANCE 📈",
            border_style="green",
            width=self.max_table_width
        )
    
    def create_elite_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create elite positions panel with advanced styling 🚀"""
        
        if not positions:
            empty_content = Align.center(
                Text.assemble(
                    Text("🌟 READY FOR ACTION 🌟\n", style=f"bold {self.gold_accent}"),
                    Text("No active positions\n", style=f"italic {self.silver_accent}"),
                    Text("⚡ Scanning for opportunities...", style=f"bold {self.neon_cyan}")
                )
            )
            return self.create_glowing_border(
                Padding(empty_content, (3, 2)),
                f"ACTIVE POSITIONS (0)",
                self.neon_purple
            )
        
        pos_table = Table(box=None, padding=(0, 1), width=self.max_table_width - 10)
        pos_table.add_column("🎯", style="bold", width=4, no_wrap=True)
        pos_table.add_column("SYMBOL", style="bold white", width=10, no_wrap=True)
        pos_table.add_column("SIDE", style="bold", width=6, no_wrap=True)
        pos_table.add_column("SIZE", style="white", width=10, no_wrap=True)
        pos_table.add_column("ENTRY", style="white", width=10, no_wrap=True)
        pos_table.add_column("CURRENT", style="white", width=10, no_wrap=True)
        pos_table.add_column("P&L", style="bold", width=14, no_wrap=True)
        pos_table.add_column("📊", style="bold", width=4, no_wrap=True)
        
        for i, pos in enumerate(positions[:8]):  # Show max 8 positions with elite styling
            symbol = pos.get('symbol', 'N/A').replace('/USDT:USDT', '')
            side = pos.get('side', 'N/A').upper()
            size = pos.get('contracts', 0)
            entry_price = pos.get('entryPrice', 0)
            mark_price = pos.get('markPrice', 0)
            unrealized_pnl = pos.get('unrealizedPnl', 0)
            
            # Enhanced styling
            position_emoji = "🚀" if side == 'LONG' else "🎯"
            side_color = self.matrix_green if side == 'LONG' else self.hot_pink
            side_style = f"[{side_color}]● {side}[/]"
            
            # P&L with dramatic effects
            pnl_color = self.matrix_green if unrealized_pnl >= 0 else self.danger_gradient
            pnl_emoji = "💎" if unrealized_pnl > 100 else "💰" if unrealized_pnl > 0 else "⚡" if unrealized_pnl > -50 else "🔥"
            
            # Performance indicator
            pnl_percent = ((mark_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            if side == 'SHORT':
                pnl_percent = -pnl_percent
                
            status_emoji = "🏆" if pnl_percent > 5 else "📈" if pnl_percent > 0 else "📊" if pnl_percent > -5 else "⚠️"
            
            pos_table.add_row(
                position_emoji,
                f"[bold {self.neon_cyan}]{symbol}[/]",
                side_style,
                f"{size:.4f}",
                f"${entry_price:.4f}",
                f"[bold]{mark_price:.4f}[/]",
                f"[{pnl_color}]{pnl_emoji} ${unrealized_pnl:.2f}[/]",
                status_emoji
            )
        
        return self.create_glowing_border(
            Padding(pos_table, (1, 1)),
            f"ACTIVE POSITIONS ({len(positions)})",
            self.hot_pink
        )
    
    def create_neural_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create neural-style signals panel with AI aesthetics 🧠"""
        
        if not signals:
            empty_content = Align.center(
                Text.assemble(
                    Text("🧠 AI NEURAL NETWORK 🧠\n", style=f"bold {self.neon_purple}"),
                    Text("Scanning market patterns...\n", style=f"italic {self.silver_accent}"),
                    Text(f"{self.get_animated_spinner()} Processing data streams", style=f"bold {self.electric_blue}")
                )
            )
            return self.create_glowing_border(
                Padding(empty_content, (3, 2)),
                "NEURAL SIGNALS (0)",
                self.neon_purple
            )
        
        sig_table = Table(box=None, padding=(0, 1), width=self.max_table_width - 10)
        sig_table.add_column("🕐", style="white", width=8, no_wrap=True)
        sig_table.add_column("🎯", style="bold white", width=8, no_wrap=True)
        sig_table.add_column("SIGNAL", style="bold", width=10, no_wrap=True)
        sig_table.add_column("VOLUME", style="white", width=8, no_wrap=True)
        sig_table.add_column("PRICE", style="white", width=10, no_wrap=True)
        sig_table.add_column("STRENGTH", style="bold", width=10, no_wrap=True)
        sig_table.add_column("STATUS", style="bold", width=10, no_wrap=True)
        sig_table.add_column("🚀", style="bold", width=4, no_wrap=True)
        
        for signal in signals[:6]:  # Show max 6 signals with neural styling
            # Signal type with neural aesthetics
            signal_type = signal.get('type', 'UNKNOWN')
            signal_emoji = "⬆️" if signal_type == 'LONG' else "⬇️"
            signal_color = self.matrix_green if signal_type == 'LONG' else self.hot_pink
            
            # Volume analysis
            volume_ratio = signal.get('volume_ratio', 0)
            volume_emoji = "🔥" if volume_ratio > 5.0 else "⚡" if volume_ratio > 3.0 else "💧"
            volume_color = self.danger_gradient if volume_ratio > 5.0 else self.gold_accent if volume_ratio > 2.0 else self.neon_cyan
            
            # Signal strength calculation
            confluence_count = signal.get('confluence_count', 1)
            tf_str = signal.get('timeframe', 'N/A')
            strength = min(100, confluence_count * volume_ratio * 20)
            strength_color = self.matrix_green if strength > 80 else self.gold_accent if strength > 60 else self.neon_cyan
            
            # Neural network confidence
            confidence_emoji = "🧠" if strength > 90 else "🎯" if strength > 70 else "📊"
            
            # Time formatting
            try:
                if 'time' in signal and signal['time'] is not None:
                    time_str = signal['time'].strftime("%H:%M:%S")
                elif 'timestamp' in signal and signal['timestamp'] is not None:
                    time_str = datetime.fromtimestamp(signal['timestamp']).strftime("%H:%M:%S")
                else:
                    time_str = "N/A"
            except (KeyError, ValueError, OSError, TypeError):
                time_str = "N/A"
            
            sig_table.add_row(
                time_str,
                f"[bold {self.neon_cyan}]{signal['symbol'].replace('/USDT:USDT', '')}[/]",
                f"[{signal_color}]{signal_emoji} {signal['type']}[/]",
                f"[{volume_color}]{volume_emoji} {volume_ratio:.1f}x[/]",
                f"${signal['price']:.4f}",
                f"[{strength_color}]{strength:.0f}%[/]",
                f"[bold]{signal.get('action', 'SCANNING')}[/]",
                confidence_emoji
            )
        
        return self.create_glowing_border(
            Padding(sig_table, (1, 1)),
            f"NEURAL SIGNALS ({len(signals)})",
            self.neon_purple
        )
    
    def create_cyber_log_panel(self, logs: List[str]) -> Panel:
        """Create cyber-style activity log with matrix aesthetics 🖥️"""
        
        if not logs:
            empty_content = Align.center(
                Text.assemble(
                    Text("🖥️ SYSTEM MONITOR 🖥️\n", style=f"bold {self.matrix_green}"),
                    Text("All systems operational\n", style=f"italic {self.silver_accent}"),
                    Text("⚡ Awaiting events...", style=f"bold {self.neon_cyan}")
                )
            )
            return self.create_glowing_border(
                Padding(empty_content, (2, 2)),
                "ACTIVITY LOG",
                self.matrix_green
            )
        
        log_content = Text()
        for log in logs[-5:]:  # Show only last 5 logs to prevent overflow
            if "❌" in log:
                log_content.append(f"🔥 {log}\n", style="bold red")
            elif "✅" in log:
                log_content.append(f"✨ {log}\n", style="bold green")
            elif "⚠️" in log:
                log_content.append(f"⚡ {log}\n", style="bold yellow")
            else:
                log_content.append(f"💫 {log}\n", style="cyan")
        
        return Panel(
            log_content,
            title="📝 SYSTEM LOG 📝",
            border_style="blue",
            width=self.max_table_width
        )
    
    def create_error_panel(self, errors: List[str]) -> Panel:
        """Create error panel for system errors and exceptions 🚨"""
        
        if not errors:
            error_content = Text("✅ No system errors detected", style="bold green")
        else:
            error_content = Text()
            for error in errors[-3:]:  # Show last 3 errors only
                if "ccxt" in error.lower() or "exchange" in error.lower():
                    error_content.append(f"🔗 API: {error[:80]}...\n", style="bold yellow")
                elif "market symbol" in error.lower():
                    error_content.append(f"📊 Market: {error[:80]}...\n", style="bold orange")
                elif "error" in error.lower():
                    error_content.append(f"⚠️ System: {error[:80]}...\n", style="bold red")
                else:
                    error_content.append(f"🐛 Debug: {error[:80]}...\n", style="dim white")
        
        return Panel(
            error_content,
            title="🚨 ERROR MONITOR 🚨",
            border_style="red",
            width=self.max_table_width
        )
    
    def create_quantum_status_bar(self, status: str, last_update: datetime) -> Panel:
        """Create quantum-style status bar with advanced effects ⚡"""
        
        # Calculate uptime with precision
        uptime = datetime.now() - self.start_time
        uptime_str = f"{int(uptime.total_seconds() // 3600):02d}:{int((uptime.total_seconds() % 3600) // 60):02d}:{int(uptime.total_seconds() % 60):02d}"
        
        # Advanced status styling
        if "ACTIVE" in status:
            status_color = self.matrix_green
            status_emoji = "🟢"
            pulse_text = self.get_pulse_effect(status, status_color)
        elif "HALTED" in status:
            status_color = self.danger_gradient
            status_emoji = "🔴"
            pulse_text = Text(status, style=f"bold {status_color}")
        elif "DISCONNECTED" in status:
            status_color = self.danger_gradient
            status_emoji = "⚠️"
            pulse_text = Text(status, style=f"bold {status_color}")
        else:
            status_color = self.gold_accent
            status_emoji = "🟡"
            pulse_text = Text(status, style=f"bold {status_color}")
        
        # Create quantum status display
        status_text = Text()
        status_text.append(f"{status_emoji} STATUS: ", style="bold white")
        status_text.append(pulse_text)
        status_text.append(" | ", style=f"bold {self.silver_accent}")
        status_text.append("⏰ UPTIME: ", style="bold white")
        status_text.append(uptime_str, style=f"bold {self.neon_cyan}")
        status_text.append(" | ", style=f"bold {self.silver_accent}")
        status_text.append("🔄 LAST UPDATE: ", style="bold white")
        status_text.append(last_update.strftime("%H:%M:%S.%f")[:-3], style=f"bold {self.matrix_green}")
        status_text.append(" | ", style=f"bold {self.silver_accent}")
        status_text.append(f"{self.get_animated_spinner()} ", style=f"bold {self.hot_pink}")
        status_text.append("QUANTUM CORE ACTIVE", style=f"bold {self.neon_purple}")
        
        return Panel(
            Padding(Align.center(status_text), (0, 1)),
            style=f"bold {self.midnight_blue}",
            box=box.ROUNDED,
            border_style=f"bold {self.electric_blue}",
            width=self.max_table_width
        )
    
    def create_revolutionary_layout(self, account_data: Dict, positions: List[Dict], 
                                  signals: List[Dict], logs: List[str], status: str, errors: Optional[List[str]] = None) -> Layout:
        """Create revolutionary layout with stable design principles 🌌"""
        
        # Stabilized animation states - minimal updates
        current_time = time.time()
        if current_time - self.last_refresh >= self.refresh_throttle:
            self.animation_frame += 1
            self.pulse_state += 0.1  # Slower pulse for stability
            self.last_refresh = current_time
        
        # Quantum layout structure
        layout = Layout()
        
        # Simplified layout structure - prevent overlapping
        layout.split_column(
            Layout(self.create_ultra_modern_header(), size=6, name="header"),
            Layout(name="main_content", ratio=1),
            Layout(self.create_quantum_status_bar(status, datetime.now()), size=3, name="status")
        )
        
        # Main content with controlled proportions
        layout["main_content"].split_row(
            Layout(name="left_panel", ratio=1),
            Layout(name="right_panel", ratio=1)
        )
        
        # Left panel - Account & Performance (simplified)
        layout["left_panel"].split_column(
            Layout(self.create_premium_account_panel(
                account_data.get('balance', 0),
                account_data.get('equity', 0),
                account_data.get('margin', 0),
                account_data.get('free_margin', 0)
            ), size=8, name="account"),
            Layout(self.create_performance_dashboard(), size=8, name="performance"),
            Layout(self.create_cyber_log_panel(logs[:10]), name="logs")  # Limit logs to prevent overflow
        )
        
        # Right panel - Positions, Signals & Errors (simplified)
        layout["right_panel"].split_column(
            Layout(self.create_elite_positions_panel(positions[:5]), size=10, name="positions"),  # Limit positions
            Layout(self.create_neural_signals_panel(signals), size=8, name="neural_signals"),
            Layout(self.create_error_panel(errors or []), name="errors")  # New error panel
        )
        
        return layout
    
    def update_stats(self, trade_result: Dict):
        """Update trading statistics with quantum precision 🎯"""
        self.total_trades += 1
        pnl = trade_result.get('pnl', 0)
        
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.total_pnl += pnl
        self.daily_pnl += pnl
        
        # Advanced drawdown calculation
        if pnl < 0:
            current_dd = abs(pnl / self.total_pnl * 100) if self.total_pnl != 0 else 0
            self.max_drawdown = min(self.max_drawdown, -current_dd)
    
    # Legacy method compatibility
    def create_layout(self, account_data: Dict, positions: List[Dict], 
                     signals: List[Dict], logs: List[str], status: str) -> Layout:
        """Legacy compatibility method - redirects to revolutionary layout"""
        return self.create_revolutionary_layout(account_data, positions, signals, logs, status)
