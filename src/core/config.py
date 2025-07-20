#!/usr/bin/env python3
"""
🏔️ Alpine Trading Bot - Centralized Configuration
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AlpineConfig:
    """Centralized configuration for Alpine Trading Bot"""
    
    # ===== API CONFIGURATION =====
    api_key: str = "bg_5400882ef43c5596ffcf4af0c697b250"
    api_secret: str = "60e42c8f086221d6dd992fc93e5fb810b0354adaa09b674558c14cbd49969d45"
    passphrase: str = "22672267"
    sandbox: bool = False
    
    # ===== TRADING PARAMETERS =====
    # Position Management
    max_positions: int = 20
    position_size_pct: float = 9.5  # % of balance per trade
    min_order_size: float = 5.0  # Minimum order size in USDT
    max_hold_time_hours: int = 12  # Maximum position hold time
    
    # Risk Management
    stop_loss_pct: float = 1.5  # Stop loss percentage
    take_profit_pct: float = 1.5  # Take profit percentage
    max_drawdown_pct: float = 30.0  # Maximum drawdown allowed
    trailing_stop: bool = True  # Enable trailing stop loss
    
    # Leverage Settings
    leverage: int = 50  # Default leverage
    min_leverage: int = 50  # Minimum leverage requirement
    max_leverage: int = 125  # Maximum leverage allowed
    
    # ===== STRATEGY PARAMETERS =====
    # Signal Generation
    min_signal_confidence: float = 65.0  # Minimum confidence to trade
    min_trade_confidence: float = 55.0  # Minimum confidence for execution
    min_volume_ratio: float = 1.5  # Minimum volume ratio
    volume_lookback: int = 20  # Volume analysis lookback period
    volume_std_multiplier: float = 1.2  # Volume standard deviation multiplier
    
    # Timeframes
    primary_timeframe: str = "3m"
    timeframes: List[str] = field(default_factory=lambda: ["3m"])
    
    # ===== UI SETTINGS =====
    # Display
    refresh_rate: int = 1  # Display refresh rate (seconds)
    log_level: str = "INFO"  # Logging level
    steampunk_theme: bool = True  # Use steampunk theme
    
    # Colors (Steampunk Theme)
    primary_color: str = "#00FFB3"  # Mint green
    secondary_color: str = "#8B008B"  # Dark purple
    accent_color: str = "#FF69B4"  # Pink
    warning_color: str = "#FF8C00"  # Orange (bear signals)
    
    # ===== EXCHANGE SETTINGS =====
    exchange_name: str = "bitget"
    default_type: str = "swap"  # Futures trading
    margin_mode: str = "cross"  # Cross margin mode
    enable_rate_limit: bool = True
    
    # ===== TRADING PAIRS =====
    trading_pairs: List[str] = field(default_factory=lambda: [
        'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'BNB/USDT:USDT',
        'ADA/USDT:USDT', 'DOT/USDT:USDT', 'MATIC/USDT:USDT', 'AVAX/USDT:USDT',
        'LINK/USDT:USDT', 'UNI/USDT:USDT'
    ])
    
    # ===== BOT METADATA =====
    bot_name: str = "Alpine Trading Bot"
    version: str = "2.0"
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Ensure timeframes is always a list
        if isinstance(self.timeframes, str):
            self.timeframes = [self.timeframes]
        
        # Calculate risk/reward ratio
        self.risk_reward_ratio = self.take_profit_pct / self.stop_loss_pct
    
    def get_exchange_config(self) -> Dict:
        """Get exchange configuration for CCXT"""
        return {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'sandbox': self.sandbox,
            'enableRateLimit': self.enable_rate_limit,
            'options': {
                'defaultType': self.default_type,
                'marginMode': self.margin_mode
            }
        }
    
    def save_to_file(self, filepath: str = "alpine_config.json"):
        """Save configuration to JSON file"""
        config_dict = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'passphrase': self.passphrase,
            'sandbox': self.sandbox,
            'max_positions': self.max_positions,
            'position_size_pct': self.position_size_pct,
            'min_order_size': self.min_order_size,
            'max_hold_time_hours': self.max_hold_time_hours,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'max_drawdown_pct': self.max_drawdown_pct,
            'trailing_stop': self.trailing_stop,
            'leverage': self.leverage,
            'min_leverage': self.min_leverage,
            'max_leverage': self.max_leverage,
            'min_signal_confidence': self.min_signal_confidence,
            'min_trade_confidence': self.min_trade_confidence,
            'min_volume_ratio': self.min_volume_ratio,
            'volume_lookback': self.volume_lookback,
            'volume_std_multiplier': self.volume_std_multiplier,
            'primary_timeframe': self.primary_timeframe,
            'timeframes': self.timeframes,
            'refresh_rate': self.refresh_rate,
            'log_level': self.log_level,
            'steampunk_theme': self.steampunk_theme,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'accent_color': self.accent_color,
            'warning_color': self.warning_color,
            'exchange_name': self.exchange_name,
            'default_type': self.default_type,
            'margin_mode': self.margin_mode,
            'enable_rate_limit': self.enable_rate_limit,
            'trading_pairs': self.trading_pairs,
            'bot_name': self.bot_name,
            'version': self.version
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str = "alpine_config.json") -> 'AlpineConfig':
        """Load configuration from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        else:
            return cls()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # API validation
        if not self.api_key or len(self.api_key) < 10:
            errors.append("Invalid API key")
        if not self.api_secret or len(self.api_secret) < 10:
            errors.append("Invalid API secret")
        
        # Trading validation
        if self.position_size_pct <= 0 or self.position_size_pct > 100:
            errors.append("Position size must be between 0 and 100%")
        if self.stop_loss_pct <= 0 or self.stop_loss_pct > 10:
            errors.append("Stop loss must be between 0 and 10%")
        if self.take_profit_pct <= 0 or self.take_profit_pct > 20:
            errors.append("Take profit must be between 0 and 20%")
        if self.leverage < self.min_leverage or self.leverage > self.max_leverage:
            errors.append(f"Leverage must be between {self.min_leverage}x and {self.max_leverage}x")
        
        # Strategy validation
        if self.min_signal_confidence < 0 or self.min_signal_confidence > 100:
            errors.append("Signal confidence must be between 0 and 100%")
        if self.min_trade_confidence < 0 or self.min_trade_confidence > 100:
            errors.append("Trade confidence must be between 0 and 100%")
        
        return errors
    
    def get_summary(self) -> Dict:
        """Get configuration summary"""
        return {
            'bot_name': self.bot_name,
            'version': self.version,
            'exchange': self.exchange_name,
            'trading_pairs': len(self.trading_pairs),
            'leverage_range': f"{self.min_leverage}x-{self.max_leverage}x",
            'default_leverage': f"{self.leverage}x",
            'risk_reward': f"1:{self.risk_reward_ratio:.1f}",
            'stop_loss': f"{self.stop_loss_pct}%",
            'take_profit': f"{self.take_profit_pct}%",
            'position_size': f"{self.position_size_pct}%",
            'min_confidence': f"{self.min_signal_confidence}%",
            'timeframe': self.primary_timeframe,
            'theme': "Steampunk" if self.steampunk_theme else "Default"
        }

# Global configuration instance
config = AlpineConfig()

def get_config() -> AlpineConfig:
    """Get the global configuration instance"""
    return config

def get_exchange_config() -> Dict:
    """Get exchange configuration for CCXT"""
    return config.get_exchange_config()

def load_config(filepath: str = "alpine_config.json") -> AlpineConfig:
    """Load configuration from file"""
    global config
    config = AlpineConfig.load_from_file(filepath)
    return config

def save_config(filepath: str = "alpine_config.json") -> None:
    """Save current configuration to file"""
    config.save_to_file(filepath)

def validate_config() -> List[str]:
    """Validate current configuration"""
    return config.validate()

def get_config_summary() -> Dict:
    """Get configuration summary"""
    return config.get_summary()

# Legacy compatibility
TradingConfig = AlpineConfig 