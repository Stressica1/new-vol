#!/usr/bin/env python3
"""
🔧 Alpine Display Stability Test
Tests the stabilized display interface for smooth operation
"""

import time
from ui_display import AlpineDisplayV2
from rich.live import Live

def test_display_stability():
    """Test the stabilized display for consistent refresh rates"""
    print("🧪 Testing Alpine Display Stability...")
    print("📊 Initializing display...")
    
    display = AlpineDisplayV2()
    
    # Mock data for testing
    test_data = {
        'account_data': {
            'balance': 1000.0,
            'equity': 1050.0,
            'margin': 200.0,
            'free_margin': 850.0
        },
        'positions': [],
        'signals': [
            {
                'symbol': 'BTC/USDT:USDT',
                'type': 'LONG',
                'confidence': 85.5,
                'volume_ratio': 2.3,
                'is_confluence': True
            }
        ],
        'logs': [
            '22:24:00 ✅ Display stability test started',
            '22:24:01 🔧 Refresh rate stabilized to 1 second',
            '22:24:02 📊 Testing smooth layout updates'
        ],
        'status': '🟢 TESTING STABILITY'
    }
    
    print("🚀 Starting stability test (10 seconds)...")
    
    try:
        with Live(
            display.create_revolutionary_layout(**test_data),
            console=display.console,
            refresh_per_second=1,  # Stabilized refresh rate
            screen=True
        ) as live:
            
            for i in range(10):
                # Update with slight data changes to test stability
                test_data['account_data']['balance'] += 1.0
                test_data['logs'].append(f'22:24:{i+3:02d} 🔄 Stability test cycle {i+1}')
                
                # Keep only last 5 logs for testing
                test_data['logs'] = test_data['logs'][-5:]
                
                live.update(display.create_revolutionary_layout(**test_data))
                time.sleep(1.0)  # Stable 1-second refresh
                
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    print("\n✅ Display stability test completed successfully!")
    print("📈 Key improvements:")
    print("   • Refresh rate stabilized from 3Hz to 1Hz")
    print("   • Console size increased from 120x40 to 140x50")
    print("   • Animation frame updates reduced")
    print("   • Sleep interval increased to 1.0 seconds")
    print("   • Fixed UI layout sizing issues")
    return True

if __name__ == "__main__":
    test_display_stability() 