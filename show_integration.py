#!/usr/bin/env python3
"""
Show Volume Anomaly → Alpine Bot → Bitget Integration
"""

import json

def show_integration_results():
    """Show how volume anomaly results feed into Bitget trading"""
    
    try:
        with open('results_fixed.json', 'r') as f:
            data = json.load(f)
        
        print("🏔️ ALPINE-BITGET INTEGRATION PREVIEW")
        print("=" * 60)
        print("📊 Volume Anomaly Analysis → 🏔️ Alpine Bot → 💱 Bitget Trading")
        print("=" * 60)
        
        high_priority = data['trading_targets']['high_priority']
        medium_priority = data['trading_targets']['medium_priority'][:15]
        
        print(f"\n🎯 HIGH PRIORITY TARGETS ({len(high_priority)} coins):")
        for i, target in enumerate(high_priority, 1):
            symbol = target['symbol']
            score = target['score']
            confidence = target['confidence']
            print(f"  {i}. {symbol:8} - Score: {score:5.1f} - Confidence: {confidence:6.1%}")
        
        print(f"\n📈 MEDIUM PRIORITY TARGETS (top 15 of {len(data['trading_targets']['medium_priority'])}):")
        for i, target in enumerate(medium_priority, 1):
            symbol = target['symbol']
            score = target['score']
            confidence = target['confidence']
            print(f"  {i:2}. {symbol:8} - Score: {score:5.1f} - Confidence: {confidence:6.1%}")
        
        print(f"\n💱 BITGET TRADING PAIRS FOR ALPINE BOT:")
        print("-" * 40)
        all_targets = high_priority + medium_priority
        for i, target in enumerate(all_targets, 1):
            symbol = target['symbol']
            bitget_pair = f"{symbol}/USDT:USDT"
            print(f"  {i:2}. {bitget_pair}")
        
        print(f"\n📊 INTEGRATION SUMMARY:")
        print(f"  • Total pairs selected: {len(all_targets)}")
        print(f"  • High priority: {len(high_priority)}")
        print(f"  • Medium priority: {len(medium_priority)}")
        print(f"  • Ready for Bitget trading via Alpine Bot")
        
        # Show what Alpine Bot would receive
        print(f"\n🔧 ALPINE BOT CONFIGURATION UPDATE:")
        print("TRADING_PAIRS = [")
        for target in all_targets:
            symbol = target['symbol']
            print(f'    "{symbol}/USDT:USDT",')
        print("]")
        
    except FileNotFoundError:
        print("❌ Results file not found. Run volume anomaly analysis first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_integration_results() 