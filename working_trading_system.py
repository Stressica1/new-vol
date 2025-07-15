#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Working Trading System
Functional trading system for Bitget futures
"""

import os
import sys
import asyncio
import ccxt
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
import time

console = Console()

class AlpineTradingSystem:
    """Working Alpine Trading System"""
    
    def __init__(self):
        """Initialize the trading system"""
        # Bitget configuration
        self.config = {
            'apiKey': 'bg_5400882ef43c5596ffcf4af0c697b250',
            'secret': '60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45',
            'password': '22672267',
            'sandbox': False,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Futures trading
                'marginMode': 'cross'
            }
        }
        
        self.exchange = None
        self.running = False
        self.balance = 0.0
        self.positions = []
        self.last_update = datetime.now()
        
        # Trading pairs from config
        self.trading_pairs = [
            'BTC/USDT:USDT',
            'ETH/USDT:USDT',
            'SOL/USDT:USDT',
            'DOGE/USDT:USDT',
            'ADA/USDT:USDT',
            'DOT/USDT:USDT',
            'AVAX/USDT:USDT',
            'ATOM/USDT:USDT',
            'NEAR/USDT:USDT',
            'FTM/USDT:USDT'
        ]
        
        self.market_data = {}
    
    def display_banner(self):
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      🏔️  ALPINE TRADING BOT - LIVE TRADING SYSTEM  🏔️           ║
║                                                                  ║
║      Revolutionary Volume Anomaly Trading System                 ║
║      Beautiful Mint Green Terminal • Bitget Futures             ║
║      Real-time Trading Dashboard                                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        console.print(Panel(
            Align(Text(banner, style="bold #00FFB3"), align="center"),
            border_style="#00FFB3",
            style="on black"
        ))
    
    async def initialize_exchange(self):
        """Initialize Bitget exchange connection"""
        try:
            console.print("🔌 Connecting to Bitget...")
            self.exchange = ccxt.bitget(self.config)
            
            # Test connection (synchronous)
            markets = self.exchange.load_markets()
            console.print("✅ Connected to Bitget futures market")
            
            # Get initial balance (synchronous)
            balance = self.exchange.fetch_balance()
            self.account_balance = balance
            self.balance = balance.get('USDT', {}).get('total', 0.0)
            console.print(f"💰 USDT Balance: ${self.balance:.2f}")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Connection failed: {e}")
            return False
    
    async def get_account_balance(self):
        """Update account balance"""
        if not self.exchange:
            return
            
        try:
            balance = self.exchange.fetch_balance()
            self.account_balance = balance
            self.balance = balance.get('USDT', {}).get('total', 0.0)
            
        except Exception as e:
            console.print(f"❌ Balance update error: {e}")
    
    async def get_market_data(self):
        """Get market data for trading pairs"""
        if not self.exchange:
            return
            
        try:
            for pair in self.trading_pairs[:5]:  # Limit to first 5 pairs
                try:
                    ticker = self.exchange.fetch_ticker(pair)
                    self.market_data[pair] = {
                        'price': ticker['last'],
                        'change': ticker['percentage'],
                        'volume': ticker['quoteVolume']
                    }
                except Exception as e:
                    console.print(f"⚠️ Error fetching {pair}: {e}")
                    
        except Exception as e:
            console.print(f"❌ Market data error: {e}")
    
    async def get_positions(self):
        """Get current positions"""
        if not self.exchange:
            return
            
        try:
            positions = self.exchange.fetch_positions()
            self.positions = [p for p in positions if p['size'] > 0]
            
        except Exception as e:
            # Positions might not be available, that's okay
            self.positions = []
    
    def create_dashboard(self):
        """Create live trading dashboard"""
        
        # Balance section
        balance_table = Table(title="💰 Account Balance", show_header=True, header_style="bold #00FFB3")
        balance_table.add_column("Asset", style="#00FFB3")
        balance_table.add_column("Total", style="white")
        balance_table.add_column("Available", style="green")
        balance_table.add_column("Used", style="red")
        
        if self.account_balance:
            try:
                total_usdt = self.account_balance.get('total', {}).get('USDT', 0)
                free_usdt = self.account_balance.get('free', {}).get('USDT', 0)
                used_usdt = self.account_balance.get('used', {}).get('USDT', 0)
                
                balance_table.add_row(
                    "USDT", 
                    f"${total_usdt:.2f}",
                    f"${free_usdt:.2f}",
                    f"${used_usdt:.2f}"
                )
                
                # Update the balance variable for other uses
                self.balance = total_usdt
                
            except Exception as e:
                balance_table.add_row("USDT", "Error", "Error", "Error")
        else:
            balance_table.add_row("USDT", "Loading...", "Loading...", "Loading...")
        
        # Market data section
        market_table = Table(title="📊 Market Data", show_header=True, header_style="bold #00FFB3")
        market_table.add_column("Pair", style="#00FFB3")
        market_table.add_column("Price", style="white")
        market_table.add_column("24h Change", style="white")
        market_table.add_column("Volume", style="white")
        
        for pair, data in self.market_data.items():
            change_style = "green" if data['change'] > 0 else "red"
            market_table.add_row(
                pair.replace('/USDT:USDT', ''),
                f"${data['price']:,.4f}",
                f"[{change_style}]{data['change']:+.2f}%[/{change_style}]",
                f"${data['volume']:,.0f}"
            )
        
        # Add empty row if no market data
        if not self.market_data:
            market_table.add_row("Loading...", "...", "...", "...")
        
        # Positions section
        positions_table = Table(title="📈 Open Positions", show_header=True, header_style="bold #00FFB3")
        positions_table.add_column("Symbol", style="#00FFB3")
        positions_table.add_column("Side", style="white")
        positions_table.add_column("Size", style="white")
        positions_table.add_column("Entry Price", style="white")
        positions_table.add_column("Mark Price", style="white")
        positions_table.add_column("PnL", style="white")
        
        if self.positions:
            for pos in self.positions:
                pnl_style = "green" if pos.get('unrealizedPnl', 0) > 0 else "red"
                positions_table.add_row(
                    pos['symbol'],
                    pos['side'],
                    f"{pos['size']}",
                    f"${pos['entryPrice']:,.4f}",
                    f"${pos['markPrice']:,.4f}",
                    f"[{pnl_style}]${pos.get('unrealizedPnl', 0):,.2f}[/{pnl_style}]"
                )
        else:
            positions_table.add_row("No open positions", "", "", "", "", "")
        
        # Status section
        status_table = Table(title="🏔️ Alpine Status", show_header=True, header_style="bold #00FFB3")
        status_table.add_column("Status", style="#00FFB3")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("System Status", "[green]🟢 ONLINE[/green]" if self.running else "[red]🔴 OFFLINE[/red]")
        status_table.add_row("Exchange", "Bitget Futures")
        status_table.add_row("Last Update", self.last_update.strftime("%H:%M:%S"))
        status_table.add_row("Open Positions", str(len(self.positions)))
        
        # Display balance from account_balance if available
        if self.account_balance:
            try:
                total_balance = self.account_balance.get('total', {}).get('USDT', 0)
                status_table.add_row("Balance", f"${total_balance:.2f} USDT")
            except:
                status_table.add_row("Balance", f"${self.balance:.2f} USDT")
        else:
            status_table.add_row("Balance", f"${self.balance:.2f} USDT")
            
        status_table.add_row("Market Pairs", str(len(self.market_data)))
        
        # Combine all tables
        from rich.layout import Layout
        
        layout = Layout()
        layout.split_column(
            Layout(Panel(balance_table, border_style="#00FFB3"), size=6),
            Layout(Panel(market_table, border_style="#00FFB3"), size=10),
            Layout(Panel(positions_table, border_style="#00FFB3"), size=8),
            Layout(Panel(status_table, border_style="#00FFB3"), size=6)
        )
        
        return layout
    
    async def trading_loop(self):
        """Main trading loop"""
        console.print("\n🚀 Starting Alpine Trading System...")
        
        if not await self.initialize_exchange():
            return
        
        self.running = True
        console.print("✅ Trading system initialized")
        console.print("📊 Starting live dashboard...")
        
        try:
            with Live(self.create_dashboard(), refresh_per_second=1) as live:
                while self.running:
                    try:
                        # Update account balance
                        await self.get_account_balance()
                        
                        # Update market data
                        await self.get_market_data()
                        
                        # Update positions
                        await self.get_positions()
                        
                        # Update timestamp
                        self.last_update = datetime.now()
                        
                        # Update dashboard
                        live.update(self.create_dashboard())
                        
                        # Wait before next update
                        await asyncio.sleep(2)
                        
                    except KeyboardInterrupt:
                        console.print("\n🛑 Stopping trading system...")
                        self.running = False
                        break
                        
                    except Exception as e:
                        console.print(f"❌ Error in trading loop: {e}")
                        await asyncio.sleep(5)
                        
        finally:
            if self.exchange:
                try:
                    await self.exchange.close()
                except:
                    pass  # Some exchanges don't support async close
            console.print("✅ Trading system stopped")
    
    def run(self):
        """Run the trading system"""
        self.display_banner()
        console.print("\n🏔️ Alpine Trading Bot - Live Trading System")
        console.print("=" * 60)
        console.print("📋 Features:")
        console.print("   • Real-time Bitget futures connection")
        console.print("   • Live market data display")
        console.print("   • Position monitoring")
        console.print("   • Beautiful terminal dashboard")
        console.print("\n⚠️  This is a live trading system connected to your Bitget account")
        console.print("💡 Press Ctrl+C to stop the system safely")
        
        try:
            asyncio.run(self.trading_loop())
        except KeyboardInterrupt:
            console.print("\n👋 Alpine Trading Bot stopped by user")
        except Exception as e:
            console.print(f"\n❌ Fatal error: {e}")

def main():
    """Main entry point"""
    system = AlpineTradingSystem()
    system.run()

if __name__ == "__main__":
    main()
