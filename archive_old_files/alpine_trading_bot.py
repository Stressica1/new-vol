#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Unified Production System
🚀 Real-time futures trading with 25x leverage focus
🎯 Mint-on-Black UI theme with visual feedback
"""

import asyncio
import ccxt
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from dataclasses import dataclass
import time

# 🎨 Mint-on-Black Theme Configuration
console = Console(color_system="256")

@dataclass
class TradingConfig:
    """📋 Trading configuration with strict parameters"""
    api_key: str = 'bg_5400882ef43c5596ffcf4af0c697b250'
    api_secret: str = '60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45'
    passphrase: str = '22672267'
    sandbox: bool = False
    max_positions: int = 10
    position_size_pct: float = 2.0  # 2% per position
    leverage_filter: int = 25  # Only pairs with 25x+ leverage
    stop_loss_pct: float = 1.5
    take_profit_pct: float = 3.0
    cooldown_minutes: int = 3
    max_daily_trades: int = 50

@dataclass 
class Position:
    """📊 Active position tracking"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_pct: float
    leverage: int
    timestamp: datetime
    
class AlpineTradingBot:
    """🏔️ Main Alpine Trading Bot - Production Ready"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.console = console
        self.exchange = None
        self.running = False
        self.start_time = datetime.now()
        
        # 📊 Trading State
        self.positions: List[Position] = []
        self.balance = 0.0
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.successful_trades = 0
        self.last_trade_times = {}
        
        # 🎯 Market Data
        self.trading_pairs = []
        self.market_data = {}
        self.signals = []
        
        # 🛡️ Risk Management
        self.emergency_stop = False
        self.daily_loss_limit = -500.0  # $500 daily loss limit
        
        # 📝 Logging Setup
        self.setup_logging()
        
    def setup_logging(self):
        """📝 Setup unified logging across all modules"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('alpine_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AlpineBot')
        
    def display_banner(self):
        """🎨 Mint-on-Black startup banner"""
        banner_text = """
🏔️ ALPINE TRADING BOT 🏔️
        
⚡ Status: ACTIVE & HUNTING
🎯 Leverage Focus: 25x+ Only  
💰 Position Size: 2% per trade
🛡️ Risk Management: ENABLED
🚀 Real-time Execution: ON
        
🎨 Theme: Mint on Black/Charcoal
        """
        
        panel = Panel(
            Align.center(Text(banner_text, style="bold #00FF7F")),
            border_style="#2F4F4F",
            title="🚀 PRODUCTION SYSTEM ONLINE",
            title_align="center"
        )
        self.console.print(panel)
        
    async def initialize_exchange(self):
        """⚡ Initialize Bitget exchange connection"""
        try:
            self.console.print("🔌 Connecting to Bitget exchange...", style="#00FF7F")
            
            self.exchange = ccxt.bitget({
                'apiKey': self.config.api_key,
                'secret': self.config.api_secret,
                'password': self.config.passphrase,
                'sandbox': self.config.sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',
                    'marginMode': 'cross'
                }
            })
            
            # Test connection
            markets = self.exchange.load_markets()
            balance = self.exchange.fetch_balance({'type': 'swap'})
            self.balance = balance.get('USDT', {}).get('total', 0.0)
            
            self.console.print(f"✅ Connected! Balance: ${self.balance:.2f}", style="bold #00FF7F")
            
            # Load trading pairs with 25x leverage
            await self.load_high_leverage_pairs(markets)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Exchange connection failed: {e}", style="bold red")
            self.logger.error(f"Exchange initialization failed: {e}")
            return False
            
    async def load_high_leverage_pairs(self, markets):
        """🎯 Load only pairs with 25x+ leverage"""
        try:
            self.console.print("🔍 Scanning for 25x+ leverage pairs...", style="#00FF7F")
            
            leverage_pairs = []
            for symbol, market in markets.items():
                if (market.get('type') == 'swap' and 
                    market.get('quote') == 'USDT' and 
                    market.get('active', True)):
                    
                    # Check leverage via contract info
                    try:
                        contract_info = market.get('info', {})
                        max_leverage = contract_info.get('maxLeverage', 1)
                        
                        if int(max_leverage) >= self.config.leverage_filter:
                            leverage_pairs.append({
                                'symbol': symbol,
                                'max_leverage': int(max_leverage),
                                'base': market.get('base'),
                                'quote': market.get('quote')
                            })
                    except:
                        continue
            
            # Sort by leverage (highest first)
            leverage_pairs.sort(key=lambda x: x['max_leverage'], reverse=True)
            self.trading_pairs = leverage_pairs[:50]  # Top 50 high-leverage pairs
            
            self.console.print(f"✅ Loaded {len(self.trading_pairs)} high-leverage pairs", style="bold #00FF7F")
            
            # Display top pairs
            table = Table(title="🎯 High Leverage Pairs", style="#00FF7F")
            table.add_column("Symbol", style="#00FF7F")
            table.add_column("Max Leverage", style="cyan")
            table.add_column("Asset", style="white")
            
            for pair in self.trading_pairs[:10]:
                table.add_row(
                    pair['symbol'], 
                    f"{pair['max_leverage']}x",
                    pair['base']
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ Failed to load leverage pairs: {e}", style="bold red")
            self.logger.error(f"Failed to load leverage pairs: {e}")
            
    def generate_signals(self, symbol: str, timeframe: str = '5m', limit: int = 100):
        """🎯 Generate trading signals based on volume anomaly + RSI"""
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            if len(df) < 20:
                return None
                
            # Calculate indicators
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Signal logic
            latest = df.iloc[-1]
            volume_spike = latest['volume_ratio'] > 2.0
            rsi_oversold = latest['rsi'] < 30
            rsi_overbought = latest['rsi'] > 70
            
            signal = None
            if volume_spike and rsi_oversold:
                signal = {
                    'symbol': symbol,
                    'side': 'buy',
                    'confidence': min(90, 50 + (latest['volume_ratio'] * 10)),
                    'price': latest['close'],
                    'volume_ratio': latest['volume_ratio'],
                    'rsi': latest['rsi'],
                    'timestamp': datetime.now()
                }
            elif volume_spike and rsi_overbought:
                signal = {
                    'symbol': symbol,
                    'side': 'sell',
                    'confidence': min(90, 50 + (latest['volume_ratio'] * 10)),
                    'price': latest['close'],
                    'volume_ratio': latest['volume_ratio'],
                    'rsi': latest['rsi'],
                    'timestamp': datetime.now()
                }
                
            return signal
            
        except Exception as e:
            self.logger.error(f"Signal generation failed for {symbol}: {e}")
            return None
            
    async def execute_trade(self, signal: dict):
        """🚀 Execute trade with proper risk management"""
        try:
            symbol = signal['symbol']
            side = signal['side']
            
            # Check cooldown
            if symbol in self.last_trade_times:
                cooldown = timedelta(minutes=self.config.cooldown_minutes)
                if datetime.now() - self.last_trade_times[symbol] < cooldown:
                    return False
                    
            # Check position limits
            if len(self.positions) >= self.config.max_positions:
                return False
                
            # Calculate position size
            position_value = self.balance * (self.config.position_size_pct / 100)
            leverage = 25  # Use 25x leverage
            quantity = (position_value * leverage) / signal['price']
            
            # Place order
            order = self.exchange.create_market_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=quantity,
                params={
                    'leverage': leverage,
                    'marginMode': 'cross'
                }
            )
            
            if order['status'] == 'closed':
                # Set stop loss and take profit
                sl_price = signal['price'] * (0.985 if side == 'buy' else 1.015)
                tp_price = signal['price'] * (1.03 if side == 'buy' else 0.97)
                
                # Place SL order
                self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side='sell' if side == 'buy' else 'buy',
                    amount=quantity,
                    params={'stopPrice': sl_price}
                )
                
                # Place TP order  
                self.exchange.create_order(
                    symbol=symbol,
                    type='take_profit_market',
                    side='sell' if side == 'buy' else 'buy',
                    amount=quantity,
                    params={'stopPrice': tp_price}
                )
                
                # Track position
                position = Position(
                    symbol=symbol,
                    side=side,
                    size=quantity,
                    entry_price=signal['price'],
                    current_price=signal['price'],
                    pnl=0.0,
                    pnl_pct=0.0,
                    leverage=leverage,
                    timestamp=datetime.now()
                )
                self.positions.append(position)
                
                # Update tracking
                self.last_trade_times[symbol] = datetime.now()
                self.total_trades += 1
                
                self.console.print(
                    f"🚀 Trade executed: {side.upper()} {symbol} @ ${signal['price']:.6f}",
                    style="bold #00FF7F"
                )
                self.logger.info(f"Trade executed: {side} {symbol} @ {signal['price']}")
                
                return True
                
        except Exception as e:
            self.console.print(f"❌ Trade execution failed: {e}", style="bold red")
            self.logger.error(f"Trade execution failed: {e}")
            return False
            
    async def update_positions(self):
        """📊 Update position data and PnL"""
        try:
            if not self.positions:
                return
                
            positions_data = self.exchange.fetch_positions()
            active_positions = [p for p in positions_data if p['size'] > 0]
            
            for position in self.positions:
                # Find matching exchange position
                exchange_pos = next((p for p in active_positions if p['symbol'] == position.symbol), None)
                
                if exchange_pos:
                    position.current_price = exchange_pos['markPrice']
                    position.pnl = exchange_pos['unrealizedPnl'] or 0
                    position.pnl_pct = exchange_pos['percentage'] or 0
                    
        except Exception as e:
            self.logger.error(f"Failed to update positions: {e}")
            
    def create_dashboard(self):
        """🎨 Create mint-on-black real-time dashboard"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=8),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header - Bot Status
        status_emoji = "🟢" if self.running else "🔴"
        uptime = datetime.now() - self.start_time
        header_text = f"""
{status_emoji} Alpine Trading Bot | Uptime: {str(uptime).split('.')[0]}
💰 Balance: ${self.balance:.2f} | 📊 Positions: {len(self.positions)}/{self.config.max_positions}
📈 Daily P&L: ${self.daily_pnl:.2f} | 🎯 Trades: {self.total_trades}
        """
        header_panel = Panel(
            Align.center(Text(header_text, style="bold #00FF7F")),
            border_style="#2F4F4F",
            title="🏔️ ALPINE STATUS",
            title_align="center"
        )
        layout["header"].update(header_panel)
        
        # Left - Active Positions
        if self.positions:
            pos_table = Table(title="📊 Active Positions", style="#00FF7F")
            pos_table.add_column("Symbol", style="#00FF7F")
            pos_table.add_column("Side", style="cyan")
            pos_table.add_column("Size", style="white")
            pos_table.add_column("Entry", style="yellow")
            pos_table.add_column("Current", style="yellow")
            pos_table.add_column("P&L", style="green")
            
            for pos in self.positions[-10:]:  # Show last 10
                pnl_style = "green" if pos.pnl >= 0 else "red"
                pos_table.add_row(
                    pos.symbol.replace('/USDT:USDT', ''),
                    f"{pos.side.upper()} {pos.leverage}x",
                    f"{pos.size:.4f}",
                    f"${pos.entry_price:.6f}",
                    f"${pos.current_price:.6f}",
                    f"${pos.pnl:.2f} ({pos.pnl_pct:.1f}%)",
                    style=pnl_style
                )
            layout["left"].update(pos_table)
        else:
            no_pos_panel = Panel(
                Align.center(Text("🎯 Hunting for signals...", style="bold #00FF7F")),
                border_style="#2F4F4F",
                title="📊 Positions"
            )
            layout["left"].update(no_pos_panel)
            
        # Right - Recent Signals
        if self.signals:
            sig_table = Table(title="🎯 Recent Signals", style="#00FF7F")
            sig_table.add_column("Symbol", style="#00FF7F")
            sig_table.add_column("Side", style="cyan")
            sig_table.add_column("Confidence", style="yellow")
            sig_table.add_column("Volume", style="white")
            sig_table.add_column("RSI", style="white")
            
            for sig in self.signals[-10:]:
                side_emoji = "🚀" if sig['side'] == 'buy' else "📉"
                sig_table.add_row(
                    sig['symbol'].replace('/USDT:USDT', ''),
                    f"{side_emoji} {sig['side'].upper()}",
                    f"{sig['confidence']:.0f}%",
                    f"{sig['volume_ratio']:.1f}x",
                    f"{sig['rsi']:.1f}"
                )
            layout["right"].update(sig_table)
        else:
            no_sig_panel = Panel(
                Align.center(Text("🔍 Scanning markets...", style="bold #00FF7F")),
                border_style="#2F4F4F",
                title="🎯 Signals"
            )
            layout["right"].update(no_sig_panel)
            
        # Footer - System Health
        health_text = f"🛡️ Risk Management: ACTIVE | 🚫 Emergency Stop: {'YES' if self.emergency_stop else 'NO'}"
        footer_panel = Panel(
            Align.center(Text(health_text, style="bold white")),
            border_style="#2F4F4F",
            title="🔧 System Health"
        )
        layout["footer"].update(footer_panel)
        
        return layout
        
    async def trading_loop(self):
        """🔄 Main trading loop with real-time dashboard"""
        self.console.print("🚀 Starting trading loop...", style="bold #00FF7F")
        
        with Live(self.create_dashboard(), refresh_per_second=1) as live:
            while self.running:
                try:
                    # Update positions
                    await self.update_positions()
                    
                    # Scan for signals
                    for pair_info in self.trading_pairs[:20]:  # Scan top 20 pairs
                        symbol = pair_info['symbol']
                        signal = self.generate_signals(symbol)
                        
                        if signal and signal['confidence'] > 60:
                            self.signals.append(signal)
                            
                            # Execute trade if conditions are met
                            if not self.emergency_stop:
                                await self.execute_trade(signal)
                    
                    # Keep only recent signals
                    if len(self.signals) > 50:
                        self.signals = self.signals[-50:]
                        
                    # Update dashboard
                    live.update(self.create_dashboard())
                    
                    # Risk check
                    if self.daily_pnl < self.daily_loss_limit:
                        self.emergency_stop = True
                        self.console.print("🚨 EMERGENCY STOP: Daily loss limit reached!", style="bold red")
                        
                    await asyncio.sleep(5)  # 5-second loop
                    
                except Exception as e:
                    self.logger.error(f"Trading loop error: {e}")
                    await asyncio.sleep(10)
                    
    async def start(self):
        """🚀 Start the Alpine trading bot"""
        self.display_banner()
        
        if not await self.initialize_exchange():
            return
            
        self.running = True
        self.console.print("🎯 Alpine Trading Bot is now LIVE!", style="bold #00FF7F")
        
        try:
            await self.trading_loop()
        except KeyboardInterrupt:
            self.console.print("\n🛑 Shutting down Alpine Bot...", style="bold yellow")
            self.running = False
        except Exception as e:
            self.console.print(f"❌ Critical error: {e}", style="bold red")
            self.logger.error(f"Critical error: {e}")
        finally:
            if self.exchange:
                self.exchange.close()
            self.console.print("✅ Alpine Bot shutdown complete", style="bold #00FF7F")

async def main():
    """🏔️ Main entry point"""
    config = TradingConfig()
    bot = AlpineTradingBot(config)
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())