#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Enhanced Logging & Traceback System
Comprehensive logging upgrade with detailed error tracking and debugging capabilities
"""

import sys
import os
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from loguru import logger
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class AlpineLogger:
    """Enhanced logging system for Alpine Trading Bot"""
    
    def __init__(self, name: str = "Alpine", log_level: str = "DEBUG"):
        self.name = name
        self.log_level = log_level
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Remove default logger
        logger.remove()
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Console logging with colors
        logger.add(
            sys.stderr,
            level=self.log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # File logging - Debug level
        logger.add(
            log_dir / f"alpine_debug_{datetime.now().strftime('%Y%m%d')}.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="100 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # File logging - Info level
        logger.add(
            log_dir / f"alpine_info_{datetime.now().strftime('%Y%m%d')}.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="50 MB",
            retention="14 days",
            compression="zip"
        )
        
        # Error logging with full traceback
        logger.add(
            log_dir / f"alpine_errors_{datetime.now().strftime('%Y%m%d')}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Trading activity log
        logger.add(
            log_dir / f"alpine_trading_{datetime.now().strftime('%Y%m%d')}.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            rotation="20 MB",
            retention="30 days",
            filter=lambda record: "TRADE" in record["message"] or "SIGNAL" in record["message"]
        )
        
        logger.info(f"🏔️ Alpine Logger initialized for {self.name}")
    
    def log_system_info(self):
        """Log comprehensive system information"""
        logger.info("=" * 80)
        logger.info("🏔️ ALPINE TRADING BOT - SYSTEM INFORMATION")
        logger.info("=" * 80)
        logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🐍 Python Version: {sys.version}")
        logger.info(f"💻 Platform: {sys.platform}")
        logger.info(f"📁 Working Directory: {os.getcwd()}")
        logger.info(f"🔧 Python Path: {sys.path[:3]}...")
        logger.info("=" * 80)
    
    def log_config(self, config: Dict[str, Any]):
        """Log configuration safely (without sensitive data)"""
        logger.info("⚙️ CONFIGURATION LOADED")
        logger.info("-" * 40)
        
        # Safe config logging (mask sensitive data)
        safe_config = {}
        for key, value in config.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'pass']):
                safe_config[key] = "*" * 8
            else:
                safe_config[key] = value
        
        logger.info(f"📋 Config: {json.dumps(safe_config, indent=2, default=str)}")
        logger.info("-" * 40)
    
    def log_exception(self, exc: Exception, context: str = ""):
        """Log exception with comprehensive details"""
        logger.error(f"💥 EXCEPTION OCCURRED: {context}")
        logger.error(f"🔥 Exception Type: {type(exc).__name__}")
        logger.error(f"📝 Exception Message: {str(exc)}")
        
        # Get caller information
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_frame = frame.f_back
            logger.error(f"📍 Location: {caller_frame.f_code.co_filename}:{caller_frame.f_lineno} in {caller_frame.f_code.co_name}")
        
        # Full traceback
        tb_str = traceback.format_exc()
        logger.error(f"🕸️ Full Traceback:\n{tb_str}")
        
        # Additional context if available
        if hasattr(exc, '__dict__'):
            logger.error(f"🔍 Exception Details: {exc.__dict__}")
    
    def log_trade_activity(self, activity_type: str, symbol: str, details: Dict[str, Any]):
        """Log trading activity with structured data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "type": activity_type,
            "symbol": symbol,
            "details": details
        }
        
        logger.info(f"📊 TRADE {activity_type.upper()}: {symbol} | {json.dumps(details, default=str)}")
    
    def log_signal(self, signal_data: Dict[str, Any]):
        """Log trading signals with detailed information"""
        logger.info(f"🎯 SIGNAL DETECTED: {json.dumps(signal_data, indent=2, default=str)}")
    
    def log_performance(self, performance_data: Dict[str, Any]):
        """Log performance metrics"""
        logger.info(f"📈 PERFORMANCE UPDATE: {json.dumps(performance_data, indent=2, default=str)}")

# Global logger instance
alpine_logger = AlpineLogger()

# Enhanced exception handler
def enhanced_exception_handler(exc_type, exc_value, exc_traceback):
    """Enhanced global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        logger.warning("⏹️ Keyboard interrupt received - shutting down gracefully")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("💥 UNHANDLED EXCEPTION OCCURRED")
    logger.error(f"🔥 Exception Type: {exc_type.__name__}")
    logger.error(f"📝 Exception Message: {str(exc_value)}")
    logger.error(f"🕸️ Traceback:\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}")
    
    # Log system state at time of crash
    logger.error(f"📅 Crash Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.error(f"💻 Current Working Directory: {os.getcwd()}")
    logger.error(f"🔧 Python Version: {sys.version}")

# Set the enhanced exception handler
sys.excepthook = enhanced_exception_handler

# Context manager for enhanced error handling
class EnhancedErrorHandler:
    """Context manager for enhanced error handling"""
    
    def __init__(self, operation_name: str, reraise: bool = False):
        self.operation_name = operation_name
        self.reraise = reraise
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"🚀 Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.success(f"✅ Operation completed successfully: {self.operation_name} ({duration:.2f}s)")
        else:
            logger.error(f"❌ Operation failed: {self.operation_name} ({duration:.2f}s)")
            alpine_logger.log_exception(exc_value, f"Operation: {self.operation_name}")
            
            if self.reraise:
                return False  # Re-raise the exception
            else:
                return True  # Suppress the exception

# Decorator for enhanced function logging
def log_function_calls(func):
    """Decorator to log function calls with parameters and return values"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # Log function entry
        logger.debug(f"🔄 Entering {func_name}")
        logger.debug(f"📋 Args: {args[:3]}{'...' if len(args) > 3 else ''}")
        logger.debug(f"📋 Kwargs: {list(kwargs.keys())}")
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.debug(f"✅ {func_name} completed successfully ({duration:.3f}s)")
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {func_name} failed ({duration:.3f}s)")
            alpine_logger.log_exception(e, f"Function: {func_name}")
            raise
    
    return wrapper

# Utility functions for logging
def log_startup_banner():
    """Log startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                          🏔️  ALPINE TRADING BOT - ENHANCED LOGGING  🏔️                        ║
    ║                      Next-Generation AI-Powered Trading with Full Debugging                    ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
    """
    logger.info(banner)
    alpine_logger.log_system_info()

def log_shutdown():
    """Log shutdown information"""
    logger.info("⏹️ ALPINE TRADING BOT SHUTTING DOWN")
    logger.info(f"📅 Shutdown Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("👋 Thank you for using Alpine Trading Bot!")

# Initialize logging on import
if __name__ == "__main__":
    log_startup_banner()
    logger.info("🧪 Enhanced logging system test completed successfully!")
