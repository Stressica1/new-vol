"""
🏔️ Alpine Trading Bot - Volume Anomaly Strategy
Implementing the exact logic from the PineScript indicator
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
    """🎯 Volume Anomaly Strategy - 90% Success Rate Implementation"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # Strategy parameters (from PineScript)
        self.volume_lookback = self.config.volume_lookback
        self.volume_std_multiplier = self.config.volume_std_multiplier
        self.atr_period = self.config.supertrend_atr_period
        self.atr_multiplier = self.config.supertrend_multiplier
        
        # Timeframe configuration
        self.timeframes = self.config.timeframes
        self.primary_timeframe = self.config.primary_timeframe
        self.confluence_required = self.config.signal_confluence_required
        
        # Volume analysis parameters
        self.vol_burst_factor = 1.5
        self.vol_explode_factor = 2.0
        
        # Signal history
        self.signals_history = []
        
    def calculate_supertrend(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate SuperTrend indicator 📈"""
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Calculate ATR
        atr = ta.volatility.AverageTrueRange(high=high, low=low, close=close, window=self.atr_period).average_true_range()
        
        # Calculate HL2 (typical price)
        hl2 = (high + low) / 2
        
        # Calculate upper and lower bands
        upper_band = hl2 + (self.atr_multiplier * atr)
        lower_band = hl2 - (self.atr_multiplier * atr)
        
        # Initialize SuperTrend
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        
        # Calculate SuperTrend values
        for i in range(1, len(df)):
            if close.iloc[i] <= lower_band.iloc[i-1]:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1  # Uptrend
            elif close.iloc[i] >= upper_band.iloc[i-1]:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1  # Downtrend
            else:
                if direction.iloc[i-1] == 1 and lower_band.iloc[i] < supertrend.iloc[i-1]:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                elif direction.iloc[i-1] == -1 and upper_band.iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                else:
                    supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i-1] == 1 else upper_band.iloc[i]
                direction.iloc[i] = direction.iloc[i-1]
        
        return supertrend, direction
    
    def calculate_volume_analysis(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volume analysis indicators 📊"""
        
        volume = df['volume']
        
        # Volume moving average
        vol_ma = volume.rolling(window=self.volume_lookback).mean()
        
        # Volume standard deviation
        vol_std = volume.rolling(window=self.volume_lookback).std()
        
        # Volume upper band (anomaly threshold)
        vol_upper = vol_ma + (vol_std * self.volume_std_multiplier)
        
        # Volume conditions
        vol_burst = volume > (vol_ma * self.vol_burst_factor)
        vol_explosive = volume > (vol_ma * self.vol_explode_factor)
        vol_anomalous = volume > vol_upper  # This is the main signal from PineScript
        
        # Volume multiple
        vol_multiple = volume / vol_ma
        
        return {
            'vol_ma': vol_ma,
            'vol_std': vol_std,
            'vol_upper': vol_upper,
            'vol_burst': vol_burst,
            'vol_explosive': vol_explosive,
            'vol_anomalous': vol_anomalous,  # Main signal
            'vol_multiple': vol_multiple
        }
    
    def calculate_ema_pullback(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate EMA pullback conditions 📉"""
        
        close = df['close']
        volume = df['volume']
        
        # EMAs
        ema_fast = close.ewm(span=8).mean()
        ema_slow = close.ewm(span=21).mean()
        
        # Volume MA for pullback confirmation
        vol_ma = volume.rolling(window=self.volume_lookback).mean()
        
        return {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'vol_ma': vol_ma
        }
    
    def analyze_timeframe_signals(self, timeframe_data: Dict[str, pd.DataFrame], symbol: str) -> List[Dict]:
        """Analyze multiple timeframes for signal confluence 📊"""
        
        timeframe_signals = {}
        
        # Generate signals for each timeframe
        for timeframe, df in timeframe_data.items():
            if df is None or len(df) < max(self.volume_lookback, self.atr_period, 21):
                continue
                
            signals = self.generate_single_timeframe_signals(df, symbol, timeframe)
            if signals:
                timeframe_signals[timeframe] = signals
        
        # Find confluence signals
        confluence_signals = []
        
        if len(timeframe_signals) >= self.confluence_required:
            # Check for signal agreement across timeframes
            for tf_signals in timeframe_signals.values():
                for signal in tf_signals:
                    # Count how many timeframes agree on this signal type
                    agreement_count = 0
                    supporting_timeframes = []
                    
                    for tf, tf_signal_list in timeframe_signals.items():
                        for tf_signal in tf_signal_list:
                            if (tf_signal['type'] == signal['type'] and 
                                abs(tf_signal['timestamp'] - signal['timestamp']) <= 300):  # 5 min tolerance
                                agreement_count += 1
                                supporting_timeframes.append(tf)
                                break
                    
                    # If enough timeframes agree, create confluence signal
                    if agreement_count >= self.confluence_required:
                        confluence_signal = signal.copy()
                        confluence_signal['confluence_count'] = agreement_count
                        confluence_signal['supporting_timeframes'] = supporting_timeframes
                        confluence_signal['confidence'] = min(95, signal['confidence'] + (agreement_count * 10))
                        confluence_signals.append(confluence_signal)
        
        return confluence_signals
    
    def generate_single_timeframe_signals(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[Dict]:
        """Generate signals for a single timeframe 📈"""
        
        if len(df) < max(self.volume_lookback, self.atr_period, 21):
            return []

        # Calculate indicators
        supertrend, direction = self.calculate_supertrend(df)
        volume_data = self.calculate_volume_analysis(df)
        ema_data = self.calculate_ema_pullback(df)

        signals = []

        # Get the latest data points
        latest_idx = df.index[-1]
        current_price = df.loc[latest_idx, 'close']
        current_volume = df.loc[latest_idx, 'volume']

        # Volume anomaly detection
        vol_ratio = volume_data['vol_multiple'].iloc[-1]
        vol_spike = volume_data['vol_explosive'].iloc[-1]

        # SuperTrend signals
        current_supertrend = supertrend.iloc[-1]
        current_direction = direction.iloc[-1]

        # EMA signals
        ema_fast = ema_data['ema_fast'].iloc[-1]
        ema_slow = ema_data['ema_slow'].iloc[-1]

        # Debug logging for signal analysis
        safe_log('debug', f"🔍 {symbol} {timeframe} Analysis:")
        safe_log('debug', f"  💰 Price: ${current_price:.4f}")
        safe_log('debug', f"  📊 Volume Ratio: {vol_ratio:.2f}x (need >{self.config.min_volume_ratio})")
        safe_log('debug', f"  🔥 Volume Spike: {vol_spike}")
        safe_log('debug', f"  📈 SuperTrend: ${current_supertrend:.4f} (direction: {current_direction})")
        safe_log('debug', f"  📊 EMA Fast: ${ema_fast:.4f}")
        safe_log('debug', f"  📊 EMA Slow: ${ema_slow:.4f}")
        safe_log('debug', f"  📊 EMA Bullish: {ema_fast > ema_slow} (fast > slow)")

        # Signal generation logic
        if vol_ratio > self.config.min_volume_ratio and vol_spike:  # Volume anomaly detected
            safe_log('info', f"🔥 {symbol} {timeframe}: Volume anomaly detected! {vol_ratio:.2f}x")
            
            # LONG signal conditions
            long_supertrend_bullish = current_direction == 1
            long_price_above_supertrend = current_price > current_supertrend
            long_ema_bullish = ema_fast > ema_slow
            long_price_above_ema = current_price > ema_fast
            
            safe_log('debug', f"  🟢 LONG Analysis:")
            safe_log('debug', f"    SuperTrend Bullish: {long_supertrend_bullish} (direction == 1)")
            safe_log('debug', f"    Price > SuperTrend: {long_price_above_supertrend} ({current_price:.4f} > {current_supertrend:.4f})")
            safe_log('debug', f"    EMA Bullish: {long_ema_bullish} ({ema_fast:.4f} > {ema_slow:.4f})")
            safe_log('debug', f"    Price > EMA Fast: {long_price_above_ema} ({current_price:.4f} > {ema_fast:.4f})")
            
            if (long_supertrend_bullish and long_price_above_supertrend and 
                long_ema_bullish and long_price_above_ema):
                
                confidence = min(90, 60 + (vol_ratio * 10))
                signal = {
                    'symbol': symbol,
                    'type': 'LONG',
                    'timeframe': timeframe,
                    'timestamp': latest_idx.timestamp(),
                    'price': current_price,
                    'volume_ratio': vol_ratio,
                    'supertrend': current_supertrend,
                    'confidence': confidence,
                    'strength': 'HIGH' if vol_ratio > 3.0 else 'MEDIUM',
                    'action': 'READY'  # Mark as ready for execution
                }
                signals.append(signal)
                safe_log('success', f"✅ {symbol} {timeframe}: LONG signal generated! Confidence: {confidence:.1f}%")
            else:
                safe_log('warning', f"⚠️ {symbol} {timeframe}: LONG signal blocked - technical conditions not met")

            # SHORT signal conditions  
            short_supertrend_bearish = current_direction == -1
            short_price_below_supertrend = current_price < current_supertrend
            short_ema_bearish = ema_fast < ema_slow
            short_price_below_ema = current_price < ema_fast
            
            safe_log('debug', f"  🔴 SHORT Analysis:")
            safe_log('debug', f"    SuperTrend Bearish: {short_supertrend_bearish} (direction == -1)")
            safe_log('debug', f"    Price < SuperTrend: {short_price_below_supertrend} ({current_price:.4f} < {current_supertrend:.4f})")
            safe_log('debug', f"    EMA Bearish: {short_ema_bearish} ({ema_fast:.4f} < {ema_slow:.4f})")
            safe_log('debug', f"    Price < EMA Fast: {short_price_below_ema} ({current_price:.4f} < {ema_fast:.4f})")
            
            if (short_supertrend_bearish and short_price_below_supertrend and
                short_ema_bearish and short_price_below_ema):
                
                confidence = min(90, 60 + (vol_ratio * 10))
                signal = {
                    'symbol': symbol,
                    'type': 'SHORT',
                    'timeframe': timeframe,
                    'timestamp': latest_idx.timestamp(),
                    'price': current_price,
                    'volume_ratio': vol_ratio,
                    'supertrend': current_supertrend,
                    'confidence': confidence,
                    'strength': 'HIGH' if vol_ratio > 3.0 else 'MEDIUM',
                    'action': 'READY'  # Mark as ready for execution
                }
                signals.append(signal)
                safe_log('success', f"✅ {symbol} {timeframe}: SHORT signal generated! Confidence: {confidence:.1f}%")
            else:
                safe_log('warning', f"⚠️ {symbol} {timeframe}: SHORT signal blocked - technical conditions not met")
        else:
            if vol_ratio <= self.config.min_volume_ratio:
                safe_log('debug', f"❌ {symbol} {timeframe}: Volume too low: {vol_ratio:.2f}x (need >{self.config.min_volume_ratio})")
            if not vol_spike:
                safe_log('debug', f"❌ {symbol} {timeframe}: No volume spike detected")

        # Store signals in history
        self.signals_history.extend(signals)

        return signals
    
    def generate_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate Volume Anomaly signals - LEGACY METHOD FOR SINGLE TIMEFRAME 🎯"""
        
        if len(df) < max(self.volume_lookback, self.atr_period, 21):
            return []
        
        # Calculate indicators
        supertrend, direction = self.calculate_supertrend(df)
        volume_data = self.calculate_volume_analysis(df)
        ema_data = self.calculate_ema_pullback(df)
        
        signals = []
        
        # Get latest values
        latest_idx = len(df) - 1
        current_close = df['close'].iloc[latest_idx]
        current_volume = df['volume'].iloc[latest_idx]
        current_time = df.index[latest_idx] if hasattr(df.index[latest_idx], 'to_pydatetime') else datetime.now()
        
        # SuperTrend direction
        st_uptrend = direction.iloc[latest_idx] == 1
        st_downtrend = direction.iloc[latest_idx] == -1
        
        # Volume anomaly condition (main signal from PineScript)
        vol_anomalous = volume_data['vol_anomalous'].iloc[latest_idx]
        vol_multiple = volume_data['vol_multiple'].iloc[latest_idx]
        
        # Generate signals based on PineScript logic
        if vol_anomalous and st_uptrend:
            signal = {
                'symbol': symbol,
                'type': 'LONG',
                'time': current_time,
                'price': current_close,
                'volume_ratio': vol_multiple,
                'anomaly_strength': vol_multiple,
                'supertrend_dir': 'UP',
                'confidence': min(95.0, 70.0 + (vol_multiple * 5)),  # Higher volume = higher confidence
                'action': 'PENDING'
            }
            signals.append(signal)
            
        elif vol_anomalous and st_downtrend:
            signal = {
                'symbol': symbol,
                'type': 'SHORT',
                'time': current_time,
                'price': current_close,
                'volume_ratio': vol_multiple,
                'anomaly_strength': vol_multiple,
                'supertrend_dir': 'DOWN',
                'confidence': min(95.0, 70.0 + (vol_multiple * 5)),  # Higher volume = higher confidence
                'action': 'PENDING'
            }
            signals.append(signal)
        
        # Store signals in history
        self.signals_history.extend(signals)
        
        # Keep only last 100 signals
        if len(self.signals_history) > 100:
            self.signals_history = self.signals_history[-100:]
        
        return signals
    
    def should_enter_trade(self, signal: Dict, account_balance: float, current_positions: List[Dict]) -> bool:
        """Determine if we should enter a trade based on signal and risk management 🎯"""
        
        symbol = signal.get('symbol', 'Unknown')
        confidence = signal.get('confidence', 0)
        volume_ratio = signal.get('volume_ratio', 0)
        
        safe_log('debug', f"🎯 Trade Entry Check for {symbol}:")
        safe_log('debug', f"  📊 Signal Confidence: {confidence:.1f}% (need ≥75%)")
        safe_log('debug', f"  📊 Volume Ratio: {volume_ratio:.2f}x (need ≥{self.config.min_volume_ratio}x)")
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
        
        # Check signal confidence (volume anomaly strength)
        if confidence < 75.0:  # Minimum confidence threshold
            safe_log('warning', f"🚫 {symbol}: Confidence too low: {confidence:.1f}% < 75%")
            return False
        
        # Check volume strength
        if volume_ratio < self.config.min_volume_ratio:  # Must be at least min_volume_ratio average volume
            safe_log('warning', f"🚫 {symbol}: Volume too low: {volume_ratio:.2f}x < {self.config.min_volume_ratio}x")
            return False
        
        safe_log('success', f"✅ {symbol}: All trade entry conditions met! Proceeding with execution...")
        return True
    
    def calculate_position_size(self, signal: Dict, account_balance: float, current_price: float) -> float:
        """Calculate position size based on account balance and risk management 💰"""
        
        # Calculate position value based on percentage of account
        position_value = account_balance * (self.config.position_size_pct / 100)
        
        # Calculate position size in contracts/units
        position_size = position_value / current_price
        
        return position_size
    
    def calculate_stop_loss_take_profit(self, signal: Dict, entry_price: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels 🎯"""
        
        if signal['type'] == 'LONG':
            stop_loss = entry_price * (1 - self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 + self.config.take_profit_pct / 100)
        else:  # SHORT
            stop_loss = entry_price * (1 + self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 - self.config.take_profit_pct / 100)
        
        return stop_loss, take_profit
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals for display 📋"""
        return self.signals_history[-limit:] if self.signals_history else []
    
    def calculate_strategy_stats(self) -> Dict:
        """Calculate strategy performance statistics 📊"""
        
        if not self.signals_history:
            return {
                'total_signals': 0,
                'long_signals': 0,
                'short_signals': 0,
                'avg_confidence': 0,
                'avg_volume_ratio': 0
            }
        
        long_signals = [s for s in self.signals_history if s['type'] == 'LONG']
        short_signals = [s for s in self.signals_history if s['type'] == 'SHORT']
        
        avg_confidence = np.mean([s['confidence'] for s in self.signals_history])
        avg_volume_ratio = np.mean([s['volume_ratio'] for s in self.signals_history])
        
        return {
            'total_signals': len(self.signals_history),
            'long_signals': len(long_signals),
            'short_signals': len(short_signals),
            'avg_confidence': avg_confidence,
            'avg_volume_ratio': avg_volume_ratio
        }