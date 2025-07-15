#!/usr/bin/env python3
"""Test trading components import"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.trading.trade_executor import OptimizedTradeExecutor
    print("✅ OptimizedTradeExecutor imported successfully")
    
    from src.trading.trading_engine import TradingEngine
    print("✅ TradingEngine imported successfully")
    
    print("🚀 All trading components available!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
