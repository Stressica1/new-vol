# API Documentation

## Overview

The Alpine Trading Bot provides a comprehensive API for automated trading operations.

## Core Classes

### AlpineBot

Main bot engine that orchestrates all trading operations.

```python
from alpine_bot import AlpineBot, TradingConfig

config = TradingConfig()
bot = AlpineBot(config)
```

#### Methods

##### `start()`
Start the trading bot.

```python
success = bot.start()
```

**Returns**: `bool` - True if started successfully

##### `stop()`
Stop the trading bot.

```python
bot.stop()
```

##### `run()`
Run the bot (blocking call).

```python
bot.run()
```

### TradingConfig

Configuration class for trading parameters.

```python
from alpine_bot.core.config import TradingConfig

config = TradingConfig()
config.max_positions = 10
config.leverage = 25
```

#### Properties

- `max_positions`: Maximum simultaneous positions
- `position_size_pct`: Position size as percentage
- `leverage`: Leverage for futures trading
- `min_order_size`: Minimum order size in USDT
- `API_KEY`: Bitget API key
- `API_SECRET`: Bitget API secret
- `PASSPHRASE`: Bitget passphrase

## Trading Module

### VolumeAnomalyStrategy

Volume anomaly detection strategy.

```python
from alpine_bot.trading.strategy import VolumeAnomalyStrategy

strategy = VolumeAnomalyStrategy(config)
```

#### Methods

##### `analyze_signals(symbol, timeframe)`
Analyze trading signals for a symbol.

```python
signals = strategy.analyze_signals("BTC/USDT:USDT", "1h")
```

**Parameters**:
- `symbol`: Trading pair symbol
- `timeframe`: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)

**Returns**: List of signal dictionaries

### AlpineRiskManager

Risk management system.

```python
from alpine_bot.trading.risk_manager import AlpineRiskManager

risk_manager = AlpineRiskManager(config)
```

#### Methods

##### `can_open_position(symbol, side, size, price)`
Check if position can be opened.

```python
can_open, reason = risk_manager.can_open_position(
    "BTC/USDT:USDT", "buy", 0.001, 50000
)
```

**Parameters**:
- `symbol`: Trading pair symbol
- `side`: Position side ("buy" or "sell")
- `size`: Position size
- `price`: Entry price

**Returns**: `(bool, str)` - (can_open, reason)

##### `calculate_position_size(symbol, price, risk_pct)`
Calculate position size based on risk.

```python
size = risk_manager.calculate_position_size(
    "BTC/USDT:USDT", 50000, 2.0
)
```

## Exchange Module

### BitgetClient

Bitget exchange connector.

```python
from alpine_bot.exchange.bitget_client import BitgetClient

client = BitgetClient(config)
```

#### Methods

##### `test_connection()`
Test exchange connectivity.

```python
success = client.test_connection()
```

##### `get_balance()`
Get account balance.

```python
balance = client.get_balance()
```

##### `get_positions()`
Get current positions.

```python
positions = client.get_positions()
```

##### `place_order(symbol, side, amount, price=None)`
Place an order.

```python
order = client.place_order(
    "BTC/USDT:USDT", "buy", 0.001, 50000
)
```

## UI Module

### AlpineDisplay

Terminal-based user interface.

```python
from alpine_bot.ui.display import AlpineDisplay

display = AlpineDisplay(config)
```

#### Methods

##### `start(bot)`
Start the display interface.

```python
display.start(bot)
```

##### `stop()`
Stop the display interface.

```python
display.stop()
```

## Data Structures

### Signal Format

```python
{
    "symbol": "BTC/USDT:USDT",
    "type": "buy" | "sell",
    "confidence": 85.5,
    "volume_ratio": 3.2,
    "price": 50000.0,
    "timestamp": "2024-01-01T12:00:00Z",
    "timeframe": "1h",
    "is_confluence": True,
    "confluence_timeframes": ["1h", "4h"]
}
```

### Position Format

```python
{
    "symbol": "BTC/USDT:USDT",
    "side": "buy" | "sell",
    "size": 0.001,
    "entry_price": 50000.0,
    "current_price": 51000.0,
    "unrealized_pnl": 50.0,
    "percentage": 2.0
}
```

## Error Handling

All API methods may raise exceptions:

```python
try:
    bot.start()
except Exception as e:
    print(f"Error: {e}")
```

Common exceptions:
- `ConnectionError`: Exchange connection issues
- `AuthenticationError`: API credential problems
- `InsufficientFundsError`: Not enough balance
- `InvalidSymbolError`: Invalid trading pair

## Examples

### Basic Usage

```python
from alpine_bot import AlpineBot, TradingConfig

# Create configuration
config = TradingConfig()
config.max_positions = 5
config.leverage = 20

# Create and run bot
bot = AlpineBot(config)
bot.run()
```

### Custom Strategy

```python
from alpine_bot.trading.strategy import VolumeAnomalyStrategy

class CustomStrategy(VolumeAnomalyStrategy):
    def analyze_signals(self, symbol, timeframe):
        # Custom signal logic
        return super().analyze_signals(symbol, timeframe)

# Use custom strategy
config = TradingConfig()
bot = AlpineBot(config)
bot.strategy = CustomStrategy(config)
bot.run()
```

### Testing

```python
# Test connectivity
success = bot.exchange_client.test_connection()

# Test signals
signals = bot.strategy.analyze_signals("BTC/USDT:USDT", "1h")

# Test risk management
can_open, reason = bot.risk_manager.can_open_position(
    "BTC/USDT:USDT", "buy", 0.001, 50000
)
```