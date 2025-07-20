#!/usr/bin/env python3
"""
🚀 Alpine Trading Bot Launcher
Clean, unified entry point for the trading system
"""

import asyncio
import sys
from alpine_trading_bot import main

if __name__ == "__main__":
    print("🏔️ Launching Alpine Trading Bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Alpine Bot shutdown complete")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start Alpine Bot: {e}")
        sys.exit(1)