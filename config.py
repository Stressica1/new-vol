"""
🏔️ Alpine Trading Bot Configuration
Beautiful mint green terminal displays with hunter green gradients
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TradingConfig:
    """Alpine Trading Configuration 🏔️"""
    
    # 🔐 Bitget API Credentials
    API_KEY: str = "bg_5400882ef43c5596ffcf4af0c697b250"
    API_SECRET: str = "60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45"
    PASSPHRASE: str = "22672267"
    SANDBOX: bool = False  # Set to True for testing
    
    # 💰 Trading Parameters
    max_daily_loss_pct: float = 50.0
    max_positions: int = 20
    position_size_pct: float = 2.5
    stop_loss_pct: float = 2.5
    take_profit_pct: float = 3.0
    max_drawdown_pct: float = 50.0
    trailing_stop: bool = True
    trailing_stop_pct: float = 1.0
    
    # 🎯 Strategy Parameters (Volume Anomaly from PineScript)
    volume_lookback: int = 20
    volume_std_multiplier: float = 2.0
    supertrend_atr_period: int = 10
    supertrend_multiplier: float = 3.0
    
    # 📊 Display Settings
    refresh_rate: float = 1.0  # seconds
    max_log_lines: int = 100
    
    # 🎨 UI Colors (Mint Green Theme)
    COLORS = {
        'primary': '#00FFB3',      # Mint Green
        'secondary': '#355E3B',    # Hunter Green
        'success': '#00FF7F',      # Spring Green
        'warning': '#FFB347',      # Peach
        'danger': '#FF6B6B',       # Light Red
        'info': '#87CEEB',         # Sky Blue
        'background': '#1E1E1E',   # Dark Gray
        'text': '#FFFFFF',         # White
        'accent': '#98FB98'        # Pale Green
    }

# 📈 Supported Trading Pairs
TRADING_PAIRS = [
    'BTC/USDT:USDT',
    'ETH/USDT:USDT', 
    'SOL/USDT:USDT',
    'ADA/USDT:USDT',
    'MATIC/USDT:USDT',
    'LINK/USDT:USDT',
    'DOT/USDT:USDT',
    'AVAX/USDT:USDT'
]

# 🚀 Bot Settings
BOT_NAME = "Alpine"
VERSION = "v1.0.0"
AUTHOR = "Alpine Trading Systems"

def get_exchange_config() -> Dict[str, Any]:
    """Get Bitget exchange configuration"""
    config = TradingConfig()
    return {
        'apiKey': config.API_KEY,
        'secret': config.API_SECRET,
        'password': config.PASSPHRASE,
        'sandbox': config.SANDBOX,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # For futures trading
            'marginMode': 'isolated'
        }
    }