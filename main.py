#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Main Entry Point
Enhanced entry point with comprehensive logging and error handling
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced logging system
from enhanced_logging import (
    alpine_logger, 
    EnhancedErrorHandler, 
    log_function_calls,
    log_startup_banner,
    log_shutdown
)
from loguru import logger

@log_function_calls
def main():
    """Main entry point for Alpine Trading Bot with enhanced logging"""
    
    # Initialize logging system
    log_startup_banner()
    
    with EnhancedErrorHandler("Alpine Bot Startup"):
        logger.info("🏔️ Alpine Trading Bot - Starting with Enhanced Logging...")
        logger.info("=" * 80)
        
        try:
            # Import from the new structure
            logger.info("📦 Importing Alpine Trading Bot components...")
            from src.core.bot import AlpineBot
            from src.core.config import get_exchange_config
            
            logger.success("✅ Successfully imported Alpine Trading Bot components")
            
            # Get and log configuration
            config = get_exchange_config()
            alpine_logger.log_config(config)
            
            # Create and run the bot
            logger.info("🚀 Initializing Alpine Trading Bot...")
            bot = AlpineBot()
            
            logger.info("▶️ Starting Alpine Trading Bot...")
            bot.run()
            
        except ImportError as e:
            logger.error(f"❌ Import Error: {e}")
            alpine_logger.log_exception(e, "Import Error")
            logger.warning("\n🔧 Trying to run with legacy structure...")
            
            with EnhancedErrorHandler("Legacy Bot Startup"):
                try:
                    # Try legacy imports if available
                    logger.info("📦 Attempting legacy imports...")
                    from archives.old_versions.alpine_bot import AlpineTradingBot as LegacyBot
                    
                    logger.success("✅ Legacy imports successful - Running with legacy bot...")
                    bot = LegacyBot()
                    bot.run()
                    
                except Exception as legacy_error:
                    logger.error(f"❌ Legacy import also failed: {legacy_error}")
                    alpine_logger.log_exception(legacy_error, "Legacy Import Failure")
                    
                    logger.info("\n📋 Available options:")
                    logger.info("  1. Use the launcher: python scripts/deployment/launch_alpine.py")
                    logger.info("  2. Run individual components from src/ directory")
                    logger.info("  3. Check the documentation in docs/")
                    logger.info("  4. Check the log files in logs/ directory for detailed error information")
                    return 1
                    
        except Exception as e:
            logger.error(f"❌ Critical error starting bot: {e}")
            alpine_logger.log_exception(e, "Critical Bot Startup Error")
            
            logger.info("\n🔧 Troubleshooting suggestions:")
            logger.info("  1. Check the error logs in logs/alpine_errors_*.log")
            logger.info("  2. Try running with the launcher: python scripts/deployment/launch_alpine.py")
            logger.info("  3. Verify all dependencies are installed: pip install -r requirements.txt")
            logger.info("  4. Check the configuration in src/core/config.py")
            return 1
    
    logger.success("🎉 Alpine Trading Bot session completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
