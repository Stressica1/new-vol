#!/usr/bin/env python3
"""
🛑 Kill All Bots Script
Quickly kill all Alpine and trading bot processes
"""

from bot_manager import kill_all_alpine_bots
from rich.console import Console
from rich.panel import Panel

def main():
    console = Console()
    
    console.print(Panel.fit(
        "🛑 KILL ALL TRADING BOTS",
        style="bold red"
    ))
    
    kill_all_alpine_bots()
    
    console.print("\n🏁 All bot processes terminated!")

if __name__ == "__main__":
    main() 