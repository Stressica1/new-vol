#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Main Entry Point
========================================

Professional volume anomaly trading system with real-time monitoring.
Single entry point for all bot operations.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Add alpine_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from alpine_bot import AlpineBot, TradingConfig, __version__

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Alpine Trading Bot - Professional Volume Anomaly Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start bot with default settings
  python main.py --test             # Run connectivity tests
  python main.py --status           # Show bot status
  python main.py --config custom.py # Use custom configuration
        """
    )
    
    parser.add_argument(
        "--version", action="version",
        version=f"Alpine Trading Bot v{__version__}"
    )
    
    parser.add_argument(
        "--test", action="store_true",
        help="Run connectivity and system tests"
    )
    
    parser.add_argument(
        "--status", action="store_true", 
        help="Show current bot status"
    )
    
    parser.add_argument(
        "--config", type=str,
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Reduce logging output"
    )
    
    return parser


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Setup logging configuration"""
    logger.remove()
    
    if quiet:
        level = "WARNING"
    elif verbose:
        level = "DEBUG"
    else:
        level = "INFO"
    
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level
    )
    
    logger.add(
        "logs/alpine_bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="DEBUG"
    )


def load_config(config_path: str = None) -> TradingConfig:
    """Load trading configuration"""
    if config_path:
        # Load custom configuration
        # This would implement custom config loading
        logger.info(f"Loading custom configuration from: {config_path}")
        return TradingConfig()
    else:
        return TradingConfig()


def run_tests():
    """Run connectivity and system tests"""
    logger.info("🧪 Running Alpine Trading Bot tests...")
    
    try:
        config = TradingConfig()
        bot = AlpineBot(config)
        
        # Test exchange connectivity
        if not bot.exchange_client.test_connection():
            logger.error("❌ Exchange connectivity test failed")
            return False
        
        logger.success("✅ All tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def show_status():
    """Show current bot status"""
    logger.info("📊 Alpine Trading Bot Status")
    logger.info("=" * 50)
    
    # This would show actual status
    logger.info("Status: Not implemented yet")
    logger.info("=" * 50)


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.quiet)
    
    # Show version and header
    logger.info(f"🏔️ Alpine Trading Bot v{__version__}")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Handle different modes
        if args.test:
            success = run_tests()
            sys.exit(0 if success else 1)
        
        elif args.status:
            show_status()
            sys.exit(0)
        
        else:
            # Start the bot
            logger.info("🚀 Starting Alpine Trading Bot...")
            bot = AlpineBot(config)
            bot.run()
    
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()