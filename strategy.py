#!/usr/bin/env python3
"""
🏔️ Alpine Trading Strategy - Volume Anomaly Detection
"""

import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class VolumeAnomalyStrategy:
    """Volume Anomaly Strategy with confluence signals"""
    
    def __init__(self, config=None):
        self.name = "Volume Anomaly Strategy"
        self.version = "2.0"
        self.config = config
        
        # Strategy parameters
        self.volume_lookback = 20
        self.volume_std_multiplier = 0.8  # Reduced from 1.2 to allow more signals
        self.min_volume_ratio = 1.5  # Reduced from 2.75 to allow more signals
        self.supertrend_atr_period = 6
        self.supertrend_multiplier = 2.0
        
        # Fibonacci parameters
        self.fib_pivot_length = 20
        self.fib_golden_zone_low = 0.7
        self.fib_golden_zone_high = 0.885
        
        # Confidence thresholds
        self.min_signal_confidence = 40.0  # Reduced from 50.0
        self.min_trade_confidence = 45.0   # Reduced from 55.0
        self.confluence_min_confidence = 50.0  # Reduced from 60.0
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=self.volume_lookback).mean()
            df['volume_std'] = df['volume'].rolling(window=self.volume_lookback).std()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['volume_anomaly'] = df['volume'] > (df['volume_sma'] + self.volume_std_multiplier * df['volume_std'])
            
            # Price indicators
            df['hl2'] = (df['high'] + df['low']) / 2
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=self.supertrend_atr_period)
            
            # Enhanced SuperTrend Calculation (REPLACES RSI)
            df = self.calculate_supertrend(df)
            
            # MACD (Keep for confluence)
            macd_line, macd_signal, macd_histogram = ta.trend.MACD(df['close']).macd(), ta.trend.MACD(df['close']).macd_signal(), ta.trend.MACD(df['close']).macd_diff()
            df['macd'] = macd_line
            df['macd_signal'] = macd_signal
            df['macd_histogram'] = macd_histogram
            
            # Moving averages
            df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
            df['ema_50'] = ta.trend.ema_indicator(df['close'], window=50)
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return df
    
    def calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SuperTrend indicator - REPLACES RSI as primary trend indicator
        
        SuperTrend is more responsive to price changes and provides clearer trend signals
        than RSI, making it ideal for volume anomaly trading.
        """
        try:
            if len(df) < self.supertrend_atr_period:
                # Initialize with basic values if insufficient data
                df['supertrend'] = df['close']
                df['supertrend_direction'] = 1
                df['supertrend_upper'] = df['close'] * 1.02
                df['supertrend_lower'] = df['close'] * 0.98
                return df
            
            # Calculate basic SuperTrend bands
            df['supertrend_upper'] = df['hl2'] + (self.supertrend_multiplier * df['atr'])
            df['supertrend_lower'] = df['hl2'] - (self.supertrend_multiplier * df['atr'])
            
            # Initialize SuperTrend and direction arrays
            supertrend = np.zeros(len(df))
            direction = np.ones(len(df))
            
            # Calculate SuperTrend values
            for i in range(len(df)):
                if i == 0:
                    supertrend[i] = df['supertrend_upper'].iloc[i]
                    direction[i] = -1
                    continue
                
                # Get current values
                close = df['close'].iloc[i]
                prev_close = df['close'].iloc[i-1]
                upper = df['supertrend_upper'].iloc[i]
                lower = df['supertrend_lower'].iloc[i]
                prev_upper = df['supertrend_upper'].iloc[i-1]
                prev_lower = df['supertrend_lower'].iloc[i-1]
                
                # Calculate final upper and lower bands
                final_upper = upper if (upper < prev_upper or prev_close > prev_upper) else prev_upper
                final_lower = lower if (lower > prev_lower or prev_close < prev_lower) else prev_lower
                
                # Determine SuperTrend direction and value
                if close <= final_lower:
                    supertrend[i] = final_lower
                    direction[i] = 1  # Bullish
                elif close >= final_upper:
                    supertrend[i] = final_upper
                    direction[i] = -1  # Bearish
                else:
                    supertrend[i] = supertrend[i-1]
                    direction[i] = direction[i-1]
                
                # Override based on trend continuation
                if direction[i] == 1 and direction[i-1] == -1:
                    supertrend[i] = final_lower
                elif direction[i] == -1 and direction[i-1] == 1:
                    supertrend[i] = final_upper
                elif direction[i] == direction[i-1]:
                    if direction[i] == 1:
                        supertrend[i] = final_lower
                    else:
                        supertrend[i] = final_upper
            
            # Add to DataFrame
            df['supertrend'] = supertrend
            df['supertrend_direction'] = direction
            
            # Calculate SuperTrend signal strength (replaces RSI overbought/oversold)
            df['supertrend_strength'] = np.where(
                direction == 1,
                ((df['close'] - supertrend) / supertrend * 100),  # Bullish strength
                ((supertrend - df['close']) / supertrend * 100)   # Bearish strength
            )
            
            # SuperTrend trend quality (replaces RSI momentum)
            df['supertrend_quality'] = np.where(
                df['supertrend_strength'] > 2.0, 'STRONG',
                np.where(df['supertrend_strength'] > 1.0, 'MODERATE', 'WEAK')
            )
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating SuperTrend: {e}")
            # Fallback to basic calculation
            df['supertrend_upper'] = df['hl2'] + (self.supertrend_multiplier * df['atr'])
            df['supertrend_lower'] = df['hl2'] - (self.supertrend_multiplier * df['atr'])
            df['supertrend'] = df['close']
            df['supertrend_direction'] = 1
            df['supertrend_strength'] = 1.0
            df['supertrend_quality'] = 'WEAK'
            return df

    def detect_volume_anomaly(self, df: pd.DataFrame, max_leverage: float = 1.0) -> Dict:
        """Detect volume anomaly signals using SuperTrend (REPLACES RSI)"""
        try:
            if len(df) < self.volume_lookback:
                return {'signal': None, 'confidence': 0}

            latest = df.iloc[-1]
            
            # Check if we have valid data
            if pd.isna(latest['volume_ratio']) or pd.isna(latest['close']):
                return {'signal': None, 'confidence': 0}
            
            # Check minimum volume ratio (more lenient)
            if latest['volume_ratio'] < 1.2:  # Reduced from 1.5
                return {'signal': None, 'confidence': 0}
            
            # Get SuperTrend signals (REPLACES RSI LOGIC)
            supertrend_direction = latest.get('supertrend_direction', 0)
            supertrend_strength = latest.get('supertrend_strength', 0)
            supertrend_quality = latest.get('supertrend_quality', 'WEAK')
            current_price = latest['close']
            supertrend_value = latest.get('supertrend', current_price)
            
            # Determine signal direction using SuperTrend
            signal_type = None
            confidence = 0
            
            # BULLISH SIGNAL - SuperTrend based (REPLACES RSI oversold)
            if (supertrend_direction == 1 and  # SuperTrend bullish
                current_price > latest.get('ema_20', current_price) and
                current_price > supertrend_value):
                signal_type = 'BUY'
                confidence = 65  # Base confidence
                
                # SuperTrend strength bonus (REPLACES RSI momentum)
                if supertrend_quality == 'STRONG':
                    confidence += 15
                elif supertrend_quality == 'MODERATE':
                    confidence += 10
                else:
                    confidence += 5
                
                # SuperTrend strength percentage bonus
                confidence += min(supertrend_strength * 2, 15)
            
            # BEARISH SIGNAL - SuperTrend based (REPLACES RSI overbought)
            elif (supertrend_direction == -1 and  # SuperTrend bearish
                  current_price < latest.get('ema_20', current_price) and
                  current_price < supertrend_value):
                signal_type = 'SELL'
                confidence = 65  # Base confidence
                
                # SuperTrend strength bonus (REPLACES RSI momentum)
                if supertrend_quality == 'STRONG':
                    confidence += 15
                elif supertrend_quality == 'MODERATE':
                    confidence += 10
                else:
                    confidence += 5
                
                # SuperTrend strength percentage bonus
                confidence += min(supertrend_strength * 2, 15)
            
            # If we have a signal, boost confidence based on volume strength
            if signal_type:
                volume_strength = min(latest['volume_ratio'] / 1.2, 3.0)
                confidence += volume_strength * 20  # Volume boost
                
                # Additional confidence boosts for volume spikes
                if latest['volume_ratio'] > 1.5:
                    confidence += 8
                if latest['volume_ratio'] > 2.0:
                    confidence += 12
                if latest['volume_ratio'] > 3.0:
                    confidence += 8
                
                # MACD confluence (keep for additional confirmation)
                macd_bullish = latest.get('macd', 0) > latest.get('macd_signal', 0)
                macd_bearish = latest.get('macd', 0) < latest.get('macd_signal', 0)
                
                if signal_type == 'BUY' and macd_bullish:
                    confidence += 5
                elif signal_type == 'SELL' and macd_bearish:
                    confidence += 5
                
                # LEVERAGE BOOST - Higher leverage = higher confidence
                if max_leverage >= 100:
                    confidence += 5  # 100x+ leverage boost
                elif max_leverage >= 75:
                    confidence += 3  # 75x+ leverage boost
                elif max_leverage >= 50:
                    confidence += 2  # 50x+ leverage boost
                
                # Cap confidence at 95
                confidence = min(confidence, 95)
            
            return {
                'signal': signal_type,
                'confidence': confidence,
                'volume_ratio': latest['volume_ratio'],
                'price': latest['close'],
                'supertrend_direction': supertrend_direction,
                'supertrend_strength': supertrend_strength,
                'supertrend_quality': supertrend_quality,
                'max_leverage': max_leverage,
                'notional_multiplier': max_leverage,  # For position sizing
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Error detecting volume anomaly: {e}")
            return {'signal': None, 'confidence': 0}
    
    def scan_for_signals(self, market_data: Dict) -> List[Dict]:
        """Scan multiple pairs for signals"""
        signals = []
        
        for symbol, data in market_data.items():
            try:
                if len(data) < 50:  # Need enough data
                    continue
                
                # Calculate indicators
                df = self.calculate_indicators(data.copy())
                
                # Detect signal
                signal = self.detect_volume_anomaly(df)
                
                if signal['signal'] and signal['confidence'] >= self.min_signal_confidence:
                    signal['symbol'] = symbol
                    signals.append(signal)
                    
            except Exception as e:
                print(f"❌ Error scanning {symbol}: {e}")
                continue
        
        # Sort by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        return signals[:5]  # Return top 5 signals

def main():
    """Test the strategy"""
    strategy = VolumeAnomalyStrategy()
    print(f"✅ {strategy.name} v{strategy.version} initialized")

if __name__ == "__main__":
    main()
