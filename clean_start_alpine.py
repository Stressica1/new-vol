#!/usr/bin/env python3
"""
🚀 Clean Start Alpine Bot
Ensures all other bot processes are killed before starting
"""

import os
import sys
import time
from bot_manager import AlpineBotManager
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

def main():
    console = Console()
    manager = AlpineBotManager()
    
    # Header
    console.print(Panel.fit(
        "🏔️ ALPINE BOT CLEAN STARTUP\n🛑 Terminating all existing bots first",
        style="bold green"
    ))
    
    # Step 1: Find existing processes
    console.print("\n🔍 [yellow]Step 1: Scanning for existing bot processes...[/yellow]")
    existing = manager.find_alpine_processes()
    
    if existing:
        console.print(f"Found {len(existing)} existing bot processes:")
        for proc in existing:
            console.print(f"  • PID {proc['pid']}: {proc['name']}")
    else:
        console.print("✅ No existing bot processes found")
    
    # Step 2: Kill all processes
    console.print("\n🛑 [red]Step 2: Terminating all bot processes...[/red]")
    killed_count = manager.kill_alpine_processes(exclude_current=False)
    
    if killed_count > 0:
        console.print(f"✅ Successfully terminated {killed_count} processes")
        
        # Wait and double-check
        console.print("\n⏳ [yellow]Waiting for processes to fully terminate...[/yellow]")
        for i in track(range(3), description="Waiting..."):
            time.sleep(1)
        
        # Final verification
        remaining = manager.find_alpine_processes()
        if remaining:
            console.print(f"⚡ [red]Force killing {len(remaining)} stubborn processes...[/red]")
            for proc in remaining:
                try:
                    os.kill(proc['pid'], 9)  # SIGKILL
                    console.print(f"  💀 Force killed PID {proc['pid']}")
                except:
                    pass
    
    # Step 3: Clean start
    console.print("\n🚀 [bold green]Step 3: Starting fresh Alpine Bot...[/bold green]")
    console.print("=" * 60)
    
    # Import and run Alpine bot
    try:
        from alpine_bot import main as alpine_main
        alpine_main()
    except KeyboardInterrupt:
        console.print("\n👋 Terminated by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 