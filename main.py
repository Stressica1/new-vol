#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Main Entry Point
🚀 Professional trading system with Bloomberg Terminal-inspired interface
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path
from loguru import logger

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from alpine_bot_complete import AlpineCompleteBot

def main():
    """Main entry point for Alpine Trading Bot"""
    try:
        logger.info("🏔️ Starting Alpine Trading Bot...")
        
        # Create and start the bot
        bot = AlpineCompleteBot()
        
        # Start the trading system
        asyncio.run(bot.start())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 