# 🏔️ Alpine Trading Bot

**Professional Trading System with Bloomberg Terminal-Inspired Interface**

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your API keys in .env file
cp .env.example .env
# Edit .env with your exchange API keys

# Run the bot
python main.py
```

## 📁 Project Structure

```
volume-anom/
├── src/                    # Main source code
│   ├── core/              # Core bot functionality
│   │   ├── alpine_bot.py  # Main bot class
│   │   ├── config_manager.py  # Configuration management
│   │   ├── multi_exchange_config.py  # Multi-exchange setup
│   │   └── main.py        # Entry point
│   ├── trading/           # Trading engine and strategies
│   │   ├── strategy.py    # Volume anomaly strategy
│   │   ├── risk_manager_v2.py  # Risk management
│   │   ├── position_sizing.py  # Position sizing logic
│   │   ├── trade_executor.py  # Trade execution
│   │   ├── technical_indicators.py  # Technical analysis
│   │   ├── signal_analysis.py  # Signal analysis
│   │   ├── parameter_validation.py  # Parameter validation
│   │   ├── monte_carlo_optimization.py  # Monte Carlo optimization
│   │   ├── live_backtest.py  # Live backtesting
│   │   ├── supertrend_strategy.py  # Supertrend strategy
│   │   └── supertrend_integration.py  # Supertrend integration
│   ├── exchange/          # Exchange integrations
│   │   └── bitget_client.py  # Bitget exchange client
│   ├── ui/                # User interface components
│   │   ├── display.py     # Display components
│   │   ├── trading_dashboard.py  # Trading dashboard
│   │   └── ui_display.py  # UI display logic
│   └── utils/             # Common utilities
│       ├── market_scanner.py  # Market scanning
│       ├── vortecs_scanner.py  # Vortecs scanning
│       ├── ml_scorer.py   # ML scoring system
│       ├── scoring_system.py  # Scoring system
│       ├── supertrend_scorer.py  # Supertrend scoring
│       └── vortecs_scorer.py  # Vortecs scoring
├── scripts/               # Deployment and utility scripts
│   ├── deployment/        # Deployment scripts
│   │   ├── launch_alpine.py  # Bot launcher
│   │   └── launch_windows.bat  # Windows launcher
│   └── utilities/         # Utility scripts
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/       # Integration tests
│   └── backtests/        # Backtesting modules
├── docs/                  # Documentation
├── data/                  # Trading data and results
├── logs/                  # Application logs
├── archives/              # Old versions and deprecated files
├── config.json           # Main configuration
├── requirements.txt       # Dependencies
├── README.md             # This documentation
└── CHANGELOG.md          # Change log
```

## 🎯 Features

### 📊 **Trading Strategy**
- **Volume Anomaly Detection**: Advanced volume spike analysis with 4.5x threshold
- **RSI Integration**: Enhanced RSI calculation with 35/65 levels
- **Multi-timeframe Analysis**: 1m and 3m timeframe scanning
- **Confidence Scoring**: Advanced confidence calculation with multiple factors
- **Confluence Trading**: Multi-timeframe signal confirmation

### 🔌 **Multi-Exchange Support**
- **Bitget**: Primary exchange with full futures support
- **MEXC**: Secondary exchange with futures trading
- **Binance**: Tertiary exchange with futures trading
- **OKX**: Quaternary exchange with swap trading
- **Bybit**: Optional exchange (disabled by default)
- **Gate.io**: Optional exchange (disabled by default)

### 🚨 **Risk Management**
- **Capital Management**: Maximum 68% capital in play
- **Emergency Shutdown**: Automatic shutdown at 85% capital usage
- **Position Sizing**: 11% per trade with maximum 5 positions
- **Stop Loss**: Fixed 1.25% SL / 1.5% TP ratio
- **Daily Limits**: Maximum 50 trades per day

### 🎨 **Professional Interface**
- **Bloomberg Terminal Theme**: Professional terminal-style display
- **Real-time Updates**: Live data updates with timestamps
- **Multi-Exchange Summary**: Shows all connected exchanges with status
- **Performance Metrics**: Win rate, success rate, and trading statistics
- **Capital Management**: Real-time capital utilization tracking

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Bitget API Configuration
BITGET_API_KEY=your_api_key
BITGET_SECRET_KEY=your_secret_key
BITGET_PASSPHRASE=your_passphrase

# Additional Exchange APIs (optional)
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET_KEY=your_mexc_secret_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### Trading Configuration
- **Leverage**: 25x leverage focus
- **Position Size**: 11% per trade
- **Max Positions**: 5 positions maximum
- **Capital Limit**: 68% maximum capital in play
- **Emergency Threshold**: 85% capital usage shutdown

## 📈 Performance

### Trading Metrics
- **Win Rate Target**: 85-92% win rate
- **Risk/Reward**: 1:1.5 ratio (1.25% SL / 1.5% TP)
- **Daily Signals**: 1-5 signals per day per pair
- **Timeframes**: 5m/15m optimized timeframes
- **Pairs**: High-volume trading pairs

### Risk Controls
- **Capital Management**: Strict 68% capital limit
- **Emergency Procedures**: Automatic shutdown at 85%
- **Position Limits**: Maximum 5 simultaneous positions
- **Daily Loss Limit**: -19% daily loss limit

## 🔧 Development

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Backtests
python -m pytest tests/backtests/
```

### Logging
- **Unified Logging**: Consistent logging across all modules with loguru
- **Traceback Logging**: Comprehensive error handling with full tracebacks
- **Log Rotation**: Daily log rotation with 7-day retention
- **Log Location**: `logs/alpine_bot.log`

## 📚 Documentation

- **API Documentation**: `docs/api/`
- **Configuration Guide**: `docs/configuration.md`
- **Installation Guide**: `docs/installation.md`
- **Change Log**: `CHANGELOG.md`

## 🚨 Important Notes

- **Risk Warning**: This is a high-risk trading system suitable for experienced traders
- **Capital Management**: Never exceed 68% capital in play
- **Emergency Procedures**: System will automatically shutdown at 85% capital usage
- **Testing**: Always test in sandbox mode before live trading
- **Monitoring**: Monitor the system continuously during operation

## 📞 Support

For issues and questions, check the documentation in the `docs/` directory or review the `CHANGELOG.md` for recent updates.

---

**🏔️ Alpine Trading Bot - Professional Trading System** 