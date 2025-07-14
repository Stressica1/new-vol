#!/usr/bin/env python3
"""
🤖 Alpine Bot Manager - Process Control System
Automatically kills all other Alpine bot processes when starting a new bot
"""

import os
import sys
import psutil
import signal
import time
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class AlpineBotManager:
    """🔧 Alpine Bot Process Manager"""
    
    def __init__(self):
        self.alpine_processes = [
            'alpine_bot.py',
            'simple_alpine.py', 
            'simple_alpine_trader.py',
            'trading_dashboard.py',
            'volume_anom_bot.py'
        ]
    
    def find_alpine_processes(self) -> List[dict]:
        """Find all running Alpine bot processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1:
                    script_name = os.path.basename(cmdline[1]) if len(cmdline) > 1 else ''
                    
                    # Check if it's an Alpine bot process
                    if script_name in self.alpine_processes:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': script_name,
                            'cmdline': ' '.join(cmdline)
                        })
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
                continue
                
        return processes
    
    def kill_alpine_processes(self, exclude_current: bool = True) -> int:
        """Kill all Alpine bot processes (excluding current if specified)"""
        current_pid = os.getpid()
        killed_count = 0
        
        processes = self.find_alpine_processes()
        
        if not processes:
            console.print("✅ No running Alpine bot processes found")
            return 0
        
        console.print(f"\n🔍 Found {len(processes)} Alpine bot processes:")
        
        for proc in processes:
            if exclude_current and proc['pid'] == current_pid:
                console.print(f"  • [yellow]PID {proc['pid']}[/yellow]: {proc['name']} [dim](current process - skipping)[/dim]")
                continue
                
            console.print(f"  • [red]PID {proc['pid']}[/red]: {proc['name']}")
            
            try:
                # Try graceful termination first
                os.kill(proc['pid'], signal.SIGTERM)
                
                # Wait a bit for graceful shutdown
                time.sleep(1)
                
                # Check if process still exists, force kill if needed
                try:
                    os.kill(proc['pid'], 0)  # Check if process exists
                    console.print(f"    ⚡ Force killing PID {proc['pid']}")
                    os.kill(proc['pid'], signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already terminated
                    
                killed_count += 1
                console.print(f"    ✅ Killed {proc['name']} (PID {proc['pid']})")
                
            except ProcessLookupError:
                console.print(f"    ⚠️ Process {proc['pid']} already terminated")
            except PermissionError:
                console.print(f"    ❌ Permission denied for PID {proc['pid']}")
            except Exception as e:
                console.print(f"    ❌ Error killing PID {proc['pid']}: {e}")
        
        if killed_count > 0:
            console.print(f"\n🛑 Killed {killed_count} Alpine bot processes")
            time.sleep(2)  # Give time for cleanup
        
        return killed_count
    
    def start_bot_with_cleanup(self, bot_script: str):
        """Start a bot after killing all other Alpine processes"""
        console.print(Panel.fit(
            Text("🤖 ALPINE BOT MANAGER", style="bold green", justify="center"),
            subtitle=f"Starting {bot_script}"
        ))
        
        # Kill all other Alpine processes
        self.kill_alpine_processes(exclude_current=True)
        
        # Clear logs directory
        try:
            if os.path.exists('logs'):
                for log_file in os.listdir('logs'):
                    if log_file.endswith('.log'):
                        os.remove(os.path.join('logs', log_file))
                console.print("🧹 Cleared old log files")
        except Exception as e:
            console.print(f"⚠️ Could not clear logs: {e}")
        
        console.print(f"\n🚀 Starting {bot_script}...")
        console.print("=" * 60)
        
        # Start the bot
        try:
            os.execv(sys.executable, [sys.executable, bot_script])
        except Exception as e:
            console.print(f"❌ Failed to start {bot_script}: {e}")
            sys.exit(1)

def kill_all_alpine_bots():
    """Standalone function to kill all Alpine bot processes"""
    manager = AlpineBotManager()
    killed = manager.kill_alpine_processes(exclude_current=False)
    
    if killed > 0:
        console.print(f"\n✅ Successfully killed {killed} Alpine bot processes")
    else:
        console.print("✅ No Alpine bot processes were running")

def main():
    """Main entry point for bot manager"""
    if len(sys.argv) < 2:
        console.print("Usage: python bot_manager.py <bot_script>")
        console.print("       python bot_manager.py kill  # Kill all bots")
        console.print("")
        console.print("Available bots:")
        console.print("  • alpine_bot.py")
        console.print("  • simple_alpine.py") 
        console.print("  • simple_alpine_trader.py")
        console.print("  • trading_dashboard.py")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "kill":
        kill_all_alpine_bots()
        return
    
    if not command.endswith('.py'):
        command += '.py'
    
    if not os.path.exists(command):
        console.print(f"❌ Bot script '{command}' not found")
        sys.exit(1)
    
    manager = AlpineBotManager()
    manager.start_bot_with_cleanup(command)

if __name__ == "__main__":
    main() 