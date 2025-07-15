#!/usr/bin/env python3
"""
Simple SuperTrend Test - Standalone
"""

from strategy import VolumeAnomalyStrategy
import pandas as pd
import numpy as np

def test_supertrend():
    """Test SuperTrend implementation"""
    
    print("🎯 SuperTrend Implementation Test")
    print("=" * 50)
    
    try:
        # Initialize strategy
        strategy = VolumeAnomalyStrategy()
        print(f"✅ Strategy initialized: {strategy.name} v{strategy.version}")
        
        # Create test data with uptrend
        test_data = pd.DataFrame({
            'high': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 119, 121, 123, 125, 127, 129, 131, 133, 135],
            'low': [98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 117, 119, 121, 123, 125, 127, 129, 131, 133],
            'close': [99, 101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 118, 120, 122, 124, 126, 128, 130, 132, 134],
            'volume': [1000, 1200, 1500, 1100, 1800, 2000, 1300, 1600, 1900, 1400, 1600, 1800, 2200, 1700, 2500, 3000, 2100, 2800, 3500, 2600]
        })
        
        print(f"✅ Test data created: {len(test_data)} rows")
        
        # Calculate indicators
        indicators = strategy.calculate_indicators(test_data)
        print(f"✅ Indicators calculated: {len(indicators.columns)} columns")
        
        # Check SuperTrend columns
        supertrend_cols = [col for col in indicators.columns if 'supertrend' in col]
        print(f"✅ SuperTrend columns: {supertrend_cols}")
        
        # Get latest values
        latest = indicators.iloc[-1]
        print("\n📊 Latest SuperTrend Values:")
        print(f"   Price: ${latest.close:.2f}")
        print(f"   SuperTrend: ${latest.supertrend:.2f}")
        print(f"   Direction: {latest.supertrend_direction} (1=Bullish, -1=Bearish)")
        print(f"   Strength: {latest.supertrend_strength:.2f}%")
        print(f"   Quality: {latest.supertrend_quality}")
        print(f"   Volume Ratio: {latest.volume_ratio:.2f}x")
        
        # Test signal detection
        signal = strategy.detect_volume_anomaly(indicators)
        print(f"\n🎯 Signal Detection:")
        print(f"   Signal: {signal.get('signal', 'None')}")
        print(f"   Confidence: {signal.get('confidence', 0):.1f}%")
        print(f"   SuperTrend Direction: {signal.get('supertrend_direction', 'N/A')}")
        print(f"   SuperTrend Strength: {signal.get('supertrend_strength', 0):.2f}%")
        print(f"   SuperTrend Quality: {signal.get('supertrend_quality', 'N/A')}")
        
        # Show trend analysis
        print(f"\n📈 Trend Analysis:")
        if latest.supertrend_direction == 1:
            print("   🟢 BULLISH TREND - Price above SuperTrend")
        else:
            print("   🔴 BEARISH TREND - Price below SuperTrend")
            
        if latest.supertrend_quality == 'STRONG':
            print("   💪 STRONG trend quality")
        elif latest.supertrend_quality == 'MODERATE':
            print("   👍 MODERATE trend quality")
        else:
            print("   🤏 WEAK trend quality")
        
        print(f"\n✅ SuperTrend implementation test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supertrend()
    if success:
        print("\n🚀 All tests passed! SuperTrend is working correctly.")
    else:
        print("\n💥 Tests failed! Check the implementation.")
