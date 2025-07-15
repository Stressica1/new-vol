"""
Alpine Trading Bot - Core Bot Engine
===================================

Main bot engine that orchestrates all trading operations.
Enhanced with comprehensive logging and error handling.
"""

import threading
import time
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from .config import TradingConfig
from .manager import AlpineBotManager
from ..trading.strategy import VolumeAnomalyStrategy
from ..trading.risk_manager_v2 import AlpineRiskManager
from ..exchange.bitget_client import BitgetClient
from ..ui.display import AlpineDisplay

# Import enhanced logging
try:
    from enhanced_logging import alpine_logger, EnhancedErrorHandler, log_function_calls
except ImportError:
    # Fallback if enhanced logging not available
    def log_function_calls(func):
        return func
    
    class EnhancedErrorHandler:
        def __init__(self, name, reraise=False):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
    
    class alpine_logger:
        @staticmethod
        def log_exception(exc, context=""):
            logger.error(f"Exception in {context}: {exc}")


class AlpineBot:
    """
    Main Alpine Trading Bot Engine
    
    Orchestrates all trading operations including:
    - Market data collection
    - Signal analysis
    - Risk management
    - Trade execution
    - Real-time monitoring
    """
    
    @log_function_calls
    def __init__(self, config: Optional[TradingConfig] = None):
        """Initialize the Alpine Trading Bot"""
        logger.info("🏔️ Initializing Alpine Trading Bot...")
        
        self.config = config or TradingConfig()
        self.running = False
        self.setup_logging()
        self.setup_signal_handlers()
        
        # Initialize components with error handling
        with EnhancedErrorHandler("Component Initialization"):
            self.exchange_client = BitgetClient(self.config)
            logger.success("✅ Exchange client initialized")
            
            self.strategy = VolumeAnomalyStrategy(self.config)
            logger.success("✅ Trading strategy initialized")
            
            self.risk_manager = AlpineRiskManager(self.config)
            logger.success("✅ Risk manager initialized")
            
            self.display = AlpineDisplay(self.config)
            logger.success("✅ Display system initialized")
            
            self.bot_manager = AlpineBotManager(self.config)
            logger.success("✅ Bot manager initialized")
        
        # Runtime data
        self.market_data = {}
        self.positions = []
        self.signals = []
        self.logs = []
        
        logger.success("� Alpine Trading Bot initialization completed")
    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            logger.remove()
            logger.add(
                "logs/alpine_bot_{time:YYYY-MM-DD}.log",
                rotation="1 day",
                retention="30 days",
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
                backtrace=True,
                diagnose=True
            )
            logger.info("🔧 Logging system initialized")
        except Exception as e:
            print(f"❌ Failed to setup logging: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.debug("🔧 Signal handlers configured")
        except Exception as e:
            logger.error(f"❌ Failed to setup signal handlers: {e}")
            alpine_logger.log_exception(e, "Signal Handler Setup")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.warning(f"⚠️ Received signal {signum}, initiating graceful shutdown...")
        self.stop()
    
    @log_function_calls
    def start(self):
        """Start the trading bot"""
        logger.info("🚀 Starting Alpine Trading Bot...")
        
        with EnhancedErrorHandler("Bot Startup"):
            # Test connectivity first
            logger.info("🔌 Testing exchange connectivity...")
            if not self.exchange_client.test_connection():
                logger.error("❌ Failed to connect to exchange")
                return False
            
            logger.success("✅ Exchange connectivity confirmed")
            
            # Initialize components
            self.running = True
            
            # Start monitoring threads
            logger.info("🔄 Starting monitoring threads...")
            self._start_monitoring_threads()
            
            # Start the display
            logger.info("🖥️ Starting display system...")
            self.display.start(self)
            
            logger.success("🎉 Alpine Trading Bot started successfully")
            return True
    
    @log_function_calls
    def stop(self):
        """Stop the trading bot"""
        logger.info("🛑 Stopping Alpine Trading Bot...")
        self.running = False
        
        # Stop display
        if hasattr(self.display, 'stop'):
            self.display.stop()
        
        logger.info("Alpine Trading Bot stopped")
    
    @log_function_calls
    def _start_monitoring_threads(self):
        """Start background monitoring threads"""
        
        # Market data monitoring
        market_thread = threading.Thread(target=self._market_monitor_loop, daemon=True)
        market_thread.start()
        
        # Signal analysis
        signal_thread = threading.Thread(target=self._signal_analysis_loop, daemon=True)
        signal_thread.start()
        
        # Risk monitoring
        risk_thread = threading.Thread(target=self._risk_monitor_loop, daemon=True)
        risk_thread.start()
        
        logger.success("🔄 Background monitoring threads started")
    
    def _market_monitor_loop(self):
        """Monitor market data continuously"""
        logger.info("📊 Market monitoring loop started")
        
        while self.running:
            try:
                with EnhancedErrorHandler("Market Data Update"):
                    # Update market data
                    self._update_market_data()
                    time.sleep(1)  # 1 second intervals
                    
            except Exception as e:
                logger.error(f"❌ Market monitor error: {e}")
                alpine_logger.log_exception(e, "Market Monitor Loop")
                time.sleep(5)
        
        logger.info("📊 Market monitoring loop stopped")
    
    def _signal_analysis_loop(self):
        """Analyze signals continuously"""
        logger.info("🎯 Signal analysis loop started")
        
        while self.running:
            try:
                with EnhancedErrorHandler("Signal Analysis"):
                    # Analyze signals
                    self._analyze_signals()
                    time.sleep(5)  # 5 second intervals
                    
            except Exception as e:
                logger.error(f"❌ Signal analysis error: {e}")
                alpine_logger.log_exception(e, "Signal Analysis Loop")
                time.sleep(10)
        
        logger.info("🎯 Signal analysis loop stopped")
    
    def _risk_monitor_loop(self):
        """Monitor risk continuously"""
        logger.info("🛡️ Risk monitoring loop started")
        
        while self.running:
            try:
                with EnhancedErrorHandler("Risk Monitoring"):
                    # Update risk metrics
                    self._update_risk_metrics()
                    time.sleep(2)  # 2 second intervals
                    
            except Exception as e:
                logger.error(f"❌ Risk monitor error: {e}")
                alpine_logger.log_exception(e, "Risk Monitor Loop")
                time.sleep(5)
        
        logger.info("🛡️ Risk monitoring loop stopped")
    
    @log_function_calls
    def _update_market_data(self):
        """Update market data for all trading pairs"""
        try:
            # Get positions from exchange
            positions = self.exchange_client.get_positions()
            if positions:
                self.positions = positions
                logger.debug(f"📈 Updated {len(positions)} positions")
                
            # Update market data would go here
            # This will be implemented based on existing logic
            
        except Exception as e:
            logger.error(f"❌ Failed to update market data: {e}")
            alpine_logger.log_exception(e, "Market Data Update")
    
    @log_function_calls
    def _analyze_signals(self):
        """Analyze trading signals"""
        try:
            # Get signals from strategy
            signals = self.strategy.get_signals()
            if signals:
                self.signals = signals
                logger.debug(f"🎯 Generated {len(signals)} signals")
                
                # Log signal activity
                for signal in signals:
                    alpine_logger.log_signal(signal)
                    
        except Exception as e:
            logger.error(f"❌ Failed to analyze signals: {e}")
            alpine_logger.log_exception(e, "Signal Analysis")
    
    @log_function_calls
    def _update_risk_metrics(self):
        """Update risk management metrics"""
        try:
            # Get risk metrics from risk manager
            risk_metrics = self.risk_manager.get_current_risk_metrics()
            if risk_metrics:
                logger.debug(f"🛡️ Risk metrics updated: {risk_metrics}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update risk metrics: {e}")
            alpine_logger.log_exception(e, "Risk Metrics Update")
    
    @log_function_calls
    def run(self):
        """Main run method"""
        try:
            logger.info("🚀 Running Alpine Trading Bot...")
            
            if self.start():
                logger.success("✅ Bot started successfully, entering main loop")
                
                # Keep running until stopped
                while self.running:
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            self.stop()


def main():
    """Main entry point for the bot"""
    try:
        config = TradingConfig()
        bot = AlpineBot(config)
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()