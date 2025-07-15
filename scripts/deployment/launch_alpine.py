#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Cross-Platform Launcher
Simple terminal launcher for Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['rich', 'ccxt', 'pandas', 'loguru', 'watchdog']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def display_banner():
    """Display beautiful startup banner"""
    clear_screen()
    
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║      🏔️  ALPINE TRADING BOT - Cross-Platform Launcher  🏔️        ║
    ║                                                                  ║
    ║      Revolutionary Volume Anomaly Trading System                 ║
    ║      Beautiful Mint Green Terminal • 90% Success Rate           ║
    ║      Real-time Bitget Perpetuals Trading                        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel(
        Align(Text(banner, style="bold #00FFB3"), align="center"),
        border_style="#00FFB3",
        style="on black"
    ))

def show_menu():
    """Show main menu"""
    console.print("\n[bold #00FFB3]🚀 ALPINE TRADING SYSTEM - Choose Your Mission:[/bold #00FFB3]\n")
    
    options = [
        "[1] 🌿 Launch Full Trading System (Recommended)",
        "[2] 🔌 Test Bitget Connection Only", 
        "[3] 📊 Run Trading Dashboard Only",
        "[4] 🤖 Alpine Bot Only (Advanced)",
        "[5] 📈 Volume Anomaly Bot Only",
        "[6] 💻 Check System Status",
        "[7] ❌ Exit"
    ]
    
    for option in options:
        console.print(f"  {option}", style="#00FFB3")
    
    console.print()

def run_command(cmd, description):
    """Run a command and handle errors"""
    try:
        console.print(f"\n[bold #00FFB3]🚀 {description}...[/bold #00FFB3]")
        
        result = subprocess.run(cmd, shell=True, capture_output=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        return False
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        return False

def check_system_status():
    """Check system status and configuration"""
    console.print("\n[bold #00FFB3]💻 SYSTEM STATUS CHECK[/bold #00FFB3]\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    console.print(f"🐍 Python Version: [green]{python_version}[/green]")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        console.print(f"📦 Missing Packages: [red]{', '.join(missing)}[/red]")
        console.print("\n[yellow]Run: pip install -r requirements.txt[/yellow]")
    else:
        console.print("📦 Dependencies: [green]✅ All packages installed[/green]")
    
    # Check configuration files in new structure
    config_files = [
        ('src/core/config.py', 'Configuration'),
        ('src/core/bot.py', 'Bot Core'),
        ('scripts/deployment/start_trading.py', 'Trading Script'),
        ('tests/unit/test_connection.py', 'Connection Test'),
        ('src/ui/trading_dashboard.py', 'Trading Dashboard'),
        ('src/exchange/bitget_client.py', 'Bitget Client')
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            console.print(f"📁 {description}: [green]✅ Found[/green]")
        else:
            console.print(f"📁 {description}: [red]❌ Missing[/red]")
    
    # Check data directories
    data_dirs = ['data/logs', 'data/results', 'data/configs']
    for dir_path in data_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            console.print(f"📋 {dir_path}: [yellow]⚠️ Created[/yellow]")
        else:
            console.print(f"📋 {dir_path}: [green]✅ Ready[/green]")
    
    # Check .env file
    if os.path.exists('.env'):
        console.print("🔐 Environment File: [green]✅ Found[/green]")
    else:
        console.print("🔐 Environment File: [red]❌ Missing[/red]")
        console.print("   [yellow]Copy .env.example to .env and configure your API keys[/yellow]")
    
    # Check requirements.txt
    if os.path.exists('requirements.txt'):
        console.print("📋 Requirements File: [green]✅ Found[/green]")
    else:
        console.print("📋 Requirements File: [red]❌ Missing[/red]")
    
    console.print(f"\n💾 Working Directory: [cyan]{os.getcwd()}[/cyan]")

def main():
    """Main launcher function"""
    while True:
        display_banner()
        
        # Quick dependency check
        missing = check_dependencies()
        if missing:
            console.print(f"\n[red]❌ Missing dependencies: {', '.join(missing)}[/red]")
            console.print("[yellow]Please install: pip3 install -r requirements.txt[/yellow]")
            input("\nPress Enter to continue anyway...")
        
        show_menu()
        
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                # Full trading system
                success = run_command(f"{sys.executable} working_trading_system.py", "Launching Full Trading System")
                
            elif choice == "2":
                # Test connection
                success = run_command(f"{sys.executable} tests/unit/test_connection_simple.py", "Testing Bitget Connection")
                
            elif choice == "3":
                # Dashboard only  
                success = run_command(f"{sys.executable} -m src.ui.trading_dashboard", "Launching Trading Dashboard")
                
            elif choice == "4":
                # Alpine bot only
                success = run_command(f"{sys.executable} -m src.core.bot", "Launching Alpine Bot")
                
            elif choice == "5":
                # Volume bot only
                success = run_command(f"{sys.executable} archives/old_versions/volume_anom_bot.py", "Launching Volume Anomaly Bot")
                
            elif choice == "6":
                # System status
                check_system_status()
                input("\nPress Enter to continue...")
                continue
                
            elif choice == "7":
                console.print("\n[bold #00FFB3]👋 Thank you for using Alpine Trading Bot![/bold #00FFB3]")
                console.print("[#00FFB3]May your trades be profitable! 🚀[/#00FFB3]\n")
                break
                
            else:
                console.print("\n[red]❌ Invalid choice. Please try again.[/red]")
                time.sleep(2)
                continue
            
            # After running command
            if choice in ["1", "2", "3", "4", "5"]:
                console.print(f"\n[#00FFB3]Process completed. Returning to menu...[/#00FFB3]")
                time.sleep(3)
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error: {str(e)}[/red]")
            time.sleep(2)

if __name__ == "__main__":
    main() 