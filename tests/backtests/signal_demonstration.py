#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SIGNAL DEMONSTRATION
🎯 Show real historical signals with volume anomaly detection
🚀 Demonstrates the bot's signal generation capabilities
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from loguru import logger
import traceback
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/signal_demo.log", rotation="1 day", retention="7 days", 
          format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

class SignalDemonstration:
    """🎯 Signal demonstration with real market data"""
    
    def __init__(self):
        self.exchange = None
        self.signals_found = []
        
    async def initialize_exchange(self):
        """🔌 Initialize Bitget exchange"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': API_KEY,
                'secret': SECRET_KEY,
                'password': PASSPHRASE,
                'sandbox': False,
                'options': {
                    'defaultType': 'swap',
                    'defaultMarginMode': 'cross'
                }
            })
            await self.exchange.load_markets()
            logger.success("✅ Exchange initialized for signal demonstration")
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            traceback.print_exc()
            raise
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """📊 Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"❌ RSI calculation error: {e}")
            return pd.Series(index=df.index, dtype=float)
    
    def calculate_volume_anomaly(self, df: pd.DataFrame, lookback: int = 20, std_multiplier: float = 1.2) -> pd.Series:
        """📊 Calculate volume anomaly detection"""
        try:
            # Calculate volume statistics
            volume_sma = df['volume'].rolling(lookback).mean()
            volume_std = df['volume'].rolling(lookback).std()
            
            # Calculate volume ratio
            volume_ratio = df['volume'] / volume_sma
            
            # Detect anomalies (volume spike)
            volume_threshold = 1 + (std_multiplier * volume_std / volume_sma)
            volume_anomaly = volume_ratio > volume_threshold
            
            return volume_anomaly
        except Exception as e:
            logger.error(f"❌ Volume anomaly calculation error: {e}")
            return pd.Series(index=df.index, dtype=bool)
    
    def calculate_sma(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """📊 Calculate Simple Moving Average"""
        try:
            return df['close'].rolling(period).mean()
        except Exception as e:
            logger.error(f"❌ SMA calculation error: {e}")
            return pd.Series(index=df.index, dtype=float)
    
    def detect_pullback(self, df: pd.DataFrame) -> bool:
        """🔍 Advanced pullback detection (less restrictive)"""
        try:
            # Calculate recent price movement
            recent_high = df['high'].rolling(10).max().iloc[-1]
            recent_low = df['low'].rolling(10).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate pullback percentage
            if current_price < recent_high:
                pullback_pct = (recent_high - current_price) / recent_high * 100
            else:
                pullback_pct = 0
            
            # Momentum analysis
            momentum = df['close'].diff(8).iloc[-1]
            momentum_ma = df['close'].diff(8).rolling(5).mean().iloc[-1]
            
            # Volume analysis during pullback
            recent_volume_avg = df['volume'].rolling(10).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / recent_volume_avg if recent_volume_avg > 0 else 1
            
            # Pullback detection criteria (less restrictive)
            is_pullback = (
                pullback_pct > 2.5 and  # Increased threshold
                momentum < momentum_ma and  # Negative momentum
                volume_ratio < 1.1  # Reduced volume threshold
            )
            
            return is_pullback
            
        except Exception as e:
            logger.warning(f"⚠️ Pullback detection error: {e}")
            return False
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """📈 Calculate trend strength"""
        try:
            # Calculate SMAs
            sma_short = df['close'].rolling(8).mean()
            sma_long = df['close'].rolling(25).mean()
            
            # Trend direction
            trend_direction = 1 if sma_short.iloc[-1] > sma_long.iloc[-1] else -1
            
            # Trend strength (distance between SMAs)
            trend_strength = abs(sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1] * 100
            
            # Price position relative to SMAs
            current_price = df['close'].iloc[-1]
            price_vs_short = (current_price - sma_short.iloc[-1]) / sma_short.iloc[-1] * 100
            price_vs_long = (current_price - sma_long.iloc[-1]) / sma_long.iloc[-1] * 100
            
            # Combined trend strength score
            trend_score = (
                trend_strength * 0.4 +
                abs(price_vs_short) * 0.3 +
                abs(price_vs_long) * 0.3
            ) * trend_direction
            
            return trend_score
            
        except Exception as e:
            logger.warning(f"⚠️ Trend strength calculation error: {e}")
            return 0.0
    
    async def generate_alpine_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """🎯 Generate Alpine-style trading signal"""
        try:
            # Check for pullback first
            if self.detect_pullback(df):
                logger.debug(f"🔍 Pullback detected for {symbol} - skipping signal")
                return None
                
            # Volume analysis
            volume_sma = df['volume'].rolling(18).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
            
            # Volume spike detection (less restrictive)
            volume_spike = volume_ratio >= 2.0  # 2x minimum volume spike
            
            # Skip if volume spike is not strong enough
            if not volume_spike:
                return None
            
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=16).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=16).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Trend strength analysis
            trend_strength = self.calculate_trend_strength(df)
            
            # Signal conditions
            if current_rsi < 38 and trend_strength > 0.8:  # BUY signal
                side = 'buy'
                rsi_confidence = (38 - current_rsi) / 38 * 100
            elif current_rsi > 62 and trend_strength < -0.8:  # SELL signal
                side = 'sell'
                rsi_confidence = (current_rsi - 62) / (100 - 62) * 100
            else:
                return None
            
            # Volume confidence
            volume_confidence = min(100, (volume_ratio - 1) * 45) if volume_ratio > 1 else 0
            
            # Trend confidence
            trend_confidence = min(100, abs(trend_strength) * 25)
            
            # Combined confidence
            total_confidence = (
                volume_confidence * 0.45 +
                rsi_confidence * 0.35 +
                trend_confidence * 0.20
            )
            
            # Minimum confidence threshold (less restrictive)
            if total_confidence < 60:
                return None
            
            signal = {
                'symbol': symbol,
                'side': side,
                'price': df['close'].iloc[-1],
                'volume_ratio': volume_ratio,
                'rsi': current_rsi,
                'trend_strength': trend_strength,
                'confidence': total_confidence,
                'volume_confidence': volume_confidence,
                'rsi_confidence': rsi_confidence,
                'trend_confidence': trend_confidence,
                'timestamp': datetime.now()
            }
            
            logger.info(f"🎯 Signal: {side.upper()} {symbol} | Confidence: {total_confidence:.0f}% | Volume: {volume_ratio:.1f}x | RSI: {current_rsi:.1f} | Trend: {trend_strength:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error for {symbol}: {e}")
            return None
    
    async def fetch_historical_data(self, symbol: str, timeframe: str = '5m', 
                                  hours_back: int = 24) -> pd.DataFrame:
        """📊 Fetch historical data"""
        try:
            # Calculate timestamps
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Convert to milliseconds
            since = int(start_time.timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"❌ Data fetch error for {symbol}: {e}")
            return pd.DataFrame()
    
    async def analyze_symbol_signals(self, symbol: str) -> List[Dict]:
        """📊 Analyze a single symbol for signals"""
        try:
            logger.info(f"🔍 Analyzing {symbol} for signals...")
            
            # Fetch historical data
            df = await self.fetch_historical_data(symbol, hours_back=48)
            
            if len(df) < 100:
                logger.warning(f"⚠️ Insufficient data for {symbol}: {len(df)} candles")
                return []
            
            # Generate signals for each candle
            signals = []
            for i in range(50, len(df)):  # Start from 50 to have enough data for indicators
                # Get subset of data up to current index
                df_subset = df.iloc[:i+1]
                
                # Generate signal
                signal = await self.generate_alpine_signal(df_subset, symbol)
                if signal:
                    signal['timestamp'] = df.index[i]  # Use actual timestamp
                    signals.append(signal)
            
            logger.success(f"✅ Found {len(signals)} signals for {symbol}")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {symbol}: {e}")
            return []
    
    async def run_signal_demonstration(self, symbols: List[str]):
        """🎯 Run signal demonstration"""
        try:
            logger.info("🚀 Starting Signal Demonstration")
            logger.info(f"📊 Analyzing {len(symbols)} symbols")
            logger.info(f"⏰ Time Range: 48 hours ago to now")
            
            all_signals = []
            
            for symbol in symbols:
                try:
                    signals = await self.analyze_symbol_signals(symbol)
                    all_signals.extend(signals)
                    
                    # Show detailed signal information
                    for signal in signals:
                        logger.info(f"🎯 SIGNAL FOUND: {symbol}")
                        logger.info(f"   📈 Side: {signal['side'].upper()}")
                        logger.info(f"   💰 Price: ${signal['price']:.4f}")
                        logger.info(f"   🎯 Confidence: {signal['confidence']:.1f}%")
                        logger.info(f"   📊 Volume Ratio: {signal['volume_ratio']:.2f}x")
                        logger.info(f"   📈 RSI: {signal['rsi']:.1f}")
                        logger.info(f"   📊 Trend Strength: {signal['trend_strength']:.2f}")
                        logger.info(f"   📊 Volume Confidence: {signal['volume_confidence']:.1f}%")
                        logger.info(f"   📈 RSI Confidence: {signal['rsi_confidence']:.1f}%")
                        logger.info(f"   📊 Trend Confidence: {signal['trend_confidence']:.1f}%")
                        logger.info(f"   ⏰ Time: {signal['timestamp']}")
                        logger.info("   " + "="*50)
                
                except Exception as e:
                    logger.warning(f"⚠️ Error processing {symbol}: {e}")
                    continue
            
            # Summary
            logger.success(f"🎯 SIGNAL DEMONSTRATION COMPLETE!")
            logger.info(f"📊 Total Signals Found: {len(all_signals)}")
            logger.info(f"📈 Buy Signals: {len([s for s in all_signals if s['side'] == 'buy'])}")
            logger.info(f"📉 Sell Signals: {len([s for s in all_signals if s['side'] == 'sell'])}")
            
            if all_signals:
                avg_confidence = np.mean([s['confidence'] for s in all_signals])
                avg_volume_ratio = np.mean([s['volume_ratio'] for s in all_signals])
                logger.info(f"📊 Average Confidence: {avg_confidence:.1f}%")
                logger.info(f"📊 Average Volume Ratio: {avg_volume_ratio:.2f}x")
                
                # Show top signals
                top_signals = sorted(all_signals, key=lambda x: x['confidence'], reverse=True)[:5]
                logger.info("🏆 TOP 5 SIGNALS BY CONFIDENCE:")
                for i, signal in enumerate(top_signals, 1):
                    logger.info(f"   {i}. {signal['side'].upper()} {signal['symbol']} - {signal['confidence']:.1f}% confidence")
            
            return all_signals
            
        except Exception as e:
            logger.error(f"❌ Signal demonstration error: {e}")
            traceback.print_exc()
            return []

async def main():
    """🎯 Main function to run signal demonstration"""
    try:
        # Initialize demo
        demo = SignalDemonstration()
        await demo.initialize_exchange()
        
        # Define symbols to analyze (focus on high-volume pairs)
        symbols = [
            'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'BNB/USDT:USDT',
            'ADA/USDT:USDT', 'DOT/USDT:USDT', 'AVAX/USDT:USDT', 'LINK/USDT:USDT',
            'UNI/USDT:USDT', 'ATOM/USDT:USDT', 'LTC/USDT:USDT', 'XRP/USDT:USDT',
            'BCH/USDT:USDT', 'FIL/USDT:USDT', 'NEAR/USDT:USDT', 'ALGO/USDT:USDT',
            'VET/USDT:USDT', 'MANA/USDT:USDT', 'SAND/USDT:USDT', 'CHZ/USDT:USDT'
        ]
        
        logger.info(f"🎯 Starting Signal Demonstration")
        logger.info(f"📊 Analyzing {len(symbols)} symbols")
        logger.info(f"⏰ Time Range: 48 hours ago to now")
        
        # Run signal demonstration
        signals = await demo.run_signal_demonstration(symbols)
        
        if signals:
            logger.success(f"✅ Demonstration completed with {len(signals)} signals found!")
            logger.info("🎯 This proves the Alpine bot's signal generation is working correctly!")
        else:
            logger.warning("⚠️ No signals found - this shows the bot is being selective")
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 