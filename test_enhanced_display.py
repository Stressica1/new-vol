#!/usr/bin/env python3
"""
Test script to verify the enhanced display is working
"""

import sys
from pathlib import Path
import time

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_display():
    """Test the enhanced display system"""
    
    print("🧪 Testing Enhanced Alpine Display...")
    print("=" * 50)
    
    try:
        from src.ui.display import AlpineDisplay
        
        # Create display instance
        display = AlpineDisplay()
        
        # Test data
        account_data = {
            'balance': 12500.0,
            'equity': 12750.0,
            'margin': 250.0,
            'free_margin': 12500.0
        }
        
        positions = [
            {
                'symbol': 'BTC/USDT:USDT',
                'side': 'LONG',
                'contracts': 0.1,
                'entryPrice': 43000.0,
                'markPrice': 43500.0,
                'unrealizedPnl': 50.0
            }
        ]
        
        signals = [
            {
                'symbol': 'BTC/USDT',
                'signal': 'BUY',
                'type': 'VOLUME_ANOMALY',
                'price': 43250.0,
                'confidence': 0.85,
                'timestamp': time.time()
            }
        ]
        
        logs = [
            "🚀 Alpine Bot initialized",
            "💎 Connected to Bitget exchange",
            "📊 Scanning for volume anomalies...",
            "🎯 Signal detected: BTC/USDT - BUY"
        ]
        
        # Test the revolutionary layout
        layout = display.create_revolutionary_layout(account_data, positions, signals, logs, "RUNNING")
        
        print("✅ Revolutionary layout created successfully!")
        
        # Render the display
        display.console.clear()
        display.console.print(layout)
        
        print("\n🎉 Enhanced display is working!")
        
        # Keep it running for a few seconds to see the display
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_display()
    sys.exit(0 if success else 1)
