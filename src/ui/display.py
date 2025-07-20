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
        
        # 🌈 Steampunk color palette with mechanical elegance
        self.mint_green = "#00FFB3"      # Mint green (main accent)
        self.dark_purple = "#4A148C"     # Dark purple (steampunk elegance)
        self.hot_pink = "#FF69B4"        # Hot pink (bull signals)
        self.dark_orange = "#FF8C00"     # Dark orange (bear signals)
        self.neon_cyan = "#00FFFF"       # Neon cyan (steampunk glow)
        self.neon_purple = "#9D4EDD"     # Neon purple (steampunk accent)
        self.bright_red = "#FF4444"      # Bright red (critical alerts)
        self.deep_sky_blue = "#00BFFF"   # Deep sky blue (info messages)
        self.dark_navy = "#1A1A2E"       # Dark navy (steampunk background)
        self.light_gray = "#E0E0E0"      # Light gray (readable text)
        
        # 🎨 Steampunk gradient styles
        self.primary_gradient = f"{self.mint_green} to {self.dark_purple}"
        self.success_gradient = f"{self.hot_pink} to {self.neon_purple}"
        self.danger_gradient = f"{self.dark_orange} to {self.bright_red}"
        self.accent_gradient = f"{self.neon_cyan} to {self.neon_purple}"
        self.steampunk_gradient = f"{self.mint_green} to {self.dark_purple}"
        
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
        """Create steampunk ultra-modern header with mechanical elegance"""
        header_text = Text()
        header_text.append("⚙️ ", style=f"bold {self.mint_green}")
        header_text.append("STEAMPUNK", style=f"bold {self.mint_green}")
        header_text.append(" ALPINE ", style=f"bold {self.light_gray}")
        header_text.append("TRADING ENGINE", style=f"bold {self.dark_purple}")
        header_text.append(" ⚙️", style=f"bold {self.mint_green}")
        
        # Add mechanical status indicators
        status_text = Text()
        status_text.append("🔧 ", style=f"{self.neon_cyan}")
        status_text.append("ENGINE ACTIVE", style=f"bold {self.hot_pink}")
        status_text.append(" | ", style=f"{self.light_gray}")
        status_text.append("⚡", style=f"{self.neon_cyan}")
        status_text.append(" MAXIMUM LEVERAGE", style=f"bold {self.dark_orange}")
        
        # Create mechanical layout
        table = Table.grid(padding=1)
        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_row(header_text, status_text)
        
        return Panel(
            table,
            box=box.DOUBLE,
            style=f"{self.mint_green}",
            border_style=f"{self.dark_purple}",
            title="⚙️ MECHANICAL TRADING SYSTEM ⚙️"
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
        """Create steampunk elite positions panel with mechanical precision"""
        if not positions:
            return Panel(
                Align.center("🔧 No active positions - Engine scanning for opportunities..."),
                title="⚙️ MECHANICAL POSITIONS ⚙️",
                border_style=f"{self.dark_purple}",
                style=f"{self.mint_green}"
            )
        
        table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        table.add_column("Symbol", style=f"bold {self.neon_purple}", width=12)
        table.add_column("Type", justify="center", width=8)
        table.add_column("Size", justify="right", width=10)
        table.add_column("Entry", justify="right", width=10)
        table.add_column("Current", justify="right", width=10)
        table.add_column("P&L", justify="right", width=12)
        table.add_column("ROI%", justify="center", width=8)
        
        for pos in positions[:8]:  # Show first 8 positions
            symbol = pos.get('symbol', 'N/A')
            side = pos.get('side', 'N/A')
            size = pos.get('size', 0.0)
            entry_price = pos.get('entry_price', 0.0)
            current_price = pos.get('current_price', 0.0)
            pnl = pos.get('pnl', 0.0)
            roi = pos.get('roi', 0.0)
            
            # Steampunk color coding
            if side.upper() in ['LONG', 'BUY']:
                side_color = f"{self.hot_pink}"  # Hot pink for bulls
            else:
                side_color = f"{self.dark_orange}"  # Dark orange for bears
            
            # P&L color coding
            if pnl > 0:
                pnl_color = f"{self.hot_pink}"  # Hot pink for profits
                roi_color = f"{self.hot_pink}"
            elif pnl < 0:
                pnl_color = f"{self.dark_orange}"  # Dark orange for losses
                roi_color = f"{self.dark_orange}"
            else:
                pnl_color = f"{self.light_gray}"
                roi_color = f"{self.light_gray}"
            
            table.add_row(
                symbol,
                f"[{side_color}]{side}[/{side_color}]",
                f"{size:,.2f}",
                f"${entry_price:,.4f}",
                f"${current_price:,.4f}",
                f"[{pnl_color}]${pnl:,.2f}[/{pnl_color}]",
                f"[{roi_color}]{roi:+.2f}%[/{roi_color}]"
            )
        
        return Panel(
            table,
            title=f"⚙️ MECHANICAL POSITIONS ({len(positions)}) ⚙️",
            border_style=f"{self.dark_purple}",
            style=f"{self.mint_green}"
        )
    
    def create_neural_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create steampunk neural signals panel with mechanical precision"""
        if not signals:
            return Panel(
                Align.center("🔧 Scanning for mechanical signals..."),
                title="⚙️ MECHANICAL SIGNALS ⚙️",
                border_style=f"{self.dark_purple}",
                style=f"{self.mint_green}"
            )
        
        table = Table(show_header=True, header_style=f"bold {self.mint_green}", box=box.SIMPLE)
        table.add_column("Symbol", style=f"bold {self.neon_purple}", width=12)
        table.add_column("Signal", justify="center", width=8)
        table.add_column("Confidence", justify="center", width=10)
        table.add_column("Volume", justify="center", width=10)
        table.add_column("Price", justify="right", width=10)
        table.add_column("Time", justify="center", width=8)
        
        for signal in signals[:6]:  # Show first 6 signals
            symbol = signal.get('symbol', 'N/A')
            signal_type = signal.get('signal', 'N/A')
            confidence = signal.get('confidence', 0)
            volume_ratio = signal.get('volume_ratio', 0)
            price = signal.get('price', 0.0)
            timestamp = signal.get('timestamp', datetime.now())
            
            # Steampunk color coding for signals
            if signal_type.upper() in ['BUY', 'LONG']:
                signal_color = f"{self.hot_pink}"  # Hot pink for bulls
                signal_icon = "🔧"
            elif signal_type.upper() in ['SELL', 'SHORT']:
                signal_color = f"{self.dark_orange}"  # Dark orange for bears
                signal_icon = "⚙️"
            else:
                signal_color = f"{self.light_gray}"
                signal_icon = "🔩"
            
            # Confidence color coding
            if confidence >= 80:
                conf_color = f"{self.hot_pink}"  # Hot pink for high confidence
            elif confidence >= 60:
                conf_color = f"{self.neon_cyan}"  # Neon cyan for medium confidence
            else:
                conf_color = f"{self.dark_orange}"  # Dark orange for low confidence
            
            # Format time
            time_str = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else "N/A"
            
            table.add_row(
                symbol,
                f"[{signal_color}]{signal_icon} {signal_type}[/{signal_color}]",
                f"[{conf_color}]{confidence:.1f}%[/{conf_color}]",
                f"{volume_ratio:.1f}x",
                f"${price:,.4f}",
                time_str
            )
        
        return Panel(
            table,
            title=f"⚙️ MECHANICAL SIGNALS ({len(signals)}) ⚙️",
            border_style=f"{self.dark_purple}",
            style=f"{self.mint_green}"
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
