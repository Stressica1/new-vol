#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - HISTORICAL SIGNAL DEMONSTRATION
🎯 Show real signals from 24 hours ago with actual market data
🚀 Demonstrates volume anomaly detection with RSI confirmation
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
logger.add("logs/historical_demo.log", rotation="1 day", retention="7 days", 
          format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

class HistoricalSignalDemo:
    """🎯 Historical signal demonstration with real market data"""
    
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
            logger.success("✅ Exchange initialized for historical demo")
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
    
    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[Dict]:
        """🎯 Generate trading signal with volume anomaly + RSI"""
        try:
            if index < 50:  # Need enough data for indicators
                return None
            
            current_price = df['close'].iloc[index]
            current_volume = df['volume'].iloc[index]
            current_rsi = df['rsi'].iloc[index]
            volume_anomaly = df['volume_anomaly'].iloc[index]
            sma_20 = df['sma_20'].iloc[index]
            sma_50 = df['sma_50'].iloc[index]
            
            # Skip if any values are NaN
            if pd.isna(current_rsi) or pd.isna(sma_20) or pd.isna(sma_50):
                return None
            
            signal = None
            confidence = 0.0
            reasons = []
            
            # Volume anomaly condition (30 points)
            if volume_anomaly:
                volume_ratio = current_volume / df['volume'].rolling(20).mean().iloc[index]
                reasons.append(f"Volume spike: {volume_ratio:.2f}x")
                confidence += 30.0
            
            # RSI conditions (25 points each)
            rsi_condition = False
            if current_rsi < 30:  # Oversold
                rsi_condition = True
                reasons.append(f"RSI oversold: {current_rsi:.1f}")
                confidence += 25.0
            elif current_rsi > 70:  # Overbought
                rsi_condition = True
                reasons.append(f"RSI overbought: {current_rsi:.1f}")
                confidence += 25.0
            
            # Trend condition (20 points)
            trend_condition = False
            if sma_20 > sma_50:  # Uptrend
                trend_condition = True
                reasons.append("Uptrend (SMA20 > SMA50)")
                confidence += 20.0
            elif sma_20 < sma_50:  # Downtrend
                trend_condition = True
                reasons.append("Downtrend (SMA20 < SMA50)")
                confidence += 20.0
            
            # Price action condition (25 points)
            price_action = False
            if current_price > sma_20:  # Price above SMA20
                price_action = True
                reasons.append("Price above SMA20")
                confidence += 25.0
            elif current_price < sma_20:  # Price below SMA20
                price_action = True
                reasons.append("Price below SMA20")
                confidence += 25.0
            
            # Generate signal if confidence is high enough
            if confidence >= 60.0:  # Lowered from 75% to 60% to show more signals
                if rsi_condition and (volume_anomaly or trend_condition):
                    if current_rsi < 35 and current_price > sma_20:  # Relaxed RSI condition
                        signal = {
                            'side': 'buy',
                            'price': current_price,
                            'confidence': confidence,
                            'reasons': reasons,
                            'timestamp': df.index[index],
                            'volume_ratio': current_volume / df['volume'].rolling(20).mean().iloc[index],
                            'rsi': current_rsi,
                            'sma_20': sma_20,
                            'sma_50': sma_50
                        }
                    elif current_rsi > 65 and current_price < sma_20:  # Relaxed RSI condition
                        signal = {
                            'side': 'sell',
                            'price': current_price,
                            'confidence': confidence,
                            'reasons': reasons,
                            'timestamp': df.index[index],
                            'volume_ratio': current_volume / df['volume'].rolling(20).mean().iloc[index],
                            'rsi': current_rsi,
                            'sma_20': sma_20,
                            'sma_50': sma_50
                        }
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return None
    
    async def fetch_historical_data(self, symbol: str, timeframe: str = '5m', 
                                  hours_back: int = 24) -> pd.DataFrame:
        """📊 Fetch historical data from 24 hours ago"""
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
    
    async def analyze_symbol(self, symbol: str) -> List[Dict]:
        """📊 Analyze a single symbol for signals"""
        try:
            logger.info(f"🔍 Analyzing {symbol} for historical signals...")
            
            # Fetch historical data
            df = await self.fetch_historical_data(symbol, hours_back=48)
            
            if len(df) < 100:
                logger.warning(f"⚠️ Insufficient data for {symbol}: {len(df)} candles")
                return []
            
            # Calculate indicators
            df['rsi'] = self.calculate_rsi(df, 14)
            df['volume_anomaly'] = self.calculate_volume_anomaly(df, 20, 1.2)
            df['sma_20'] = self.calculate_sma(df, 20)
            df['sma_50'] = self.calculate_sma(df, 50)
            
            # Generate signals
            signals = []
            for i in range(50, len(df)):
                signal = self.generate_signal(df, i)
                if signal:
                    signals.append(signal)
            
            logger.success(f"✅ Found {len(signals)} signals for {symbol}")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {symbol}: {e}")
            return []
    
    async def run_historical_demo(self, symbols: List[str]):
        """🎯 Run historical signal demonstration"""
        try:
            logger.info("🚀 Starting Historical Signal Demonstration")
            logger.info(f"📊 Analyzing {len(symbols)} symbols from 24 hours ago")
            
            all_signals = []
            
            for symbol in symbols:
                try:
                    signals = await self.analyze_symbol(symbol)
                    all_signals.extend(signals)
                    
                    # Show detailed signal information
                    for signal in signals:
                        logger.info(f"🎯 SIGNAL FOUND: {symbol}")
                        logger.info(f"   📈 Side: {signal['side'].upper()}")
                        logger.info(f"   💰 Price: ${signal['price']:.4f}")
                        logger.info(f"   🎯 Confidence: {signal['confidence']:.1f}%")
                        logger.info(f"   📊 Volume Ratio: {signal['volume_ratio']:.2f}x")
                        logger.info(f"   📈 RSI: {signal['rsi']:.1f}")
                        logger.info(f"   📊 SMA20: ${signal['sma_20']:.4f}")
                        logger.info(f"   📊 SMA50: ${signal['sma_50']:.4f}")
                        logger.info(f"   📝 Reasons: {', '.join(signal['reasons'])}")
                        logger.info(f"   ⏰ Time: {signal['timestamp']}")
                        logger.info("   " + "="*50)
                
                except Exception as e:
                    logger.warning(f"⚠️ Error processing {symbol}: {e}")
                    continue
            
            # Summary
            logger.success(f"🎯 HISTORICAL DEMO COMPLETE!")
            logger.info(f"📊 Total Signals Found: {len(all_signals)}")
            logger.info(f"📈 Buy Signals: {len([s for s in all_signals if s['side'] == 'buy'])}")
            logger.info(f"📉 Sell Signals: {len([s for s in all_signals if s['side'] == 'sell'])}")
            
            if all_signals:
                avg_confidence = np.mean([s['confidence'] for s in all_signals])
                avg_volume_ratio = np.mean([s['volume_ratio'] for s in all_signals])
                logger.info(f"📊 Average Confidence: {avg_confidence:.1f}%")
                logger.info(f"📊 Average Volume Ratio: {avg_volume_ratio:.2f}x")
            
            return all_signals
            
        except Exception as e:
            logger.error(f"❌ Historical demo error: {e}")
            traceback.print_exc()
            return []

async def main():
    """🎯 Main function to run historical signal demonstration"""
    try:
        # Initialize demo
        demo = HistoricalSignalDemo()
        await demo.initialize_exchange()
        
        # Define symbols to analyze
        symbols = [
            'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'BNB/USDT:USDT',
            'ADA/USDT:USDT', 'DOT/USDT:USDT', 'AVAX/USDT:USDT', 'LINK/USDT:USDT',
            'UNI/USDT:USDT', 'ATOM/USDT:USDT', 'LTC/USDT:USDT', 'XRP/USDT:USDT',
            'BCH/USDT:USDT', 'FIL/USDT:USDT', 'NEAR/USDT:USDT', 'FTM/USDT:USDT',
            'ALGO/USDT:USDT', 'VET/USDT:USDT', 'MANA/USDT:USDT', 'SAND/USDT:USDT'
        ]
        
        logger.info(f"🎯 Starting Historical Signal Demo")
        logger.info(f"📊 Analyzing {len(symbols)} symbols")
        logger.info(f"⏰ Time Range: 24 hours ago to now")
        
        # Run historical analysis with extended time range
        logger.info("🔍 Running with extended 48-hour analysis to find more signals...")
        signals = await demo.run_historical_demo(symbols)
        
        if signals:
            logger.success(f"✅ Demo completed with {len(signals)} signals found!")
        else:
            logger.warning("⚠️ No signals found in the historical period")
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 