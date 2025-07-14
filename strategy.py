"""
🏔️ Alpine Trading Bot - Enhanced Volume Anomaly Strategy
Optimized for 1m/3m confluence signals with dynamic position sizing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
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
    """🎯 Enhanced Volume Anomaly Strategy - Optimized for 1m/3m Confluence"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # Strategy parameters (optimized for 1m/3m scalping)
        self.volume_lookback = self.config.volume_lookback
        self.volume_std_multiplier = self.config.volume_std_multiplier
        self.atr_period = self.config.supertrend_atr_period
        self.atr_multiplier = self.config.supertrend_multiplier
        
        # Confluence configuration
        self.timeframes = self.config.timeframes  # ['1m', '3m']
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
        
        safe_log('success', f"🎯 Enhanced Strategy initialized for {self.timeframes} confluence trading")

    def calculate_supertrend(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """📈 Enhanced SuperTrend calculation for faster signals"""
        try:
            if len(df) < self.atr_period:
                safe_log('warning', f"⚠️ Insufficient data for SuperTrend: {len(df)} < {self.atr_period}")
                return pd.Series([np.nan] * len(df)), pd.Series([0] * len(df))
            
            # Calculate ATR with optimized period for scalping
            atr = ta.volatility.AverageTrueRange(
                high=df['high'],
                low=df['low'], 
                close=df['close'],
                window=self.atr_period
            ).average_true_range()
            
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
        """📊 Enhanced volume analysis optimized for scalping"""
        try:
            if len(df) < self.volume_lookback:
                safe_log('warning', f"⚠️ Insufficient data for volume analysis: {len(df)} < {self.volume_lookback}")
                return {
                    'volume_ratio': pd.Series([1.0] * len(df)),
                    'volume_burst': pd.Series([False] * len(df)),
                    'volume_explode': pd.Series([False] * len(df))
                }
            
            # Rolling volume statistics (optimized for scalping)
            volume_sma = df['volume'].rolling(window=self.volume_lookback).mean()
            volume_std = df['volume'].rolling(window=self.volume_lookback).std()
            
            # Volume ratio calculation
            volume_ratio = df['volume'] / volume_sma
            
            # Enhanced volume thresholds for scalping
            volume_threshold = volume_sma + (volume_std * self.volume_std_multiplier)
            
            # Volume burst detection (moderate anomaly)
            volume_burst = (df['volume'] > volume_threshold) & (volume_ratio >= self.vol_burst_factor)
            
            # Volume explosion detection (extreme anomaly) 
            volume_explode = (df['volume'] > volume_threshold * 1.5) & (volume_ratio >= self.vol_explode_factor)
            
            return {
                'volume_ratio': volume_ratio,
                'volume_burst': volume_burst,
                'volume_explode': volume_explode
            }
            
        except Exception as e:
            safe_log('warning', f"⚠️ Volume analysis error: {e}")
            return {
                'volume_ratio': pd.Series([1.0] * len(df)),
                'volume_burst': pd.Series([False] * len(df)),
                'volume_explode': pd.Series([False] * len(df))
            }

    def calculate_ema_pullback(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """📈 EMA pullback analysis for trend confirmation"""
        try:
            # Fast EMA for scalping (optimized periods)
            ema_fast = ta.trend.EMAIndicator(df['close'], window=8).ema_indicator()
            ema_slow = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
            
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

    def analyze_confluence_signals(self, timeframe_data: Dict[str, pd.DataFrame], symbol: str) -> List[Dict]:
        """🎯 Analyze confluence signals across 1m/3m timeframes"""
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

    def generate_single_timeframe_signals(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[Dict]:
        """📊 Generate signals for a single timeframe with enhanced logic"""
        try:
            if len(df) < 20:  # Minimum data requirement
                safe_log('warning', f"⚠️ Insufficient data for signal generation: {len(df)} < 20")
                return []
            
            signals = []
            
            # Calculate all indicators
            supertrend, trend = self.calculate_supertrend(df)
            volume_analysis = self.calculate_volume_analysis(df)
            ema_analysis = self.calculate_ema_pullback(df)
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            current_volume_ratio = volume_analysis['volume_ratio'].iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            current_trend = trend.iloc[-1]
            
            # Volume conditions
            volume_burst = volume_analysis['volume_burst'].iloc[-1]
            volume_explode = volume_analysis['volume_explode'].iloc[-1]
            
            # Trend conditions
            trend_up = ema_analysis['trend_up'].iloc[-1]
            trend_down = ema_analysis['trend_down'].iloc[-1]
            pullback_long = ema_analysis['pullback_long'].iloc[-1]
            pullback_short = ema_analysis['pullback_short'].iloc[-1]
            
            # Signal generation logic (optimized for scalping)
            signal_strength = 0
            signal_type = None
            signal_reasons = []
            
            # LONG signal conditions
            if (current_trend > 0 and trend_up and 
                (volume_burst or volume_explode) and
                current_price > current_supertrend):
                
                signal_type = 'LONG'
                signal_strength += 30  # Base strength
                signal_reasons.append("SuperTrend bullish")
                
                if pullback_long:
                    signal_strength += 20
                    signal_reasons.append("EMA pullback")
                
                if volume_explode:
                    signal_strength += 25
                    signal_reasons.append("Volume explosion")
                elif volume_burst:
                    signal_strength += 15
                    signal_reasons.append("Volume burst")
                
                if current_volume_ratio >= self.config.min_volume_ratio:
                    signal_strength += 10
                    signal_reasons.append(f"High volume ({current_volume_ratio:.1f}x)")
            
            # SHORT signal conditions
            elif (current_trend < 0 and trend_down and 
                  (volume_burst or volume_explode) and
                  current_price < current_supertrend):
                
                signal_type = 'SHORT'
                signal_strength += 30  # Base strength
                signal_reasons.append("SuperTrend bearish")
                
                if pullback_short:
                    signal_strength += 20
                    signal_reasons.append("EMA pullback")
                
                if volume_explode:
                    signal_strength += 25
                    signal_reasons.append("Volume explosion")
                elif volume_burst:
                    signal_strength += 15
                    signal_reasons.append("Volume burst")
                
                if current_volume_ratio >= self.config.min_volume_ratio:
                    signal_strength += 10
                    signal_reasons.append(f"High volume ({current_volume_ratio:.1f}x)")
            
            # Create signal if strength meets threshold
            if signal_type and signal_strength >= 60:  # Minimum 60% confidence for scalping
                signal = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'type': signal_type,
                    'confidence': min(signal_strength, 100),
                    'entry_price': current_price,
                    'volume_ratio': current_volume_ratio,
                    'supertrend': current_supertrend,
                    'trend_direction': current_trend,
                    'reasons': signal_reasons,
                    'timestamp': datetime.now(),
                    'is_confluence': False  # Will be set by confluence analysis
                }
                
                signals.append(signal)
                safe_log('info', f"📊 {timeframe} Signal: {symbol} {signal_type} (Confidence: {signal_strength}%)")
                safe_log('debug', f"   📋 Reasons: {', '.join(signal_reasons)}")
            
            return signals
            
        except Exception as e:
            safe_log('warning', f"⚠️ Signal generation error for {timeframe}: {e}")
            return []

    def should_enter_trade(self, signal: Dict, account_balance: float, current_positions: List[Dict]) -> bool:
        """🎯 Enhanced trade entry logic with confluence consideration"""
        
        symbol = signal.get('symbol', 'Unknown')
        confidence = signal.get('confidence', 0)
        volume_ratio = signal.get('volume_ratio', 0)
        is_confluence = signal.get('is_confluence', False)
        
        # Lower thresholds for confluence signals
        min_confidence = 65.0 if is_confluence else 75.0
        min_volume_ratio = self.config.min_volume_ratio * (0.8 if is_confluence else 1.0)
        
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

    def calculate_position_size(self, signal: Dict, account_balance: float, current_price: float) -> float:
        """💰 Enhanced position sizing with confluence boost"""
        
        is_confluence = signal.get('is_confluence', False)
        
        # Base position value
        base_position_pct = self.config.position_size_pct
        
        # Apply confluence multiplier
        if is_confluence:
            position_pct = base_position_pct * self.config.confluence_position_multiplier
            safe_log('info', f"🚀 Confluence boost applied: {base_position_pct}% → {position_pct:.1f}%")
        else:
            position_pct = base_position_pct
        
        # Calculate position value
        position_value = account_balance * (position_pct / 100)
        
        # Calculate position size in contracts/units
        position_size = position_value / current_price
        
        return position_size

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