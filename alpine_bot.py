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
import traceback
from datetime import datetime, timedelta
import sys
import os
import importlib
from typing import Dict, List, Optional, Tuple
from rich.live import Live
from rich.console import Console
from loguru import logger
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
import signal # Added for signal handling

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
from ui_display import AlpineDisplayV2  # Updated to use V2
from strategy import VolumeAnomalyStrategy
from risk_manager import AlpineRiskManager
from bot_manager import AlpineBotManager

# NOTE: Watchdog functionality temporarily disabled due to import issues
# Uncomment the watchdog imports above and this class when watchdog is properly installed
# class CodeReloadHandler(FileSystemEventHandler):
#     """🔄 Hot-reload handler for code changes"""
#     
#     def __init__(self, bot_instance):
#         self.bot = bot_instance
#         self.last_reload = {}
#         self.reload_cooldown = 2.0  # Prevent rapid reloads
#         
#     def on_modified(self, event):
#         if event.is_directory:
#             return
#             
#         file_path = event.src_path
#         if not file_path.endswith('.py'):
#             return
#             
#         # Skip __pycache__ and other temp files
#         if '__pycache__' in file_path or file_path.endswith('.pyc'):
#             return
#             
#         # Check cooldown
#         current_time = time.time()
#         if file_path in self.last_reload:
#             if current_time - self.last_reload[file_path] < self.reload_cooldown:
#                 return
#                 
#         self.last_reload[file_path] = current_time
#         
#         try:
#             filename = os.path.basename(file_path)
#             if filename in ['strategy.py', 'risk_manager.py', 'ui_display.py', 'config.py']:
#                 logger.info(f"🔄 Detected change in {filename}, hot-reloading...")
#                 self.bot.log_activity(f"🔄 Hot-reloading {filename}...", "INFO")
#                 self.bot.hot_reload_module(filename)
#         except Exception as e:
#             logger.error(f"❌ Error handling file change: {e}")
#             self.bot.log_activity(f"❌ Reload error: {e}", "ERROR")

class AlpineBot:
    """🏔️ Alpine Trading Bot V2.0 - Next-Generation Confluence Trading System"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # 🎨 Initialize Next-Gen UI
        self.display = AlpineDisplayV2()
        
        # 🧠 Initialize Enhanced Strategy
        self.strategy = VolumeAnomalyStrategy()
        
        # 🛡️ Initialize Enhanced Risk Manager
        self.risk_manager = AlpineRiskManager()
        
        # 📊 Trading state management
        self.active_positions = []
        self.current_signals = []
        self.activity_log = []
        self.error_log = []  # Track system errors for display
        self.account_data = {}
        self.system_status = "INITIALIZING"
        
        # 🔄 Hot-reload system
        self.watchdog_observer = None
        self.reload_handler = None
        self.reload_lock = threading.Lock()  # Thread-safe hot reloading
        
        # 📈 Performance tracking
        self.signal_count_minute = 0
        self.last_signal_time = time.time()
        self.execution_times = []
        self.api_response_times = []
        
        # 🏦 Exchange client
        self.exchange = None
        
        # 📊 Trading data
        self.positions = []
        self.market_data = {}
        self.total_signals = 0
        self.total_trades = 0
        self.last_update = datetime.now()
        self.connected = False
        self.running = False
        
        logger.info("🏔️ Alpine Bot V2.0 - Next-Generation System Initialized")
        self.log_activity("🚀 Alpine Bot V2.0 initialized with confluence trading", "SUCCESS")
        
    def setup_watchdog(self):
        """Setup file watching for hot-reload 👀"""
        try:
            # Watchdog functionality disabled due to import issues
            logger.info("👀 Watchdog disabled - hot-reload not available")
            self.log_activity("👀 Hot-reload disabled (watchdog not installed)", "INFO")
            
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
                    old_trading_halted = getattr(self.risk_manager, 'trading_halted', False)
                    
                    # Reload risk manager module
                    import risk_manager
                    importlib.reload(risk_manager)
                    
                    # Create new instance and restore state
                    new_risk_manager = risk_manager.AlpineRiskManager()
                    new_risk_manager.active_positions = old_positions
                    new_risk_manager.closed_positions = old_closed
                    new_risk_manager.daily_pnl = old_daily_pnl
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
                    new_display = ui_display.AlpineDisplayV2()
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
            if hasattr(self, 'module_backup') and self.module_backup:
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
        self.activity_log.append(log_entry)
        
        # Track errors separately for error panel
        if level == "ERROR":
            self.error_log.append(f"{timestamp}: {message}")
            if len(self.error_log) > 50:  # Keep last 50 errors
                self.error_log = self.error_log[-50:]
        
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
        if len(self.activity_log) > 100:
            self.activity_log = self.activity_log[-100:]
    
    def initialize_exchange(self) -> bool:
        """Initialize Bitget exchange connection 🔌"""
        
        try:
            logger.info("🔌 Initializing Bitget exchange connection...")
            self.log_activity("🔌 Connecting to Bitget exchange...", "INFO")
            
            # Initialize exchange
            exchange_config = get_exchange_config()
            logger.debug(f"Exchange config keys: {list(exchange_config.keys())}")
            self.log_activity(f"🔧 Exchange config loaded: {list(exchange_config.keys())}", "INFO")
            
            self.exchange = ccxt.bitget({
                'apiKey': exchange_config.get('apiKey', ''),
                'secret': exchange_config.get('secret', ''),
                'password': exchange_config.get('password', ''),
                'sandbox': exchange_config.get('sandbox', False),
                'enableRateLimit': exchange_config.get('enableRateLimit', True),
                'options': {
                    'defaultType': 'swap',  # For futures trading
                    'marginMode': 'cross'  # Use cross margin
                }
            })
            
            # Test connection
            logger.info("📡 Testing connection with load_markets()...")
            self.log_activity("📡 Testing connection with load_markets()...", "INFO")
            markets = self.exchange.load_markets()
            logger.debug(f"Loaded {len(markets)} markets")
            
            logger.info("💰 Fetching futures account balance...")
            self.log_activity("💰 Fetching futures account balance...", "INFO")
            balance = self.exchange.fetch_balance({'type': 'swap'})
            logger.debug(f"Futures balance response: {balance}")
            
            self.connected = True
            logger.success("✅ Successfully connected to Bitget!")
            self.log_activity("✅ Successfully connected to Bitget!", "SUCCESS")
            
            # Get futures balance info from the raw response
            usdt_futures_info = None
            info_list = balance.get('info', [])
            if isinstance(info_list, list):
                for info in info_list:
                    if isinstance(info, dict) and info.get('marginCoin') == 'USDT':
                        usdt_futures_info = info
                        break
            
            if usdt_futures_info:
                available = float(usdt_futures_info.get('available', 0))
                equity = float(usdt_futures_info.get('equity', 0))
                unrealized_pnl = float(usdt_futures_info.get('unrealizedPL', 0))
                logger.info(f"💰 Futures Account - Available: ${available:,.2f} | Equity: ${equity:,.2f} | Unrealized P&L: ${unrealized_pnl:,.2f}")
                self.log_activity(f"💰 Futures balance loaded - Available: ${available:,.2f} | Equity: ${equity:,.2f}", "INFO")
            else:
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
            if not self.connected or not self.exchange:
                logger.warning("Cannot fetch account data - not connected to exchange")
                return
            
            logger.debug("Fetching futures account balance...")
            # Fetch futures balance
            balance = self.exchange.fetch_balance({'type': 'swap'})
            
            # Get futures balance info from the raw response
            usdt_futures_info = None
            info_list = balance.get('info', [])
            if isinstance(info_list, list):
                for info in info_list:
                    if isinstance(info, dict) and info.get('marginCoin') == 'USDT':
                        usdt_futures_info = info
                        break
            
            if usdt_futures_info:
                available = float(usdt_futures_info.get('available', 0))
                equity = float(usdt_futures_info.get('equity', 0))
                unrealized_pnl = float(usdt_futures_info.get('unrealizedPL', 0))
                locked = float(usdt_futures_info.get('locked', 0))
                
                self.account_data = {
                    'balance': available,  # Available balance for trading
                    'equity': equity,      # Total equity including unrealized P&L
                    'margin': locked,      # Used margin (locked amount)
                    'free_margin': available,  # Free margin available
                    'unrealized_pnl': unrealized_pnl
                }
            else:
                # Fallback to regular balance
                usdt_balance = balance.get('USDT', {})
                self.account_data = {
                    'balance': usdt_balance.get('total', 0),
                    'equity': usdt_balance.get('total', 0),
                    'margin': usdt_balance.get('used', 0),
                    'free_margin': usdt_balance.get('free', 0),
                    'unrealized_pnl': 0
                }
            
            logger.debug(f"Account data updated: {self.account_data}")
            
            # Initialize risk manager with current balance
            self.risk_manager.initialize_session(self.account_data['balance'])
            
            logger.debug("Fetching positions...")
            # Fetch positions
            positions = self.exchange.fetch_positions()
            self.positions = [pos for pos in positions if float(pos['contracts'] or 0) > 0]
            logger.debug(f"Found {len(self.positions)} active positions")
            
            # Update risk manager positions
            for pos in self.positions:
                symbol = str(pos['symbol'])
                mark_price = pos.get('markPrice', 0)
                current_price = float(mark_price) if mark_price is not None else 0.0
                unrealized_pnl_val = pos.get('unrealizedPnl', 0)
                unrealized_pnl = float(unrealized_pnl_val) if unrealized_pnl_val is not None else 0.0
                self.risk_manager.update_position(symbol, current_price, unrealized_pnl)
            
        except Exception as e:
            error_msg = f"❌ Error fetching account data: {str(e)}"
            logger.exception("Error fetching account data")
            self.log_activity(error_msg, "ERROR")
    
    def fetch_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for analysis 📊"""
        
        try:
            if not self.connected or not self.exchange:
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
            column_names = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df = pd.DataFrame(ohlcv)
            df.columns = column_names
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Store in market data
            self.market_data[symbol] = df
            
            return df
            
        except Exception as e:
            error_msg = f"Market data error for {symbol}: {str(e)}"
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
                
                # Use the best signals available (prioritize confluence)
                signals = confluence_signals if confluence_signals else single_timeframe_signals
                
                if signals:
                    if not hasattr(self, 'total_signals'):
                        self.total_signals = 0
                    self.total_signals += len(signals)
                    all_signals.extend(signals)
                    
                    signal_type = "🚀 CONFLUENCE" if confluence_signals else "📈 SINGLE-TF"
                    logger.success(f"✅ {symbol}: Generated {len(signals)} {signal_type} signals")
                    
                    for signal in signals:
                        # Enhanced signal processing for confluence
                        is_confluence = signal.get('is_confluence', False)
                        timeframes_str = ", ".join(signal.get('confluence_timeframes', [signal.get('timeframe', 'N/A')]))
                        confidence = signal.get('confidence', 0)
                        volume_ratio = signal.get('volume_ratio', 0)
                        
                        signal_msg = (f"🎯 {signal['type']} {'🚀 CONFLUENCE' if is_confluence else '📈 SIGNAL'} for {symbol.replace('/USDT:USDT', '')} "
                                    f"| Vol: {volume_ratio:.1f}x | Conf: {confidence:.1f}% "
                                    f"| TFs: {timeframes_str}")
                        logger.info(signal_msg)
                        self.log_activity(signal_msg, "SIGNAL")
                        
                        # Check if we should execute this signal
                        should_enter = self.strategy.should_enter_trade(
                            signal,
                            self.account_data.get('balance', 1000),  # Default balance for testing
                            [pos for pos in self.active_positions]  # Convert to proper format
                        )
                        
                        if should_enter:
                            success = self.execute_trade(signal)  # Use real trade execution, not simulation
                            if success:
                                self.log_activity(f"✅ {'🚀 Confluence' if is_confluence else '📈 Standard'} trade executed", "SUCCESS")
                else:
                    logger.debug(f"❌ {symbol}: No signals detected on any timeframe")
                
            except Exception as e:
                error_msg = f"Signal analysis error for {symbol}: {str(e)}"
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

    def generate_signals(self) -> List[Dict]:
        """Generate executor-friendly signals for the TradingOrchestrator ⚡️🚀

        This method wraps `analyze_signals()` and converts each internal signal
        to the generic format expected by the OptimizedTradeExecutor
        (requires keys: symbol, action, confidence, confluence)."""
        # Run the full internal analysis
        internal_signals = self.analyze_signals()

        formatted_signals: List[Dict] = []
        for sig in internal_signals:
            # Map LONG/SHORT → BUY/SELL for uniformity
            action = "BUY" if sig.get("type") == "LONG" else "SELL"

            formatted_signals.append({
                "symbol": sig.get("symbol"),
                "action": action,
                "confidence": sig.get("confidence", 0),
                # Executor uses this to adjust position sizing
                "confluence": sig.get("is_confluence", False),
                # Pass through optional data if available
                "atr": sig.get("atr"),
                # Helpful metadata for logging/debugging
                "source_bot": "AlpineBot"
            })

        # Log summary for debugging
        logger.debug(f"generate_signals → produced {len(formatted_signals)} formatted signals")

        return formatted_signals
    
    def execute_enhanced_trade(self, signal: Dict) -> bool:
        """🚀 Enhanced trade execution with confluence position sizing and dynamic stop loss"""
        
        start_time = time.time()
        
        try:
            symbol = signal['symbol']
            signal_type = signal['type']
            current_price = signal.get('entry_price', signal.get('price', 0))
            is_confluence = signal.get('is_confluence', False)
            
            logger.info(f"🎯 Executing {'🚀 CONFLUENCE' if is_confluence else '📈 STANDARD'} {signal_type} trade for {symbol}")
            
            # Calculate position size using strategy method
            position_size = self.strategy.calculate_position_size(
                signal, 
                self.account_data.get('balance', 0), 
                current_price
            )
            
            # Calculate stop loss and take profit using strategy method
            stop_loss_price, take_profit_price = self.strategy.calculate_stop_loss_take_profit(signal, current_price)
            
            logger.info(f"💰 Position size: {position_size:.4f} {'(+15% confluence boost)' if is_confluence else ''}")
            logger.info(f"🛡️ Stop loss: ${stop_loss_price:.4f}")
            logger.info(f"🎯 Take profit: ${take_profit_price:.4f}")
            
            # Simulate trade execution (replace with actual exchange calls)
            order_success = True  # Placeholder for actual order execution
            
            if order_success:
                # Record execution time
                execution_time = (time.time() - start_time) * 1000
                self.execution_times.append(execution_time)
                
                # Create enhanced position record
                position = {
                    'symbol': symbol,
                    'side': signal_type,
                    'size': position_size,
                    'entry_price': current_price,
                    'current_price': current_price,
                    'unrealized_pnl': 0.0,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price,
                    'is_confluence': is_confluence,
                    'confidence': signal.get('confidence', 0),
                    'volume_ratio': signal.get('volume_ratio', 0),
                    'timestamp': datetime.now()
                }
                
                self.active_positions.append(position)
                
                logger.success(f"✅ Enhanced trade executed successfully in {execution_time:.1f}ms")
                self.log_activity(f"✅ {'🚀 Confluence' if is_confluence else '📈 Standard'} {signal_type} position opened on {symbol}", "SUCCESS")
                
                return True
            else:
                logger.error(f"❌ Trade execution failed for {symbol}")
                self.log_activity(f"❌ Trade execution failed for {symbol}", "ERROR")
                return False
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Enhanced trade execution error: {e}")
            self.log_activity(f"❌ Trade execution error: {e}", "ERROR")
            return False
    
    def execute_trade(self, signal: Dict) -> bool:
        """Execute a trade based on signal 💰"""
        
        try:
            if not self.connected or not self.exchange:
                logger.error("Cannot execute trade - not connected to exchange")
                self.log_activity("❌ Cannot execute trade - not connected to exchange", "ERROR")
                return False
                
            symbol = signal['symbol']
            signal_type = signal['type']
            current_price = signal['entry_price']
            
            # Bitget uses the symbol format directly (e.g., 'ALCH/USDT:USDT' for futures)
            # No conversion needed - use symbol as-is
            exchange_symbol = symbol
            logger.debug(f"🔄 Using symbol format: {exchange_symbol}")
            
            logger.info(f"🎯 Attempting to execute {signal_type} trade for {symbol} at ${current_price}")
            
            # Check if we can open position
            can_open, reason = self.risk_manager.can_open_position(signal, self.account_data.get('balance', 0))
            
            if not can_open:
                logger.warning(f"🚫 Trade rejected for {symbol}: {reason}")
                self.log_activity(f"🚫 Trade rejected: {reason}", "WARNING")
                return False
            
            # Calculate position size using risk manager
            logger.debug("Calculating position size...")
            position_size, risk_info = self.risk_manager.calculate_position_size(
                signal, self.account_data.get('balance', 0), current_price
            )
            logger.debug(f"Position size calculated: {position_size}, risk_info: {risk_info}")
            
            # Calculate stop loss and take profit using risk manager
            logger.debug("Calculating risk levels...")
            risk_levels = self.risk_manager.calculate_stop_loss_take_profit(
                signal, current_price, position_size
            )
            logger.debug(f"Risk levels: {risk_levels}")
            
            # Determine order side
            side = 'buy' if signal_type == 'LONG' else 'sell'
            logger.info(f"Placing {side} order for {symbol}: size={position_size}, price=${current_price}")
            
            # Place limit order (Bitget doesn't support market orders)
            # Adjust price slightly to ensure immediate execution
            price_adjustment = 0.001  # 0.1% adjustment
            if side == 'buy':
                # Buy slightly above current price
                limit_price = current_price * (1 + price_adjustment)
            else:
                # Sell slightly below current price  
                limit_price = current_price * (1 - price_adjustment)
                
            logger.info(f"📤 Placing {side} limit order: symbol={symbol} (exchange: {exchange_symbol}), size={position_size}, price=${limit_price:.6f}")
            
            try:
                # Use params for futures orders (Bitget-specific)
                params = {
                    'marginMode': 'cross',
                    'leverage': self.config.leverage,
                    'timeInForce': 'GTC',  # Good Till Cancelled - fixes "order validity period" error
                    'reduceOnly': False,   # New position, not closing
                    'postOnly': False      # Allow taker orders for immediate execution
                }
                
                # For Bitget, we need to set the position mode and leverage first
                try:
                    # Set position mode to one-way (unilateral) for simple trading
                    self.exchange.set_position_mode(False, exchange_symbol)
                except:
                    pass  # Ignore if already set or not supported
                
                try:
                    # Set leverage for the symbol
                    self.exchange.set_leverage(self.config.leverage, exchange_symbol)
                except Exception as leverage_error:
                    logger.warning(f"Could not set leverage: {leverage_error}")
                
                order = self.exchange.create_order(
                    symbol=exchange_symbol,
                    type='limit',
                    side=side,
                    amount=position_size,
                    price=limit_price,
                    params=params
                )
                
                logger.debug(f"Order response: {order}")
                logger.info(f"✅ Order placed successfully: ID={order.get('id', 'Unknown')}")
                
            except Exception as order_error:
                import traceback
                logger.error(f"❌ Order placement failed: {str(order_error)}")
                logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
                logger.error(f"🔍 Order parameters: symbol={symbol}, side={side}, amount={position_size}")
                logger.error(f"🔍 Exchange params: {params}")
                self.log_activity(f"❌ Order failed: {str(order_error)}", "ERROR")
                raise order_error
            
            if order and order.get('id'):
                logger.success(f"✅ Order executed successfully: {order['id']}")
                
                # Create position record
                position = {
                    'symbol': symbol,
                    'side': signal_type.lower(),
                    'entry_price': current_price,
                    'position_size': position_size,
                    'position_value': risk_info.get('adjusted_value', position_size * current_price),
                    'stop_loss': risk_levels['stop_loss'],
                    'take_profit': risk_levels['take_profit'],
                    'trailing_stop_distance': risk_levels.get('trailing_stop_distance'),
                    'order_id': order['id'],
                    'signal': signal
                }
                
                # Add to active positions and risk manager
                self.active_positions.append(position)
                self.risk_manager.add_position(position)
                
                self.total_trades += 1
                trade_msg = (f"💰 {signal_type} trade executed for {symbol.replace('/USDT:USDT', '')} "
                           f"| Size: {position_size:.4f} | Entry: ${current_price:.4f}")
                logger.success(trade_msg)
                self.log_activity(trade_msg, "TRADE")
                
                # Log position details
                logger.info(f"📊 Position opened: SL=${risk_levels['stop_loss']:.4f} | TP=${risk_levels['take_profit']:.4f}")
                self.log_activity(f"📊 Position limits: SL=${risk_levels['stop_loss']:.4f} | TP=${risk_levels['take_profit']:.4f}", "INFO")
                
                # Update display stats
                if hasattr(self.display, 'update_stats'):
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
            
            # Try to handle specific Bitget order errors
            error_str = str(e).lower()
            if "minimum order size" in error_str:
                logger.error("💡 Suggestion: Increase position size to meet minimum requirements")
            elif "invalid symbol" in error_str:
                logger.error("💡 Suggestion: Check if symbol is available for futures trading")
            elif "precision" in error_str:
                logger.error("💡 Suggestion: Adjust price/amount precision")
            
            self.log_activity(error_msg, "ERROR")
            return False
            
        except ccxt.NetworkError as e:
            error_msg = f"🌐 Network error for {symbol}: {str(e)}"
            logger.error(error_msg)
            logger.info("🔄 Retrying order in 2 seconds...")
            
            # Retry once for network errors
            try:
                import time
                time.sleep(2)
                if self.exchange is not None:
                    order = self.exchange.create_order(
                        symbol=exchange_symbol,
                        type='limit',
                        side=side,
                        amount=position_size,
                        price=limit_price,
                        params=params
                    )
                    if order and order.get('id'):
                        logger.success(f"✅ Order executed successfully on retry: {order['id']}")
                        return True
                else:
                    logger.error("❌ Exchange is None during retry")
            except Exception as retry_error:
                logger.error(f"❌ Retry also failed: {retry_error}")
            
            self.log_activity(error_msg, "ERROR")
            return False
            
        except ccxt.ExchangeError as e:
            import traceback
            error_msg = f"🏦 Exchange error for {symbol}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            logger.error(f"🔍 Order parameters: symbol={symbol}, side={side}, amount={position_size}, price={limit_price}")
            logger.error(f"🔍 Exchange params: {params}")
            
            # Common Bitget-specific error handling
            error_str = str(e).lower()
            if "order validity period" in error_str:
                logger.error("💡 Suggestion: timeInForce parameter issue - using GTC")
            elif "leverage" in error_str:
                logger.error("💡 Suggestion: Set leverage first or check leverage limits")
            elif "position mode" in error_str:
                logger.error("💡 Suggestion: Set position mode to hedge first")
            
            self.log_activity(error_msg, "ERROR")
            return False
            
        except Exception as e:
            import traceback
            error_msg = f"❌ Trade execution failed for {symbol}: {str(e)}"
            logger.exception(f"Trade execution failed for {symbol}")
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            logger.error(f"🔍 Order parameters: symbol={symbol}, side={side}, amount={position_size}, price={limit_price}")
            logger.error(f"🔍 Exchange params: {params}")
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
                
                if not self.connected or not self.exchange:
                    logger.warning("Cannot monitor positions - not connected to exchange")
                    return
                
                # Fetch current price
                ticker = self.exchange.fetch_ticker(symbol)
                last_price = ticker.get('last', 0)
                current_price = float(last_price) if last_price is not None else 0.0
                
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
            if not self.connected or not self.exchange:
                logger.error("Cannot close position - not connected to exchange")
                return
                
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
                    if hasattr(self.display, 'update_stats'):
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
                        position_list = [{'symbol': pos['symbol'], 'side': pos['side']} for pos in self.active_positions]
                        if self.strategy.should_enter_trade(signal, self.account_data.get('balance', 0), position_list):
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
        """📊 Get enhanced data for next-gen display"""
        
        # Get recent signals with confluence information
        recent_signals = self.current_signals[-20:] if self.current_signals else []
        
        # Enhanced status determination
        if not hasattr(self, 'connected') or not self.connected:
            status = "❌ DISCONNECTED"
        elif hasattr(self.risk_manager, 'trading_halted') and self.risk_manager.trading_halted:
            status = "🛑 TRADING HALTED"
        elif hasattr(self, 'running') and self.running:
            status = "🟢 ACTIVE SCALPING"
        else:
            status = "⏸️ STANDBY"
        
        return {
            'account_data': self.account_data,
            'positions': self.active_positions,
            'signals': recent_signals,
            'logs': self.activity_log[-15:] if self.activity_log else [],
            'errors': self.error_log[-10:] if hasattr(self, 'error_log') and self.error_log else [],
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
        """🚀 Start the enhanced Alpine trading bot with professional display"""
        
        # Initialize display data
        self.log_activity("🚀 Initializing Alpine Bot v2.0", "INFO")
        
        # Set running state
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            self.log_activity("⏹️ Shutdown signal received", "WARNING")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize exchange connection
        if not self.initialize_exchange():
            self.log_activity("❌ Failed to initialize exchange. Exiting.", "ERROR")
            return
        
        # Initialize strategies
        self.log_activity("📈 Loading trading strategies", "INFO")
        
        # Start background trading thread with enhanced error handling
        self.trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.trading_thread.start()
        self.log_activity("🔄 Trading thread started", "INFO")
        logger.info("Trading thread started")
        
        # Display optimization variables
        last_display_update = time.time()
        display_update_interval = 1.0  # Update display every 1 second
        
        try:
            # Initialize display data first
            self.log_activity("🎨 Initializing display interface", "INFO")
            initial_data = self.get_display_data()
            
            # Run stable display with consistent refresh rate
            with Live(
                self.display.create_revolutionary_layout(**initial_data),
                console=self.display.console,
                refresh_per_second=1,  # Stable 1 FPS
                screen=True
            ) as live:
                
                self.log_activity("✅ Display interface ready - Alpine Bot running!", "SUCCESS")
                
                while self.running:
                    current_time = time.time()
                    
                    # Only update display at consistent intervals
                    if current_time - last_display_update >= display_update_interval:
                        try:
                            display_data = self.get_display_data()
                            live.update(self.display.create_revolutionary_layout(**display_data))
                            last_display_update = current_time
                        except Exception as e:
                            self.log_activity(f"⚠️ Display update error: {str(e)}", "WARNING")
                    
                    # Consistent sleep interval
                    time.sleep(0.5)  # Sleep for half the display update interval
                    
        except KeyboardInterrupt:
            logger.warning("⏹️ Shutdown signal received")
            self.log_activity("⏹️ Shutdown signal received", "WARNING")
            self.running = False
            
        except Exception as e:
            error_msg = f"❌ Display error: {str(e)}"
            logger.exception("Display error")
            self.log_activity(error_msg, "ERROR")
            # Don't exit immediately on display errors, try to continue
            self.log_activity("🔄 Attempting to continue without display...", "WARNING")
            
            # Fallback - run without display
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
            
        finally:
            self.cleanup()
            logger.info("👋 Alpine bot shutdown complete")
            self.log_activity("👋 Alpine bot shutdown complete", "INFO")

def main():
    """Main entry point 🏔️"""
    try:
        # Kill all other Alpine bot processes first
        manager = AlpineBotManager()
        console = Console()
        
        console.print("🤖 [bold cyan]ALPINE BOT V2.0 STARTING[/bold cyan]")
        console.print("🔄 [yellow]Scanning for existing bot processes...[/yellow]")
        
        # Kill all other Alpine/trading bot processes 
        killed_count = manager.kill_alpine_processes(exclude_current=True)
        
        if killed_count > 0:
            console.print(f"✅ [green]Successfully killed {killed_count} existing bot processes[/green]")
            time.sleep(1)  # Give time for processes to fully terminate
        else:
            console.print("✅ [green]No existing bot processes found[/green]")
        
        console.print("🚀 [bold green]Starting new Alpine Bot instance...[/bold green]")
        
        # Create and run Alpine bot
        bot = AlpineBot()
        bot.run()
    except KeyboardInterrupt:
        console.print("\n👋 Alpine bot terminated by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Fatal error: {str(e)}", style="red")
        logger.exception("Fatal error in main")

if __name__ == "__main__":
    # Display startup banner
    console = Console()
    console.print("\n" + "="*60, style="bold cyan")
    console.print("🏔️  ALPINE TRADING BOT V2.0", style="bold green", justify="center")
    console.print("Volume Anomaly Strategy | 90% Success Rate", style="cyan", justify="center") 
    console.print("Beautiful Mint Green Terminal Interface", style="green", justify="center")
    console.print("🛑 AUTO-KILL OTHER BOTS ENABLED", style="bold red", justify="center")
    console.print("="*60 + "\n", style="bold cyan")
    
    main()