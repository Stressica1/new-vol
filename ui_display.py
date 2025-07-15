#!/usr/bin/env python3
"""
🏔️ Alpine UI Display - Beautiful Trading Interface
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich import box

class AlpineDisplayV2:
    """Beautiful Alpine Trading Bot Display"""
    
    def __init__(self):
        self.console = Console(width=140, height=50, force_terminal=True)
        self.name = "Alpine Display"
        self.version = "2.0"
        
        # Display colors
        self.colors = {
            'primary': '#00FFB3',      # Mint green
            'secondary': '#228B22',    # Forest green
            'success': '#32CD32',      # Lime green
            'warning': '#FFD700',      # Gold
            'error': '#FF4500',        # Red-orange
            'info': '#87CEEB',         # Sky blue
            'neutral': '#D3D3D3'       # Light gray
        }
    
    def create_header_panel(self, status: str = "RUNNING") -> Panel:
        """Create header panel"""
        header_text = Text()
        header_text.append("🏔️ ", style="bold white")
        header_text.append("ALPINE TRADING BOT", style=f"bold {self.colors['primary']}")
        header_text.append(" V2.0 ", style="bold white")
        header_text.append(f"[{status}]", style=f"bold {self.colors['success']}")
        
        return Panel(
            Align.center(header_text),
            style=self.colors['primary'],
            border_style=self.colors['secondary']
        )
    
    def create_account_panel(self, account_data: Dict) -> Panel:
        """Create account information panel"""
        table = Table(show_header=False, box=box.SIMPLE, expand=True)
        table.add_column("Label", style="bold")
        table.add_column("Value", justify="right")
        
        balance = account_data.get('balance', 0.0)
        equity = account_data.get('equity', 0.0)
        free_margin = account_data.get('free_margin', 0.0)
        
        table.add_row("💰 Balance:", f"${balance:,.2f}")
        table.add_row("📊 Equity:", f"${equity:,.2f}")
        table.add_row("🆓 Free Margin:", f"${free_margin:,.2f}")
        
        return Panel(
            table,
            title="💼 Account Info",
            border_style=self.colors['info']
        )
    
    def create_positions_panel(self, positions: List[Dict]) -> Panel:
        """Create positions panel"""
        if not positions:
            return Panel(
                Align.center("No open positions"),
                title="📈 Positions (0)",
                border_style=self.colors['neutral']
            )
        
        table = Table(show_header=True, box=box.SIMPLE, expand=True)
        table.add_column("Symbol", style="bold")
        table.add_column("Type", justify="center")
        table.add_column("Size", justify="right")
        table.add_column("P&L", justify="right")
        
        for pos in positions[:5]:  # Show first 5 positions
            symbol = pos.get('symbol', 'N/A')
            side = pos.get('side', 'N/A')
            size = pos.get('size', 0.0)
            pnl = pos.get('pnl', 0.0)
            
            pnl_color = self.colors['success'] if pnl >= 0 else self.colors['error']
            
            table.add_row(
                symbol,
                side,
                f"{size:,.2f}",
                f"[{pnl_color}]${pnl:,.2f}[/]"
            )
        
        return Panel(
            table,
            title=f"📈 Positions ({len(positions)})",
            border_style=self.colors['primary']
        )
    
    def create_signals_panel(self, signals: List[Dict]) -> Panel:
        """Create signals panel"""
        if not signals:
            return Panel(
                Align.center("Scanning for signals..."),
                title="🎯 Signals",
                border_style=self.colors['warning']
            )
        
        table = Table(show_header=True, box=box.SIMPLE, expand=True)
        table.add_column("Symbol", style="bold")
        table.add_column("Type", justify="center")
        table.add_column("Confidence", justify="center")
        table.add_column("Price", justify="right")
        
        for signal in signals[:5]:  # Show first 5 signals
            symbol = signal.get('symbol', 'N/A')
            signal_type = signal.get('signal', 'N/A')
            confidence = signal.get('confidence', 0)
            price = signal.get('price', 0.0)
            
            # Color based on signal type
            if signal_type == 'BUY':
                type_color = self.colors['success']
            elif signal_type == 'SELL':
                type_color = self.colors['error']
            else:
                type_color = self.colors['neutral']
            
            # Color based on confidence
            if confidence >= 80:
                conf_color = self.colors['success']
            elif confidence >= 60:
                conf_color = self.colors['warning']
            else:
                conf_color = self.colors['error']
            
            table.add_row(
                symbol,
                f"[{type_color}]{signal_type}[/]",
                f"[{conf_color}]{confidence:.1f}%[/]",
                f"${price:,.4f}"
            )
        
        return Panel(
            table,
            title=f"🎯 Signals ({len(signals)})",
            border_style=self.colors['primary']
        )
    
    def create_activity_panel(self, activity_log: List[Dict]) -> Panel:
        """Create activity log panel"""
        if not activity_log:
            return Panel(
                Align.center("No recent activity"),
                title="📝 Activity Log",
                border_style=self.colors['neutral']
            )
        
        text = Text()
        
        for entry in activity_log[-8:]:  # Show last 8 entries
            timestamp = entry.get('timestamp', datetime.now())
            message = entry.get('message', '')
            level = entry.get('level', 'INFO')
            
            # Format timestamp
            time_str = timestamp.strftime("%H:%M:%S")
            
            # Color based on level
            if level == 'ERROR':
                color = self.colors['error']
            elif level == 'WARNING':
                color = self.colors['warning']
            elif level == 'SUCCESS':
                color = self.colors['success']
            else:
                color = self.colors['info']
            
            text.append(f"[{time_str}] ", style="dim")
            text.append(f"{message}\n", style=color)
        
        return Panel(
            text,
            title="📝 Activity Log",
            border_style=self.colors['info']
        )
    
    def create_revolutionary_layout(self, **kwargs) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header
        layout["header"].update(self.create_header_panel(kwargs.get('status', 'RUNNING')))
        
        # Body - split into left and right
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left side - account and positions
        layout["left"].split_column(
            Layout(name="account", size=8),
            Layout(name="positions")
        )
        
        # Right side - signals and activity
        layout["right"].split_column(
            Layout(name="signals"),
            Layout(name="activity")
        )
        
        # Fill the panels
        layout["account"].update(self.create_account_panel(kwargs.get('account_data', {})))
        layout["positions"].update(self.create_positions_panel(kwargs.get('positions', [])))
        layout["signals"].update(self.create_signals_panel(kwargs.get('signals', [])))
        layout["activity"].update(self.create_activity_panel(kwargs.get('activity_log', [])))
        
        return layout

def main():
    """Test the display"""
    display = AlpineDisplayV2()
    print(f"✅ {display.name} v{display.version} initialized")
    
    # Test layout
    test_data = {
        'account_data': {'balance': 1000.0, 'equity': 1050.0, 'free_margin': 950.0},
        'positions': [
            {'symbol': 'BTC/USDT', 'side': 'BUY', 'size': 0.01, 'pnl': 25.50},
            {'symbol': 'ETH/USDT', 'side': 'SELL', 'size': 0.5, 'pnl': -15.25}
        ],
        'signals': [
            {'symbol': 'SOL/USDT', 'signal': 'BUY', 'confidence': 85.0, 'price': 150.25}
        ],
        'activity_log': [
            {'timestamp': datetime.now(), 'message': 'Bot started', 'level': 'INFO'},
            {'timestamp': datetime.now(), 'message': 'Signal detected', 'level': 'SUCCESS'}
        ]
    }
    
    layout = display.create_revolutionary_layout(**test_data)
    display.console.print(layout)

if __name__ == "__main__":
    main()
