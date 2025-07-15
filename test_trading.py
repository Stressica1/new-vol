#!/usr/bin/env python3
"""
Force Trading Test - Create a manual signal to test trading execution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ccxt
from datetime import datetime
from config import TradingConfig, get_exchange_config

# Import trading execution components
try:
    from src.trading.trade_executor import OptimizedTradeExecutor
    from src.trading.trading_engine import TradingEngine
    TRADING_ENABLED = True
except ImportError as e:
    print(f"❌ Trading components not available: {e}")
    TRADING_ENABLED = False

def test_trading_execution():
    """Test trading execution with a manual signal"""
    
    if not TRADING_ENABLED:
        print("❌ Trading execution is not available")
        return
    
    print("🚀 Testing trading execution...")
    
    # Initialize components
    config = TradingConfig()
    exchange_config = get_exchange_config()
    
    # Initialize exchange
    exchange = ccxt.bitget({
        'apiKey': exchange_config['apiKey'],
        'secret': exchange_config['secret'],
        'password': exchange_config['password'],
        'sandbox': exchange_config.get('sandbox', False),
        'enableRateLimit': True,
        'options': exchange_config.get('options', {})
    })
    
    # Initialize trading components
    try:
        trade_executor = OptimizedTradeExecutor(exchange)
        trading_engine = TradingEngine()
        print("✅ Trading components initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize trading components: {e}")
        return
    
    # Get current balance
    try:
        balance = exchange.fetch_balance({'type': 'swap'})
        usdt_info = balance.get('USDT', {})
        available_balance = float(usdt_info.get('total', 0) or 0)
        print(f"💰 Available balance: ${available_balance:.2f}")
        
        if available_balance < 10:
            print("❌ Insufficient balance for testing")
            return
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return
    
    # Create a manual trading signal
    test_signal = {
        'symbol': 'BTC/USDT:USDT',
        'type': 'BUY',
        'action': 'BUY',
        'confidence': 85,
        'price': 50000,  # Example price
        'volume_spike_pct': 500,
        'signal_score': 75,
        'max_leverage': 50,
        'timestamp': datetime.now()
    }
    
    print(f"📊 Test signal: {test_signal}")
    
    # Execute the trade
    try:
        print("🔥 Executing test trade...")
        order_result = trade_executor.execute_signal(test_signal)
        
        if order_result:
            print(f"✅ TRADE EXECUTED SUCCESSFULLY!")
            print(f"   Order ID: {order_result.get('id', 'N/A')}")
            print(f"   Symbol: {order_result.get('symbol', 'N/A')}")
            print(f"   Side: {order_result.get('side', 'N/A')}")
            print(f"   Amount: {order_result.get('amount', 'N/A')}")
            print(f"   Price: {order_result.get('price', 'N/A')}")
            print(f"   Status: {order_result.get('status', 'N/A')}")
        else:
            print("❌ Trade execution failed - No order result")
            
    except Exception as e:
        print(f"❌ Trade execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trading_execution()
