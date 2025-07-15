import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """
    Technical indicators calculator for crypto scoring system
    
    Provides all technical indicators needed for the scoring system:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Moving Averages (EMA, SMA)
    - ATR (Average True Range)
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        try:
            if len(prices) < period + 1:
                return 50.0  # Neutral RSI if insufficient data
                
            prices = np.array(prices)
            deltas = np.diff(prices)
            
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
                
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return max(0, min(100, rsi))
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[float, float]:
        """Calculate MACD and signal line"""
        try:
            if len(prices) < slow_period:
                return 0.0, 0.0
                
            prices = np.array(prices)
            
            # Calculate EMAs
            ema_fast = TechnicalIndicators.calculate_ema(prices, fast_period)
            ema_slow = TechnicalIndicators.calculate_ema(prices, slow_period)
            
            # MACD line
            macd_line = ema_fast - ema_slow
            
            # Signal line (EMA of MACD)
            macd_history = [macd_line] * signal_period  # Simplified for current calculation
            signal_line = TechnicalIndicators.calculate_ema(np.array(macd_history), signal_period)
            
            return macd_line, signal_line
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        try:
            if len(prices) < period:
                current_price = prices[-1] if prices else 0
                return current_price * 1.05, current_price, current_price * 0.95
                
            prices = np.array(prices)
            
            # Simple Moving Average (middle band)
            sma = np.mean(prices[-period:])
            
            # Standard deviation
            std = np.std(prices[-period:])
            
            # Upper and lower bands
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            
            return upper_band, sma, lower_band
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            current_price = prices[-1] if prices else 0
            return current_price * 1.05, current_price, current_price * 0.95
    
    @staticmethod
    def calculate_ema(prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return np.mean(prices) if len(prices) > 0 else 0
                
            # Calculate EMA
            multiplier = 2 / (period + 1)
            ema = prices[0]  # Start with first price
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
                
            return ema
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return np.mean(prices) if len(prices) > 0 else 0
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return np.mean(prices) if len(prices) > 0 else 0
                
            return np.mean(prices[-period:])
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return np.mean(prices) if len(prices) > 0 else 0
    
    @staticmethod
    def calculate_atr(high_prices: List[float], low_prices: List[float], close_prices: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            if len(high_prices) < 2 or len(low_prices) < 2 or len(close_prices) < 2:
                return 0.0
                
            high_prices = np.array(high_prices)
            low_prices = np.array(low_prices)
            close_prices = np.array(close_prices)
            
            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(high_prices)):
                tr1 = high_prices[i] - low_prices[i]
                tr2 = abs(high_prices[i] - close_prices[i-1])
                tr3 = abs(low_prices[i] - close_prices[i-1])
                
                true_range = max(tr1, tr2, tr3)
                true_ranges.append(true_range)
            
            # Average True Range
            if len(true_ranges) < period:
                return np.mean(true_ranges) if true_ranges else 0.0
                
            return np.mean(true_ranges[-period:])
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_all_indicators(
        prices: List[float],
        high_prices: List[float],
        low_prices: List[float],
        volumes: List[float]
    ) -> dict:
        """Calculate all technical indicators at once"""
        try:
            current_price = prices[-1] if prices else 0
            
            # RSI (keep for compatibility but SuperTrend is primary)
            rsi = TechnicalIndicators.calculate_rsi(prices)
            
            # MACD
            macd, macd_signal = TechnicalIndicators.calculate_macd(prices)
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(prices)
            
            # Moving Averages
            ema_12 = TechnicalIndicators.calculate_ema(np.array(prices), 12)
            ema_26 = TechnicalIndicators.calculate_ema(np.array(prices), 26)
            sma_50 = TechnicalIndicators.calculate_sma(prices, 50)
            sma_200 = TechnicalIndicators.calculate_sma(prices, 200)
            
            # ATR
            atr = TechnicalIndicators.calculate_atr(high_prices, low_prices, prices)
            
            # SuperTrend (PRIMARY INDICATOR - replaces RSI)
            supertrend_values, supertrend_direction = TechnicalIndicators.calculate_supertrend(
                high_prices, low_prices, prices, atr_period=10, multiplier=3.0
            )
            supertrend = supertrend_values[-1] if supertrend_values else current_price
            trend_direction = supertrend_direction[-1] if supertrend_direction else 1
            
            # Calculate SuperTrend strength
            supertrend_strength = 0.0
            if trend_direction == 1:  # Bullish
                supertrend_strength = ((current_price - supertrend) / supertrend * 100) if supertrend > 0 else 0.0
            else:  # Bearish
                supertrend_strength = ((supertrend - current_price) / supertrend * 100) if supertrend > 0 else 0.0
            
            # Additional momentum indicators
            price_change_24h = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else 0
            price_change_7d = ((prices[-1] - prices[-8]) / prices[-8] * 100) if len(prices) >= 8 else 0
            
            # Volume analysis
            volume_24h = volumes[-1] if volumes else 0
            volume_7d_avg = np.mean(volumes[-7:]) if len(volumes) >= 7 else volume_24h
            
            return {
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'bollinger_upper': bb_upper,
                'bollinger_middle': bb_middle,
                'bollinger_lower': bb_lower,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'atr': atr,
                'supertrend': supertrend,
                'supertrend_direction': trend_direction,
                'supertrend_strength': supertrend_strength,
                'price_change_24h': price_change_24h,
                'price_change_7d': price_change_7d,
                'volume_24h': volume_24h,
                'volume_7d_avg': volume_7d_avg,
                'current_price': current_price,
                'high_24h': high_prices[-1] if high_prices else current_price,
                'low_24h': low_prices[-1] if low_prices else current_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return {
                'rsi': 50.0,
                'macd': 0.0,
                'macd_signal': 0.0,
                'bollinger_upper': current_price * 1.05,
                'bollinger_middle': current_price,
                'bollinger_lower': current_price * 0.95,
                'ema_12': current_price,
                'ema_26': current_price,
                'sma_50': current_price,
                'sma_200': current_price,
                'atr': current_price * 0.02,
                'price_change_24h': 0.0,
                'price_change_7d': 0.0,
                'volume_24h': 0.0,
                'volume_7d_avg': 0.0,
                'current_price': current_price,
                'high_24h': current_price,
                'low_24h': current_price
            }

class VolumeAnalyzer:
    """Advanced volume analysis for volume anomaly detection"""
    
    @staticmethod
    def detect_volume_anomaly(volumes: List[float], threshold: float = 2.0) -> dict:
        """Detect volume anomalies"""
        try:
            if len(volumes) < 2:
                return {
                    'is_anomaly': False,
                    'anomaly_ratio': 1.0,
                    'volume_trend': 'stable',
                    'volume_score': 50.0
                }
                
            volumes = np.array(volumes)
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[:-1])
            
            # Volume anomaly ratio
            anomaly_ratio = current_volume / max(avg_volume, 1)
            
            # Determine if it's an anomaly
            is_anomaly = anomaly_ratio >= threshold
            
            # Volume trend
            if len(volumes) >= 3:
                recent_trend = np.mean(volumes[-3:]) / np.mean(volumes[-6:-3]) if len(volumes) >= 6 else 1.0
                if recent_trend > 1.2:
                    volume_trend = 'increasing'
                elif recent_trend < 0.8:
                    volume_trend = 'decreasing'
                else:
                    volume_trend = 'stable'
            else:
                volume_trend = 'stable'
            
            # Volume score based on anomaly strength
            if anomaly_ratio >= 5.0:
                volume_score = 95.0
            elif anomaly_ratio >= 3.0:
                volume_score = 90.0
            elif anomaly_ratio >= 2.0:
                volume_score = 80.0
            elif anomaly_ratio >= 1.5:
                volume_score = 70.0
            elif anomaly_ratio >= 1.0:
                volume_score = 60.0
            else:
                volume_score = 30.0
                
            return {
                'is_anomaly': is_anomaly,
                'anomaly_ratio': anomaly_ratio,
                'volume_trend': volume_trend,
                'volume_score': volume_score,
                'current_volume': current_volume,
                'avg_volume': avg_volume
            }
            
        except Exception as e:
            logger.error(f"Error detecting volume anomaly: {e}")
            return {
                'is_anomaly': False,
                'anomaly_ratio': 1.0,
                'volume_trend': 'stable',
                'volume_score': 50.0,
                'current_volume': 0.0,
                'avg_volume': 0.0
            }
    
    @staticmethod
    def calculate_volume_profile(volumes: List[float], prices: List[float]) -> dict:
        """Calculate volume profile metrics"""
        try:
            if len(volumes) < 5 or len(prices) < 5:
                return {
                    'volume_weighted_price': prices[-1] if prices else 0,
                    'volume_momentum': 0.0,
                    'volume_volatility': 0.0
                }
                
            volumes = np.array(volumes)
            prices = np.array(prices)
            
            # Volume Weighted Average Price (VWAP)
            vwap = np.sum(volumes * prices) / np.sum(volumes)
            
            # Volume momentum (rate of change)
            volume_momentum = (volumes[-1] - volumes[-2]) / volumes[-2] if len(volumes) >= 2 else 0
            
            # Volume volatility
            volume_volatility = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
            
            return {
                'volume_weighted_price': vwap,
                'volume_momentum': volume_momentum,
                'volume_volatility': volume_volatility
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return {
                'volume_weighted_price': prices[-1] if prices else 0,
                'volume_momentum': 0.0,
                'volume_volatility': 0.0
            }

# Test the indicators
if __name__ == "__main__":
    # Sample price data
    sample_prices = [100, 102, 98, 105, 103, 107, 109, 106, 108, 110, 
                     112, 109, 111, 113, 115, 112, 114, 116, 118, 115]
    sample_highs = [p * 1.02 for p in sample_prices]
    sample_lows = [p * 0.98 for p in sample_prices]
    sample_volumes = [1000000, 1200000, 800000, 1500000, 1100000, 
                      1800000, 2000000, 1300000, 1600000, 1900000,
                      2200000, 1400000, 1700000, 2100000, 2300000,
                      1500000, 1800000, 2000000, 2400000, 1600000]
    
    # Calculate all indicators
    indicators = TechnicalIndicators.calculate_all_indicators(
        sample_prices, sample_highs, sample_lows, sample_volumes
    )
    
    # Volume analysis
    volume_analysis = VolumeAnalyzer.detect_volume_anomaly(sample_volumes)
    
    print("=== TECHNICAL INDICATORS TEST ===")
    print(f"RSI: {indicators['rsi']:.2f}")
    print(f"MACD: {indicators['macd']:.2f}")
    print(f"MACD Signal: {indicators['macd_signal']:.2f}")
    print(f"Bollinger Upper: {indicators['bollinger_upper']:.2f}")
    print(f"Bollinger Lower: {indicators['bollinger_lower']:.2f}")
    print(f"EMA 12: {indicators['ema_12']:.2f}")
    print(f"EMA 26: {indicators['ema_26']:.2f}")
    print(f"SMA 50: {indicators['sma_50']:.2f}")
    print(f"ATR: {indicators['atr']:.2f}")
    
    print("\n=== VOLUME ANALYSIS ===")
    print(f"Volume Anomaly: {volume_analysis['is_anomaly']}")
    print(f"Anomaly Ratio: {volume_analysis['anomaly_ratio']:.2f}")
    print(f"Volume Trend: {volume_analysis['volume_trend']}")
    print(f"Volume Score: {volume_analysis['volume_score']:.2f}")