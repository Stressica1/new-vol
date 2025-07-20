#!/usr/bin/env python3
"""
🔧 Configuration Management System for Alpine Trading Bot
✅ Centralized configuration management with validation and persistence
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class LoggingConfig:
    """📝 Logging configuration"""
    level: str = "INFO"
    rotation: str = "1 day"
    retention: str = "7 days"
    format: str = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    file_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    performance_log: bool = True
    performance_rotation: str = "1 hour"
    performance_retention: str = "24 hours"

@dataclass
class PerformanceConfig:
    """📊 Performance monitoring configuration"""
    enabled: bool = True
    update_interval: float = 2.0
    track_memory: bool = True
    track_cpu: bool = True
    track_response_times: bool = True
    max_response_time_history: int = 1000
    performance_log_file: str = "logs/performance.log"

@dataclass
class ErrorHandlingConfig:
    """🛡️ Error handling configuration"""
    max_retries: int = 3
    retry_backoff: float = 2.0
    max_consecutive_errors: int = 5
    emergency_stop_on_errors: bool = True
    log_all_errors: bool = True
    error_notification: bool = False

@dataclass
class TradingConfig:
    """📋 Trading configuration"""
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""
    sandbox: bool = False
    max_positions: int = 5
    position_size_pct: float = 11.0
    leverage_filter: int = 25
    stop_loss_pct: float = 1.25
    take_profit_pct: float = 1.5
    cooldown_minutes: int = 0
    max_daily_trades: int = 50
    daily_loss_limit: float = -19.0
    
    # Performance settings
    update_interval: float = 2.0
    batch_size: int = 50
    max_signals: int = 25

class ConfigManager:
    """🔧 Configuration management system"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.error_handling_config = ErrorHandlingConfig()
        self.trading_config = TradingConfig()
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """📂 Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Load each configuration section
                if 'logging' in data:
                    self.logging_config = LoggingConfig(**data['logging'])
                if 'performance' in data:
                    self.performance_config = PerformanceConfig(**data['performance'])
                if 'error_handling' in data:
                    self.error_handling_config = ErrorHandlingConfig(**data['error_handling'])
                if 'trading' in data:
                    self.trading_config = TradingConfig(**data['trading'])
                
                logger.info(f"✅ Configuration loaded from {self.config_file}")
            else:
                logger.info(f"📝 No configuration file found, using defaults")
                self.save_config()
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            logger.info("📝 Using default configuration")
    
    def save_config(self):
        """💾 Save configuration to file"""
        try:
            config_data = {
                'logging': asdict(self.logging_config),
                'performance': asdict(self.performance_config),
                'error_handling': asdict(self.error_handling_config),
                'trading': asdict(self.trading_config),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"✅ Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
    
    def validate_config(self) -> bool:
        """🔍 Validate all configuration settings"""
        errors = []
        
        # Validate logging config
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging_config.level not in valid_levels:
            errors.append(f"Invalid log level: {self.logging_config.level}")
        
        # Validate performance config
        if self.performance_config.update_interval <= 0:
            errors.append("Performance update interval must be positive")
        
        if self.performance_config.max_response_time_history <= 0:
            errors.append("Max response time history must be positive")
        
        # Validate error handling config
        if self.error_handling_config.max_retries <= 0:
            errors.append("Max retries must be positive")
        
        if self.error_handling_config.retry_backoff <= 0:
            errors.append("Retry backoff must be positive")
        
        # Validate trading config
        if self.trading_config.max_positions <= 0:
            errors.append("Max positions must be positive")
        
        if self.trading_config.position_size_pct <= 0:
            errors.append("Position size percentage must be positive")
        
        if self.trading_config.leverage_filter < 25:
            errors.append("Leverage filter must be at least 25x")
        
        if self.trading_config.stop_loss_pct <= 0 or self.trading_config.take_profit_pct <= 0:
            errors.append("Stop loss and take profit must be positive")
        
        if self.trading_config.daily_loss_limit >= 0:
            errors.append("Daily loss limit must be negative")
        
        # Check total position size limit
        total_position_size = self.trading_config.position_size_pct * self.trading_config.max_positions
        if total_position_size > 55:
            errors.append(f"Total position size ({total_position_size}%) exceeds 55% limit")
        
        if errors:
            logger.error("❌ Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.success("✅ Configuration validation passed")
        return True
    
    def get_config_summary(self) -> Dict[str, Any]:
        """📊 Get configuration summary"""
        return {
            'logging': {
                'level': self.logging_config.level,
                'rotation': self.logging_config.rotation,
                'retention': self.logging_config.retention
            },
            'performance': {
                'enabled': self.performance_config.enabled,
                'update_interval': self.performance_config.update_interval,
                'track_memory': self.performance_config.track_memory,
                'track_cpu': self.performance_config.track_cpu
            },
            'error_handling': {
                'max_retries': self.error_handling_config.max_retries,
                'retry_backoff': self.error_handling_config.retry_backoff,
                'max_consecutive_errors': self.error_handling_config.max_consecutive_errors
            },
            'trading': {
                'max_positions': self.trading_config.max_positions,
                'position_size_pct': self.trading_config.position_size_pct,
                'leverage_filter': self.trading_config.leverage_filter,
                'stop_loss_pct': self.trading_config.stop_loss_pct,
                'take_profit_pct': self.trading_config.take_profit_pct,
                'daily_loss_limit': self.trading_config.daily_loss_limit
            }
        }
    
    def update_config(self, section: str, key: str, value: Any):
        """🔄 Update configuration setting"""
        try:
            if section == 'logging':
                setattr(self.logging_config, key, value)
            elif section == 'performance':
                setattr(self.performance_config, key, value)
            elif section == 'error_handling':
                setattr(self.error_handling_config, key, value)
            elif section == 'trading':
                setattr(self.trading_config, key, value)
            else:
                logger.error(f"❌ Invalid configuration section: {section}")
                return False
            
            logger.info(f"✅ Updated {section}.{key} = {value}")
            self.save_config()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update configuration: {e}")
            return False
    
    def reset_to_defaults(self):
        """🔄 Reset configuration to defaults"""
        self.logging_config = LoggingConfig()
        self.performance_config = PerformanceConfig()
        self.error_handling_config = ErrorHandlingConfig()
        self.trading_config = TradingConfig()
        
        logger.info("🔄 Configuration reset to defaults")
        self.save_config()

def create_default_config():
    """📝 Create default configuration file"""
    config_manager = ConfigManager()
    config_manager.save_config()
    return config_manager

if __name__ == "__main__":
    # Create default configuration
    config_manager = create_default_config()
    
    # Validate configuration
    if config_manager.validate_config():
        print("✅ Configuration created and validated successfully")
        
        # Show configuration summary
        summary = config_manager.get_config_summary()
        print("\n📊 Configuration Summary:")
        for section, settings in summary.items():
            print(f"\n{section.upper()}:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
    else:
        print("❌ Configuration validation failed") 