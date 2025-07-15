"""
Alpine Trading Bot - Professional Volume Anomaly Trading System
================================================================

A production-ready trading bot implementing volume anomaly detection
strategies with professional risk management and real-time monitoring.

Components:
- Core: Bot engine, configuration, and management
- Trading: Strategy implementation and position sizing
- Exchange: Exchange connectors and order management
- UI: Terminal-based user interface with real-time displays
"""

__version__ = "2.0.0"
__author__ = "Alpine Development Team"

from .core.bot import AlpineBot
from .core.config import TradingConfig
from .core.manager import AlpineBotManager

__all__ = [
    "AlpineBot",
    "TradingConfig", 
    "AlpineBotManager",
    "__version__",
]