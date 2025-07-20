#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - COMPLETE VERSION
🎯 Signal generation + Trade execution + Beautiful UI + Comprehensive debugging
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
import time
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich import box

# Load environment variables
load_dotenv()

# Get credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/alpine_complete.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

# Rich console for beautiful UI
console = Console()

class AlpineCompleteBot:
    """🏔️ Complete Alpine Trading Bot with UI and Trade Execution"""
    
    def __init__(self):
        self.exchange = None
        self.signals = []
        self.trades = []
        self.positions = []
        self.running = True
        self.scan_count = 0
        self.total_signals = 0
        self.total_trades = 0
        self.win_count = 0
        self.loss_count = 0
        self.balance = 0.0
        self.available_pairs = []
        self.blacklisted_pairs = []
        
    async def initialize_exchange(self):
        """🔌 Initialize Bitget exchange with 25x leverage filtering"""
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
            
            # Get balance
            balance = await self.exchange.fetch_balance({'type': 'swap'})
            self.balance = float(balance.get('USDT', {}).get('free', 0))
            
            # Filter pairs for 25x leverage
            await self.filter_leverage_pairs()
            
            logger.success(f"✅ Exchange initialized - Balance: ${self.balance:.2f}")
            logger.info(f"📊 Available pairs: {len(self.available_pairs)}")
            logger.info(f"🚫 Blacklisted pairs: {len(self.blacklisted_pairs)}")
            
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            raise
    
    async def filter_leverage_pairs(self):
        """🔍 Filter pairs for 25x leverage support"""
        try:
            logger.info("🔍 Filtering pairs for 25x leverage support...")
            
            # Get all USDT pairs
            all_pairs = [symbol for symbol in self.exchange.symbols if ':USDT' in symbol]
            
            for pair in all_pairs:
                try:
                    # Check leverage tiers using the correct method
                    leverage_info = await self.exchange.fetch_market_leverage_tiers(pair)
                    
                    if leverage_info and len(leverage_info) > 0:
                        max_leverage = max([tier.get('maxLeverage', 0) for tier in leverage_info])
                        
                        if max_leverage >= 25:
                            self.available_pairs.append(pair)
                            logger.debug(f"✅ {pair} supports {max_leverage}x leverage")
                        else:
                            self.blacklisted_pairs.append(pair)
                            logger.debug(f"🚫 {pair} only supports {max_leverage}x leverage")
                    else:
                        # If no leverage info, assume it supports 25x+ and add it
                        self.available_pairs.append(pair)
                        logger.debug(f"✅ {pair} - No leverage info, assuming 25x+ support")
                        
                except Exception as e:
                    self.blacklisted_pairs.append(pair)
                    logger.debug(f"🚫 {pair} - Error checking leverage: {e}")
                    continue
            
            # Limit to top 50 pairs for performance
            self.available_pairs = self.available_pairs[:50]
            logger.success(f"✅ Filtered {len(self.available_pairs)} pairs with 25x+ leverage")
            
        except Exception as e:
            logger.error(f"❌ Leverage filtering failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            
            # Fallback: Add all USDT pairs if leverage filtering fails
            logger.info("🔄 Using fallback method - adding all USDT pairs...")
            all_pairs = [symbol for symbol in self.exchange.symbols if ':USDT' in symbol]
            self.available_pairs = all_pairs[:50]  # Limit to top 50
            logger.success(f"✅ Fallback: Added {len(self.available_pairs)} pairs")
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """📈 Calculate trend strength with detailed debugging"""
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
            
            # Volume analysis
            volume_sma = df['volume'].rolling(18).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
            
            logger.debug(f"📊 Volume Analysis - Current: {df['volume'].iloc[-1]:.0f}, SMA: {volume_sma.iloc[-1]:.0f}, Ratio: {volume_ratio:.2f}x")
            
            # Volume spike detection (EVEN LESS RESTRICTIVE FOR TESTING)
            volume_spike = volume_ratio >= 1.2  # Reduced from 1.5 to 1.2x
            
            if not volume_spike:
                logger.debug(f"📊 {symbol} - Volume spike too weak ({volume_ratio:.2f}x)")
                return None
            
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=16).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=16).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            logger.debug(f"📈 RSI Analysis - Current RSI: {current_rsi:.1f}")
            
            # Trend strength analysis
            trend_strength = self.calculate_trend_strength(df)
            
            # Signal conditions (EVEN LESS RESTRICTIVE FOR TESTING)
            if current_rsi < 45 and trend_strength > 0.3:  # BUY signal (was 40 and 0.5)
                side = 'buy'
                rsi_confidence = (45 - current_rsi) / 45 * 100
                logger.debug(f"📈 BUY Signal detected - RSI: {current_rsi:.1f}, Trend: {trend_strength:.2f}")
            elif current_rsi > 55 and trend_strength < -0.3:  # SELL signal (was 60 and -0.5)
                side = 'sell'
                rsi_confidence = (current_rsi - 55) / (100 - 55) * 100
                logger.debug(f"📉 SELL Signal detected - RSI: {current_rsi:.1f}, Trend: {trend_strength:.2f}")
            else:
                logger.debug(f"📊 {symbol} - No signal conditions met (RSI: {current_rsi:.1f}, Trend: {trend_strength:.2f})")
                return None
            
            # Volume confidence (LESS RESTRICTIVE)
            volume_confidence = min(100, (volume_ratio - 1) * 30) if volume_ratio > 1 else 0  # Reduced multiplier
            
            # Trend confidence (LESS RESTRICTIVE)
            trend_confidence = min(100, abs(trend_strength) * 20)  # Reduced multiplier
            
            # Combined confidence (LESS RESTRICTIVE)
            total_confidence = (
                volume_confidence * 0.40 +  # Reduced weight
                rsi_confidence * 0.40 +    # Increased weight
                trend_confidence * 0.20     # Same weight
            )
            
            # Minimum confidence threshold (EVEN LESS RESTRICTIVE FOR TESTING)
            if total_confidence < 40:  # Reduced from 50% to 40%
                logger.debug(f"📊 {symbol} - Confidence too low ({total_confidence:.1f}%)")
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
            
            logger.success(f"🎯 SIGNAL: {side.upper()} {symbol} | Confidence: {total_confidence:.0f}% | Volume: {volume_ratio:.1f}x | RSI: {current_rsi:.1f} | Trend: {trend_strength:.2f}")
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
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
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
            
            # Calculate position size (11% of balance, max $19)
            position_size_pct = 11.0
            max_trade_value = min(self.balance * (position_size_pct / 100), 19.0)
            target_notional = max(5.0, max_trade_value)
            quantity = target_notional / price
            
            logger.debug(f"💰 Trade Details - Balance: ${self.balance:.2f}, Trade Value: ${target_notional:.2f}, Quantity: {quantity:.6f}")
            
            # Check minimum amount
            trade_value = quantity * price
            if trade_value < 5.0:
                logger.warning(f"⚠️ Trade value too small: ${trade_value:.2f}")
                return False
            
            # Place order with 25x leverage
            order = await self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=quantity,
                params={
                    'leverage': 25,
                    'marginMode': 'cross'
                }
            )
            
            logger.success(f"✅ Order created: {order.get('id', 'N/A')}")
            
            # Wait for order to be processed
            await asyncio.sleep(1.0)
            
            # Check order status
            order_status = await self.exchange.fetch_order(order['id'], symbol)
            
            if order_status and order_status.get('status') in ['closed', 'filled']:
                fill_price = order_status.get('average') or order_status.get('price') or price
                
                # Calculate TP/SL prices
                if side == 'buy':
                    sl_price = fill_price * (1 - 1.25 / 100)  # 1.25% SL
                    tp_price = fill_price * (1 + 1.5 / 100)   # 1.5% TP
                else:
                    sl_price = fill_price * (1 + 1.25 / 100)  # 1.25% SL
                    tp_price = fill_price * (1 - 1.5 / 100)   # 1.5% TP
                
                # Place stop loss and take profit orders
                try:
                    sl_order = await self.exchange.create_order(
                        symbol=symbol,
                        type='stop',
                        side='sell' if side == 'buy' else 'buy',
                        amount=quantity,
                        price=sl_price,
                        params={
                            'stopPrice': sl_price,
                            'triggerPrice': sl_price,
                            'stopLoss': True
                        }
                    )
                    logger.success(f"✅ SL order placed: {sl_order.get('id', 'N/A')}")
                except Exception as sl_error:
                    logger.warning(f"⚠️ SL order failed: {sl_error}")
                
                try:
                    tp_order = await self.exchange.create_order(
                        symbol=symbol,
                        type='limit',
                        side='sell' if side == 'buy' else 'buy',
                        amount=quantity,
                        price=tp_price
                    )
                    logger.success(f"✅ TP order placed: {tp_order.get('id', 'N/A')}")
                except Exception as tp_error:
                    logger.warning(f"⚠️ TP order failed: {tp_error}")
                
                # Record trade
                trade = {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': fill_price,
                    'quantity': quantity,
                    'sl_price': sl_price,
                    'tp_price': tp_price,
                    'order_id': order['id'],
                    'sl_order_id': sl_order.get('id') if 'sl_order' in locals() else None,
                    'tp_order_id': tp_order.get('id') if 'tp_order' in locals() else None,
                    'timestamp': datetime.now(),
                    'status': 'open'
                }
                
                self.trades.append(trade)
                self.total_trades += 1
                
                logger.success(f"✅ Trade executed successfully: {side.upper()} {symbol} at ${fill_price:.4f}")
                return True
            else:
                logger.error(f"❌ Order not filled: {order_status}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return False
    
    async def scan_symbols(self, symbols: List[str]):
        """🔍 Scan symbols for signals with comprehensive logging"""
        try:
            logger.info(f"🔍 Scanning {len(symbols)} symbols for signals...")
            
            for symbol in symbols:
                try:
                    logger.debug(f"🔍 Analyzing {symbol}...")
                    
                    # Fetch historical data
                    df = await self.fetch_historical_data(symbol, hours_back=24)
                    
                    if len(df) < 100:
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
        """🎨 Create beautiful Mint/Black UI layout"""
        layout = Layout()
        
        # Header
        header = Panel(
            Align.center(
                Text("🏔️ ALPINE TRADING BOT", style="bold green", justify="center")
            ),
            style="on black",
            border_style="green"
        )
        
        # Status panel with proper win rate calculation
        win_rate = (self.win_count / max(1, self.total_trades) * 100) if self.total_trades > 0 else 0.0
        status_text = f"""
🔄 Status: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}
💰 Balance: ${self.balance:.2f}
📊 Scan Count: {self.scan_count}
🎯 Total Signals: {self.total_signals}
🚀 Total Trades: {self.total_trades}
📈 Win Rate: {win_rate:.1f}%
        """
        
        status_panel = Panel(
            Text(status_text, style="green"),
            title="📊 BOT STATUS",
            style="on black",
            border_style="green"
        )
        
        # Recent signals panel
        recent_signals = self.signals[-5:] if self.signals else []
        signals_text = ""
        
        for signal in recent_signals:
            signals_text += f"🎯 {signal['side'].upper()} {signal['symbol']} | {signal['confidence']:.0f}% | {signal['volume_ratio']:.1f}x\n"
        
        if not signals_text:
            signals_text = "📊 No signals yet..."
        
        signals_panel = Panel(
            Text(signals_text, style="green"),
            title="🎯 RECENT SIGNALS",
            style="on black",
            border_style="green"
        )
        
        # Recent trades panel
        recent_trades = self.trades[-5:] if self.trades else []
        trades_text = ""
        
        for trade in recent_trades:
            trades_text += f"🚀 {trade['side'].upper()} {trade['symbol']} | ${trade['entry_price']:.4f}\n"
        
        if not trades_text:
            trades_text = "📊 No trades yet..."
        
        trades_panel = Panel(
            Text(trades_text, style="green"),
            title="🚀 RECENT TRADES",
            style="on black",
            border_style="green"
        )
        
        # Available pairs panel
        pairs_text = f"📊 Available: {len(self.available_pairs)}\n🚫 Blacklisted: {len(self.blacklisted_pairs)}"
        
        pairs_panel = Panel(
            Text(pairs_text, style="green"),
            title="🔍 PAIRS STATUS",
            style="on black",
            border_style="green"
        )
        
        # Improved layout with better proportions
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
            
            with Live(self.create_ui_layout(), refresh_per_second=1, screen=True) as live:
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
                        logger.info("⏳ Waiting 30 seconds before next scan...")
                        await asyncio.sleep(30)
                        
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
        bot = AlpineCompleteBot()
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main()) 