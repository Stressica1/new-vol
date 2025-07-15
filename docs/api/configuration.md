# Configuration Guide

## Overview

The Alpine Trading Bot uses a configuration system that allows you to customize trading parameters, risk management, and system behavior.

## Configuration Files

### Main Configuration
- `alpine_bot/core/config.py` - Main configuration class
- `.env` - Environment variables for API keys

### Trading Parameters

#### Position Management
```python
max_positions = 20              # Maximum simultaneous positions
position_size_pct = 20.0        # Position size as % of account
leverage = 35                   # Leverage for futures trading
min_order_size = 10.0           # Minimum order size in USDT
```

#### Risk Management
```python
max_daily_loss_pct = 50.0       # Maximum daily loss %
max_drawdown_pct = 30.0         # Maximum drawdown %
stop_loss_pct = 1.5             # Stop loss %
take_profit_pct = 3.0           # Take profit %
```

#### Strategy Parameters
```python
volume_lookback = 20            # Volume analysis period
volume_std_multiplier = 1.2     # Volume standard deviation multiplier
min_volume_ratio = 2.75         # Minimum volume ratio for signals
supertrend_atr_period = 6       # SuperTrend ATR period
```

### Exchange Configuration

#### API Credentials
```python
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
PASSPHRASE = "your_passphrase"
SANDBOX = False                 # Set to True for testing
```

## Environment Variables

Create a `.env` file:
```env
BITGET_API_KEY=your_api_key_here
BITGET_API_SECRET=your_api_secret_here
BITGET_PASSPHRASE=your_passphrase_here
BITGET_SANDBOX=false
```

## Custom Configuration

### Creating Custom Config
```python
from alpine_bot.core.config import TradingConfig

class CustomConfig(TradingConfig):
    max_positions = 10
    position_size_pct = 15.0
    leverage = 25
```

### Using Custom Config
```python
from alpine_bot import AlpineBot

config = CustomConfig()
bot = AlpineBot(config)
```

## Trading Pairs

Configure trading pairs in `config.py`:
```python
TRADING_PAIRS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    # Add more pairs
]
```

## Logging Configuration

Adjust logging levels:
```python
# In main.py
setup_logging(verbose=True)  # Debug level
setup_logging(quiet=True)    # Warning level only
```

## Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Test configurations** in sandbox mode first
4. **Monitor risk parameters** regularly
5. **Keep backups** of working configurations

## Validation

Test your configuration:
```bash
python main.py --test
```