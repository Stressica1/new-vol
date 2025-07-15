#!/usr/bin/env python3
"""
🎯 Volume Spike Scalping Example with 1.25% Stop Loss
Shows actual profit/loss calculations for ZEREBRO scalping opportunity
"""

def calculate_scalp_trade(entry_price, leverage, direction="BUY"):
    """Calculate scalp trade targets with 1.25% stop loss"""
    
    # Updated scalping parameters
    target_profit = 0.02  # 2% profit target
    stop_loss = 0.0125    # 1.25% stop loss (improved from 1%)
    
    if direction == "BUY":
        # For long positions
        target_1 = entry_price * (1 + target_profit * 0.5)  # 1% target
        target_2 = entry_price * (1 + target_profit)        # 2% target
        stop_loss_price = entry_price * (1 - stop_loss)     # 1.25% stop loss
    else:
        # For short positions
        target_1 = entry_price * (1 - target_profit * 0.5)  # 1% target
        target_2 = entry_price * (1 - target_profit)        # 2% target
        stop_loss_price = entry_price * (1 + stop_loss)     # 1.25% stop loss
    
    # Calculate potential profits with leverage
    profit_target_1_pct = target_profit * 0.5 * leverage * 100  # 1% * leverage
    profit_target_2_pct = target_profit * leverage * 100        # 2% * leverage
    max_loss_pct = stop_loss * leverage * 100                   # 1.25% * leverage
    
    return {
        'entry_price': entry_price,
        'target_1': target_1,
        'target_2': target_2,
        'stop_loss_price': stop_loss_price,
        'profit_target_1_pct': profit_target_1_pct,
        'profit_target_2_pct': profit_target_2_pct,
        'max_loss_pct': max_loss_pct,
        'leverage': leverage,
        'direction': direction,
        'risk_reward_ratio': (target_profit * 0.5) / stop_loss  # Target 1 vs Stop Loss
    }

def print_scalp_example():
    """Print example scalp trade for ZEREBRO"""
    
    print("🎯 VOLUME SPIKE SCALPING EXAMPLE - ZEREBRO")
    print("=" * 60)
    print("📊 Volume Spike: +2,421% (EXTREME SCALPING OPPORTUNITY)")
    print("⚡ Signal: BUY with 87% confidence")
    print("🔥 Leverage: 75x")
    print("=" * 60)
    
    # Example trade calculation
    entry_price = 0.000123  # Example ZEREBRO price
    leverage = 75
    
    trade = calculate_scalp_trade(entry_price, leverage, "BUY")
    
    print(f"\n💰 TRADE SETUP:")
    print(f"   📍 Entry Price: ${trade['entry_price']:.6f}")
    print(f"   🎯 Target 1 (1%): ${trade['target_1']:.6f}")
    print(f"   🚀 Target 2 (2%): ${trade['target_2']:.6f}")
    print(f"   🛡️ Stop Loss (1.25%): ${trade['stop_loss_price']:.6f}")
    
    print(f"\n📈 PROFIT/LOSS WITH 75x LEVERAGE:")
    print(f"   💎 Target 1 Profit: +{trade['profit_target_1_pct']:.1f}%")
    print(f"   🚀 Target 2 Profit: +{trade['profit_target_2_pct']:.1f}%")
    print(f"   📉 Max Loss: -{trade['max_loss_pct']:.1f}%")
    
    print(f"\n⚖️ RISK/REWARD ANALYSIS:")
    print(f"   🎯 Risk/Reward Ratio: 1:{trade['risk_reward_ratio']:.2f}")
    print(f"   💡 Risk 1.25% to make 1-2% (75-150% with leverage)")
    print(f"   ⚡ Hold Time: 3-9 minutes maximum")
    
    print(f"\n🎯 IMPROVED STOP LOSS BENEFITS:")
    print(f"   ✅ Better risk management (1.25% vs 1% before)")
    print(f"   ✅ Accounts for market volatility")
    print(f"   ✅ Reduces false stop-outs")
    print(f"   ✅ Still excellent risk/reward ratio")
    
    print("\n" + "=" * 60)
    print("🚀 READY TO SCALP VOLUME SPIKES!")
    print("=" * 60)

if __name__ == "__main__":
    print_scalp_example()
