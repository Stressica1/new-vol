# Bitget Futures Trading System

A comprehensive Python-based trading system for Bitget futures with advanced risk management, trade execution, and monitoring capabilities.

## 🚀 Features

### Core Functionality
- **Complete Bitget Futures API Integration** - Full support for all trading operations
- **Advanced Risk Management** - Multi-layered risk controls and monitoring
- **Real-time Trade Execution** - Market, limit, and stop orders
- **Position Management** - Automated position tracking and management
- **Comprehensive Monitoring** - Real-time system and performance monitoring

### Risk Management
- **Position Size Calculation** - Automatic position sizing based on risk parameters
- **Daily Loss Limits** - Configurable maximum daily loss protection
- **Drawdown Protection** - Maximum drawdown monitoring and alerts
- **Emergency Stop** - Instant system shutdown capability
- **Multiple Risk Levels** - Low, Medium, High, and Critical risk classifications

### Trading Features
- **Market Orders** - Instant execution at current market prices
- **Limit Orders** - Precise entry and exit price control
- **Stop Orders** - Automated stop-loss and take-profit orders
- **Position Closing** - Manual and automatic position closure
- **Order Management** - Full order lifecycle management

## 📋 Requirements

- Python 3.8+
- Bitget Futures API credentials
- Internet connection for API access

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd bitget-trading-system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API credentials:**
```bash
cp .env.example .env
# Edit .env with your Bitget API credentials
```

## ⚙️ Configuration

### API Credentials
Set up your Bitget API credentials in the `.env` file:

```env
BITGET_API_KEY=your_api_key_here
BITGET_API_SECRET=your_api_secret_here
BITGET_PASSPHRASE=your_passphrase_here
```

### Risk Management Settings
Configure risk parameters in `.env`:

```env
MAX_POSITION_SIZE=1000.0          # Maximum position size in USDT
MAX_DAILY_LOSS=100.0              # Maximum daily loss in USDT
MAX_DRAWDOWN=0.05                 # Maximum drawdown (5%)
STOP_LOSS_PERCENTAGE=0.02         # Stop loss percentage (2%)
TAKE_PROFIT_PERCENTAGE=0.04       # Take profit percentage (4%)
RISK_PER_TRADE=0.01               # Risk per trade (1% of account)
MAX_OPEN_POSITIONS=5              # Maximum open positions
```

### Trading Settings
Configure trading parameters:

```env
DEFAULT_SYMBOL=BTCUSDT             # Default trading symbol
LEVERAGE=1                         # Trading leverage
ORDER_TYPE=limit                   # Default order type
MIN_ORDER_SIZE=5.0                 # Minimum order size in USDT
```

## 🚀 Usage

### Quick Start - Test System
```bash
python main.py test
```

This runs a comprehensive test suite that verifies:
- ✅ API connectivity
- ✅ Account access
- ✅ Risk management system
- ✅ Position monitoring
- ✅ Trade execution capabilities

### Start Trading System
```bash
python main.py start
```

Starts the full trading system with:
- Real-time position monitoring
- Risk management enforcement
- Order execution capabilities
- Automated trade management

### Interactive Mode
```bash
python main.py interactive
```

Provides an interactive shell with commands:
- `test` - Run comprehensive tests
- `start` - Start trading system
- `status` - Show system status
- `balance` - Show account balance
- `positions` - Show current positions
- `risk` - Show risk metrics
- `quit` - Exit

## 📊 System Components

### 1. Bitget Client (`bitget_client.py`)
- Complete API wrapper for Bitget Futures
- Connection management and error handling
- Account, position, and order management
- Real-time data retrieval

### 2. Risk Management (`risk_management.py`)
- Position sizing calculations
- Risk level determination
- Daily loss tracking
- Drawdown monitoring
- Emergency stop functionality

### 3. Trading Engine (`trading_engine.py`)
- Order execution and management
- Position monitoring
- Trade lifecycle management
- Multi-threaded operation

### 4. Configuration (`config.py`)
- Centralized configuration management
- Environment variable integration
- Validation and defaults

## 🔧 API Reference

### Trading Engine

```python
from trading_engine import trading_engine

# Place market order
order = trading_engine.place_market_order(
    symbol="BTCUSDT_UMCBL",
    side="open_long",
    size=0.001
)

# Place limit order
order = trading_engine.place_limit_order(
    symbol="BTCUSDT_UMCBL",
    side="open_long",
    size=0.001,
    price=50000.0
)

# Close position
trading_engine.close_position("BTCUSDT_UMCBL")

# Get trading summary
summary = trading_engine.get_trading_summary()
```

### Risk Management

```python
from risk_management import risk_manager

# Check if position can be opened
can_open, reason = risk_manager.can_open_position(
    symbol="BTCUSDT_UMCBL",
    side="open_long",
    size=0.001,
    price=50000.0
)

# Calculate position size
position_size = risk_manager.calculate_position_size(
    symbol="BTCUSDT_UMCBL",
    entry_price=50000.0,
    stop_loss_price=49000.0
)

# Get risk summary
risk_summary = risk_manager.get_risk_summary()
```

### Bitget Client

```python
from bitget_client import bitget_client

# Test connection
success = bitget_client.test_connection()

# Get account info
account_info = bitget_client.get_account_info()

# Get current positions
positions = bitget_client.get_positions()

# Get account balance
balance = bitget_client.get_balance()
```

## 📈 Monitoring and Logging

### Real-time Monitoring
The system provides comprehensive monitoring:

- **Account Balance** - Real-time balance and equity tracking
- **Position Status** - Live position monitoring with PnL
- **Risk Metrics** - Continuous risk assessment
- **Order Status** - Real-time order execution tracking
- **System Health** - Component status monitoring

### Logging
All activities are logged to:
- **Console** - Real-time status updates
- **File** - Detailed logs in `trading_system.log`
- **Rotation** - Daily log rotation with 30-day retention

## 🛡️ Security Features

### API Security
- Secure credential storage in environment variables
- Request signing and authentication
- Rate limiting and error handling

### Risk Controls
- Maximum position size limits
- Daily loss limits
- Drawdown protection
- Emergency stop functionality
- Multi-level risk assessment

### Operational Security
- Graceful shutdown handling
- Error recovery mechanisms
- Connection monitoring
- Failsafe mechanisms

## 🔧 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify API credentials in `.env`
   - Check internet connection
   - Ensure IP whitelisting if required

2. **Risk Management Rejection**
   - Check risk configuration in `.env`
   - Verify account balance
   - Review position limits

3. **Order Execution Failed**
   - Check symbol format (e.g., "BTCUSDT_UMCBL")
   - Verify account balance
   - Check market hours

### Debug Mode
Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk and may not be suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consider consulting with a financial advisor before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue in the repository
4. Provide relevant configuration and log information

---

**Happy Trading! 🚀**
