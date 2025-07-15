#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Main Engine
Functional trading bot with proper structure and working components
"""

import sys
import os
import time
import threading
import signal
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.config import TradingConfig
    from src.core.bot import AlpineBot as CoreAlpineBot
    print("✅ Using new structure imports")
except ImportError:
    try:
        from working_trading_system import AlpineTradingSystem as CoreAlpineBot
        print("✅ Using working trading system")
    except ImportError:
        print("❌ No working bot implementation found")
        sys.exit(1)

class AlpineBot:
    """🏔️ Alpine Trading Bot - Main Wrapper"""
    
    def __init__(self):
        """Initialize the Alpine Bot"""
        self.bot_instance = None
        self.running = False
        
        # Kill existing processes
        self.cleanup_existing_processes()
        
        # Initialize bot
        try:
            self.bot_instance = CoreAlpineBot()
            print("✅ Bot initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing bot: {e}")
            raise
    
    def cleanup_existing_processes(self):
        """Clean up any existing bot processes"""
        try:
            import psutil
            current_pid = os.getpid()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue
                        
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(term in cmdline for term in ['alpine_bot', 'trading_system', 'bot.py']):
                        print(f"🛑 Killing existing process: {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except ImportError:
            # psutil not available, use simple approach
            os.system("pkill -f 'alpine_bot\\|trading_system\\|bot.py' 2>/dev/null || true")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n⏹️ Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """🚀 Start the Alpine bot"""
        if not self.bot_instance:
            print("❌ Bot not initialized")
            return
        
        self.setup_signal_handlers()
        self.running = True
        
        print("🏔️ Alpine Trading Bot Starting...")
        print("=" * 60)
        
        try:
            # Use the appropriate method based on bot type
            if hasattr(self.bot_instance, 'run'):
                self.bot_instance.run()
            elif hasattr(self.bot_instance, 'start'):
                self.bot_instance.start()
            else:
                print("❌ Bot doesn't have run() or start() method")
                
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        if hasattr(self.bot_instance, 'stop'):
            self.bot_instance.stop()
        print("👋 Alpine bot stopped")

def main():
    """Main entry point"""
    try:
        bot = AlpineBot()
        bot.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
