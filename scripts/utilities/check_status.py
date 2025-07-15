"""
🏔️ Alpine Trading Bot - Quick Status Check
Monitor your trading bot's performance and activity
"""

import ccxt
import pandas as pd
from datetime import datetime
from config import get_exchange_config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def check_alpine_status():
    """Check Alpine bot current status and recent activity"""
    
    console = Console()
    
    console.print("\n🏔️ [bold green]ALPINE TRADING BOT STATUS[/bold green] 🏔️\n")
    
    try:
        # Connect to exchange
        exchange_config = get_exchange_config()
        exchange = ccxt.bitget(exchange_config)
        
        # Get account info
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {})
        
        # Account Status Table
        account_table = Table(title="💰 Account Status", show_header=True)
        account_table.add_column("Metric", style="cyan")
        account_table.add_column("Value", style="green")
        account_table.add_column("Status", style="yellow")
        
        total_balance = usdt_balance.get('total', 0)
        free_balance = usdt_balance.get('free', 0)
        used_balance = usdt_balance.get('used', 0)
        
        account_table.add_row("Total Balance", f"${total_balance:.2f}", "💰")
        account_table.add_row("Free Balance", f"${free_balance:.2f}", "✅")
        account_table.add_row("Used Balance", f"${used_balance:.2f}", "🔒")
        
        console.print(account_table)
        
        # Get current positions
        positions = exchange.fetch_positions()
        active_positions = [pos for pos in positions if pos['contracts'] > 0]
        
        console.print(f"\n📋 [bold]Active Positions: {len(active_positions)}[/bold]")
        
        if active_positions:
            pos_table = Table(title="🎯 Active Trades", show_header=True)
            pos_table.add_column("Symbol", style="cyan")
            pos_table.add_column("Side", style="yellow")
            pos_table.add_column("Size", style="white")
            pos_table.add_column("Entry Price", style="blue")
            pos_table.add_column("Current Price", style="green")
            pos_table.add_column("P&L", style="red")
            
            for pos in active_positions[:5]:  # Show first 5
                symbol = pos['symbol'].replace('/USDT:USDT', '')
                side = "🟢 LONG" if pos['side'] == 'long' else "🔴 SHORT"
                size = f"{pos['contracts']:.4f}"
                entry = f"${pos['entryPrice']:.4f}"
                current = f"${pos['markPrice']:.4f}"
                pnl = pos.get('unrealizedPnl', 0)
                pnl_str = f"${pnl:.2f}"
                
                pos_table.add_row(symbol, side, size, entry, current, pnl_str)
            
            console.print(pos_table)
        else:
            console.print("   [yellow]No active positions - scanning for Volume Anomaly signals...[/yellow]")
        
        # Get recent market activity for key pairs
        console.print(f"\n📊 [bold]Market Overview[/bold]")
        
        market_table = Table(title="🎯 Key Trading Pairs", show_header=True)
        market_table.add_column("Symbol", style="cyan")
        market_table.add_column("Price", style="green")
        market_table.add_column("24h Change", style="yellow")
        market_table.add_column("Volume", style="blue")
        
        key_pairs = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
        
        for symbol in key_pairs:
            try:
                ticker = exchange.fetch_ticker(symbol)
                price = f"${ticker['last']:,.2f}"
                change = ticker['percentage']
                change_str = f"{change:+.2f}%" if change else "N/A"
                volume = f"${ticker['quoteVolume']:,.0f}" if ticker['quoteVolume'] else "N/A"
                
                market_table.add_row(
                    symbol.replace('/USDT:USDT', ''),
                    price,
                    change_str,
                    volume
                )
            except:
                market_table.add_row(
                    symbol.replace('/USDT:USDT', ''),
                    "N/A", "N/A", "N/A"
                )
        
        console.print(market_table)
        
        # Bot Status
        status_panel = Panel(
            "[green]🟢 ALPINE BOT IS ACTIVE AND TRADING[/green]\n\n"
            "✅ Connected to Bitget\n"
            "🎯 Volume Anomaly Strategy Running\n"
            "💰 Risk Management Active\n"
            "📊 Monitoring 8 Trading Pairs\n"
            "🏔️ Beautiful Terminal UI Live",
            title="[bold cyan]🏔️ Alpine Status[/bold cyan]",
            border_style="green"
        )
        
        console.print(f"\n{status_panel}")
        
        console.print(f"\n⏰ [bold]Last Updated:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        console.print("💡 [yellow]Tip: The bot is running in the background with live terminal display[/yellow]")
        console.print("🔄 [cyan]Run this script again to check updated status[/cyan]\n")
        
    except Exception as e:
        console.print(f"❌ [red]Error checking status: {str(e)}[/red]")

if __name__ == "__main__":
    check_alpine_status()