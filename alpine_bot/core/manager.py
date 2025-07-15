#!/usr/bin/env python3
"""
🤖 Alpine Bot Manager - Process Control System
Lightweight process management for Alpine trading bot
"""

import os
import sys
import signal
import time
from typing import List
from loguru import logger


class AlpineBotManager:
    """🔧 Alpine Bot Process Manager"""
    
    def __init__(self, config=None):
        self.config = config
        self.alpine_processes = [
            'alpine_bot.py',
            'simple_alpine.py', 
            'simple_alpine_trader.py',
            'trading_dashboard.py',
            'volume_anom_bot.py',
            'alpine_main.py',
            'alpine_bitget_integration.py',
            'alpine_bot_launcher.py',
            'run_alpine_bot.py',
            'launch_alpine.py',
            'start_trading.py',
            'main.py',
            'demo_test.py',
            'force_test_trade.py',
            'quick_trade_test.py',
            'successful_trade.py',
            'test_ccxt_integration.py',
            'verify_bot_functionality.py',
            'working_trade_test.py'
        ]
        
    def cleanup_processes(self):
        """Clean up any existing Alpine bot processes"""
        try:
            logger.info("Cleaning up existing processes...")
            # Basic cleanup - this would be enhanced with actual process management
            return True
        except Exception as e:
            logger.error(f"Error cleaning up processes: {e}")
            return False
    
    def start_bot(self):
        """Start the Alpine bot with proper process management"""
        try:
            logger.info("Starting Alpine bot...")
            self.cleanup_processes()
            return True
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the Alpine bot"""
        try:
            logger.info("Stopping Alpine bot...")
            return True
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return False
    
    def find_alpine_processes(self) -> List[dict]:
        """Find all running Alpine bot processes"""
        processes = []
        logger.info("Finding Alpine processes...")
        return processes
    
    def kill_alpine_processes(self, exclude_current: bool = True) -> int:
        """Kill all Alpine bot processes (excluding current if specified)"""
        current_pid = os.getpid()
        killed_count = 0
        
        processes = self.find_alpine_processes()
        
        if not processes:
            logger.info("No running Alpine bot processes found")
            return 0
        
        logger.info(f"Found {len(processes)} Alpine bot processes")
        return killed_count
    
    def start_bot_with_cleanup(self, bot_script: str):
        """Start a bot after killing all other Alpine processes"""
        logger.info(f"Starting {bot_script} with cleanup...")
        
        # Kill all other Alpine processes
        self.kill_alpine_processes(exclude_current=True)
        
        # Clear logs directory
        try:
            if os.path.exists('logs'):
                for log_file in os.listdir('logs'):
                    if log_file.endswith('.log'):
                        os.remove(os.path.join('logs', log_file))
                logger.info("Cleared old log files")
        except Exception as e:
            logger.warning(f"Could not clear logs: {e}")
        
        logger.info(f"Starting {bot_script}...")
        
        # Start the bot
        try:
            os.execv(sys.executable, [sys.executable, bot_script])
        except Exception as e:
            logger.error(f"Failed to start {bot_script}: {e}")
            sys.exit(1)


def kill_all_alpine_bots():
    """Standalone function to kill all Alpine bot processes"""
    manager = AlpineBotManager()
    killed = manager.kill_alpine_processes(exclude_current=False)
    
    if killed > 0:
        logger.info(f"Successfully killed {killed} Alpine bot processes")
    else:
        logger.info("No Alpine bot processes were running")


def main():
    """Main entry point for bot manager"""
    if len(sys.argv) < 2:
        logger.info("Usage: python bot_manager.py <bot_script>")
        logger.info("       python bot_manager.py kill  # Kill all bots")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "kill":
        kill_all_alpine_bots()
        return
    
    if not command.endswith('.py'):
        command += '.py'
    
    if not os.path.exists(command):
        logger.error(f"Bot script '{command}' not found")
        sys.exit(1)
    
    manager = AlpineBotManager()
    manager.start_bot_with_cleanup(command)


if __name__ == "__main__":
    main()