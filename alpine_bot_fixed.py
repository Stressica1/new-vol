#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - Volume Anomaly Strategy v3.0
Dynamic Configuration System - No Hardcoded Values
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
import sys
from loguru import logger
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live

# DYNAMIC CONFIGURATION SYSTEM - NO HARDCODED VALUES
class DynamicConfig:
    """🎯 Dynamic configuration system - all values are configurable"""
    
    def __init__(self):
        # Exchange Configuration
        self.exchange_name = 'bitget'
        self.api_key = 'your_api_key_here'
        self.secret = 'your_secret_here'
        self.password = 'your_password_here'
        
        # Trading Parameters
        self.position_size_pct = 11.0  # Percentage of balance per trade
        self.min_notional = 125.0  # Minimum trade value in USDT
        self.leverage = 25  # Leverage for futures trading
        self.stop_loss_pct = 1.25  # Stop loss percentage
        self.take_profit_pct = 1.5  # Take profit percentage
        
        # Volume Explosion Detection
        self.volume_sma_period = 3  # Period for volume SMA
        self.volume_recent_period = 10  # Period for recent high
        self.volume_cumulative_period = 3  # Period for cumulative calculation
        self.volume_explosion_threshold = 1.0  # Minimum explosion ratio (lowered from 1.2)
        
        # RSI Configuration
        self.rsi_period = 14  # Standard RSI period
        self.rsi_buy_threshold = 60  # RSI threshold for buy signals (raised from 45)
        self.rsi_sell_threshold = 40  # RSI threshold for sell signals (lowered from 55)
        self.rsi_confidence_range = 20  # Range for RSI confidence calculation
        
        # Trend Analysis
        self.trend_sma_short = 8  # Short SMA period
        self.trend_sma_long = 21  # Long SMA period
        self.trend_buy_threshold = 0.05  # Minimum trend strength for buy (lowered from 0.15)
        self.trend_sell_threshold = -0.05  # Maximum trend strength for sell (raised from -0.15)
        self.trend_strength_multiplier = 200  # Multiplier for trend confidence calculation
        
        # Signal Confidence Weights
        self.volume_weight = 0.4  # Volume explosion weight
        self.rsi_weight = 0.4     # RSI weight
        self.trend_weight = 0.2   # Trend weight
        self.min_confidence = 30   # Minimum confidence threshold (lowered from 65)
        self.min_data_points = 100  # Minimum data points required
        
        # UI Configuration
        self.ui_refresh_rate = 1  # UI refresh rate per second
        self.scan_interval = 30  # Seconds between scans
        self.max_signals_display = 5  # Maximum signals to display
        self.max_trades_display = 5  # Maximum trades to display
        
        # Data Fetching
        self.timeframe = '5m'  # Default timeframe
        self.hours_back = 24  # Hours of historical data
        self.max_candles = 1000  # Maximum candles to fetch
        
        # Logging
        self.log_level = "INFO"
        self.log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}"
        
    def update_from_environment(self):
        """🔄 Update configuration from environment variables"""
        import os
        
        # Exchange settings
        if os.getenv('EXCHANGE_NAME'):
            self.exchange_name = os.getenv('EXCHANGE_NAME')
        if os.getenv('BITGET_API_KEY'):
            self.api_key = os.getenv('BITGET_API_KEY')
            logger.info(f"🔑 API Key loaded: {self.api_key[:10]}...")
        if os.getenv('BITGET_API_SECRET'):
            self.secret = os.getenv('BITGET_API_SECRET')
            logger.info(f"🔐 Secret loaded: {self.secret[:10]}...")
        if os.getenv('BITGET_API_PASSPHRASE'):
            self.password = os.getenv('BITGET_API_PASSPHRASE')
            logger.info(f"🔓 Passphrase loaded: {self.password[:5]}...")
            
        # Trading parameters
        if os.getenv('POSITION_SIZE_PCT'):
            self.position_size_pct = float(os.getenv('POSITION_SIZE_PCT'))
        if os.getenv('MIN_NOTIONAL'):
            self.min_notional = float(os.getenv('MIN_NOTIONAL'))
        if os.getenv('LEVERAGE'):
            self.leverage = int(os.getenv('LEVERAGE'))
        if os.getenv('STOP_LOSS_PCT'):
            self.stop_loss_pct = float(os.getenv('STOP_LOSS_PCT'))
        if os.getenv('TAKE_PROFIT_PCT'):
            self.take_profit_pct = float(os.getenv('TAKE_PROFIT_PCT'))
            
        # Volume detection
        if os.getenv('VOLUME_EXPLOSION_THRESHOLD'):
            self.volume_explosion_threshold = float(os.getenv('VOLUME_EXPLOSION_THRESHOLD'))
            
        # Signal thresholds
        if os.getenv('MIN_CONFIDENCE'):
            self.min_confidence = float(os.getenv('MIN_CONFIDENCE'))
            
        # Scan interval
        if os.getenv('SCAN_INTERVAL'):
            self.scan_interval = int(os.getenv('SCAN_INTERVAL'))

# Initialize dynamic configuration
config = DynamicConfig()
config.update_from_environment()  # Load from environment variables

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/alpine_fixed.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}")

# Rich console for beautiful UI
console = Console()

class AlpineFixedBot:
    """🏔️ Fixed Alpine Trading Bot with UI and Trade Execution"""
    
    def __init__(self):
        """🎯 Initialize Alpine Trading Bot with dynamic configuration"""
        self.exchange = None
        self.balance = 100.0  # Demo balance
        self.available_pairs = []
        self.signals = []
        self.trades = []
        self.scan_count = 0
        self.total_signals = 0
        self.total_trades = 0
        self.win_count = 0
        self.running = True
        
        # Demo mode - no API authentication required
        self.demo_mode = False
        logger.info("🔐 REAL TRADING MODE - API authentication required")
        
        # Setup logging
        logger.remove()
        logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
        logger.add("logs/alpine_fixed.log", rotation="10 MB", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}")
    
    async def initialize_exchange(self):
        """🔄 Initialize exchange connection"""
        try:
            if self.demo_mode:
                logger.info("🎮 DEMO MODE: Initializing exchange without authentication...")
                self.exchange = ccxt.bitget({
                    'sandbox': False,
                    'options': {
                        'defaultType': 'swap'
                    }
                })
                
                # Load markets without authentication
                logger.info("🔄 Loading all available markets from Bitget...")
                markets = await self.exchange.load_markets()
                logger.info(f"📊 Loaded {len(markets)} total markets from Bitget")
                
                usdt_pairs = []
                total_markets = len(markets)
                
                for symbol, market in markets.items():
                    # Filter for USDT perpetual futures
                    if (market['quote'] == 'USDT' and 
                        market['type'] == 'swap' and 
                        market['active'] and
                        'USDT:USDT' in symbol):
                        usdt_pairs.append(symbol)
                
                if not usdt_pairs:
                    raise Exception("No USDT perpetual pairs found")
                
                logger.success(f"✅ Found {len(usdt_pairs)} USDT perpetual pairs out of {total_markets} total markets")
                self.available_pairs = usdt_pairs
                logger.success(f"✅ Loaded {len(self.available_pairs)} USDT pairs from Bitget")
                logger.success(f"✅ DEMO MODE: Balance set to ${self.balance:.2f}")
                
            else:
                # Real trading mode with authentication
                self.exchange = ccxt.bitget({
                    'apiKey': config.api_key,
                    'secret': config.secret,
                    'password': config.password,
                    'sandbox': False,
                    'options': {
                        'defaultType': 'swap'
                    }
                })
                
                # Test connection
                await self.exchange.load_markets()
                
                # Get balance
                balance = await self.exchange.fetch_balance({'type': 'swap'})
                self.balance = float(balance.get('USDT', {}).get('free', 0))
                
                # Load ALL available USDT pairs from Bitget
                try:
                    logger.info("🔄 Loading all available markets from Bitget...")
                    markets = await self.exchange.load_markets()
                    logger.info(f"📊 Loaded {len(markets)} total markets from Bitget")
                    
                    usdt_pairs = []
                    total_markets = len(markets)
                    
                    for symbol, market in markets.items():
                        # Filter for USDT perpetual futures
                        if (market['quote'] == 'USDT' and 
                            market['type'] == 'swap' and 
                            market['active'] and
                            'USDT:USDT' in symbol):
                            usdt_pairs.append(symbol)
                    
                    if not usdt_pairs:
                        raise Exception("No USDT perpetual pairs found")
                    
                    logger.success(f"✅ Found {len(usdt_pairs)} USDT perpetual pairs out of {total_markets} total markets")
                    self.available_pairs = usdt_pairs
                    logger.success(f"✅ Loaded {len(self.available_pairs)} USDT pairs from Bitget")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load markets from Bitget: {e}")
                    logger.error(f"🔍 Traceback: {traceback.format_exc()}")
                    logger.error("❌ Cannot continue without market data. Please check your connection and API credentials.")
                    raise Exception(f"Failed to load markets: {e}")
            
            logger.success(f"✅ Exchange initialized - Balance: ${self.balance:.2f}")
            logger.info(f"📊 Available pairs: {len(self.available_pairs)}")
            
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            raise
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """📈 Calculate trend strength with detailed debugging"""
        try:
            # Calculate SMAs
            sma_short = df['close'].rolling(config.trend_sma_short).mean()
            sma_long = df['close'].rolling(config.trend_sma_long).mean()
            
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
            
            logger.debug(f"📊 Trend Analysis - Direction: {trend_direction}, Strength: {trend_strength:.2f}%, Score: {trend_score:.2f}")
            
            return trend_score
            
        except Exception as e:
            logger.warning(f"⚠️ Trend strength calculation error: {e}")
            logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
            return 0.0
    
    async def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """🎯 Generate trading signal with comprehensive debugging"""
        try:
            logger.debug(f"🔍 Analyzing {symbol} for signals...")
            
            # Volume analysis - VOLUME EXPLOSION DETECTION
            # Use 3-period SMA for immediate explosion detection
            volume_sma = df['volume'].rolling(config.volume_sma_period).mean()
            current_volume = df['volume'].iloc[-1]
            
            # Calculate volume explosion ratio
            if volume_sma.iloc[-1] > 0:
                volume_ratio = current_volume / volume_sma.iloc[-1]
            else:
                volume_ratio = 1.0
            
            # Volume explosion detection using multiple timeframes
            # 1. Immediate explosion (current vs 3-period SMA)
            immediate_explosion = volume_ratio
            
            # 2. Recent explosion (current vs 10-period high)
            recent_high = df['volume'].rolling(config.volume_recent_period).max().iloc[-1]
            recent_explosion = current_volume / recent_high if recent_high > 0 else 1.0
            
            # 3. Cumulative explosion (sum of last 3 periods vs 10-period average)
            recent_volume_sum = df['volume'].tail(config.volume_cumulative_period).sum()
            avg_volume_10 = df['volume'].rolling(config.volume_recent_period).mean().iloc[-1]
            cumulative_explosion = recent_volume_sum / (avg_volume_10 * config.volume_cumulative_period) if avg_volume_10 > 0 else 1.0
            
            # Use the highest explosion ratio
            final_volume_ratio = max(immediate_explosion, recent_explosion, cumulative_explosion)
            
            # RSI calculation (FIXED - Standard 14-period)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=config.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=config.rsi_period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Trend strength analysis
            trend_strength = self.calculate_trend_strength(df)
            
            logger.info(f"🔍 ANALYZING {symbol}:")
            logger.info(f"   📊 Volume: {df['volume'].iloc[-1]:.0f} vs SMA: {volume_sma.iloc[-1]:.0f} = {volume_ratio:.2f}x")
            logger.info(f"   💥 Volume Explosion: {final_volume_ratio:.2f}x (Immediate: {immediate_explosion:.2f}x, Recent: {recent_explosion:.2f}x, Cumulative: {cumulative_explosion:.2f}x)")
            logger.info(f"   📈 Price: ${df['close'].iloc[-1]:.4f}")
            logger.info(f"   🎯 RSI: {current_rsi:.1f}")
            logger.info(f"   📊 Trend Strength: {trend_strength:.2f}")
            
            # Volume explosion detection (REAL EXPLOSION THRESHOLD)
            volume_explosion = final_volume_ratio >= config.volume_explosion_threshold  # Real volume explosion threshold
            
            if not volume_explosion:
                logger.warning(f"❌ {symbol} - Volume explosion too weak ({final_volume_ratio:.2f}x < {config.volume_explosion_threshold:.2f}x)")
                return None
            
            # Signal conditions (LESS RESTRICTIVE FOR TESTING)
            if current_rsi < config.rsi_buy_threshold and trend_strength > config.trend_buy_threshold:  # BUY signal (less restrictive)
                side = 'buy'
                rsi_confidence = max(0, (config.rsi_buy_threshold - current_rsi) / config.rsi_confidence_range * 100)  # Better scaling: 100% at RSI 20, 50% at RSI 30
                logger.info(f"   ✅ BUY Signal - RSI: {current_rsi:.1f} < {config.rsi_buy_threshold:.1f}, Trend: {trend_strength:.2f} > {config.trend_buy_threshold:.1f}")
            elif current_rsi > config.rsi_sell_threshold and trend_strength < config.trend_sell_threshold:  # SELL signal (less restrictive)
                side = 'sell'
                rsi_confidence = max(0, (current_rsi - config.rsi_sell_threshold) / config.rsi_confidence_range * 100)  # Better scaling: 100% at RSI 80, 50% at RSI 70
                logger.info(f"   ✅ SELL Signal - RSI: {current_rsi:.1f} > {config.rsi_sell_threshold:.1f}, Trend: {trend_strength:.2f} < {config.trend_sell_threshold:.1f}")
            else:
                logger.warning(f"❌ {symbol} - RSI conditions not met (RSI: {current_rsi:.1f}, Trend: {trend_strength:.2f})")
                return None
            
            # Volume confidence (EXPLOSION-BASED CALCULATION)
            if final_volume_ratio >= config.volume_explosion_threshold:
                volume_confidence = min(100, (final_volume_ratio - config.volume_explosion_threshold) / config.volume_explosion_threshold * 100)  # 100% for 5x explosion, 50% for 3.75x
            else:
                volume_confidence = 0  # No volume explosion
            
            # Trend confidence (FIXED CALCULATION - PROPER SCALING)
            trend_confidence = min(100, abs(trend_strength) * config.trend_strength_multiplier)  # Scale up trend strength for better range
            
            # Combined confidence (PROPER WEIGHTING)
            total_confidence = (
                volume_confidence * config.volume_weight +  # Volume weight
                rsi_confidence * config.rsi_weight +    # RSI weight (most important)
                trend_confidence * config.trend_weight     # Trend weight
            )
            
            logger.info(f"   📊 Confidence Breakdown:")
            logger.info(f"      Volume: {volume_confidence:.1f}% ({config.volume_weight*100:.0f}% weight)")
            logger.info(f"      RSI: {rsi_confidence:.1f}% ({config.rsi_weight*100:.0f}% weight)")
            logger.info(f"      Trend: {trend_confidence:.1f}% ({config.trend_weight*100:.0f}% weight)")
            logger.info(f"      TOTAL: {total_confidence:.1f}%")
            
            # Minimum confidence threshold (LOWER FOR TESTING)
            if total_confidence < config.min_confidence:  # Lower threshold for testing
                logger.warning(f"❌ {symbol} - Confidence too low ({total_confidence:.1f}% < {config.min_confidence:.1f}%)")
                return None
            
            signal = {
                'symbol': symbol,
                'side': side,
                'price': df['close'].iloc[-1],
                'volume_ratio': final_volume_ratio,
                'rsi': current_rsi,
                'trend_strength': trend_strength,
                'confidence': total_confidence,
                'volume_confidence': volume_confidence,
                'rsi_confidence': rsi_confidence,
                'trend_confidence': trend_confidence,
                'timestamp': datetime.now()
            }
            
            logger.success(f"🎯 SIGNAL: {side.upper()} {symbol} | Confidence: {total_confidence:.0f}% | Volume: {final_volume_ratio:.1f}x | RSI: {current_rsi:.1f} | Trend: {trend_strength:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error for {symbol}: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return None
    
    async def fetch_historical_data(self, symbol: str, timeframe: str = '5m', 
                                  hours_back: int = 24) -> pd.DataFrame:
        """📊 Fetch historical data with error handling"""
        try:
            # Calculate timestamps
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Convert to milliseconds
            since = int(start_time.timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=config.max_candles)
            
            # DEBUG: Check raw OHLCV structure
            if ohlcv and len(ohlcv) > 0:
                logger.debug(f"🔍 Raw OHLCV sample for {symbol}: {ohlcv[0]}")
                logger.debug(f"🔍 OHLCV structure: {len(ohlcv[0])} elements")
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # DEBUG: Check volume data
            logger.debug(f"🔍 Volume data sample for {symbol}: {df['volume'].head(3).tolist()}")
            logger.debug(f"🔍 Volume data type: {df['volume'].dtype}")
            
            logger.debug(f"📊 Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Data fetch error for {symbol}: {e}")
            logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
            return pd.DataFrame()
    
    async def execute_trade(self, signal: Dict) -> bool:
        """🚀 Execute trade with comprehensive error handling"""
        try:
            symbol = signal['symbol']
            side = signal['side']
            price = signal['price']
            
            logger.info(f"🚀 Executing {side.upper()} trade for {symbol} at ${price:.4f}")
            
            if self.demo_mode:
                # Demo mode - simulate trade execution
                logger.info("🎮 DEMO MODE: Simulating trade execution...")
                
                # Simulate trade success
                trade_info = {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': price,
                    'quantity': 1.0,  # Demo quantity
                    'timestamp': datetime.now(),
                    'demo': True
                }
                
                self.trades.append(trade_info)
                self.total_trades += 1
                
                logger.success(f"🎮 DEMO: {side.upper()} trade executed for {symbol} at ${price:.4f}")
                logger.info(f"🎮 DEMO: Total trades: {self.total_trades}")
                
                return True
                
            else:
                # Real trading mode
                # Calculate position size (11% of balance, minimum $125 USDT)
                position_size_pct = config.position_size_pct
                trade_value = self.balance * (position_size_pct / 100)  # 11% of balance
                target_notional = max(config.min_notional, trade_value)  # Minimum $125 USDT
                quantity = target_notional / price
                
                logger.info(f"💰 Trade calculation:")
                logger.info(f"   Balance: ${self.balance:.2f}")
                logger.info(f"   Position size: {position_size_pct}% = ${trade_value:.2f}")
                logger.info(f"   Target notional: ${target_notional:.2f}")
                logger.info(f"   Quantity: {quantity:.4f}")
                
                # Check minimum amount
                trade_value = quantity * price
                if trade_value < config.min_notional:
                    logger.warning(f"⚠️ Trade value too small: ${trade_value:.2f} (minimum {config.min_notional:.2f})")
                    return False
                
                # Place order with 25x leverage
                order = await self.exchange.create_order(
                    symbol=symbol,
                    type='market',
                    side=side,
                    amount=quantity,
                    params={
                        'leverage': config.leverage,
                        'marginMode': 'cross'
                    }
                )
                
                logger.success(f"✅ Order placed: {order['id']}")
                
                # Get fill price
                fill_price = float(order['price']) if order['price'] else price
                
                # Calculate TP/SL prices
                if side == 'buy':
                    sl_price = fill_price * (1 - config.stop_loss_pct / 100)  # 1.25% SL
                    tp_price = fill_price * (1 + config.take_profit_pct / 100)   # 1.5% TP
                else:
                    sl_price = fill_price * (1 + config.stop_loss_pct / 100)  # 1.25% SL
                    tp_price = fill_price * (1 - config.take_profit_pct / 100)   # 1.5% TP
                
                # Place stop loss and take profit orders
                sl_order = await self.exchange.create_order(
                    symbol=symbol,
                    type='stop',
                    side='sell' if side == 'buy' else 'buy',
                    amount=quantity,
                    price=sl_price,
                    params={'stopPrice': sl_price}
                )
                
                tp_order = await self.exchange.create_order(
                    symbol=symbol,
                    type='limit',
                    side='sell' if side == 'buy' else 'buy',
                    amount=quantity,
                    price=tp_price
                )
                
                logger.success(f"✅ SL/TP orders placed: SL=${sl_price:.4f}, TP=${tp_price:.4f}")
                
                # Record trade
                trade_info = {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': fill_price,
                    'quantity': quantity,
                    'sl_price': sl_price,
                    'tp_price': tp_price,
                    'timestamp': datetime.now()
                }
                
                self.trades.append(trade_info)
                self.total_trades += 1
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return False
    
    async def scan_symbols(self, symbols: List[str]):
        """🔍 Scan symbols for signals with comprehensive logging"""
        try:
            logger.info(f"🔍 Scanning {len(symbols)} symbols for signals...")
            
            for symbol_count, symbol in enumerate(symbols, 1):
                try:
                    logger.info(f"🔍 [{symbol_count}/{len(symbols)}] Analyzing {symbol}...")
                    
                    # Fetch historical data
                    df = await self.fetch_historical_data(symbol, hours_back=config.hours_back)
                    
                    if len(df) < config.min_data_points:
                        logger.warning(f"⚠️ Insufficient data for {symbol}: {len(df)} candles")
                        continue
                    
                    # Generate signal
                    signal = await self.generate_signal(df, symbol)
                    
                    if signal:
                        self.signals.append(signal)
                        self.total_signals += 1
                        
                        logger.success(f"✅ SIGNAL FOUND: {symbol}")
                        logger.info(f"   📈 Side: {signal['side'].upper()}")
                        logger.info(f"   💰 Price: ${signal['price']:.4f}")
                        logger.info(f"   🎯 Confidence: {signal['confidence']:.1f}%")
                        logger.info(f"   📊 Volume Ratio: {signal['volume_ratio']:.2f}x")
                        logger.info(f"   📈 RSI: {signal['rsi']:.1f}")
                        logger.info(f"   📊 Trend Strength: {signal['trend_strength']:.2f}")
                        logger.info("   " + "="*50)
                        
                        # Execute trade
                        trade_success = await self.execute_trade(signal)
                        if trade_success:
                            logger.success(f"🚀 Trade executed for {symbol}")
                        else:
                            logger.warning(f"⚠️ Trade execution failed for {symbol}")
                    else:
                        logger.debug(f"📊 No signal for {symbol}")
                
                except Exception as e:
                    logger.warning(f"⚠️ Error scanning {symbol}: {e}")
                    logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Symbol scanning error: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
    
    def create_ui_layout(self) -> Layout:
        """🎨 Create beautiful Dark Green/Black UI layout"""
        layout = Layout()
        
        # Header with enhanced styling
        header = Panel(
            Align.center(
                Text("🏔️ ALPINE TRADING BOT\nVolume Anomaly Strategy v3.0", style="bold #228B22", justify="center")
            ),
            style="on black",
            border_style="#228B22",
            padding=(1, 2)
        )
        
        # Status panel with enhanced styling
        status_text = f"""
🔄 Status: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}
💰 Balance: ${self.balance:.2f}
📊 Scan Count: {self.scan_count}
🎯 Total Signals: {self.total_signals}
🚀 Total Trades: {self.total_trades}
📈 Win Rate: {(self.win_count / max(1, self.total_trades) * 100):.1f}%
        """
        
        status_panel = Panel(
            Text(status_text, style="#228B22"),
            title="📊 BOT STATUS",
            style="on black",
            border_style="#228B22",
            padding=(1, 1),
            subtitle="Real-time monitoring"
        )
        
        # Recent signals panel with enhanced styling
        recent_signals = self.signals[-config.max_signals_display:] if self.signals else []
        signals_text = ""
        
        for signal in recent_signals:
            signals_text += f"🎯 {signal['side'].upper()} {signal['symbol']} | {signal['confidence']:.0f}% | {signal['volume_ratio']:.1f}x\n"
        
        if not signals_text:
            signals_text = "📊 No signals yet..."
        
        signals_panel = Panel(
            Text(signals_text, style="#228B22"),
            title="🎯 RECENT SIGNALS",
            style="on black",
            border_style="#228B22",
            padding=(1, 1),
            subtitle="Live signal detection"
        )
        
        # Recent trades panel with enhanced styling
        recent_trades = self.trades[-config.max_trades_display:] if self.trades else []
        trades_text = ""
        
        for trade in recent_trades:
            trades_text += f"🚀 {trade['side'].upper()} {trade['symbol']} | ${trade['entry_price']:.4f}\n"
        
        if not trades_text:
            trades_text = "📊 No trades yet..."
        
        trades_panel = Panel(
            Text(trades_text, style="#228B22"),
            title="🚀 RECENT TRADES",
            style="on black",
            border_style="#228B22",
            padding=(1, 1),
            subtitle="Trade execution log"
        )
        
        # Available pairs panel with enhanced styling
        pairs_text = f"📊 Available: {len(self.available_pairs)}"
        
        pairs_panel = Panel(
            Text(pairs_text, style="#228B22"),
            title="🔍 PAIRS STATUS",
            style="on black",
            border_style="#228B22",
            padding=(1, 1),
            subtitle="Market coverage"
        )
        
        # Enhanced layout with better proportions
        layout.split_column(
            Layout(header, size=3),
            Layout(name="main")
        )
        
        layout["main"].split_row(
            Layout(status_panel, size=35),
            Layout(name="right")
        )
        
        layout["right"].split_column(
            Layout(signals_panel, size=10),
            Layout(trades_panel, size=10),
            Layout(pairs_panel, size=5)
        )
        
        return layout
    
    async def trading_loop(self):
        """🔄 Main trading loop with UI updates"""
        try:
            logger.info("🚀 Starting Alpine Trading Bot with UI...")
            
            scan_count = 0
            
            with Live(self.create_ui_layout(), refresh_per_second=config.ui_refresh_rate, screen=True) as live:
                while self.running:
                    try:
                        scan_count += 1
                        self.scan_count = scan_count
                        
                        logger.info(f"📊 Scan #{scan_count} - Scanning {len(self.available_pairs)} symbols...")
                        
                        # Scan for signals
                        await self.scan_symbols(self.available_pairs)
                        
                        # Update UI
                        live.update(self.create_ui_layout())
                        
                        # Summary
                        logger.info(f"📊 Scan #{scan_count} Complete")
                        logger.info(f"🎯 Total Signals Found: {len(self.signals)}")
                        logger.info(f"📈 Buy Signals: {len([s for s in self.signals if s['side'] == 'buy'])}")
                        logger.info(f"📉 Sell Signals: {len([s for s in self.signals if s['side'] == 'sell'])}")
                        
                        # Wait before next scan
                        logger.info(f"⏳ Waiting {config.scan_interval} seconds before next scan...")
                        await asyncio.sleep(config.scan_interval)
                        
                    except Exception as e:
                        logger.error(f"❌ Trading loop error: {e}")
                        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            logger.error(f"❌ Trading loop failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
    
    async def start(self):
        """🚀 Start the bot"""
        try:
            # Initialize exchange
            await self.initialize_exchange()
            
            # Start trading loop
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        finally:
            if self.exchange:
                await self.exchange.close()

async def main():
    """🎯 Main function"""
    try:
        bot = AlpineFixedBot()
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main()) 