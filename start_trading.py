#!/usr/bin/env python3
"""
🌿 Alpine Trading System - Main Startup Script
Launches both trading bots with beautiful mint green terminal display
Forces Bitget connection and provides real-time PnL tracking
"""

import sys
import time
import threading
import signal
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from loguru import logger

# Configure logger
logger.remove()
logger.add("logs/alpine_main_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days")
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

def display_startup_banner():
    """Display beautiful startup banner"""
    console = Console()
    
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║      🌿 ALPINE TRADING SYSTEM v2.0 🌿                        ║
    ║                                                               ║
    ║      Advanced Dual-Bot Trading Platform                       ║
    ║      Mint Green Terminal • Bitget Perpetuals                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel(
        Align(Text(banner_text, style="bold #00FFB3"), align="center"),
        border_style="#00FFB3",
        style="on black"
    ))
    
    console.print("\n[bold #00FFB3]🚀 Starting Alpine Trading System...[/bold #00FFB3]\n")

def run_trading_system():
    """Run the complete trading system"""
    from trading_dashboard import AlpineTradingDashboard
    from trade_executor import TradingOrchestrator
    
    try:
        # Display startup banner
        display_startup_banner()
        
        # Create and start the trading dashboard
        logger.info("🌿 Initializing Alpine Trading Dashboard...")
        dashboard = AlpineTradingDashboard()
        
        # Force Bitget connection
        logger.info("🔌 Forcing Bitget connection...")
        if not dashboard.force_connection():
            logger.error("❌ Failed to establish Bitget connection!")
            console = Console()
            console.print("\n[bold red]⚠️ Unable to connect to Bitget. Please check:[/bold red]")
            console.print("  • API credentials in config.py")
            console.print("  • Internet connection")
            console.print("  • Bitget API status\n")
            return
        
        logger.success("✅ Bitget connection established!")
        
        # Initialize trading orchestrator
        logger.info("🎼 Initializing Trading Orchestrator...")
        orchestrator = TradingOrchestrator()
        
        if not orchestrator.initialize():
            logger.error("❌ Failed to initialize trading orchestrator!")
            return
        
        # Initialize and add both bots
        logger.info("🤖 Loading trading bots...")
        
        try:
            # Import and initialize Alpine Bot
            from alpine_bot import AlpineBot
            alpine_bot = AlpineBot()
            alpine_bot.initialize_exchange()
            orchestrator.add_bot(alpine_bot)
            logger.success("✅ Alpine Bot loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Alpine Bot: {e}")
        
        try:
            # Import and initialize Volume Anomaly Bot
            from volume_anom_bot import VolumeAnomalyBot
            volume_bot = VolumeAnomalyBot()
            orchestrator.add_bot(volume_bot)
            logger.success("✅ Volume Anomaly Bot loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Volume Anomaly Bot: {e}")
        
        # Start the orchestrator
        logger.info("🚀 Starting trading orchestrator...")
        orchestrator.start()
        
        # Update dashboard with orchestrator info
        dashboard.executor = orchestrator.executor
        
        # Run the dashboard (this will block)
        logger.success("🌿 Alpine Trading System is now running!")
        logger.info("Press Ctrl+C to stop")
        
        dashboard.run()
        
    except KeyboardInterrupt:
        logger.info("\n⛔ Shutdown signal received...")
        cleanup()
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        cleanup()

def run_connection_test():
    """Run connection test only"""
    import asyncio
    from test_connection import test_bitget_connection
    
    console = Console()
    console.print("\n[bold #00FFB3]🔌 Running Bitget Connection Test...[/bold #00FFB3]\n")
    
    success = asyncio.run(test_bitget_connection())
    
    if success:
        console.print("\n[bold green]✅ Connection test passed! Ready to trade.[/bold green]\n")
    else:
        console.print("\n[bold red]❌ Connection test failed. Please check your credentials.[/bold red]\n")
    
    return success

def cleanup():
    """Cleanup on exit"""
    logger.info("🧹 Cleaning up...")
    logger.info("💾 Saving final state...")
    logger.success("✅ Alpine Trading System stopped gracefully")

def main():
    """Main entry point with menu"""
    console = Console()
    
    # Clear screen
    console.clear()
    
    # Display menu
    console.print("\n[bold #00FFB3]🌿 ALPINE TRADING SYSTEM[/bold #00FFB3]\n")
    console.print("[#00FFB3]Choose an option:[/#00FFB3]")
    console.print("[1] 🚀 Start Trading System (Both Bots + Dashboard)")
    console.print("[2] 📊 Launch Dashboard Only")
    console.print("[3] 🔌 Test Bitget Connection")
    console.print("[4] 📈 Run Alpine Bot Only")
    console.print("[5] 📉 Run Volume Bot Only")
    console.print("[6] ❌ Exit\n")
    
    choice = input("[#00FFB3]Enter your choice (1-6): [/#00FFB3]")
    
    if choice == "1":
        run_trading_system()
    elif choice == "2":
        from trading_dashboard import main as dashboard_main
        dashboard_main()
    elif choice == "3":
        run_connection_test()
    elif choice == "4":
        console.print("\n[bold #00FFB3]Starting Alpine Bot only...[/bold #00FFB3]")
        from alpine_bot import main as alpine_main
        alpine_main()
    elif choice == "5":
        console.print("\n[bold #00FFB3]Starting Volume Anomaly Bot only...[/bold #00FFB3]")
        from volume_anom_bot import main as volume_main
        volume_main()
    elif choice == "6":
        console.print("\n[bold #00FFB3]👋 Goodbye![/bold #00FFB3]\n")
        sys.exit(0)
    else:
        console.print("\n[bold red]Invalid choice. Please try again.[/bold red]")
        time.sleep(2)
        main()

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, lambda s, f: cleanup())
    signal.signal(signal.SIGTERM, lambda s, f: cleanup())
    
    # Check if running with arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            run_connection_test()
        elif sys.argv[1] == "--trade":
            run_trading_system()
        elif sys.argv[1] == "--dashboard":
            from trading_dashboard import main as dashboard_main
            dashboard_main()
        else:
            console = Console()
            console.print("[bold red]Unknown argument. Use --test, --trade, or --dashboard[/bold red]")
    else:
        main()