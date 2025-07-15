#!/usr/bin/env python3
"""
Test script to verify the strategy is working properly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ccxt
import pandas as pd
from strategy import VolumeAnomalyStrategy
from config import TradingConfig, get_exchange_config

def test_strategy():
    """Test the strategy with real market data"""
    
    # Initialize components
    config = TradingConfig()
    exchange_config = get_exchange_config()
    strategy = VolumeAnomalyStrategy()
    
    # Initialize exchange
    exchange = ccxt.bitget({
        'apiKey': exchange_config['apiKey'],
        'secret': exchange_config['secret'],
        'password': exchange_config['password'],
        'sandbox': exchange_config.get('sandbox', False),
        'enableRateLimit': True,
        'options': exchange_config.get('options', {})
    })
    
    # Test with BTC/USDT
    symbol = 'BTC/USDT:USDT'
    
    print(f"🔍 Testing strategy with {symbol}")
    
    try:
        # Get market data
        ohlcv = exchange.fetch_ohlcv(symbol, '3m', limit=100)
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        print(f"📊 Got {len(df)} data points")
        
        # Calculate indicators
        df = strategy.calculate_indicators(df)
        
        # Show some key metrics
        latest = df.iloc[-1]
        print(f"📈 Latest data:")
        print(f"   Volume: {latest['volume']:.2f}")
        print(f"   Volume SMA: {latest['volume_sma']:.2f}")
        print(f"   Volume Ratio: {latest['volume_ratio']:.2f}")
        print(f"   Volume Anomaly: {latest['volume_anomaly']}")
        print(f"   RSI: {latest['rsi']:.2f}")
        print(f"   Price: {latest['close']:.2f}")
        
        # Check if we meet minimum requirements
        print(f"\n🎯 Strategy Requirements:")
        print(f"   Min Volume Ratio: {strategy.min_volume_ratio}")
        print(f"   Meets Volume Ratio: {latest['volume_ratio'] >= strategy.min_volume_ratio}")
        print(f"   Volume Anomaly: {latest['volume_anomaly']}")
        
        # Test signal detection
        signal = strategy.detect_volume_anomaly(df)
        
        print(f"\n🚨 Signal Result:")
        print(f"   Signal: {signal.get('signal', 'None')}")
        print(f"   Confidence: {signal.get('confidence', 0):.1f}%")
        print(f"   Volume Ratio: {signal.get('volume_ratio', 0):.2f}")
        
        if signal.get('signal'):
            print(f"✅ Signal detected! {signal['signal']} with {signal['confidence']:.1f}% confidence")
        else:
            print("❌ No signal detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strategy()
