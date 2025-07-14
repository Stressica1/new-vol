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
    position_size_pct: float = 20.0  # Base position size (20% of account) - increased for small balance
    confluence_position_multiplier: float = 1.15  # +15% size on confluence signals
    stop_loss_pct: float = 1.5  # Tighter stops for scalping (will be dynamic)
    take_profit_pct: float = 3.0  # Quick profits for scalping
    max_drawdown_pct: float = 30.0  # Tighter drawdown control
    trailing_stop: bool = True
    trailing_stop_pct: float = 0.8  # Tight trailing for scalping
    leverage: int = 35  # Leverage for futures trading (35x minimum as requested)
    min_order_size: float = 10.0  # Minimum order size in USDT
    
    # 🎯 Strategy Parameters (Volume Anomaly - MATCHED TO TRADINGVIEW SETTINGS)
    volume_lookback: int = 20  # Matches TradingView "Volume Avg Lookback: 20"
    volume_std_multiplier: float = 1.2  # Reduced for more sensitivity
    min_volume_ratio: float = 2.75  # Minimum 2.75x volume ratio as requested
    supertrend_atr_period: int = 6  # Reduced for faster signals (was 10)
    supertrend_multiplier: float = 2.0  # Reduced for more sensitivity (was 3.0)
    
    # 📐 Fibonacci Golden Zone Parameters
    fib_pivot_length: int = 20  # Pivot lookback period
    fib_golden_zone_low: float = 0.7  # Golden zone lower bound (70%)
    fib_golden_zone_high: float = 0.885  # Golden zone upper bound (88.5%)
    
    # 📊 Signal Quality Configuration - OPTIMIZED FOR MORE SIGNALS
    min_signal_confidence: float = 60.0  # Reduced from 75% to 60% for more signals
    min_trade_confidence: float = 65.0  # Minimum 65% confidence for trade execution
    confluence_min_confidence: float = 70.0  # Higher confidence required for confluence signals
    
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
# 🚀 VERIFIED BITGET TRADING PAIRS - 150 HIGH-VOLATILITY COINS FOR MAXIMUM SIGNAL DETECTION
TRADING_PAIRS = [
    "$AI/USDT:USDT",  # $AI - AI token
    "$ALT/USDT:USDT",  # $ALT - Alternative layer
    "$DEGEN/USDT:USDT",  # $DEGEN - Base ecosystem meme
    "10000000AIDOGE/USDT:USDT",  # 10000000AIDOGE - AI meme
    "1000000MOG/USDT:USDT",  # 1000000MOG - Meme token
    "10000ELON/USDT:USDT",  # 10000ELON - Elon meme
    "10000WHY/USDT:USDT",  # 10000WHY - Meme token
    "1000BONK/USDT:USDT",  # 1000BONK - Solana meme
    "1000CAT/USDT:USDT",  # 1000CAT - Cat meme
    "1000RATS/USDT:USDT",  # 1000RATS - Bitcoin ordinal
    "1000SATS/USDT:USDT",  # 1000SATS - Bitcoin inscription
    "1000XEC/USDT:USDT",  # 1000XEC - eCash
    "1INCH/USDT:USDT",  # 1INCH - DEX aggregator
    "1MBABYDOGE/USDT:USDT",  # 1MBABYDOGE - Baby Doge
    "1MCHEEMS/USDT:USDT",  # 1MCHEEMS - Cheems meme
    "A/USDT:USDT",  # A - Arweave ecosystem
    "AAVE/USDT:USDT",  # AAVE - DeFi lending
    "ACE/USDT:USDT",  # ACE - Gaming token
    "ACH/USDT:USDT",  # ACH - Payment token
    "ACT/USDT:USDT",  # ACT - AI token
    "ACX/USDT:USDT",  # ACX - Cross-chain
    "ADA/USDT:USDT",  # ADA - Cardano
    "AERGO/USDT:USDT",  # AERGO - Enterprise blockchain
    "AERO/USDT:USDT",  # AERO - Base ecosystem
    "AEVO/USDT:USDT",  # AEVO - Options trading
    "AGI/USDT:USDT",  # AGI - AI token
    "AGLD/USDT:USDT",  # AGLD - Gaming token
    "AGT/USDT:USDT",  # AGT - Agent token
    "AI16Z/USDT:USDT",  # AI16Z - AI investment
    "AIN/USDT:USDT",  # AIN - AI network
    "AIOZ/USDT:USDT",  # AIOZ - Video streaming
    "AIXBT/USDT:USDT",  # AIXBT - AI trading
    "AKT/USDT:USDT",  # AKT - Cloud computing
    "ALCH/USDT:USDT",  # ALCH - Gaming token
    "ALGO/USDT:USDT",  # ALGO - Algorand
    "ALICE/USDT:USDT",  # ALICE - Gaming metaverse
    "ALPHA/USDT:USDT",  # ALPHA - DeFi protocol
    "ALPINE/USDT:USDT",  # ALPINE - Fan token
    "AMP/USDT:USDT",  # AMP - Payment token
    "ANIME/USDT:USDT",  # ANIME - Anime ecosystem
    "ANKR/USDT:USDT",  # ANKR - Web3 infrastructure
    "APE/USDT:USDT",  # APE - ApeCoin
    "API3/USDT:USDT",  # API3 - Oracle network
    "APT/USDT:USDT",  # APT - Aptos
    "AR/USDT:USDT",  # AR - Arweave
    "ARB/USDT:USDT",  # ARB - Arbitrum
    "ARC/USDT:USDT",  # ARC - Cross-chain
    "ARK/USDT:USDT",  # ARK - Blockchain platform
    "ARKM/USDT:USDT",  # ARKM - Analytics platform
    "ARPA/USDT:USDT",  # ARPA - Privacy computing
    "ASR/USDT:USDT",  # ASR - Fan token
    "ASRR/USDT:USDT",  # ASRR - Fan token
    "ASTR/USDT:USDT",  # ASTR - Polkadot parachain
    "ATA/USDT:USDT",  # ATA - Blockchain platform
    "ATH/USDT:USDT",  # ATH - AI token
    "ATOM/USDT:USDT",  # ATOM - Cosmos
    "AUCTION/USDT:USDT",  # AUCTION - NFT marketplace
    "AUDIO/USDT:USDT",  # AUDIO - Music streaming
    "AVA/USDT:USDT",  # AVA - Gaming metaverse
    "AVAAI/USDT:USDT",  # AVAAI - AI token
    "AVAIL/USDT:USDT",  # AVAIL - Data availability
    "AVAX/USDT:USDT",  # AVAX - Avalanche
    "AVL/USDT:USDT",  # AVL - Aviation token
    "AWE/USDT:USDT",  # AWE - Gaming token
    "AXS/USDT:USDT",  # AXS - Axie Infinity
    "B/USDT:USDT",  # B - Blockchain token
    "B2/USDT:USDT",  # B2 - Layer 2 solution
    "B3/USDT:USDT",  # B3 - Gaming token
    "BABY/USDT:USDT",  # BABY - Meme token
    "BADGER/USDT:USDT",  # BADGER - DeFi protocol
    "BAKE/USDT:USDT",  # BAKE - DEX token
    "BAN/USDT:USDT",  # BAN - Meme token
    "BANANA/USDT:USDT",  # BANANA - Gaming token
    "BANANAS31/USDT:USDT",  # BANANAS31 - Meme token
    "BAND/USDT:USDT",  # BAND - Oracle network
    "BANK/USDT:USDT",  # BANK - Banking token
    "BAT/USDT:USDT",  # BAT - Browser token
    "BB/USDT:USDT",  # BB - Infrastructure
    "BCH/USDT:USDT",  # BCH - Bitcoin Cash
    "BDXN/USDT:USDT",  # BDXN - Gaming token
    "BEAM/USDT:USDT",  # BEAM - Privacy coin
    "BEL/USDT:USDT",  # BEL - Cloud storage
    "BERA/USDT:USDT",  # BERA - DeFi protocol
    "BGB/USDT:USDT",  # BGB - Exchange token
    "BGSC/USDT:USDT",  # BGSC - Gaming token
    "BICO/USDT:USDT",  # BICO - Wallet infrastructure
    "BID/USDT:USDT",  # BID - Auction platform
    "BIGTIME/USDT:USDT",  # BIGTIME - Gaming token
    "BIO/USDT:USDT",  # BIO - Biotech token
    "BLAST/USDT:USDT",  # BLAST - Layer 2
    "BLUENEW/USDT:USDT",  # BLUENEW - Meme token
    "BLUR/USDT:USDT",  # BLUR - NFT marketplace
    "BMT/USDT:USDT",  # BMT - Gaming token
    "BNB/USDT:USDT",  # BNB - Binance Coin
    "BNT/USDT:USDT",  # BNT - Bancor
    "BOMBNEW/USDT:USDT",  # BOMBNEW - Meme token
    "BOME/USDT:USDT",  # BOME - Meme token
    "BR/USDT:USDT",  # BR - Fan token
    "BRETT/USDT:USDT",  # BRETT - Base meme
    "BROCCOLI/USDT:USDT",  # BROCCOLI - Meme token
    "BSV/USDT:USDT",  # BSV - Bitcoin SV
    "BSW/USDT:USDT",  # BSW - DEX token
    "BTC/USDT:USDT",  # BTC - Bitcoin
    "BULLA/USDT:USDT",  # BULLA - Meme token
    "C98/USDT:USDT",  # C98 - Wallet platform
    "CAKE/USDT:USDT",  # CAKE - PancakeSwap
    "CARV/USDT:USDT",  # CARV - Gaming data
    "CATI/USDT:USDT",  # CATI - Gaming token
    "CBK/USDT:USDT",  # CBK - Payment token
    "CELO/USDT:USDT",  # CELO - Mobile payments
    "CELR/USDT:USDT",  # CELR - Layer 2
    "CETUS/USDT:USDT",  # CETUS - DEX protocol
    "CFX/USDT:USDT",  # CFX - Conflux
    "CGPT/USDT:USDT",  # CGPT - AI token
    "CHESS/USDT:USDT",  # CHESS - DeFi protocol
    "CHILLGUY/USDT:USDT",  # CHILLGUY - Trending meme
    "CHR/USDT:USDT",  # CHR - Gaming blockchain
    "CHZ/USDT:USDT",  # CHZ - Fan tokens
    "CKB/USDT:USDT",  # CKB - Nervos Network
    "COMP/USDT:USDT",  # COMP - Compound
    "COOKIE/USDT:USDT",  # COOKIE - Gaming token
    "CORE/USDT:USDT",  # CORE - Blockchain platform
    "COS/USDT:USDT",  # COS - Content platform
    "COTI/USDT:USDT",  # COTI - Payment platform
    "COW/USDT:USDT",  # COW - DEX protocol
    "CRO/USDT:USDT",  # CRO - Crypto.com
    "CROSS/USDT:USDT",  # CROSS - Cross-chain
    "CRV/USDT:USDT",  # CRV - Curve DAO
    "CTC/USDT:USDT",  # CTC - Gaming token
    "CTK/USDT:USDT",  # CTK - Cloud platform
    "CTSI/USDT:USDT",  # CTSI - Cartesi
    "CUDIS/USDT:USDT",  # CUDIS - Payment token
    "CVC/USDT:USDT",  # CVC - Identity verification
    "CVX/USDT:USDT",  # CVX - DeFi protocol
    "CYBER/USDT:USDT",  # CYBER - Social protocol
    "DBR/USDT:USDT",  # DBR - DeFi protocol
    "DEEP/USDT:USDT",  # DEEP - AI computing
    "DENT/USDT:USDT",  # DENT - Mobile data
    "DEXE/USDT:USDT",  # DEXE - Trading platform
    "DF/USDT:USDT",  # DF - DeFi protocol
    "DIA/USDT:USDT",  # DIA - Oracle platform
    "DMC/USDT:USDT",  # DMC - Data storage
    "DOG/USDT:USDT",  # DOG - Meme token
    "DOGE/USDT:USDT",  # DOGE - Dogecoin
    "DOGS/USDT:USDT",  # DOGS - Telegram meme
    "DOLO/USDT:USDT",  # DOLO - Gaming token
    "DOOD/USDT:USDT",  # DOOD - Meme token
    "DOT/USDT:USDT",  # DOT - Polkadot
    "DRIFT/USDT:USDT",  # DRIFT - Derivatives
    "DUCK/USDT:USDT",  # DUCK - Meme token
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
            'marginMode': 'cross'
        }
    }
