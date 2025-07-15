#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Configuration
"""

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TradingConfig:
    """Trading configuration"""
    
    # API Configuration
    API_KEY: str = "bg_5400882ef43c5596ffcf4af0c697b250"
    API_SECRET: str = "60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45"
    PASSPHRASE: str = "22672267"
    SANDBOX: bool = False
    
    # Trading parameters
    max_positions: int = 20
    position_size_pct: float = 9.5  # Adjusted to target $175 notional with 50x leverage
    stop_loss_pct: float = 1.5
    take_profit_pct: float = 3.0
    leverage: int = 50  # Set to 50x leverage
    min_order_size: float = 5.0  # Reduced from 10.0 to 5.0
    max_hold_time_hours: int = 12  # Maximum position hold time in hours
    
    # Strategy parameters
    volume_lookback: int = 20
    volume_std_multiplier: float = 1.2
    min_volume_ratio: float = 2.75
    min_signal_confidence: float = 50.0  # Lowered from 60.0 to enable more signals for trading
    min_trade_confidence: float = 65.0
    
    # Timeframes
    timeframes: List[str] = None
    primary_timeframe: str = "3m"
    
    def __post_init__(self):
        # Force 3m timeframe only for consistency
        self.timeframes = ["3m"]
        self.primary_timeframe = "3m"

def get_exchange_config() -> Dict:
    """Get exchange configuration"""
    config = TradingConfig()
    
    return {
        'apiKey': config.API_KEY,
        'secret': config.API_SECRET,
        'password': config.PASSPHRASE,
        'sandbox': config.SANDBOX,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',
            'marginMode': 'cross'
        }
    }

# Trading pairs
TRADING_PAIRS = [
    'BTC/USDT:USDT',
    'ETH/USDT:USDT',
    'SOL/USDT:USDT',
    'BNB/USDT:USDT',
    'ADA/USDT:USDT',
    'DOT/USDT:USDT',
    'MATIC/USDT:USDT',
    'AVAX/USDT:USDT',
    'LINK/USDT:USDT',
    'UNI/USDT:USDT'
]

# Bot metadata
BOT_NAME = "Alpine Trading Bot"
VERSION = "2.0"

if __name__ == "__main__":
    config = TradingConfig()
    print(f"✅ {BOT_NAME} v{VERSION} configuration loaded")
    print(f"📊 Trading pairs: {len(TRADING_PAIRS)}")
    print(f"🎯 Primary timeframe: {config.primary_timeframe}")
