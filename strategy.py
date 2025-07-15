"""
🏔️ Alpine Trading Bot - Enhanced Volume Anomaly Strategy
Optimized for 1m/3m confluence signals with dynamic position sizing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import ta
from config import TradingConfig

def safe_log(level: str, message: str):
    """Safe logging that works during hot-reload"""
    try:
        from loguru import logger
        if level == 'debug':
            logger.debug(message)
        elif level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'success':
            logger.success(message)
        else:
            logger.info(message)
    except (ImportError, NameError):
        # Fallback to print during hot-reload
        print(f"[{level.upper()}] {message}")

class VolumeAnomalyStrategy:
    """🎯 Enhanced Volume Anomaly Strategy - Optimized for 3m Timeframe"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # Strategy parameters (optimized for 3m scalping)
        self.volume_lookback = self.config.volume_lookback
        self.volume_std_multiplier = self.config.volume_std_multiplier
        self.atr_period = self.config.supertrend_atr_period
        self.atr_multiplier = self.config.supertrend_multiplier
        
        # Confluence configuration
        self.timeframes = self.config.timeframes  # ['3m']
        self.primary_timeframe = self.config.primary_timeframe
        self.confluence_required = self.config.signal_confluence_required
        self.confluence_boost = self.config.confluence_confidence_boost
        
        # Enhanced volume analysis
        self.vol_burst_factor = 1.5
        self.vol_explode_factor = 2.0
        
        # Signal tracking
        self.signals_history = []
        self.confluence_signals_count = 0
        self.total_signals_count = 0
        
        safe_log('success', f"🎯 Enhanced Strategy initialized for {self.timeframes} timeframe trading")

    def calculate_supertrend(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """📈 Enhanced SuperTrend calculation for faster signals"""
        try:
            if len(df) < self.atr_period:
                safe_log('warning', f"⚠️ Insufficient data for SuperTrend: {len(df)} < {self.atr_period}")
                return pd.Series([np.nan] * len(df)), pd.Series([0] * len(df))
            
            # Calculate ATR manually for compatibility
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=self.atr_period).mean()
            
            # Calculate SuperTrend bands
            hl2 = (df['high'] + df['low']) / 2
            upper_band = hl2 + (self.atr_multiplier * atr)
            lower_band = hl2 - (self.atr_multiplier * atr)
            
            # Initialize arrays
            supertrend = pd.Series(index=df.index, dtype=float)
            trend = pd.Series(index=df.index, dtype=int)
            
            for i in range(len(df)):
                if i == 0:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    trend.iloc[i] = 1
                    continue
                
                # SuperTrend calculation logic
                if df['close'].iloc[i] <= supertrend.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    trend.iloc[i] = -1
                else:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    trend.iloc[i] = 1
                    
                # Adjust for trend continuity
                if trend.iloc[i] == 1 and trend.iloc[i-1] == 1:
                    if lower_band.iloc[i] > supertrend.iloc[i-1]:
                        supertrend.iloc[i] = lower_band.iloc[i]
                    else:
                        supertrend.iloc[i] = supertrend.iloc[i-1]
                        
                elif trend.iloc[i] == -1 and trend.iloc[i-1] == -1:
                    if upper_band.iloc[i] < supertrend.iloc[i-1]:
                        supertrend.iloc[i] = upper_band.iloc[i]
                    else:
                        supertrend.iloc[i] = supertrend.iloc[i-1]
            
            return supertrend, trend
            
        except Exception as e:
            safe_log('warning', f"⚠️ SuperTrend calculation error: {e}")
            return pd.Series([np.nan] * len(df)), pd.Series([0] * len(df))

    def calculate_volume_analysis(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """📊 ORIGINAL Volume Anomaly Analysis - Pure Statistical Detection"""
        try:
            if len(df) < self.volume_lookback:
                safe_log('warning', f"⚠️ Insufficient data for volume analysis: {len(df)} < {self.volume_lookback}")
                return {
                    'volume_ratio': pd.Series([1.0] * len(df)),
                    'high_volume_anomaly': pd.Series([False] * len(df)),
                    'extreme_volume_anomaly': pd.Series([False] * len(df)),
                    'volume_zscore': pd.Series([0.0] * len(df)),
                    'volume_percentile': pd.Series([0.5] * len(df))
                }
            
            # ORIGINAL VOLUME ANOMALY CALCULATION
            # Calculate volume moving average and standard deviation
            volume_ma = df['volume'].rolling(window=self.volume_lookback).mean()
            volume_std = df['volume'].rolling(window=self.volume_lookback).std()
            
            # Calculate volume anomaly score (z-score) - ORIGINAL METHOD
            volume_zscore = (df['volume'] - volume_ma) / volume_std
            
            # Calculate volume percentile - ORIGINAL METHOD
            volume_percentile = df['volume'].rolling(window=self.volume_lookback).rank(pct=True)
            
            # Volume ratio for display
            volume_ratio = df['volume'] / volume_ma
            
            # ORIGINAL VOLUME ANOMALY CONDITIONS
            high_volume_anomaly = (volume_percentile > 0.95) & (volume_zscore > 2)
            extreme_volume_anomaly = (volume_percentile > 0.99) & (volume_zscore > 3)
            
            return {
                'volume_ratio': volume_ratio,
                'high_volume_anomaly': high_volume_anomaly,
                'extreme_volume_anomaly': extreme_volume_anomaly,
                'volume_zscore': volume_zscore,
                'volume_percentile': volume_percentile
            }
            
        except Exception as e:
            safe_log('warning', f"⚠️ Volume analysis error: {e}")
            return {
                'volume_ratio': pd.Series([1.0] * len(df)),
                'high_volume_anomaly': pd.Series([False] * len(df)),
                'extreme_volume_anomaly': pd.Series([False] * len(df)),
                'volume_zscore': pd.Series([0.0] * len(df)),
                'volume_percentile': pd.Series([0.5] * len(df))
            }

    def calculate_ema_pullback(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """📈 EMA pullback analysis for trend confirmation"""
        try:
            # Fast EMA for scalping (optimized periods)
            ema_fast = df['close'].ewm(span=8).mean()
            ema_slow = df['close'].ewm(span=21).mean()
            
            # Trend direction
            trend_up = ema_fast > ema_slow
            trend_down = ema_fast < ema_slow
            
            # Pullback detection (price near EMA)
            pullback_threshold = 0.002  # 0.2% for scalping
            
            pullback_long = trend_up & (df['close'] <= ema_fast * (1 + pullback_threshold))
            pullback_short = trend_down & (df['close'] >= ema_fast * (1 - pullback_threshold))
            
            return {
                'ema_fast': ema_fast,
                'ema_slow': ema_slow,
                'trend_up': trend_up,
                'trend_down': trend_down,
                'pullback_long': pullback_long,
                'pullback_short': pullback_short
            }
            
        except Exception as e:
            safe_log('warning', f"⚠️ EMA pullback error: {e}")
            return {
                'ema_fast': pd.Series([df['close'].iloc[-1]] * len(df)),
                'ema_slow': pd.Series([df['close'].iloc[-1]] * len(df)),
                'trend_up': pd.Series([True] * len(df)),
                'trend_down': pd.Series([False] * len(df)),
                'pullback_long': pd.Series([False] * len(df)),
                'pullback_short': pd.Series([False] * len(df))
            }

    def calculate_fibonacci_golden_zone(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """📐 Calculate Fibonacci Golden Zone levels"""
        try:
            pivot_length = self.config.fib_pivot_length
            golden_low = self.config.fib_golden_zone_low
            golden_high = self.config.fib_golden_zone_high
            
            # Find swing highs and lows using rolling max/min
            swing_high = df['high'].rolling(window=pivot_length*2+1, center=True).max()
            swing_low = df['low'].rolling(window=pivot_length*2+1, center=True).min()
            
            # Calculate Fibonacci levels
            fib_range = swing_high - swing_low
            fib_70 = swing_low + (fib_range * golden_low)      # 70% level
            fib_885 = swing_low + (fib_range * golden_high)    # 88.5% level
            
            # Determine if price is in golden zone
            in_golden_zone = (df['close'] >= fib_70) & (df['close'] <= fib_885)
            
            # Golden zone strength (how deep in zone)
            golden_zone_position = np.where(
                in_golden_zone,
                (df['close'] - fib_70) / (fib_885 - fib_70),
                np.nan
            )
            
            return {
                'swing_high': pd.Series(swing_high, index=df.index),
                'swing_low': pd.Series(swing_low, index=df.index),
                'fib_70': pd.Series(fib_70, index=df.index),
                'fib_885': pd.Series(fib_885, index=df.index),
                'in_golden_zone': pd.Series(in_golden_zone, index=df.index),
                'golden_zone_position': pd.Series(golden_zone_position, index=df.index)
            }
            
        except Exception as e:
            safe_log('warning', f"⚠️ Fibonacci Golden Zone calculation error: {e}")
            return {
                'swing_high': pd.Series([np.nan] * len(df)),
                'swing_low': pd.Series([np.nan] * len(df)),
                'fib_70': pd.Series([np.nan] * len(df)),
                'fib_885': pd.Series([np.nan] * len(df)),
                'in_golden_zone': pd.Series([False] * len(df)),
                'golden_zone_position': pd.Series([np.nan] * len(df))
            }

    def analyze_confluence_signals(self, timeframe_data: Dict[str, pd.DataFrame], symbol: str) -> List[Dict]:
        """🎯 Analyze signals across configured timeframes (3m)"""
        try:
            confluence_signals = []
            
            # Generate signals for each timeframe
            timeframe_signals = {}
            for timeframe, df in timeframe_data.items():
                if timeframe in self.timeframes:
                    signals = self.generate_single_timeframe_signals(df, symbol, timeframe)
                    timeframe_signals[timeframe] = signals
                    safe_log('debug', f"📊 {timeframe} generated {len(signals)} signals for {symbol}")
            
            # Find confluence signals (signals that appear in multiple timeframes)
            if len(timeframe_signals) >= self.confluence_required:
                # Get the most recent signals from each timeframe
                recent_signals = {}
                for tf, signals in timeframe_signals.items():
                    if signals:  # Only if there are signals
                        # Get most recent signal
                        recent_signals[tf] = signals[-1]
                
                # Check for confluence (same direction signals within time window)
                if len(recent_signals) >= self.confluence_required:
                    signal_types = [sig['type'] for sig in recent_signals.values()]
                    
                    # Check if signals agree on direction
                    if len(set(signal_types)) == 1:  # All signals same direction
                        # Create confluence signal
                        primary_signal = recent_signals[self.primary_timeframe]
                        
                        # Boost confidence for confluence
                        boosted_confidence = min(primary_signal['confidence'] + self.confluence_boost * 100, 100.0)
                        
                        confluence_signal = {
                            **primary_signal,
                            'is_confluence': True,
                            'confluence_timeframes': list(recent_signals.keys()),
                            'original_confidence': primary_signal['confidence'],
                            'confidence': boosted_confidence,
                            'confluence_boost': self.confluence_boost * 100
                        }
                        
                        confluence_signals.append(confluence_signal)
                        self.confluence_signals_count += 1
                        
                        safe_log('success', f"🚀 CONFLUENCE SIGNAL: {symbol} {confluence_signal['type']} across {confluence_signal['confluence_timeframes']}")
                        safe_log('success', f"   📈 Confidence boosted: {primary_signal['confidence']:.1f}% → {boosted_confidence:.1f}% (+{self.confluence_boost*100:.0f}%)")
            
            # Also include high-quality single timeframe signals
            for tf, signals in timeframe_signals.items():
                for signal in signals:
                    if signal['confidence'] >= 80.0:  # High confidence threshold
                        signal['is_confluence'] = False
                        confluence_signals.append(signal)
            
            self.total_signals_count += len(confluence_signals)
            
            return confluence_signals
            
        except Exception as e:
            safe_log('warning', f"⚠️ Confluence analysis error: {e}")
            return []

    def analyze_timeframe_signals(self, timeframe_data: Dict[str, pd.DataFrame], symbol: str) -> List[Dict]:
        """Alias for backwards-compatibility 🔄

        AlpineBot still expects a `analyze_timeframe_signals` method on the strategy
        instance.  The original method was renamed to `analyze_confluence_signals`.
        This thin wrapper simply forwards the call so that existing integrations
        continue to work without touching other modules.
        """
        # Directly reuse the more descriptive implementation
        return self.analyze_confluence_signals(timeframe_data, symbol)

    def generate_single_timeframe_signals(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[Dict]:
        """📊 ORIGINAL Volume Anomaly Signals + SuperTrend Confirmation"""
        try:
            if len(df) < 20:  # Minimum data requirement
                safe_log('warning', f"⚠️ Insufficient data for signal generation: {len(df)} < 20")
                return []
            
            signals = []
            
            # Calculate indicators
            supertrend, trend = self.calculate_supertrend(df)
            volume_analysis = self.calculate_volume_analysis(df)
            fibonacci = self.calculate_fibonacci_golden_zone(df)
            
            # Calculate price momentum (ORIGINAL METHOD)
            df['price_momentum'] = df['close'].pct_change(periods=3)
            df['price_change'] = df['close'].pct_change()
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            current_volume_ratio = volume_analysis['volume_ratio'].iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            current_trend = trend.iloc[-1]
            
            # ORIGINAL Volume Anomaly conditions
            high_volume_anomaly = volume_analysis['high_volume_anomaly'].iloc[-1]
            extreme_volume_anomaly = volume_analysis['extreme_volume_anomaly'].iloc[-1]
            volume_zscore = volume_analysis['volume_zscore'].iloc[-1]
            volume_percentile = volume_analysis['volume_percentile'].iloc[-1]
            
            # Fibonacci Golden Zone conditions
            in_golden_zone = fibonacci['in_golden_zone'].iloc[-1] if not pd.isna(fibonacci['in_golden_zone'].iloc[-1]) else False
            golden_zone_position = fibonacci['golden_zone_position'].iloc[-1] if not pd.isna(fibonacci['golden_zone_position'].iloc[-1]) else 0
            
            # Price momentum values
            price_momentum = df['price_momentum'].iloc[-1]
            price_change = df['price_change'].iloc[-1]
            
            signal_type = None
            signal_strength = 0
            signal_reasons = []
            
            # ENHANCED LONG signal conditions: Volume + momentum + trend OR Fibonacci confirmation
            volume_condition = (high_volume_anomaly or extreme_volume_anomaly or current_volume_ratio >= self.config.min_volume_ratio)
            
            long_momentum_condition = price_momentum > 0.0005 and price_change > 0  # Reduced from 0.001
            short_momentum_condition = price_momentum < -0.0005 and price_change < 0  # Reduced from 0.001
            
            # SuperTrend conditions (handle NaN values)
            if pd.isna(current_supertrend):
                # If SuperTrend is NaN, use price momentum as trend proxy
                supertrend_bullish = price_momentum > 0
                supertrend_bearish = price_momentum < 0
            else:
                supertrend_bullish = current_price > current_supertrend
                supertrend_bearish = current_price < current_supertrend
            
            # Multiple signal conditions for better signal generation
            long_condition = (
                volume_condition and long_momentum_condition and 
                (supertrend_bullish or in_golden_zone)  # SuperTrend OR Golden Zone
            )
            
            short_condition = (
                volume_condition and short_momentum_condition and 
                (supertrend_bearish or in_golden_zone)  # SuperTrend OR Golden Zone
            )
            
            if long_condition:
                signal_type = 'LONG'
                signal_reasons.append("Enhanced Volume + Momentum Analysis")
                
                # Base scoring system
                if extreme_volume_anomaly:
                    signal_strength = 85  # Extreme anomaly = 85%
                    signal_reasons.append(f"EXTREME Volume Anomaly (99th percentile, {volume_zscore:.1f}σ)")
                elif high_volume_anomaly:
                    signal_strength = 70   # High anomaly = 70%
                    signal_reasons.append(f"High Volume Anomaly (95th percentile, {volume_zscore:.1f}σ)")
                elif current_volume_ratio >= self.config.min_volume_ratio:
                    signal_strength = 60   # Base volume signal = 60%
                    signal_reasons.append(f"Volume Ratio {current_volume_ratio:.1f}x")
                
                # Trend confirmation bonuses
                if supertrend_bullish and not pd.isna(current_supertrend):
                    signal_strength += 10
                    signal_reasons.append("SuperTrend Bullish")
                elif pd.isna(current_supertrend):
                    signal_reasons.append("SuperTrend Calculation Issue (using momentum)")
                
                # Fibonacci Golden Zone bonus
                if in_golden_zone:
                    signal_strength += 15
                    signal_reasons.append(f"Fibonacci Golden Zone (position: {golden_zone_position:.2f})")
                
                # Momentum bonuses
                if price_momentum > 0.002:
                    signal_strength += 5
                    signal_reasons.append("Strong Positive Momentum")
                elif price_momentum > 0.001:
                    signal_strength += 3
                    signal_reasons.append("Good Positive Momentum")
                
                # Cap at 100%
                signal_strength = min(signal_strength, 100)
                    
            elif short_condition:
                signal_type = 'SHORT'
                signal_reasons.append("Enhanced Volume + Momentum Analysis")
                
                # Base scoring system
                if extreme_volume_anomaly:
                    signal_strength = 85  # Extreme anomaly = 85%
                    signal_reasons.append(f"EXTREME Volume Anomaly (99th percentile, {volume_zscore:.1f}σ)")
                elif high_volume_anomaly:
                    signal_strength = 70   # High anomaly = 70%
                    signal_reasons.append(f"High Volume Anomaly (95th percentile, {volume_zscore:.1f}σ)")
                elif current_volume_ratio >= self.config.min_volume_ratio:
                    signal_strength = 60   # Base volume signal = 60%
                    signal_reasons.append(f"Volume Ratio {current_volume_ratio:.1f}x")
                
                # Trend confirmation bonuses
                if supertrend_bearish and not pd.isna(current_supertrend):
                    signal_strength += 10
                    signal_reasons.append("SuperTrend Bearish")
                elif pd.isna(current_supertrend):
                    signal_reasons.append("SuperTrend Calculation Issue (using momentum)")
                
                # Fibonacci Golden Zone bonus
                if in_golden_zone:
                    signal_strength += 15
                    signal_reasons.append(f"Fibonacci Golden Zone (position: {golden_zone_position:.2f})")
                
                # Momentum bonuses
                if price_momentum < -0.002:
                    signal_strength += 5
                    signal_reasons.append("Strong Negative Momentum")
                elif price_momentum < -0.001:
                    signal_strength += 3
                    signal_reasons.append("Good Negative Momentum")
                
                # Cap at 100%
                signal_strength = min(signal_strength, 100)
            
            # Create signal if detected
            if signal_type and signal_strength >= self.config.min_signal_confidence:
                signal = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'type': signal_type,
                    'confidence': signal_strength,
                    'entry_price': current_price,
                    'volume_ratio': current_volume_ratio,
                    'volume_zscore': volume_zscore,
                    'volume_percentile': volume_percentile,
                    'price_momentum': price_momentum,
                    'supertrend': current_supertrend,
                    'trend_direction': current_trend,
                    'reasons': signal_reasons,
                    'timestamp': datetime.now(),
                    'is_confluence': False  # Will be set by confluence analysis
                }
                
                signals.append(signal)
                safe_log('info', f"📊 {timeframe} Signal: {symbol} {signal_type} (Confidence: {signal_strength}%)")
                safe_log('debug', f"   📋 Reasons: {', '.join(signal_reasons)}")
            else:
                if signal_type:
                    safe_log('debug', f"🚫 {symbol} {timeframe}: Signal below threshold ({signal_strength:.1f}% < {self.config.min_signal_confidence}%)")
            
            return signals
            
        except Exception as e:
            safe_log('warning', f"⚠️ Signal generation error for {timeframe}: {e}")
            return []

    def should_enter_trade(self, signal: Dict, account_balance: float, current_positions: List[Dict]) -> bool:
        """🎯 Enhanced trade entry logic with high conviction requirement"""
        
        symbol = signal.get('symbol', 'Unknown')
        confidence = signal.get('confidence', 0)
        volume_ratio = signal.get('volume_ratio', 0)
        is_confluence = signal.get('is_confluence', False)
        
        # Use consistent 75% threshold for all signals (high conviction only)
        min_confidence = self.config.min_trade_confidence  # 75% for all signals
        min_volume_ratio = self.config.min_volume_ratio
        
        safe_log('debug', f"🎯 Trade Entry Check for {symbol}:")
        safe_log('debug', f"  📊 Signal Type: {'CONFLUENCE' if is_confluence else 'SINGLE TF'}")
        safe_log('debug', f"  📊 Confidence: {confidence:.1f}% (need ≥{min_confidence:.1f}%)")
        safe_log('debug', f"  📊 Volume Ratio: {volume_ratio:.2f}x (need ≥{min_volume_ratio:.1f}x)")
        safe_log('debug', f"  📊 Current Positions: {len(current_positions)}/{self.config.max_positions}")
        
        # Check position limits
        if len(current_positions) >= self.config.max_positions:
            safe_log('warning', f"🚫 {symbol}: Max positions reached ({len(current_positions)}/{self.config.max_positions})")
            return False
        
        # Check if we already have a position in this symbol
        for pos in current_positions:
            if pos['symbol'] == signal['symbol']:
                safe_log('warning', f"🚫 {symbol}: Already have position in this symbol")
                return False
        
        # Check signal confidence
        if confidence < min_confidence:
            safe_log('warning', f"🚫 {symbol}: Confidence too low: {confidence:.1f}% < {min_confidence:.1f}%")
            return False
        
        # Check volume strength
        if volume_ratio < min_volume_ratio:
            safe_log('warning', f"🚫 {symbol}: Volume too low: {volume_ratio:.2f}x < {min_volume_ratio:.1f}x")
            return False
        
        if is_confluence:
            safe_log('success', f"✅ {symbol}: CONFLUENCE SIGNAL - All conditions met! 🚀")
        else:
            safe_log('success', f"✅ {symbol}: High-quality signal - All conditions met!")
        
        return True

    def calculate_position_size(self, signal: Dict, account_balance: float, current_price: float) -> Dict[str, Union[float, int, bool, str, None]]:
        """💰 Enhanced position sizing with leverage and budget constraints"""
        
        try:
            from position_sizing import create_position_sizer
            
            # Create position sizer with current account balance
            sizer = create_position_sizer(account_balance)
            
            # Get signal details
            confidence = signal.get('confidence', 0)
            is_confluence = signal.get('is_confluence', False)
            
            # Calculate stop loss price
            stop_loss_price = None
            if signal.get('type') == 'LONG':
                stop_loss_price = current_price * (1 - self.config.stop_loss_pct / 100)
            elif signal.get('type') == 'SHORT':
                stop_loss_price = current_price * (1 + self.config.stop_loss_pct / 100)
            
            # Calculate position size with all constraints
            position_details = sizer.calculate_position_size_with_constraints(
                signal_confidence=confidence,
                entry_price=current_price,
                stop_loss_price=stop_loss_price,
                is_confluence=is_confluence
            )
            
            # Validate position viability
            is_viable, reason = sizer.validate_position_viability(position_details)
            
            if not is_viable:
                safe_log('warning', f"⚠️ Position not viable: {reason}")
                # Return minimum viable position
                return {
                    'position_size_usdt': self.config.min_order_size,
                    'position_size_units': self.config.min_order_size / current_price,
                    'required_capital': self.config.min_order_size / self.config.leverage,
                    'leverage_used': self.config.leverage,
                    'risk_amount': account_balance * (self.config.risk_per_trade / 100),
                    'entry_price': current_price,
                    'stop_loss_price': stop_loss_price,
                    'is_viable': False,
                    'reason': reason
                }
            
            # Add validation info to result
            position_details['is_viable'] = True
            position_details['reason'] = "Position is viable"
            
            safe_log('info', f"💰 Position sizing complete: {position_details['position_size_usdt']:.2f} USDT with {position_details['leverage_used']}x leverage")
            
            return position_details
            
        except Exception as e:
            safe_log('error', f"❌ Error in position sizing: {e}")
            # Return minimum viable position as fallback
            return {
                'position_size_usdt': self.config.min_order_size,
                'position_size_units': self.config.min_order_size / current_price,
                'required_capital': self.config.min_order_size / self.config.leverage,
                'leverage_used': self.config.leverage,
                'risk_amount': account_balance * (self.config.risk_per_trade / 100),
                'entry_price': current_price,
                'stop_loss_price': None,
                'is_viable': False,
                'reason': f"Error: {str(e)}"
            }

    def calculate_stop_loss_take_profit(self, signal: Dict, entry_price: float) -> Tuple[float, float]:
        """🎯 Calculate stop loss and take profit with tighter scalping levels"""
        
        is_confluence = signal.get('is_confluence', False)
        
        # Tighter levels for scalping, slightly wider for confluence
        stop_loss_pct = self.config.stop_loss_pct * (1.1 if is_confluence else 1.0)
        take_profit_pct = self.config.take_profit_pct * (1.2 if is_confluence else 1.0)
        
        if signal['type'] == 'LONG':
            stop_loss = entry_price * (1 - stop_loss_pct / 100)
            take_profit = entry_price * (1 + take_profit_pct / 100)
        else:  # SHORT
            stop_loss = entry_price * (1 + stop_loss_pct / 100)
            take_profit = entry_price * (1 - take_profit_pct / 100)
        
        return stop_loss, take_profit

    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """📋 Get recent signals for display"""
        return self.signals_history[-limit:] if self.signals_history else []

    def calculate_strategy_stats(self) -> Dict:
        """📊 Enhanced strategy statistics with confluence metrics"""
        
        if not self.signals_history:
            return {
                'total_signals': 0,
                'confluence_signals': 0,
                'confluence_rate': 0,
                'long_signals': 0,
                'short_signals': 0,
                'avg_confidence': 0,
                'avg_volume_ratio': 0
            }
        
        confluence_signals = [s for s in self.signals_history if s.get('is_confluence', False)]
        long_signals = [s for s in self.signals_history if s['type'] == 'LONG']
        short_signals = [s for s in self.signals_history if s['type'] == 'SHORT']
        
        avg_confidence = np.mean([s['confidence'] for s in self.signals_history])
        avg_volume_ratio = np.mean([s['volume_ratio'] for s in self.signals_history])
        confluence_rate = len(confluence_signals) / len(self.signals_history) if self.signals_history else 0
        
        return {
            'total_signals': len(self.signals_history),
            'confluence_signals': len(confluence_signals),
            'confluence_rate': confluence_rate * 100,
            'long_signals': len(long_signals),
            'short_signals': len(short_signals),
            'avg_confidence': avg_confidence,
            'avg_volume_ratio': avg_volume_ratio
        }