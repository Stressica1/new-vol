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
    
    # 💰 Trading Parameters - AGGRESSIVE 2% RISK STRATEGY (1M/3M HIGH WIN RATE)
    max_daily_loss_pct: float = 50.0  # Matches 50% max drawdown
    max_positions: int = 20  # Maximum 20 trades at 2% risk each
    position_size_pct: float = 2.0  # Base position size (2% of account)
    confluence_position_multiplier: float = 1.15  # +15% size on confluence signals
    stop_loss_pct: float = 1.5  # Tighter stops for scalping (will be dynamic)
    take_profit_pct: float = 3.0  # Quick profits for scalping
    max_drawdown_pct: float = 30.0  # Tighter drawdown control
    trailing_stop: bool = True
    trailing_stop_pct: float = 0.8  # Tight trailing for scalping
    leverage: int = 1  # Leverage for futures trading (1x = no leverage)
    
    # 🎯 Strategy Parameters (Volume Anomaly - TUNED FOR 3M SCALPING)
    volume_lookback: int = 10  # Faster signals for scalping
    volume_std_multiplier: float = 1.5  # More sensitive for frequent signals
    min_volume_ratio: float = 2.8  # Lower threshold for more signals
    supertrend_atr_period: int = 6  # Faster trend detection for scalping
    supertrend_multiplier: float = 2.0  # More sensitive signals
    
    # 📊 Signal Quality Configuration - HIGH CONVICTION TRADING
    min_signal_confidence: float = 75.0  # Minimum 75% confidence for signal generation
    min_trade_confidence: float = 75.0  # Minimum 75% confidence for trade execution
    confluence_min_confidence: float = 75.0  # Minimum confidence for confluence signals (same as single TF now)
    
    # ⚡ Dynamic Stop Loss Configuration (ATR-based volatility)
    use_dynamic_stop_loss: bool = True
    atr_period: int = 14  # Period for ATR calculation
    atr_multiplier: float = 1.5  # ATR multiplier for dynamic stops
    min_stop_loss_pct: float = 0.5  # Minimum stop loss (0.5%)
    max_stop_loss_pct: float = 3.0  # Maximum stop loss (3.0%)
    
    # 🛡️ Risk Management Configuration - AGGRESSIVE 2% PER TRADE STRATEGY
    max_daily_loss: float = 1000.0  # Maximum daily loss in USDT (50% of typical account)
    max_position_size: float = 200.0  # Maximum position size in USDT (increased for 2% risk)
    max_drawdown: float = 0.50  # Maximum drawdown (50% - AGGRESSIVE)
    max_open_positions: int = 20  # Maximum 20 trades at 2% each = 40% max exposure
    risk_per_trade: float = 0.02  # Risk per trade (2% of account - CONFIRMED)
    stop_loss_percentage: float = 0.015  # Stop loss percentage (1.5%)
    take_profit_percentage: float = 0.03  # Take profit percentage (3%)
    enable_stop_loss: bool = True
    enable_take_profit: bool = True
    
    # ⏱️ Timeframe Configuration - FOCUS ON 3M ONLY (HIGH WIN RATE)
    timeframes: List[str] = field(default_factory=lambda: ['3m'])  # Only 3-minute timeframe for cleaner signals
    primary_timeframe: str = '3m'  # Primary execution timeframe
    signal_confluence_required: int = 1  # Only one timeframe available
    confluence_confidence_boost: float = 0.15  # +15% confidence on confluence signals
    
    # �� Display Settings - Optimized for stable terminal display
    refresh_rate: float = 1.0  # Stable 1-second refresh for consistent display
    display_refresh_per_second: int = 1  # Rich Live display refresh rate
    display_update_throttle: float = 1.0  # Minimum time between display updates
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
