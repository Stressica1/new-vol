#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SIMPLE RUNNER
🎯 Run the Alpine bot with signal generation
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

class SimpleAlpineBot:
    """🎯 Simple Alpine bot with signal generation"""
    
    def __init__(self):
        self.exchange = None
        self.signals = []
        self.running = True
        
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
            logger.success("✅ Exchange initialized successfully")
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            raise
    
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
    
    async def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """🎯 Generate trading signal WITHOUT pullback detection"""
        try:
            # Volume analysis
            volume_sma = df['volume'].rolling(18).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
            
            # Volume spike detection
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
            
            # Minimum confidence threshold
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
    
    async def scan_symbols(self, symbols: List[str]):
        """🔍 Scan symbols for signals"""
        try:
            logger.info(f"🔍 Scanning {len(symbols)} symbols for signals...")
            
            for symbol in symbols:
                try:
                    # Fetch historical data
                    df = await self.fetch_historical_data(symbol, hours_back=24)
                    
                    if len(df) < 100:
                        logger.warning(f"⚠️ Insufficient data for {symbol}: {len(df)} candles")
                        continue
                    
                    # Generate signal
                    signal = await self.generate_signal(df, symbol)
                    
                    if signal:
                        self.signals.append(signal)
                        logger.success(f"✅ SIGNAL FOUND: {symbol}")
                        logger.info(f"   📈 Side: {signal['side'].upper()}")
                        logger.info(f"   💰 Price: ${signal['price']:.4f}")
                        logger.info(f"   🎯 Confidence: {signal['confidence']:.1f}%")
                        logger.info(f"   📊 Volume Ratio: {signal['volume_ratio']:.2f}x")
                        logger.info(f"   📈 RSI: {signal['rsi']:.1f}")
                        logger.info(f"   📊 Trend Strength: {signal['trend_strength']:.2f}")
                        logger.info("   " + "="*50)
                    else:
                        logger.debug(f"📊 No signal for {symbol}")
                
                except Exception as e:
                    logger.warning(f"⚠️ Error scanning {symbol}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Symbol scanning error: {e}")
    
    async def trading_loop(self):
        """🔄 Main trading loop"""
        try:
            logger.info("🚀 Starting Alpine Trading Bot...")
            
            # Define symbols to scan
            symbols = [
                'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'BNB/USDT:USDT',
                'ADA/USDT:USDT', 'DOT/USDT:USDT', 'AVAX/USDT:USDT', 'LINK/USDT:USDT',
                'UNI/USDT:USDT', 'ATOM/USDT:USDT', 'LTC/USDT:USDT', 'XRP/USDT:USDT'
            ]
            
            scan_count = 0
            
            while self.running:
                try:
                    scan_count += 1
                    logger.info(f"📊 Scan #{scan_count} - Scanning {len(symbols)} symbols...")
                    
                    # Scan for signals
                    await self.scan_symbols(symbols)
                    
                    # Summary
                    logger.info(f"📊 Scan #{scan_count} Complete")
                    logger.info(f"🎯 Total Signals Found: {len(self.signals)}")
                    logger.info(f"📈 Buy Signals: {len([s for s in self.signals if s['side'] == 'buy'])}")
                    logger.info(f"📉 Sell Signals: {len([s for s in self.signals if s['side'] == 'sell'])}")
                    
                    # Wait before next scan
                    logger.info("⏳ Waiting 30 seconds before next scan...")
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    logger.error(f"❌ Trading loop error: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"❌ Trading loop failed: {e}")
    
    async def start(self):
        """🚀 Start the bot"""
        try:
            # Initialize exchange
            await self.initialize_exchange()
            
            # Start trading loop
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
        finally:
            if self.exchange:
                await self.exchange.close()

async def main():
    """🎯 Main function"""
    try:
        bot = SimpleAlpineBot()
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 