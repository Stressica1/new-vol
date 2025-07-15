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
            
            # VHMA - Volume Weighted Hull Moving Average (REPLACES MACD)
            df = self.calculate_vhma(df)
            
            # MFI - Money Flow Index (REPLACES MACD Signal)
            df = self.calculate_mfi(df)
            
            # Bollinger Bands (REPLACES MACD Histogram)
            df = self.calculate_bollinger_bands(df)
            
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

    def calculate_vhma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volume Weighted Hull Moving Average (VHMA) - REPLACES MACD
        
        VHMA combines Hull Moving Average with volume weighting for more accurate
        trend detection with volume consideration.
        """
        try:
            if len(df) < 20:
                df['vhma'] = df['close']
                df['vhma_signal'] = 0
                return df
            
            # Calculate Hull Moving Average components
            period = 14
            half_period = period // 2
            sqrt_period = int(np.sqrt(period))
            
            # Volume weighted prices
            df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
            
            # Hull MA calculation with volume weighting
            wma_half = df['vwap'].rolling(window=half_period).mean()
            wma_full = df['vwap'].rolling(window=period).mean()
            
            # Hull calculation
            hull_raw = 2 * wma_half - wma_full
            df['vhma'] = hull_raw.rolling(window=sqrt_period).mean()
            
            # VHMA signal (momentum)
            df['vhma_signal'] = df['vhma'].diff()
            df['vhma_momentum'] = df['vhma_signal'].rolling(window=3).mean()
            
            # VHMA trend strength
            df['vhma_strength'] = np.where(
                df['vhma_signal'] > 0, 
                abs(df['vhma_signal']), 
                -abs(df['vhma_signal'])
            )
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating VHMA: {e}")
            df['vhma'] = df['close']
            df['vhma_signal'] = 0
            df['vhma_momentum'] = 0
            df['vhma_strength'] = 0
            return df
    
    def calculate_mfi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Money Flow Index (MFI) - REPLACES MACD Signal
        
        MFI is a momentum oscillator that uses price and volume to identify
        overbought/oversold conditions and money flow direction.
        """
        try:
            if len(df) < 15:
                df['mfi'] = 50
                df['mfi_signal'] = 0
                return df
            
            # Calculate typical price
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            
            # Calculate raw money flow
            df['raw_money_flow'] = df['typical_price'] * df['volume']
            
            # Calculate positive and negative money flow
            df['price_change'] = df['typical_price'].diff()
            
            positive_flow = np.where(df['price_change'] > 0, df['raw_money_flow'], 0)
            negative_flow = np.where(df['price_change'] < 0, df['raw_money_flow'], 0)
            
            # 14-period money flow
            period = 14
            positive_mf = pd.Series(positive_flow).rolling(window=period).sum()
            negative_mf = pd.Series(negative_flow).rolling(window=period).sum()
            
            # Calculate MFI
            money_flow_ratio = positive_mf / (negative_mf + 1e-10)  # Avoid division by zero
            df['mfi'] = 100 - (100 / (1 + money_flow_ratio))
            
            # MFI signal (momentum and divergence)
            df['mfi_signal'] = df['mfi'].diff()
            df['mfi_momentum'] = df['mfi_signal'].rolling(window=3).mean()
            
            # MFI conditions
            df['mfi_overbought'] = df['mfi'] > 80
            df['mfi_oversold'] = df['mfi'] < 20
            df['mfi_bullish'] = (df['mfi'] > 50) & (df['mfi_signal'] > 0)
            df['mfi_bearish'] = (df['mfi'] < 50) & (df['mfi_signal'] < 0)
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating MFI: {e}")
            df['mfi'] = 50
            df['mfi_signal'] = 0
            df['mfi_momentum'] = 0
            df['mfi_overbought'] = False
            df['mfi_oversold'] = False
            df['mfi_bullish'] = False
            df['mfi_bearish'] = False
            return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands (BB) - REPLACES MACD Histogram
        
        Bollinger Bands provide dynamic support and resistance levels
        and help identify volatility and potential reversal points.
        """
        try:
            if len(df) < 20:
                df['bb_upper'] = df['close'] * 1.02
                df['bb_middle'] = df['close']
                df['bb_lower'] = df['close'] * 0.98
                df['bb_width'] = 0.04
                df['bb_position'] = 0.5
                return df
            
            # Standard Bollinger Bands
            period = 20
            std_dev = 2.0
            
            # Calculate middle band (SMA)
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            
            # Calculate standard deviation
            rolling_std = df['close'].rolling(window=period).std()
            
            # Calculate upper and lower bands
            df['bb_upper'] = df['bb_middle'] + (rolling_std * std_dev)
            df['bb_lower'] = df['bb_middle'] - (rolling_std * std_dev)
            
            # Calculate band width (volatility measure)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Calculate position within bands (0 = lower band, 1 = upper band)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Bollinger Band signals
            df['bb_squeeze'] = df['bb_width'] < df['bb_width'].rolling(window=20).mean() * 0.8
            df['bb_expansion'] = df['bb_width'] > df['bb_width'].rolling(window=20).mean() * 1.2
            df['bb_breakout_upper'] = df['close'] > df['bb_upper']
            df['bb_breakout_lower'] = df['close'] < df['bb_lower']
            
            # BB momentum
            df['bb_momentum'] = df['bb_position'].diff()
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating Bollinger Bands: {e}")
            df['bb_upper'] = df['close'] * 1.02
            df['bb_middle'] = df['close']
            df['bb_lower'] = df['close'] * 0.98
            df['bb_width'] = 0.04
            df['bb_position'] = 0.5
            df['bb_squeeze'] = False
            df['bb_expansion'] = False
            df['bb_breakout_upper'] = False
            df['bb_breakout_lower'] = False
            df['bb_momentum'] = 0
            return df

    def detect_volume_anomaly(self, market_data: Dict, symbol: str, max_leverage: float = 1.0) -> Dict:
        """Detect volume anomaly signals using SuperTrend with MTF analysis"""
        try:
            # Get primary timeframe data (5M default)
            primary_data = market_data.get(symbol, [])
            if not primary_data or len(primary_data) < self.volume_lookback:
                return {'signal': None, 'confidence': 0}
            
            # Calculate MTF signals for enhanced confidence
            mtf_analysis = self.calculate_mtf_signals(symbol, market_data)
            
            # Convert to DataFrame and calculate indicators
            df = pd.DataFrame(primary_data)
            df = self.calculate_indicators(df)
            
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
                
                # New indicator confluence (replaces MACD)
                vhma_bullish = latest.get('vhma_signal', 0) > 0
                vhma_bearish = latest.get('vhma_signal', 0) < 0
                
                mfi_bullish = latest.get('mfi_bullish', False)
                mfi_bearish = latest.get('mfi_bearish', False)
                mfi_oversold = latest.get('mfi_oversold', False)
                mfi_overbought = latest.get('mfi_overbought', False)
                
                bb_bullish = latest.get('bb_position', 0.5) < 0.2 and latest.get('bb_momentum', 0) > 0
                bb_bearish = latest.get('bb_position', 0.5) > 0.8 and latest.get('bb_momentum', 0) < 0
                
                # VHMA confluence
                if signal_type == 'BUY' and vhma_bullish:
                    confidence += 6
                elif signal_type == 'SELL' and vhma_bearish:
                    confidence += 6
                
                # MFI confluence
                if signal_type == 'BUY' and (mfi_bullish or mfi_oversold):
                    confidence += 7
                elif signal_type == 'SELL' and (mfi_bearish or mfi_overbought):
                    confidence += 7
                
                # Bollinger Bands confluence
                if signal_type == 'BUY' and bb_bullish:
                    confidence += 5
                elif signal_type == 'SELL' and bb_bearish:
                    confidence += 5
                
                # MTF Analysis Bonus
                mtf_bonus = mtf_analysis.get('mtf_bonus', 0)
                if mtf_bonus > 0:
                    confidence += min(mtf_bonus, 25)  # Cap MTF bonus at 25 points
                    print(f"🎯 MTF Bonus: +{min(mtf_bonus, 25):.1f} ({mtf_analysis.get('total_aligned', 0)} aligned timeframes)")
                
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
                'vhma_signal': latest.get('vhma_signal', 0),
                'vhma_momentum': latest.get('vhma_momentum', 0),
                'mfi': latest.get('mfi', 50),
                'mfi_bullish': latest.get('mfi_bullish', False),
                'mfi_bearish': latest.get('mfi_bearish', False),
                'bb_position': latest.get('bb_position', 0.5),
                'bb_width': latest.get('bb_width', 0.04),
                'bb_squeeze': latest.get('bb_squeeze', False),
                'bb_expansion': latest.get('bb_expansion', False),
                'mtf_bonus': mtf_analysis.get('mtf_bonus', 0),
                'mtf_aligned': mtf_analysis.get('total_aligned', 0),
                'mtf_signals': mtf_analysis.get('mtf_signals', {}),
                'alignment_bonus': mtf_analysis.get('alignment_bonus', 0),
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

    def calculate_mtf_signals(self, symbol: str, market_data: Dict) -> Dict:
        """
        Calculate Multi-Timeframe (MTF) signals for 1M, 3M, 5M, 10M, 15M
        Each aligned timeframe provides a score bonus for signal confidence
        """
        try:
            mtf_timeframes = ['1m', '3m', '5m', '10m', '15m']
            mtf_scores = {
                '1m': 3,   # Immediate trend
                '3m': 5,   # Short-term momentum
                '5m': 8,   # Primary scalping timeframe
                '10m': 6,  # Medium-term confirmation
                '15m': 4   # Longer-term context
            }
            
            mtf_signals = {}
            total_mtf_bonus = 0
            aligned_timeframes = []
            
            print(f"🔍 Analyzing MTF signals for {symbol}")
            
            for timeframe in mtf_timeframes:
                try:
                    # Get timeframe data
                    tf_data = market_data.get(f"{symbol}_{timeframe}", market_data.get(symbol, []))
                    
                    if not tf_data or len(tf_data) < 20:
                        print(f"⚠️ Insufficient data for {timeframe}")
                        continue
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(tf_data)
                    
                    # Calculate indicators for this timeframe
                    df = self.calculate_indicators(df)
                    
                    if len(df) == 0:
                        continue
                    
                    latest = df.iloc[-1]
                    
                    # MTF Signal Analysis
                    mtf_signal = self.analyze_mtf_signal(latest, timeframe)
                    mtf_signals[timeframe] = mtf_signal
                    
                    # Calculate MTF score bonus
                    if mtf_signal['signal'] in ['BUY', 'SELL']:
                        signal_strength = mtf_signal['strength']
                        base_score = mtf_scores[timeframe]
                        
                        # Adjust score based on signal strength
                        if signal_strength >= 0.8:
                            bonus = base_score * 1.2  # Strong signal bonus
                        elif signal_strength >= 0.6:
                            bonus = base_score * 1.0  # Normal signal
                        else:
                            bonus = base_score * 0.7  # Weak signal penalty
                        
                        total_mtf_bonus += bonus
                        aligned_timeframes.append(timeframe)
                        
                        print(f"✅ {timeframe}: {mtf_signal['signal']} (strength: {signal_strength:.2f}, bonus: +{bonus:.1f})")
                    else:
                        print(f"⚪ {timeframe}: NEUTRAL")
                
                except Exception as e:
                    print(f"❌ Error analyzing {timeframe}: {e}")
                    continue
            
            # Calculate alignment bonus
            alignment_bonus = 0
            if len(aligned_timeframes) >= 3:
                # Check if signals are mostly aligned
                buy_signals = sum(1 for tf in aligned_timeframes if mtf_signals[tf]['signal'] == 'BUY')
                sell_signals = sum(1 for tf in aligned_timeframes if mtf_signals[tf]['signal'] == 'SELL')
                
                if buy_signals >= len(aligned_timeframes) * 0.7:
                    alignment_bonus = 10 + (buy_signals - 3) * 3  # Extra bonus for more aligned TFs
                elif sell_signals >= len(aligned_timeframes) * 0.7:
                    alignment_bonus = 10 + (sell_signals - 3) * 3
                
                if alignment_bonus > 0:
                    print(f"🎯 MTF Alignment Bonus: +{alignment_bonus:.1f} ({len(aligned_timeframes)} aligned timeframes)")
            
            # Total MTF bonus
            total_mtf_bonus += alignment_bonus
            
            return {
                'mtf_signals': mtf_signals,
                'mtf_bonus': total_mtf_bonus,
                'aligned_timeframes': aligned_timeframes,
                'alignment_bonus': alignment_bonus,
                'total_aligned': len(aligned_timeframes)
            }
            
        except Exception as e:
            print(f"❌ Error calculating MTF signals: {e}")
            return {
                'mtf_signals': {},
                'mtf_bonus': 0,
                'aligned_timeframes': [],
                'alignment_bonus': 0,
                'total_aligned': 0
            }
    
    def analyze_mtf_signal(self, latest: pd.Series, timeframe: str) -> Dict:
        """
        Analyze individual timeframe signal
        Returns signal type and strength for MTF analysis
        """
        try:
            # SuperTrend analysis
            supertrend_direction = latest.get('supertrend_direction', 0)
            supertrend_strength = latest.get('supertrend_strength', 0)
            
            # Volume analysis
            volume_ratio = latest.get('volume_ratio', 1.0)
            volume_anomaly = latest.get('volume_anomaly', False)
            
            # New indicator analysis
            vhma_signal = latest.get('vhma_signal', 0)
            mfi = latest.get('mfi', 50)
            bb_position = latest.get('bb_position', 0.5)
            
            # Determine signal
            signal = 'NEUTRAL'
            strength = 0.0
            
            # Primary signal from SuperTrend
            if supertrend_direction == 1:
                signal = 'BUY'
                strength = min(supertrend_strength / 3.0, 1.0)  # Normalize to 0-1
            elif supertrend_direction == -1:
                signal = 'SELL'
                strength = min(supertrend_strength / 3.0, 1.0)
            
            # Enhance strength with other indicators
            if signal == 'BUY':
                if vhma_signal > 0:
                    strength += 0.1
                if mfi > 50:
                    strength += 0.1
                if bb_position < 0.3:  # Near lower band
                    strength += 0.1
            elif signal == 'SELL':
                if vhma_signal < 0:
                    strength += 0.1
                if mfi < 50:
                    strength += 0.1
                if bb_position > 0.7:  # Near upper band
                    strength += 0.1
            
            # Volume boost
            if volume_anomaly:
                strength += 0.15
            elif volume_ratio > 1.5:
                strength += 0.1
            
            # Timeframe-specific adjustments
            if timeframe == '1m':
                strength *= 0.9  # Slightly reduce for noise
            elif timeframe == '5m':
                strength *= 1.1  # Boost primary timeframe
            elif timeframe == '15m':
                strength *= 1.05  # Boost for trend confirmation
            
            # Cap strength at 1.0
            strength = min(strength, 1.0)
            
            return {
                'signal': signal,
                'strength': strength,
                'supertrend_direction': supertrend_direction,
                'volume_ratio': volume_ratio,
                'volume_anomaly': volume_anomaly,
                'timeframe': timeframe
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {timeframe} signal: {e}")
            return {
                'signal': 'NEUTRAL',
                'strength': 0.0,
                'timeframe': timeframe
            }

def main():
    """Test the strategy"""
    strategy = VolumeAnomalyStrategy()
    print(f"✅ {strategy.name} v{strategy.version} initialized")

if __name__ == "__main__":
    main()
