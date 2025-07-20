#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SUPERTREND GOLDEN ZONE INTEGRATION
🎯 Integrates Supertrend Golden Zone strategy with existing Alpine system
🚀 Real-time trading with optimized parameters
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from loguru import logger
import traceback
from supertrend_golden_zone_strategy import (
    SupertrendGoldenZoneStrategy, 
    StrategyConfig,
    SupertrendCalculator,
    GoldenZoneCalculator
)
from dotenv import load_dotenv
from typing import List, Dict, Optional
import sys
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/supertrend_integration.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

# Get credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

@dataclass
class IntegratedPosition:
    """📊 Integrated position tracking"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    timestamp: datetime
    order_id: Optional[str] = None
    sl_order_id: Optional[str] = None
    tp_order_id: Optional[str] = None
    strategy: str = "SupertrendGoldenZone"

class SupertrendGoldenZoneIntegration:
    """🎯 Integration of Supertrend Golden Zone strategy with Alpine system"""
    
    def __init__(self):
        self.exchange = None
        self.strategy = None
        self.config = None
        self.positions = []
        self.signals = []
        self.balance = 0.0
        self.total_pnl = 0.0
        self.win_count = 0
        self.loss_count = 0
        self.is_running = False
        
    async def initialize(self, config: StrategyConfig = None):
        """🔌 Initialize the integration system"""
        try:
            # Initialize exchange
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
            
            # Initialize strategy
            if config is None:
                # Use optimized parameters from backtesting
                self.config = StrategyConfig(
                    supertrend_period=10,
                    supertrend_multiplier=3.0,
                    supertrend_atr_period=14,
                    golden_zone_start=0.72,
                    golden_zone_end=0.88,
                    zone_tolerance=0.02,
                    min_confidence=75.0,
                    min_volume_spike=1.5,
                    min_rsi=30.0,
                    max_rsi=70.0,
                    stop_loss_pct=1.25,
                    take_profit_pct=2.0,
                    max_positions=5,
                    position_size_pct=11.0
                )
            else:
                self.config = config
            
            self.strategy = SupertrendGoldenZoneStrategy(self.config)
            await self.strategy.initialize_exchange()
            
            logger.success("✅ Supertrend Golden Zone integration initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            traceback.print_exc()
            raise
    
    async def get_balance(self) -> float:
        """💰 Get account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            self.balance = usdt_balance
            return usdt_balance
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return 0.0
    
    async def get_positions(self) -> List[IntegratedPosition]:
        """📊 Get current positions"""
        try:
            positions = await self.exchange.fetch_positions()
            integrated_positions = []
            
            for pos in positions:
                if pos['size'] > 0:
                    integrated_pos = IntegratedPosition(
                        symbol=pos['symbol'],
                        side=pos['side'],
                        size=pos['size'],
                        entry_price=pos['entryPrice'],
                        current_price=pos['markPrice'],
                        pnl=pos['unrealizedPnl'],
                        pnl_percent=pos['percentage'],
                        timestamp=datetime.now(),
                        order_id=pos.get('id'),
                        strategy="SupertrendGoldenZone"
                    )
                    integrated_positions.append(integrated_pos)
            
            self.positions = integrated_positions
            return integrated_positions
            
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    async def execute_trade(self, signal: Dict) -> bool:
        """🎯 Execute trade based on signal"""
        try:
            if not signal or not signal.get('side'):
                return False
            
            symbol = signal['symbol']
            side = signal['side']
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            
            # Calculate position size
            balance = await self.get_balance()
            position_size_usdt = balance * (self.config.position_size_pct / 100)
            position_size = position_size_usdt / entry_price
            
            # Place market order
            order = await self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=position_size,
                params={
                    'leverage': 25,  # 25x leverage as per requirements
                    'marginMode': 'cross'
                }
            )
            
            # Place stop loss order
            sl_order = await self.exchange.create_order(
                symbol=symbol,
                type='stop',
                side='sell' if side == 'buy' else 'buy',
                amount=position_size,
                price=stop_loss,
                params={
                    'stopPrice': stop_loss,
                    'leverage': 25
                }
            )
            
            # Place take profit order
            tp_order = await self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='sell' if side == 'buy' else 'buy',
                amount=position_size,
                price=take_profit,
                params={
                    'leverage': 25
                }
            )
            
            logger.success(f"✅ Trade executed: {symbol} {side} at {entry_price}")
            logger.info(f"📊 Stop Loss: {stop_loss}, Take Profit: {take_profit}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
            return False
    
    async def scan_markets(self) -> List[Dict]:
        """📊 Scan markets for trading opportunities"""
        try:
            markets = await self.exchange.load_markets()
            symbols = [
                symbol for symbol in markets.keys() 
                if '/USDT' in symbol and 'SWAP' in markets[symbol]['type']
            ]
            
            signals = []
            
            for symbol in symbols[:20]:  # Scan top 20 symbols
                try:
                    # Get recent data
                    ohlcv = await self.exchange.fetch_ohlcv(symbol, '5m', limit=200)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Generate signal
                    signal = self.strategy.generate_signal(df)
                    signal['symbol'] = symbol
                    
                    if signal['side'] and signal['confidence'] >= self.config.min_confidence:
                        signals.append(signal)
                        logger.info(f"🎯 Signal found: {symbol} {signal['side']} (Confidence: {signal['confidence']:.1f}%)")
                
                except Exception as e:
                    logger.warning(f"⚠️ Error scanning {symbol}: {e}")
                    continue
            
            self.signals = signals
            return signals
            
        except Exception as e:
            logger.error(f"❌ Market scanning error: {e}")
            return []
    
    async def check_capital_limits(self) -> bool:
        """💰 Check capital management limits"""
        try:
            balance = await self.get_balance()
            positions = await self.get_positions()
            
            # Calculate capital in play
            total_position_value = sum(abs(pos.size * pos.current_price) for pos in positions)
            capital_in_play_pct = (total_position_value / balance * 100) if balance > 0 else 0
            
            # Check limits
            if capital_in_play_pct > 68.0:  # Max 68% capital in play
                logger.warning(f"⚠️ Capital limit reached: {capital_in_play_pct:.1f}%")
                return False
            
            if len(positions) >= self.config.max_positions:
                logger.warning(f"⚠️ Position limit reached: {len(positions)}/{self.config.max_positions}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Capital limit check error: {e}")
            return False
    
    async def trading_loop(self):
        """🔄 Main trading loop"""
        try:
            logger.info("🚀 Starting Supertrend Golden Zone trading loop")
            self.is_running = True
            
            while self.is_running:
                try:
                    # Check capital limits
                    if not await self.check_capital_limits():
                        logger.info("⏳ Waiting for capital limits to reset...")
                        await asyncio.sleep(60)
                        continue
                    
                    # Scan markets
                    signals = await self.scan_markets()
                    
                    # Execute trades for valid signals
                    for signal in signals:
                        if await self.check_capital_limits():
                            success = await self.execute_trade(signal)
                            if success:
                                logger.success(f"✅ Trade executed: {signal['symbol']} {signal['side']}")
                            await asyncio.sleep(2)  # Rate limiting
                    
                    # Update positions and PnL
                    await self.get_positions()
                    await self.get_balance()
                    
                    # Log status
                    logger.info(f"📊 Status - Balance: ${self.balance:.2f}, Positions: {len(self.positions)}, Signals: {len(signals)}")
                    
                    # Wait before next iteration
                    await asyncio.sleep(30)  # 30-second intervals
                    
                except Exception as e:
                    logger.error(f"❌ Trading loop error: {e}")
                    await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ Trading loop fatal error: {e}")
            traceback.print_exc()
    
    def stop_trading(self):
        """🛑 Stop trading loop"""
        self.is_running = False
        logger.info("🛑 Trading loop stopped")
    
    async def close_all_positions(self):
        """🛑 Close all open positions"""
        try:
            positions = await self.get_positions()
            
            for position in positions:
                try:
                    # Close position
                    await self.exchange.create_order(
                        symbol=position.symbol,
                        type='market',
                        side='sell' if position.side == 'buy' else 'buy',
                        amount=position.size,
                        params={'leverage': 25}
                    )
                    logger.success(f"✅ Closed position: {position.symbol}")
                    
                except Exception as e:
                    logger.error(f"❌ Error closing position {position.symbol}: {e}")
            
            logger.success("✅ All positions closed")
            
        except Exception as e:
            logger.error(f"❌ Error closing positions: {e}")
    
    async def get_performance_summary(self) -> Dict:
        """📊 Get performance summary"""
        try:
            balance = await self.get_balance()
            positions = await self.get_positions()
            
            total_pnl = sum(pos.pnl for pos in positions)
            
            return {
                'balance': balance,
                'total_pnl': total_pnl,
                'positions_count': len(positions),
                'win_count': self.win_count,
                'loss_count': self.loss_count,
                'total_trades': self.win_count + self.loss_count,
                'win_rate': (self.win_count / (self.win_count + self.loss_count) * 100) if (self.win_count + self.loss_count) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {}
    
    async def close_connection(self):
        """🔌 Close exchange connection"""
        try:
            if self.exchange:
                await self.exchange.close()
            logger.success("✅ Exchange connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing connection: {e}")

async def main():
    """🚀 Main function to run Supertrend Golden Zone integration"""
    try:
        logger.info("🏔️ Starting Supertrend Golden Zone Integration")
        
        # Initialize integration
        integration = SupertrendGoldenZoneIntegration()
        await integration.initialize()
        
        # Get initial balance
        balance = await integration.get_balance()
        logger.info(f"💰 Initial balance: ${balance:.2f}")
        
        # Start trading loop
        trading_task = asyncio.create_task(integration.trading_loop())
        
        try:
            # Run for specified time or until interrupted
            await asyncio.sleep(3600)  # Run for 1 hour
            
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal")
        
        finally:
            # Stop trading
            integration.stop_trading()
            await trading_task
            
            # Get final performance
            performance = await integration.get_performance_summary()
            logger.info("📊 Final Performance:")
            logger.info(f"💰 Final Balance: ${performance.get('balance', 0):.2f}")
            logger.info(f"📈 Total PnL: ${performance.get('total_pnl', 0):.2f}")
            logger.info(f"🎯 Win Rate: {performance.get('win_rate', 0):.1f}%")
            logger.info(f"📊 Total Trades: {performance.get('total_trades', 0)}")
            
            # Close connection
            await integration.close_connection()
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 