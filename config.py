import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BitgetConfig(BaseModel):
    """Bitget API Configuration"""
    api_key: str = Field(..., description="Bitget API Key")
    api_secret: str = Field(..., description="Bitget API Secret")
    passphrase: str = Field(..., description="Bitget API Passphrase")
    sandbox: bool = Field(default=False, description="Use sandbox environment")
    base_url: str = Field(default="https://api.bitget.com", description="Base API URL")

class RiskManagementConfig(BaseModel):
    """Risk Management Configuration"""
    max_position_size: float = Field(default=1000.0, description="Maximum position size in USDT")
    max_daily_loss: float = Field(default=100.0, description="Maximum daily loss in USDT")
    max_drawdown: float = Field(default=0.05, description="Maximum drawdown percentage (0.05 = 5%)")
    stop_loss_percentage: float = Field(default=0.02, description="Stop loss percentage (0.02 = 2%)")
    take_profit_percentage: float = Field(default=0.04, description="Take profit percentage (0.04 = 4%)")
    risk_per_trade: float = Field(default=0.01, description="Risk per trade as percentage of account (0.01 = 1%)")
    max_open_positions: int = Field(default=5, description="Maximum number of open positions")
    enable_stop_loss: bool = Field(default=True, description="Enable automatic stop loss")
    enable_take_profit: bool = Field(default=True, description="Enable automatic take profit")

class TradingConfig(BaseModel):
    """Trading Configuration"""
    default_symbol: str = Field(default="BTCUSDT", description="Default trading symbol")
    default_margin_coin: str = Field(default="USDT", description="Default margin coin")
    order_type: str = Field(default="limit", description="Default order type: limit, market")
    time_in_force: str = Field(default="normal", description="Time in force: normal, post_only, fok, ioc")
    product_type: str = Field(default="UMCBL", description="Product type: UMCBL, DMCBL, SPBL")
    leverage: int = Field(default=1, description="Trading leverage")
    min_order_size: float = Field(default=5.0, description="Minimum order size in USDT")
    price_precision: int = Field(default=4, description="Price precision")
    size_precision: int = Field(default=4, description="Size precision")

class SystemConfig(BaseModel):
    """System Configuration"""
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="trading_system.log", description="Log file path")
    enable_notifications: bool = Field(default=False, description="Enable notifications")
    notification_webhook: Optional[str] = Field(default=None, description="Webhook URL for notifications")
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    update_interval: int = Field(default=1, description="Update interval in seconds")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")

class Config(BaseModel):
    """Main Configuration"""
    bitget: BitgetConfig
    risk_management: RiskManagementConfig
    trading: TradingConfig
    system: SystemConfig

def load_config() -> Config:
    """Load configuration from environment variables"""
    
    # Bitget API configuration
    bitget_config = BitgetConfig(
        api_key=os.getenv("BITGET_API_KEY", ""),
        api_secret=os.getenv("BITGET_API_SECRET", ""),
        passphrase=os.getenv("BITGET_PASSPHRASE", ""),
        sandbox=os.getenv("BITGET_SANDBOX", "false").lower() == "true",
        base_url=os.getenv("BITGET_BASE_URL", "https://api.bitget.com")
    )
    
    # Risk management configuration
    risk_config = RiskManagementConfig(
        max_position_size=float(os.getenv("MAX_POSITION_SIZE", "1000.0")),
        max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "100.0")),
        max_drawdown=float(os.getenv("MAX_DRAWDOWN", "0.05")),
        stop_loss_percentage=float(os.getenv("STOP_LOSS_PERCENTAGE", "0.02")),
        take_profit_percentage=float(os.getenv("TAKE_PROFIT_PERCENTAGE", "0.04")),
        risk_per_trade=float(os.getenv("RISK_PER_TRADE", "0.01")),
        max_open_positions=int(os.getenv("MAX_OPEN_POSITIONS", "5")),
        enable_stop_loss=os.getenv("ENABLE_STOP_LOSS", "true").lower() == "true",
        enable_take_profit=os.getenv("ENABLE_TAKE_PROFIT", "true").lower() == "true"
    )
    
    # Trading configuration
    trading_config = TradingConfig(
        default_symbol=os.getenv("DEFAULT_SYMBOL", "BTCUSDT"),
        default_margin_coin=os.getenv("DEFAULT_MARGIN_COIN", "USDT"),
        order_type=os.getenv("ORDER_TYPE", "limit"),
        time_in_force=os.getenv("TIME_IN_FORCE", "normal"),
        product_type=os.getenv("PRODUCT_TYPE", "UMCBL"),
        leverage=int(os.getenv("LEVERAGE", "1")),
        min_order_size=float(os.getenv("MIN_ORDER_SIZE", "5.0")),
        price_precision=int(os.getenv("PRICE_PRECISION", "4")),
        size_precision=int(os.getenv("SIZE_PRECISION", "4"))
    )
    
    # System configuration
    system_config = SystemConfig(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "trading_system.log"),
        enable_notifications=os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true",
        notification_webhook=os.getenv("NOTIFICATION_WEBHOOK"),
        database_url=os.getenv("DATABASE_URL"),
        update_interval=int(os.getenv("UPDATE_INTERVAL", "1")),
        heartbeat_interval=int(os.getenv("HEARTBEAT_INTERVAL", "30"))
    )
    
    return Config(
        bitget=bitget_config,
        risk_management=risk_config,
        trading=trading_config,
        system=system_config
    )

# Global configuration instance
config = load_config()