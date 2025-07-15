#!/usr/bin/env python3
"""
🎯 Volume Spike Scalping Strategy
Targets 400%+ volume spikes for quick scalp trades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
from typing import Dict, List, Tuple, Optional

class VolumeScalpStrategy:
    """
    Advanced volume spike scalping strategy optimized for 400%+ volume spikes
    """
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.min_volume_spike = 400  # Minimum 400% volume spike
        self.optimal_volume_spike = 600  # Optimal 600%+ volume spike
        self.scalp_timeframe = '3m'  # Fast scalping timeframe
        self.max_hold_time = 9  # Maximum 9 minutes (3 candles)
        self.target_profit = 0.02  # 2% profit target
        self.stop_loss = 0.0125  # 1.25% stop loss
        
        # Track active scalp positions
        self.active_scalps = {}
        self.scalp_history = []
        
    def identify_volume_spikes(self, symbol: str, timeframe: str = '3m', limit: int = 20) -> Dict:
        """
        Identify volume spikes above 400% for scalping opportunities
        """
        try:
            # Get recent candlestick data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            if len(df) < 10:
                return None
                
            # Calculate volume moving average
            df['volume_ma'] = df['volume'].rolling(window=10).mean()
            
            # Calculate volume spike percentage
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume_ma'].iloc[-1]
            
            if avg_volume > 0:
                volume_spike_pct = ((current_volume - avg_volume) / avg_volume) * 100
            else:
                volume_spike_pct = 0
                
            # Calculate price momentum
            price_change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            
            # Calculate RSI for momentum confirmation
            rsi = self.calculate_rsi(df['close'], period=14)
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
            
            # Volume spike analysis
            spike_data = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'volume_spike_pct': volume_spike_pct,
                'price_change_pct': price_change,
                'current_price': df['close'].iloc[-1],
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0,
                'rsi': current_rsi,
                'is_spike': volume_spike_pct >= self.min_volume_spike
            }
            
            return spike_data
            
        except Exception as e:
            print(f"Error analyzing volume spike for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def evaluate_scalp_opportunity(self, spike_data: Dict) -> Dict:
        """
        Evaluate if a volume spike presents a good scalping opportunity
        """
        if not spike_data or not spike_data['is_spike']:
            return None
            
        score = 0
        signals = []
        
        # Volume spike strength (0-40 points)
        volume_pct = spike_data['volume_spike_pct']
        if volume_pct >= 1000:
            score += 40
            signals.append("🔥 EXTREME Volume Spike 1000%+")
        elif volume_pct >= 700:
            score += 35
            signals.append("🚀 MASSIVE Volume Spike 700%+")
        elif volume_pct >= 500:
            score += 30
            signals.append("💥 HUGE Volume Spike 500%+")
        elif volume_pct >= 400:
            score += 25
            signals.append("⚡ HIGH Volume Spike 400%+")
        
        # Price momentum (0-25 points)
        price_change = spike_data['price_change_pct']
        if abs(price_change) >= 3:
            score += 25
            signals.append(f"📈 Strong Price Movement {price_change:.1f}%")
        elif abs(price_change) >= 2:
            score += 20
            signals.append(f"📊 Good Price Movement {price_change:.1f}%")
        elif abs(price_change) >= 1:
            score += 15
            signals.append(f"📉 Moderate Price Movement {price_change:.1f}%")
        
        # RSI momentum (0-20 points)
        rsi = spike_data['rsi']
        if rsi > 70 and price_change > 0:
            score += 15
            signals.append("🟢 RSI Overbought + Upward")
        elif rsi < 30 and price_change < 0:
            score += 15
            signals.append("🔴 RSI Oversold + Downward")
        elif 45 <= rsi <= 55:
            score += 20
            signals.append("⚖️ RSI Neutral (Best Entry)")
        
        # Volume ratio bonus (0-15 points)
        volume_ratio = spike_data['volume_ratio']
        if volume_ratio >= 10:
            score += 15
            signals.append("💎 Volume 10x Average")
        elif volume_ratio >= 5:
            score += 10
            signals.append("🔥 Volume 5x Average")
        elif volume_ratio >= 3:
            score += 5
            signals.append("⚡ Volume 3x Average")
        
        # Determine trade direction
        if price_change > 0 and rsi < 80:
            direction = "BUY"
            entry_reason = "Volume spike with upward momentum"
        elif price_change < 0 and rsi > 20:
            direction = "SELL"
            entry_reason = "Volume spike with downward momentum"
        else:
            direction = "NEUTRAL"
            entry_reason = "Volume spike but unclear direction"
        
        # Calculate confidence
        confidence = min(score, 100)
        
        return {
            'symbol': spike_data['symbol'],
            'direction': direction,
            'score': score,
            'confidence': confidence,
            'entry_price': spike_data['current_price'],
            'volume_spike_pct': volume_pct,
            'price_change_pct': price_change,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'signals': signals,
            'entry_reason': entry_reason,
            'timestamp': spike_data['timestamp'],
            'is_scalp_ready': score >= 60 and direction != "NEUTRAL"
        }
    
    def calculate_scalp_targets(self, entry_price: float, direction: str, leverage: float = 1.0) -> Dict:
        """
        Calculate scalp profit targets and stop loss levels
        """
        if direction == "BUY":
            # For long positions
            target_1 = entry_price * (1 + self.target_profit * 0.5)  # 1% target
            target_2 = entry_price * (1 + self.target_profit)        # 2% target
            stop_loss = entry_price * (1 - self.stop_loss)           # 1.25% stop loss
        else:
            # For short positions
            target_1 = entry_price * (1 - self.target_profit * 0.5)  # 1% target
            target_2 = entry_price * (1 - self.target_profit)        # 2% target
            stop_loss = entry_price * (1 + self.stop_loss)           # 1.25% stop loss
        
        # Calculate potential profits with leverage
        profit_target_1 = self.target_profit * 0.5 * leverage * 100  # Percentage profit
        profit_target_2 = self.target_profit * leverage * 100        # Percentage profit
        max_loss = self.stop_loss * leverage * 100                   # 1.25% * leverage percentage loss
        
        return {
            'entry_price': entry_price,
            'target_1': target_1,
            'target_2': target_2,
            'stop_loss': stop_loss,
            'profit_target_1_pct': profit_target_1,
            'profit_target_2_pct': profit_target_2,
            'max_loss_pct': max_loss,
            'leverage': leverage,
            'direction': direction
        }
    
    def scan_for_scalping_opportunities(self, trading_pairs: List[str]) -> List[Dict]:
        """
        Scan all trading pairs for volume spike scalping opportunities
        """
        opportunities = []
        
        for symbol in trading_pairs:
            try:
                # Analyze volume spike
                spike_data = self.identify_volume_spikes(symbol)
                if not spike_data:
                    continue
                
                # Evaluate scalping opportunity
                scalp_opportunity = self.evaluate_scalp_opportunity(spike_data)
                if not scalp_opportunity:
                    continue
                
                # Only include high-confidence scalping opportunities
                if scalp_opportunity['is_scalp_ready']:
                    opportunities.append(scalp_opportunity)
                    
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
    
    def format_scalp_signal(self, opportunity: Dict, targets: Dict) -> str:
        """
        Format scalping signal for display
        """
        signal = f"""
🎯 **SCALP SIGNAL** - {opportunity['symbol']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 **Volume Spike:** {opportunity['volume_spike_pct']:.0f}% | **Direction:** {opportunity['direction']}
📊 **Entry:** ${targets['entry_price']:.6f} | **Score:** {opportunity['score']}/100 | **Confidence:** {opportunity['confidence']}%

🎯 **SCALP TARGETS:**
   💎 Target 1: ${targets['target_1']:.6f} ({targets['profit_target_1_pct']:.1f}% profit)
   🚀 Target 2: ${targets['target_2']:.6f} ({targets['profit_target_2_pct']:.1f}% profit)
   🛡️ Stop Loss: ${targets['stop_loss']:.6f} ({targets['max_loss_pct']:.1f}% loss - 1.25% SL)

📈 **Technical Analysis:**
   RSI: {opportunity['rsi']:.1f} | Price Change: {opportunity['price_change_pct']:.2f}%
   Volume Ratio: {opportunity['volume_ratio']:.1f}x average

💡 **Signals:**
{chr(10).join(f"   {signal}" for signal in opportunity['signals'])}

⚡ **Strategy:** Quick scalp on 3m timeframe, exit within 9 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return signal.strip()

# Example usage
if __name__ == "__main__":
    # This would be integrated into the main Alpine bot
    print("🎯 Volume Spike Scalping Strategy - Ready for 400%+ volume spikes!")
    print("📊 Optimized for quick 2-5% profits on 3m timeframe")
    print("⚡ Perfect for high-leverage scalping opportunities")
