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
    
    # 💰 Trading Parameters - OPTIMIZED FOR 1M/3M HIGH WIN RATE STRATEGY
    max_daily_loss_pct: float = 50.0
    max_positions: int = 30  # Increased for rapid scalping on 1m/3m
    position_size_pct: float = 2.0  # Base position size (2% of account)
    confluence_position_multiplier: float = 1.15  # +15% size on confluence signals
    stop_loss_pct: float = 1.5  # Tighter stops for scalping (will be dynamic)
    take_profit_pct: float = 3.0  # Quick profits for scalping
    max_drawdown_pct: float = 30.0  # Tighter drawdown control
    trailing_stop: bool = True
    trailing_stop_pct: float = 0.8  # Tight trailing for scalping
    
    # 🎯 Strategy Parameters (Volume Anomaly - TUNED FOR 1M/3M SCALPING)
    volume_lookback: int = 10  # Faster signals for scalping
    volume_std_multiplier: float = 1.5  # More sensitive for frequent signals
    min_volume_ratio: float = 2.8  # Lower threshold for more signals
    supertrend_atr_period: int = 6  # Faster trend detection for scalping
    supertrend_multiplier: float = 2.0  # More sensitive signals
    
    # ⚡ Dynamic Stop Loss Configuration (ATR-based volatility)
    use_dynamic_stop_loss: bool = True
    atr_period: int = 14  # Period for ATR calculation
    atr_multiplier: float = 1.5  # ATR multiplier for dynamic stops
    min_stop_loss_pct: float = 0.5  # Minimum stop loss (0.5%)
    max_stop_loss_pct: float = 3.0  # Maximum stop loss (3.0%)
    
    # ⏱️ Timeframe Configuration - FOCUS ON 1M/3M (HIGHEST WIN RATES)
    timeframes: List[str] = field(default_factory=lambda: ['1m', '3m'])  # Only highest win rate timeframes
    primary_timeframe: str = '1m'  # Primary execution timeframe
    signal_confluence_required: int = 2  # Both timeframes must agree for confluence
    confluence_confidence_boost: float = 0.15  # +15% confidence on confluence signals
    
    # 📊 Display Settings - Enhanced for real-time scalping
    refresh_rate: float = 0.3  # Faster refresh for scalping (300ms)
    max_log_lines: int = 50  # Reduced for cleaner display
    
    # 🎨 UI Colors (Enhanced Mint Green Cyber Theme)
    COLORS = {
        'primary': '#00FFB3',      # Mint Green
        'secondary': '#355E3B',    # Hunter Green
        'success': '#00FF7F',      # Spring Green
        'warning': '#FFD700',      # Gold
        'danger': '#FF4444',       # Bright Red
        'info': '#00BFFF',         # Deep Sky Blue
        'background': '#0D1117',   # GitHub Dark
        'text': '#F0F6FC',         # GitHub Text
        'accent': '#7C3AED',       # Purple Accent
        'chart_green': '#26A641',  # Chart Green
        'chart_red': '#DA3633',    # Chart Red
        'neon_cyan': '#00FFFF',    # Neon Cyan
        'neon_purple': '#9D4EDD',  # Neon Purple
        'gradient_start': '#00FFB3', # Mint Green
        'gradient_end': '#355E3B'    # Hunter Green
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

# Global config instance
config = TradingConfig()

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
