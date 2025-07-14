"""
🏔️ Alpine Trading Bot Configuration
Beautiful mint green terminal displays with hunter green gradients
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class TradingConfig:
    """Alpine Trading Configuration 🏔️"""
    
    # 🔐 Bitget API Credentials
    API_KEY: str = "bg_5400882ef43c5596ffcf4af0c697b250"
    API_SECRET: str = "60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45"
    PASSPHRASE: str = "22672267"
    SANDBOX: bool = False  # Set to True for testing
    
    # 💰 Trading Parameters - OPTIMIZED FOR HIGH VOLATILITY COINS
    max_daily_loss_pct: float = 50.0
    max_positions: int = 25  # Increased for more diversification across volatile coins
    position_size_pct: float = 1.5  # Reduced size per position due to higher volatility
    stop_loss_pct: float = 3.0  # Increased stop loss for volatile coins
    take_profit_pct: float = 5.0  # Increased take profit for bigger moves
    max_drawdown_pct: float = 50.0
    trailing_stop: bool = True
    trailing_stop_pct: float = 1.5  # Increased trailing stop for volatility
    
    # 🎯 Strategy Parameters (Volume Anomaly - TUNED FOR VOLATILITY)
    volume_lookback: int = 15  # Reduced for faster signals on volatile coins
    volume_std_multiplier: float = 1.8  # Reduced for more frequent signals
    min_volume_ratio: float = 3.3  # Minimum volume spike ratio for signal generation
    supertrend_atr_period: int = 8  # Reduced for faster trend detection
    supertrend_multiplier: float = 2.5  # Reduced for more sensitive signals
    
    # ⏱️ Timeframe Configuration - SHORT-TERM FOCUS
    timeframes: List[str] = field(default_factory=lambda: ['1m', '3m', '5m', '15m'])  # Only scan these timeframes
    primary_timeframe: str = '1m'  # Primary timeframe for execution
    signal_confluence_required: int = 2  # Minimum timeframes agreeing for signal
    
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

# 📈 Supported Trading Pairs - HIGH VOLATILITY & LOW PRICE FOCUS (NO BTC/ETH)
# These are the most volatile and highest ticking coins under $500 - ALL VERIFIED AVAILABLE
TRADING_PAIRS = [
    # MEME COINS - EXTREME VOLATILITY (ALL UNDER $1)
    'DOGE/USDT:USDT',      # Dogecoin - High volatility, under $1
    'SHIB/USDT:USDT',      # Shiba Inu - Micro-cap, extreme volatility
    'PEPE/USDT:USDT',      # Pepe - Meme coin, high volatility
    'FLOKI/USDT:USDT',     # Floki - Meme coin, high volatility
    'WIF/USDT:USDT',       # Dogwifhat - Solana meme, extreme volatility
    'GOAT/USDT:USDT',      # Goatseus Maximus - Viral meme, extreme volatility
    'PNUT/USDT:USDT',      # Peanut - Trending meme, high volatility
    'POPCAT/USDT:USDT',    # Popcat - Meme coin, high volatility
    'TURBO/USDT:USDT',     # Turbo - AI meme coin, high volatility
    'MOODENG/USDT:USDT',   # Moo Deng - Trending meme, extreme volatility
    
    # LOW-CAP ALTCOINS - HIGH VOLATILITY (ALL UNDER $100)
    'ADA/USDT:USDT',       # Cardano - Under $1, high volatility
    'DOT/USDT:USDT',       # Polkadot - Under $10, high volatility
    'LINK/USDT:USDT',      # Chainlink - Under $50, high volatility
    'AVAX/USDT:USDT',      # Avalanche - Under $100, high volatility
    'GALA/USDT:USDT',      # Gala - Under $1, gaming token, high volatility
    
    # TRENDING ALTCOINS - EXTREME VOLATILITY (ALL UNDER $10)
    'XRP/USDT:USDT',       # XRP - Under $5, high volatility
    'XLM/USDT:USDT',       # Stellar - Under $1, extreme volatility
    'ALGO/USDT:USDT',      # Algorand - Under $1, high volatility
    'HBAR/USDT:USDT',      # Hedera - Under $1, high volatility
    'SUI/USDT:USDT',       # Sui - Under $10, trending, high volatility
    
    # MICRO-CAP GEMS - MAXIMUM VOLATILITY (ALL UNDER $5)
    'PENGU/USDT:USDT',     # Pudgy Penguins - Under $1, extreme volatility
    'VIRTUAL/USDT:USDT',   # Virtuals Protocol - Under $5, high volatility
    'ENA/USDT:USDT',       # Ethena - Under $2, high volatility
    'ACT/USDT:USDT',       # Act - AI token, extreme volatility
    'MEME/USDT:USDT',      # Meme - Meta meme coin, high volatility
    'CHILLGUY/USDT:USDT'   # Chill Guy - Trending meme, extreme volatility
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
