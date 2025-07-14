#!/usr/bin/env python3
"""
Direct Alpine Bot Runner - Runs the bot assuming environment is set up
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Import with better error handling
        print("🏔️ Starting Alpine Trading Bot...")
        print("=" * 60)
        
        try:
            from alpine_bot import AlpineBot
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("\nPlease ensure all dependencies are installed:")
            print("  pip install ccxt pandas numpy ta rich loguru")
            sys.exit(1)
        
        # Create and run the bot
        bot = AlpineBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()