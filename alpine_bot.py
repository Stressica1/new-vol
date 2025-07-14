"""
🏔️ Alpine Trading Bot - Main Engine
Beautiful mint green terminal displays with immediate trading capabilities
Volume Anomaly Strategy with 90% success rate from PineScript
Hot-reload capable with watchdog system
"""

import threading
import time
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import importlib
from typing import Dict, List, Optional, Tuple
from rich.live import Live
from rich.console import Console
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure Loguru for detailed logging
logger.remove()  # Remove default handler
logger.add("logs/alpine_bot_{time:YYYY-MM-DD}.log", 
          rotation="1 day", 
          retention="30 days",
          level="DEBUG",
          format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}")
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")

# Import our components
from config import TradingConfig, get_exchange_config, TRADING_PAIRS, BOT_NAME, VERSION
from ui_display import AlpineDisplay
from strategy import VolumeAnomalyStrategy
from risk_manager import AlpineRiskManager

class CodeReloadHandler(FileSystemEventHandler):
    """🔄 Hot-reload handler for code changes"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.last_reload = {}
        self.reload_cooldown = 2.0  # Prevent rapid reloads
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        if not file_path.endswith('.py'):
            return
            
        # Skip __pycache__ and other temp files
        if '__pycache__' in file_path or file_path.endswith('.pyc'):
            return
            
        # Check cooldown
        current_time = time.time()
        if file_path in self.last_reload:
            if current_time - self.last_reload[file_path] < self.reload_cooldown:
                return
                
        self.last_reload[file_path] = current_time
        
        try:
            filename = os.path.basename(file_path)
            if filename in ['strategy.py', 'risk_manager.py', 'ui_display.py', 'config.py']:
                logger.info(f"🔄 Detected change in {filename}, hot-reloading...")
                self.bot.log_activity(f"🔄 Hot-reloading {filename}...", "INFO")
                self.bot.hot_reload_module(filename)
        except Exception as e:
            logger.error(f"❌ Error handling file change: {e}")
            self.bot.log_activity(f"❌ Reload error: {e}", "ERROR")

class AlpineBot:
    """🏔️ Alpine Trading Bot - Volume Anomaly Master with Hot-Reload"""
    
    def __init__(self):
        self.console = Console()
        self.config = TradingConfig()
        
        # Initialize components
        self.display = AlpineDisplay()
        self.strategy = VolumeAnomalyStrategy()
        self.risk_manager = AlpineRiskManager()
        
        # Exchange connection
        self.exchange = None
        self.connected = False
        
        # Trading state
        self.running = False
        self.last_update = datetime.now()
        
        # Data storage
        self.market_data = {}
        self.account_data = {}
        self.positions = []
        self.activity_logs = []
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_signals = 0
        self.total_trades = 0
        
        # 🔄 Hot-reload system
        self.watchdog_observer = None
        self.reload_lock = threading.Lock()
        self.module_backup = {}
        
        logger.info("🏔️ Alpine Bot initialized with hot-reload capability")
        
    def setup_watchdog(self):
        """Setup file watching for hot-reload 👀"""
        try:
            if self.watchdog_observer:
                self.watchdog_observer.stop()
                self.watchdog_observer.join()
            
            self.watchdog_observer = Observer()
            event_handler = CodeReloadHandler(self)
            
            # Watch current directory for Python files
            self.watchdog_observer.schedule(event_handler, ".", recursive=False)
            self.watchdog_observer.start()
            
            logger.info("👀 Watchdog started - monitoring code changes")
            self.log_activity("👀 Hot-reload watchdog activated", "SUCCESS")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup watchdog: {e}")
            self.log_activity(f"❌ Watchdog setup failed: {e}", "ERROR")
    
    def hot_reload_module(self, filename: str):
        """Hot-reload a specific module while preserving trading state 🔄"""
        
        with self.reload_lock:
            try:
                module_name = filename.replace('.py', '')
                
                # Backup current state
                self.backup_critical_state()
                
                logger.info(f"🔄 Hot-reloading {module_name}...")
                
                if module_name == 'strategy':
                    # Preserve strategy state
                    old_signals = getattr(self.strategy, 'signals_history', [])
                    old_timeframes = getattr(self.strategy, 'timeframes', ['1m', '3m', '5m'])
                    
                    # Reload strategy module
                    import strategy
                    importlib.reload(strategy)
                    
                    # Create new instance and restore state
                    new_strategy = strategy.VolumeAnomalyStrategy()
                    new_strategy.signals_history = old_signals
                    new_strategy.timeframes = old_timeframes
                    
                    self.strategy = new_strategy
                    logger.success("✅ Strategy module reloaded successfully")
                    self.log_activity("✅ Strategy module hot-reloaded", "SUCCESS")
                    
                elif module_name == 'risk_manager':
                    # Preserve risk manager state
                    old_positions = getattr(self.risk_manager, 'active_positions', [])
                    old_closed = getattr(self.risk_manager, 'closed_positions', [])
                    old_daily_pnl = getattr(self.risk_manager, 'daily_pnl', 0)
                    old_session_start = getattr(self.risk_manager, 'session_start_balance', 0)
                    old_trading_halted = getattr(self.risk_manager, 'trading_halted', False)
                    
                    # Reload risk manager module
                    import risk_manager
                    importlib.reload(risk_manager)
                    
                    # Create new instance and restore state
                    new_risk_manager = risk_manager.AlpineRiskManager()
                    new_risk_manager.active_positions = old_positions
                    new_risk_manager.closed_positions = old_closed
                    new_risk_manager.daily_pnl = old_daily_pnl
                    new_risk_manager.session_start_balance = old_session_start
                    new_risk_manager.trading_halted = old_trading_halted
                    
                    self.risk_manager = new_risk_manager
                    logger.success("✅ Risk manager module reloaded successfully")
                    self.log_activity("✅ Risk manager hot-reloaded", "SUCCESS")
                    
                elif module_name == 'ui_display':
                    # Preserve display state
                    old_stats = {
                        'total_trades': getattr(self.display, 'total_trades', 0),
                        'winning_trades': getattr(self.display, 'winning_trades', 0),
                        'losing_trades': getattr(self.display, 'losing_trades', 0),
                        'total_pnl': getattr(self.display, 'total_pnl', 0.0),
                        'daily_pnl': getattr(self.display, 'daily_pnl', 0.0),
                        'max_drawdown': getattr(self.display, 'max_drawdown', 0.0),
                        'start_time': getattr(self.display, 'start_time', datetime.now())
                    }
                    
                    # Reload UI display module
                    import ui_display
                    importlib.reload(ui_display)
                    
                    # Create new instance and restore state
                    new_display = ui_display.AlpineDisplay()
                    for key, value in old_stats.items():
                        setattr(new_display, key, value)
                    
                    self.display = new_display
                    logger.success("✅ UI display module reloaded successfully")
                    self.log_activity("✅ UI display hot-reloaded", "SUCCESS")
                    
                elif module_name == 'config':
                    # Reload config module
                    import config
                    importlib.reload(config)
                    
                    # Update config instance
                    self.config = config.TradingConfig()
                    logger.success("✅ Config module reloaded successfully")
                    self.log_activity("✅ Config hot-reloaded", "SUCCESS")
                    
                else:
                    logger.warning(f"⚠️ Module {module_name} not configured for hot-reload")
                    
            except Exception as e:
                logger.error(f"❌ Hot-reload failed for {filename}: {e}")
                self.log_activity(f"❌ Hot-reload failed: {e}", "ERROR")
                
                # Attempt to restore from backup
                self.restore_from_backup()
    
    def backup_critical_state(self):
        """Backup critical trading state before reload 💾"""
        try:
            self.module_backup = {
                'account_data': self.account_data.copy(),
                'positions': self.positions.copy(),
                'market_data': self.market_data.copy(),
                'total_signals': self.total_signals,
                'total_trades': self.total_trades,
                'last_update': self.last_update
            }
            logger.debug("💾 Critical state backed up")
        except Exception as e:
            logger.error(f"❌ Failed to backup state: {e}")
    
    def restore_from_backup(self):
        """Restore critical state from backup 🔄"""
        try:
            if self.module_backup:
                self.account_data = self.module_backup.get('account_data', {})
                self.positions = self.module_backup.get('positions', [])
                self.market_data = self.module_backup.get('market_data', {})
                self.total_signals = self.module_backup.get('total_signals', 0)
                self.total_trades = self.module_backup.get('total_trades', 0)
                self.last_update = self.module_backup.get('last_update', datetime.now())
                
                logger.info("🔄 State restored from backup")
                self.log_activity("🔄 State restored from backup", "INFO")
        except Exception as e:
            logger.error(f"❌ Failed to restore from backup: {e}")
        
    def log_activity(self, message: str, level: str = "INFO"):
        """Add activity log with emoji and timestamp 📝"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji_map = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TRADE": "💰",
            "SIGNAL": "🎯",
            "RELOAD": "🔄"
        }
        
        emoji = emoji_map.get(level, "📝")
        log_entry = f"{timestamp} {emoji} {message}"
        self.activity_logs.append(log_entry)
        
        # Log to Loguru as well
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "SUCCESS":
            logger.success(message)
        else:
            logger.info(message)
        
        # Keep only last 100 logs
        if len(self.activity_logs) > 100:
            self.activity_logs = self.activity_logs[-100:]
    
    def initialize_exchange(self) -> bool:
        """Initialize Bitget exchange connection 🔌"""
        
        try:
            logger.info("🔌 Initializing Bitget exchange connection...")
            self.log_activity("🔌 Connecting to Bitget exchange...", "INFO")
            
            # Initialize exchange
            exchange_config = get_exchange_config()
            logger.debug(f"Exchange config keys: {list(exchange_config.keys())}")
            self.log_activity(f"🔧 Exchange config loaded: {list(exchange_config.keys())}", "INFO")
            
            self.exchange = ccxt.bitget(exchange_config)
            
            # Test connection
            logger.info("📡 Testing connection with load_markets()...")
            self.log_activity("📡 Testing connection with load_markets()...", "INFO")
            markets = self.exchange.load_markets()
            logger.debug(f"Loaded {len(markets)} markets")
            
            logger.info("💰 Fetching account balance...")
            self.log_activity("💰 Fetching account balance...", "INFO")
            balance = self.exchange.fetch_balance()
            logger.debug(f"Balance response: {balance}")
            
            self.connected = True
            logger.success("✅ Successfully connected to Bitget!")
            self.log_activity("✅ Successfully connected to Bitget!", "SUCCESS")
            
            usdt_balance = balance.get('USDT', {}).get('total', 0)
            logger.info(f"💰 Account balance: ${usdt_balance:,.2f} USDT")
            self.log_activity(f"💰 Account balance loaded: ${usdt_balance:,.2f}", "INFO")
            
            return True
            
        except ccxt.AuthenticationError as e:
            error_msg = f"🔐 Authentication Error: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            self.log_activity("❌ Check your API credentials (Key, Secret, Passphrase)", "ERROR")
            logger.error("API Key check - ensure credentials are correct and have trading permissions")
            self.connected = False
            return False
            
        except ccxt.NetworkError as e:
            error_msg = f"🌐 Network Error: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            self.log_activity("❌ Check your internet connection", "ERROR")
            self.connected = False
            return False
            
        except ccxt.ExchangeError as e:
            error_msg = f"🏦 Exchange Error: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            self.log_activity("❌ Bitget API issue or invalid settings", "ERROR")
            logger.error(f"Exchange error details: {e}")
            self.connected = False
            return False
            
        except Exception as e:
            error_msg = f"❌ Unexpected error connecting to Bitget: {str(e)}"
            logger.exception("Unexpected error during exchange initialization")
            self.log_activity(error_msg, "ERROR")
            self.log_activity(f"🔍 Error type: {type(e).__name__}", "ERROR")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.log_activity(f"📋 Full traceback: {traceback.format_exc()}", "ERROR")
            self.connected = False
            return False
    
    def fetch_account_data(self):
        """Fetch account balance and positions 💰"""
        
        try:
            if not self.connected:
                logger.warning("Cannot fetch account data - not connected to exchange")
                return
            
            logger.debug("Fetching account balance...")
            # Fetch balance
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {})
            
            self.account_data = {
                'balance': usdt_balance.get('total', 0),
                'equity': usdt_balance.get('total', 0),  # For futures, equity = total
                'margin': usdt_balance.get('used', 0),
                'free_margin': usdt_balance.get('free', 0)
            }
            
            logger.debug(f"Account data updated: {self.account_data}")
            
            # Initialize risk manager with current balance
            self.risk_manager.initialize_session(self.account_data['balance'])
            
            logger.debug("Fetching positions...")
            # Fetch positions
            positions = self.exchange.fetch_positions()
            self.positions = [pos for pos in positions if pos['contracts'] > 0]
            logger.debug(f"Found {len(self.positions)} active positions")
            
            # Update risk manager positions
            for pos in self.positions:
                self.risk_manager.update_position(
                    pos['symbol'], 
                    pos['markPrice'], 
                    pos.get('unrealizedPnl', 0)
                )
            
        except Exception as e:
            error_msg = f"❌ Error fetching account data: {str(e)}"
            logger.exception("Error fetching account data")
            self.log_activity(error_msg, "ERROR")
    
    def fetch_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for analysis 📊"""
        
        try:
            if not self.connected:
                logger.warning(f"Cannot fetch market data for {symbol} - not connected")
                return None
            
            logger.debug(f"Fetching market data for {symbol}, timeframe: {timeframe}, limit: {limit}")
            
            # Fetch candle data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                logger.warning(f"No OHLCV data received for {symbol}")
                return None
            
            logger.debug(f"Received {len(ohlcv)} candles for {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Store in market data
            self.market_data[symbol] = df
            
            return df
            
        except Exception as e:
            error_msg = f"❌ Error fetching market data for {symbol}: {str(e)}"
            logger.exception(f"Error fetching market data for {symbol}")
            self.log_activity(error_msg, "ERROR")
            return None
    
    def analyze_signals(self):
        """Analyze all trading pairs for volume anomaly signals across multiple timeframes 🎯"""
        
        all_signals = []
        logger.debug(f"Analyzing signals for {len(TRADING_PAIRS)} trading pairs across timeframes: {self.strategy.timeframes}")
        
        for symbol in TRADING_PAIRS:
            try:
                logger.debug(f"Analyzing {symbol}")
                
                # Fetch market data for all timeframes
                timeframe_data = {}
                for timeframe in self.strategy.timeframes:
                    df = self.fetch_market_data(symbol, timeframe)
                    if df is not None and len(df) >= 30:  # Reduced from 50 to 30
                        timeframe_data[timeframe] = df
                        logger.debug(f"✅ {symbol} {timeframe}: {len(df)} candles available")
                    else:
                        logger.warning(f"⚠️ Insufficient data for {symbol} on {timeframe}: {len(df) if df is not None else 0} candles")
                
                logger.debug(f"📊 {symbol}: {len(timeframe_data)} timeframes with sufficient data")
                
                # Try confluence signals first (stricter)
                confluence_signals = []
                if len(timeframe_data) >= self.strategy.confluence_required:
                    confluence_signals = self.strategy.analyze_timeframe_signals(timeframe_data, symbol)
                    if confluence_signals:
                        logger.info(f"🎯 {symbol}: Generated {len(confluence_signals)} CONFLUENCE signals")
                
                # If no confluence signals, try single timeframe analysis (more sensitive)
                single_timeframe_signals = []
                if not confluence_signals and timeframe_data:
                    logger.debug(f"🔍 {symbol}: No confluence signals, trying single timeframe analysis...")
                    
                    # Try primary timeframe first
                    primary_tf = self.strategy.primary_timeframe
                    if primary_tf in timeframe_data:
                        single_signals = self.strategy.generate_single_timeframe_signals(
                            timeframe_data[primary_tf], symbol, primary_tf
                        )
                        if single_signals:
                            single_timeframe_signals.extend(single_signals)
                            logger.info(f"🎯 {symbol}: Generated {len(single_signals)} SINGLE TF signals on {primary_tf}")
                    
                    # If still no signals, try other timeframes
                    if not single_timeframe_signals:
                        for timeframe, df in timeframe_data.items():
                            if timeframe != primary_tf:
                                single_signals = self.strategy.generate_single_timeframe_signals(df, symbol, timeframe)
                                if single_signals:
                                    single_timeframe_signals.extend(single_signals)
                                    logger.info(f"🎯 {symbol}: Generated {len(single_signals)} SINGLE TF signals on {timeframe}")
                                    break  # Take first successful timeframe
                
                # Use the best signals available
                signals = confluence_signals if confluence_signals else single_timeframe_signals
                
                if signals:
                    self.total_signals += len(signals)
                    all_signals.extend(signals)
                    signal_type = "CONFLUENCE" if confluence_signals else "SINGLE-TF"
                    logger.success(f"✅ {symbol}: Generated {len(signals)} {signal_type} signals")
                    
                    for signal in signals:
                        timeframes_str = ", ".join(signal.get('supporting_timeframes', [signal.get('timeframe', 'N/A')]))
                        confluence_count = signal.get('confluence_count', 1)
                        signal_msg = (f"🎯 {signal['type']} signal for {symbol.replace('/USDT:USDT', '')} "
                                    f"| Vol: {signal['volume_ratio']:.1f}x | Conf: {signal['confidence']:.1f}% "
                                    f"| TFs: {timeframes_str} ({confluence_count})")
                        logger.info(signal_msg)
                        self.log_activity(signal_msg, "SIGNAL")
                else:
                    logger.debug(f"❌ {symbol}: No signals detected on any timeframe")
                
            except Exception as e:
                error_msg = f"❌ Error analyzing {symbol}: {str(e)}"
                logger.exception(f"Error analyzing {symbol}")
                self.log_activity(error_msg, "ERROR")
        
        total_count = len(all_signals)
        if total_count > 0:
            logger.success(f"🎯 TOTAL: Generated {total_count} signals across all pairs")
            self.log_activity(f"🎯 Signal scan complete: {total_count} signals found", "SUCCESS")
        else:
            logger.info("📊 Signal scan complete: No signals detected this cycle")
            self.log_activity("📊 Signal scan complete: No signals found", "INFO")
        
        return all_signals
    
    def execute_trade(self, signal: Dict) -> bool:
        """Execute a trade based on signal 💰"""
        
        try:
            symbol = signal['symbol']
            signal_type = signal['type']
            current_price = signal['price']
            
            logger.info(f"🎯 Attempting to execute {signal_type} trade for {symbol} at ${current_price}")
            
            # Check if we can open position
            can_open, reason = self.risk_manager.can_open_position(signal, self.account_data['balance'])
            
            if not can_open:
                logger.warning(f"🚫 Trade rejected for {symbol}: {reason}")
                self.log_activity(f"🚫 Trade rejected: {reason}", "WARNING")
                return False
            
            # Calculate position size
            logger.debug("Calculating position size...")
            position_size, risk_info = self.risk_manager.calculate_position_size(
                signal, self.account_data['balance'], current_price
            )
            logger.debug(f"Position size calculated: {position_size}, risk_info: {risk_info}")
            
            # Calculate stop loss and take profit
            logger.debug("Calculating risk levels...")
            risk_levels = self.risk_manager.calculate_stop_loss_take_profit(
                signal, current_price, position_size
            )
            logger.debug(f"Risk levels: {risk_levels}")
            
            # Determine order side
            side = 'buy' if signal_type == 'LONG' else 'sell'
            logger.info(f"Placing {side} order for {symbol}: size={position_size}, price=${current_price}")
            
            # Place market order
            order = self.exchange.create_market_order(
                symbol, side, position_size, current_price
            )
            
            logger.debug(f"Order response: {order}")
            
            if order and order.get('id'):
                logger.success(f"✅ Order executed successfully: {order['id']}")
                
                # Create position record
                position = {
                    'symbol': symbol,
                    'side': signal_type.lower(),
                    'entry_price': current_price,
                    'position_size': position_size,
                    'position_value': risk_info['adjusted_value'],
                    'stop_loss': risk_levels['stop_loss'],
                    'take_profit': risk_levels['take_profit'],
                    'trailing_stop_distance': risk_levels.get('trailing_stop_distance'),
                    'order_id': order['id'],
                    'signal': signal
                }
                
                # Add to risk manager
                self.risk_manager.add_position(position)
                
                self.total_trades += 1
                trade_msg = (f"💰 {signal_type} trade executed for {symbol.replace('/USDT:USDT', '')} "
                           f"| Size: {position_size:.4f} | Entry: ${current_price:.4f}")
                logger.success(trade_msg)
                self.log_activity(trade_msg, "TRADE")
                
                # Update display stats
                self.display.update_stats({'pnl': 0})  # Will be updated when closed
                
                return True
            else:
                logger.error(f"❌ Order failed - no order ID returned: {order}")
                self.log_activity(f"❌ Order failed - no response from exchange", "ERROR")
                return False
            
        except ccxt.InsufficientFunds as e:
            error_msg = f"💰 Insufficient funds for {symbol}: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            return False
            
        except ccxt.InvalidOrder as e:
            error_msg = f"📋 Invalid order for {symbol}: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            return False
            
        except ccxt.ExchangeError as e:
            error_msg = f"🏦 Exchange error for {symbol}: {str(e)}"
            logger.error(error_msg)
            self.log_activity(error_msg, "ERROR")
            return False
            
        except Exception as e:
            error_msg = f"❌ Trade execution failed for {symbol}: {str(e)}"
            logger.exception(f"Trade execution failed for {symbol}")
            self.log_activity(error_msg, "ERROR")
            return False
        
        return False
    
    def monitor_positions(self):
        """Monitor open positions for stop loss, take profit, and trailing stops 👀"""
        
        if not self.risk_manager.active_positions:
            return
        
        logger.debug(f"Monitoring {len(self.risk_manager.active_positions)} positions")
        
        for position in self.risk_manager.active_positions[:]:  # Copy list to avoid modification during iteration
            try:
                symbol = position['symbol']
                side = position['side']
                
                logger.debug(f"Monitoring position: {symbol} {side}")
                
                # Fetch current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate unrealized P&L
                entry_price = position['entry_price']
                position_size = position['position_size']
                
                if side == 'long':
                    unrealized_pnl = (current_price - entry_price) * position_size
                else:
                    unrealized_pnl = (entry_price - current_price) * position_size
                
                logger.debug(f"Position {symbol}: entry=${entry_price}, current=${current_price}, PnL=${unrealized_pnl:.2f}")
                
                # Update position
                self.risk_manager.update_position(symbol, current_price, unrealized_pnl)
                
                # Check exit conditions
                should_close = False
                close_reason = ""
                
                # Check stop loss
                if side == 'long' and current_price <= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop Loss"
                    logger.info(f"Stop loss triggered for {symbol}: ${current_price} <= ${position['stop_loss']}")
                elif side == 'short' and current_price >= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop Loss"
                    logger.info(f"Stop loss triggered for {symbol}: ${current_price} >= ${position['stop_loss']}")
                
                # Check take profit
                elif side == 'long' and current_price >= position['take_profit']:
                    should_close = True
                    close_reason = "Take Profit"
                    logger.info(f"Take profit triggered for {symbol}: ${current_price} >= ${position['take_profit']}")
                elif side == 'short' and current_price <= position['take_profit']:
                    should_close = True
                    close_reason = "Take Profit"
                    logger.info(f"Take profit triggered for {symbol}: ${current_price} <= ${position['take_profit']}")
                
                # Execute close if needed
                if should_close:
                    logger.info(f"Closing position {symbol} due to {close_reason}")
                    self.close_position(position, current_price, close_reason)
                
            except Exception as e:
                error_msg = f"❌ Error monitoring position {position.get('symbol', 'Unknown')}: {str(e)}"
                logger.exception(f"Error monitoring position {position.get('symbol', 'Unknown')}")
                self.log_activity(error_msg, "ERROR")
    
    def close_position(self, position: Dict, close_price: float, reason: str):
        """Close a position 🔄"""
        
        try:
            symbol = position['symbol']
            side = 'sell' if position['side'] == 'long' else 'buy'
            size = position['position_size']
            
            logger.info(f"Closing position: {symbol} {side} {size} at ${close_price} ({reason})")
            
            # Place closing order
            order = self.exchange.create_market_order(symbol, side, size, close_price)
            
            logger.debug(f"Close order response: {order}")
            
            if order and order.get('id'):
                # Calculate realized P&L
                entry_price = position['entry_price']
                if position['side'] == 'long':
                    realized_pnl = (close_price - entry_price) * size
                else:
                    realized_pnl = (entry_price - close_price) * size
                
                logger.info(f"Position closed successfully: P&L=${realized_pnl:.2f}")
                
                # Update risk manager
                closed_pos = self.risk_manager.close_position(symbol, close_price, realized_pnl, reason)
                
                if closed_pos:
                    pnl_emoji = "💚" if realized_pnl > 0 else "❤️"
                    close_msg = (f"{pnl_emoji} Position closed: {symbol.replace('/USDT:USDT', '')} "
                               f"| {reason} | P&L: ${realized_pnl:.2f}")
                    logger.success(close_msg)
                    self.log_activity(close_msg, "TRADE")
                    
                    # Update display stats
                    self.display.update_stats({'pnl': realized_pnl})
            else:
                logger.error(f"Failed to close position {symbol} - no order ID returned")
                
        except Exception as e:
            error_msg = f"❌ Error closing position: {str(e)}"
            logger.exception("Error closing position")
            self.log_activity(error_msg, "ERROR")
    
    def trading_loop(self):
        """Main trading loop 🔄"""
        
        logger.info("🔄 Trading loop started")
        
        while self.running:
            try:
                logger.debug("Trading loop iteration starting...")
                
                # Fetch account data
                self.fetch_account_data()
                
                # Check risk limits
                self.risk_manager.check_risk_limits(self.account_data.get('balance', 0))
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Look for new signals if trading is allowed
                if not self.risk_manager.trading_halted:
                    signals = self.analyze_signals()
                    
                    # Execute trades on valid signals
                    for signal in signals:
                        logger.debug(f"🔍 Checking signal for execution: {signal}")
                        if self.strategy.should_enter_trade(signal, self.account_data.get('balance', 0), self.positions):
                            logger.info(f"🚀 Executing trade for signal: {signal}")
                            self.execute_trade(signal)
                        else:
                            logger.warning(f"🚫 Signal rejected for {signal.get('symbol', 'Unknown')}: Failed entry conditions")
                else:
                    logger.warning("🛑 Trading halted by risk manager - no new positions allowed")
                    self.log_activity("🛑 Trading halted by risk manager", "WARNING")
                
                self.last_update = datetime.now()
                logger.debug(f"Trading loop iteration completed, sleeping for {self.config.refresh_rate}s")
                
                # Wait before next iteration
                time.sleep(self.config.refresh_rate)
                
            except Exception as e:
                error_msg = f"❌ Error in trading loop: {str(e)}"
                logger.exception("Error in trading loop")
                self.log_activity(error_msg, "ERROR")
                time.sleep(5)  # Wait longer on error
    
    def get_display_data(self) -> Dict:
        """Get data for terminal display 📊"""
        
        # Get recent signals
        recent_signals = self.strategy.get_recent_signals(10)
        
        # Get status
        if not self.connected:
            status = "❌ DISCONNECTED"
        elif self.risk_manager.trading_halted:
            status = "🛑 TRADING HALTED"
        elif self.running:
            status = "🟢 ACTIVE TRADING"
        else:
            status = "⏸️ PAUSED"
        
        return {
            'account_data': self.account_data,
            'positions': self.positions,
            'signals': recent_signals,
            'logs': self.activity_logs,
            'status': status
        }
    
    def cleanup(self):
        """Clean up resources 🧹"""
        try:
            if self.watchdog_observer:
                self.watchdog_observer.stop()
                self.watchdog_observer.join()
                logger.info("👀 Watchdog stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def run(self):
        """Start the Alpine bot with hot-reload capability 🚀"""
        
        # Create logs directory if it doesn't exist
        import os
        os.makedirs("logs", exist_ok=True)
        
        # Initialize exchange
        if not self.initialize_exchange():
            self.console.print("❌ Failed to initialize exchange. Exiting...", style="red")
            logger.error("Failed to initialize exchange, exiting...")
            return
        
        # Setup watchdog for hot-reload
        self.setup_watchdog()
        
        logger.success(f"🚀 {BOT_NAME} {VERSION} starting up with hot-reload!")
        self.log_activity(f"🚀 {BOT_NAME} {VERSION} starting up with hot-reload!", "SUCCESS")
        self.log_activity("🎯 Volume Anomaly Strategy loaded with 90% success rate", "INFO")
        self.log_activity(f"💰 Risk Management: {self.config.max_daily_loss_pct}% daily loss limit", "INFO")
        self.log_activity(f"📊 Monitoring {len(TRADING_PAIRS)} trading pairs", "INFO")
        self.log_activity("🔄 Hot-reload system activated", "SUCCESS")
        
        self.running = True
        
        # Start trading loop in background thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        logger.info("Trading thread started")
        
        try:
            # Run live display with optimized refresh
            with Live(
                self.display.create_layout(**self.get_display_data()),
                refresh_per_second=0.5,  # Reduced to prevent flashing
                screen=True
            ) as live:
                
                while self.running:
                    # Update display with throttling
                    display_data = self.get_display_data()
                    live.update(self.display.create_layout(**display_data))
                    
                    # Longer sleep to reduce flashing
                    time.sleep(2.0)  # Fixed 2-second refresh rate
                    
        except KeyboardInterrupt:
            logger.warning("⏹️ Shutdown signal received")
            self.log_activity("⏹️ Shutdown signal received", "WARNING")
            self.running = False
            
        except Exception as e:
            error_msg = f"❌ Display error: {str(e)}"
            logger.exception("Display error")
            self.log_activity(error_msg, "ERROR")
            
        finally:
            self.cleanup()
            logger.info("👋 Alpine bot shutdown complete")
            self.log_activity("👋 Alpine bot shutdown complete", "INFO")

def main():
    """Main entry point 🏔️"""
    
    # Create and run Alpine bot
    bot = AlpineBot()
    bot.run()

if __name__ == "__main__":
    # Display startup banner
    console = Console()
    console.print("\n" + "="*60, style="bold cyan")
    console.print("🏔️  ALPINE TRADING BOT", style="bold green", justify="center")
    console.print("Volume Anomaly Strategy | 90% Success Rate", style="cyan", justify="center") 
    console.print("Beautiful Mint Green Terminal Interface", style="green", justify="center")
    console.print("🔄 HOT-RELOAD ENABLED", style="bold yellow", justify="center")
    console.print("="*60 + "\n", style="bold cyan")
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n👋 Alpine bot terminated by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Fatal error: {str(e)}", style="red")
        logger.exception("Fatal error in main")
        sys.exit(1)