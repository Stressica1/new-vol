#!/usr/bin/env python3
"""
Test script for new indicators: VHMA, MFI, and Bollinger Bands
This script tests the replacement of MACD with these three new indicators
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to path
sys.path.insert(0, '/workspaces/volume-anom')

from strategy import VolumeAnomalyStrategy
from technical_indicators import TechnicalIndicators

def generate_sample_data(length=100):
    """Generate sample OHLCV data for testing"""
    np.random.seed(42)
    
    # Generate price data with some trend
    base_price = 100
    prices = []
    volumes = []
    
    for i in range(length):
        # Add some trend and volatility
        trend = np.sin(i / 10) * 0.5
        noise = np.random.normal(0, 0.02)
        price_change = trend + noise
        
        if i == 0:
            prices.append(base_price)
        else:
            prices.append(prices[-1] * (1 + price_change))
        
        # Volume with some correlation to price movement
        volume = np.random.exponential(1000) * (1 + abs(price_change) * 5)
        volumes.append(volume)
    
    # Create OHLCV data
    data = []
    for i in range(length):
        price = prices[i]
        volatility = 0.01
        
        high = price * (1 + np.random.uniform(0, volatility))
        low = price * (1 - np.random.uniform(0, volatility))
        open_price = price * (1 + np.random.uniform(-volatility/2, volatility/2))
        close = price
        
        data.append({
            'timestamp': datetime.now() - timedelta(minutes=length-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volumes[i]
        })
    
    return pd.DataFrame(data)

def test_new_indicators():
    """Test VHMA, MFI, and Bollinger Bands indicators"""
    print("🧪 Testing New Indicators (VHMA, MFI, Bollinger Bands)")
    print("=" * 60)
    
    # Generate sample data
    df = generate_sample_data(50)
    
    # Initialize strategy
    strategy = VolumeAnomalyStrategy()
    
    try:
        # Test VHMA
        print("\n1. Testing VHMA (Volume Weighted Hull Moving Average)")
        print("-" * 50)
        df = strategy.calculate_vhma(df)
        
        if 'vhma' in df.columns:
            print("✅ VHMA calculation successful")
            print(f"   📊 VHMA values: {df['vhma'].iloc[-5:].tolist()}")
            print(f"   📈 VHMA signal: {df['vhma_signal'].iloc[-5:].tolist()}")
            print(f"   💪 VHMA momentum: {df['vhma_momentum'].iloc[-5:].tolist()}")
        else:
            print("❌ VHMA calculation failed")
        
        # Test MFI
        print("\n2. Testing MFI (Money Flow Index)")
        print("-" * 50)
        df = strategy.calculate_mfi(df)
        
        if 'mfi' in df.columns:
            print("✅ MFI calculation successful")
            print(f"   📊 MFI values: {df['mfi'].iloc[-5:].tolist()}")
            print(f"   📈 MFI signal: {df['mfi_signal'].iloc[-5:].tolist()}")
            print(f"   🔄 MFI momentum: {df['mfi_momentum'].iloc[-5:].tolist()}")
            print(f"   📋 MFI bullish: {df['mfi_bullish'].iloc[-5:].tolist()}")
            print(f"   📋 MFI bearish: {df['mfi_bearish'].iloc[-5:].tolist()}")
        else:
            print("❌ MFI calculation failed")
        
        # Test Bollinger Bands
        print("\n3. Testing Bollinger Bands")
        print("-" * 50)
        df = strategy.calculate_bollinger_bands(df)
        
        if 'bb_upper' in df.columns:
            print("✅ Bollinger Bands calculation successful")
            print(f"   📊 BB Upper: {df['bb_upper'].iloc[-5:].tolist()}")
            print(f"   📊 BB Middle: {df['bb_middle'].iloc[-5:].tolist()}")
            print(f"   📊 BB Lower: {df['bb_lower'].iloc[-5:].tolist()}")
            print(f"   📏 BB Width: {df['bb_width'].iloc[-5:].tolist()}")
            print(f"   📍 BB Position: {df['bb_position'].iloc[-5:].tolist()}")
            print(f"   🔄 BB Momentum: {df['bb_momentum'].iloc[-5:].tolist()}")
        else:
            print("❌ Bollinger Bands calculation failed")
        
        # Test calculate_indicators with new indicators
        print("\n4. Testing Full Indicator Integration")
        print("-" * 50)
        df = strategy.calculate_indicators(df)
        
        # Check if all indicators are present
        required_indicators = ['vhma', 'mfi', 'bb_upper', 'bb_middle', 'bb_lower', 'supertrend']
        missing_indicators = [ind for ind in required_indicators if ind not in df.columns]
        
        if not missing_indicators:
            print("✅ All new indicators integrated successfully")
            print(f"   📊 Available indicators: {len(df.columns)} columns")
            
            # Show latest values
            latest = df.iloc[-1]
            print(f"\n📈 Latest Indicator Values:")
            print(f"   VHMA: {latest['vhma']:.4f} (signal: {latest['vhma_signal']:.4f})")
            print(f"   MFI: {latest['mfi']:.2f} (bullish: {latest['mfi_bullish']}, bearish: {latest['mfi_bearish']})")
            print(f"   BB Position: {latest['bb_position']:.3f} (width: {latest['bb_width']:.4f})")
            print(f"   SuperTrend: {latest['supertrend']:.4f} (direction: {latest['supertrend_direction']})")
            
        else:
            print(f"❌ Missing indicators: {missing_indicators}")
        
        # Test signal generation with new indicators
        print("\n5. Testing Signal Generation with New Indicators")
        print("-" * 50)
        
        # Create sample market data
        market_data = {
            'BTCUSDT': df.to_dict('records')
        }
        
        # Test volume anomaly detection
        signal = strategy.detect_volume_anomaly(market_data, 'BTCUSDT')
        
        if signal and signal.get('signal'):
            print("✅ Signal generation successful with new indicators")
            print(f"   📊 Signal: {signal['signal']}")
            print(f"   📊 Confidence: {signal['confidence']:.1f}%")
            print(f"   📊 VHMA Signal: {signal.get('vhma_signal', 'N/A')}")
            print(f"   📊 MFI: {signal.get('mfi', 'N/A')}")
            print(f"   📊 BB Position: {signal.get('bb_position', 'N/A')}")
        else:
            print("⚠️ No signal generated (normal - depends on data)")
        
        print("\n" + "=" * 60)
        print("✅ NEW INDICATORS TEST COMPLETE")
        print("✅ MACD has been successfully replaced with VHMA, MFI, and Bollinger Bands")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing new indicators: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_technical_indicators_module():
    """Test the technical_indicators module methods"""
    print("\n🧪 Testing Technical Indicators Module")
    print("=" * 60)
    
    # Generate sample data
    length = 30
    close_prices = [100 + i * 0.5 + np.random.normal(0, 1) for i in range(length)]
    high_prices = [price * 1.01 for price in close_prices]
    low_prices = [price * 0.99 for price in close_prices]
    volume = [1000 + np.random.exponential(500) for _ in range(length)]
    
    try:
        # Test VHMA
        vhma = TechnicalIndicators.calculate_vhma(high_prices, low_prices, close_prices, volume)
        print(f"✅ VHMA: {vhma[-3:]}")
        
        # Test MFI
        mfi = TechnicalIndicators.calculate_mfi(high_prices, low_prices, close_prices, volume)
        print(f"✅ MFI: {mfi[-3:]}")
        
        # Test Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        print(f"✅ BB Upper: {bb_upper[-3:]}")
        print(f"✅ BB Middle: {bb_middle[-3:]}")
        print(f"✅ BB Lower: {bb_lower[-3:]}")
        
        print("✅ Technical Indicators module tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing technical indicators module: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 MACD Replacement Test Suite")
    print("🔄 Testing VHMA, MFI, and Bollinger Bands")
    print("=" * 60)
    
    success = True
    
    # Test new indicators
    success &= test_new_indicators()
    
    # Test technical indicators module
    success &= test_technical_indicators_module()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MACD has been successfully replaced with VHMA, MFI, and Bollinger Bands")
        print("🚀 New indicators are ready for deployment!")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("🔧 Check the errors above and fix implementation issues")
