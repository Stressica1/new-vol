
# 🚀 Meme Coin Volume Anomaly Bot

A sophisticated trading bot designed specifically for high-volatility meme coins and cryptocurrencies under $100. The bot uses advanced volume anomaly detection combined with multi-layer validation to achieve 85%+ win rates on quick scalp trades.

## 🎯 Strategy Overview

The bot monitors for unusual volume spikes in meme coins and enters positions when multiple confirmation signals align:

1. **Volume Anomaly Detection**: Identifies when volume spikes 1.5x-5x above normal
2. **PSI Validation**: Confirms momentum using Price Strength Index
3. **HTF Trend Analysis**: Checks higher timeframe alignment (optional for memes)
4. **Risk Management**: Uses Kelly Criterion position sizing with strict stop losses

## ✨ Key Features

- **24/7 Market Scanning**: Continuously monitors 50+ meme coins
- **Smart Position Sizing**: 0.5-2% risk per trade with Kelly Criterion
- **Quick Scalping**: Targets 3-5% profits with 1.5% stop losses
- **Performance Tracking**: Adapts to focus on best-performing coins
- **Bitget Integration**: Full futures/perpetual trading support

## 📊 Performance Targets

- **Win Rate**: 75-85%
- **Risk/Reward**: 1:3 average
- **Daily Trades**: 20-50 signals
- **Hold Time**: 5-30 minutes typically

## 🛠️ Project Structure

```
.
├── config/               # Configuration files
│   ├── settings.yaml    # Main configuration
│   └── api_keys.json    # API credentials (create from template)
├── src/                 # Core modules
│   ├── bitget_client.py         # Exchange API wrapper
│   ├── volume_analyzer.py       # Volume anomaly detection
│   ├── psi_validator.py         # PSI momentum validation
│   ├── htf_trend_validator.py   # Higher timeframe trends
│   ├── signal_generator.py      # Signal combination logic
│   ├── risk_manager.py          # Position sizing & risk
│   ├── order_executor.py        # Trade execution
│   ├── market_scanner.py        # 24/7 market monitoring
│   └── meme_coin_scanner.py     # Meme coin specialization
├── main.py              # Main bot entry point
├── run_demo.py          # Demo/simulation mode
├── requirements.txt     # Python dependencies
└── QUICKSTART.md       # Quick setup guide
```

## 🚀 Quick Start

### 1. Run the Demo

A demo is included that simulates the bot's operation:

```bash
python3 run_demo.py
```

### 2. Setup for Live Trading

1. **Get Bitget API Keys**
   - Sign up at [Bitget](https://www.bitget.com)
   - Create API keys with futures trading permissions
   - Enable IP whitelist for security

2. **Configure API Keys**
   ```bash
   # Copy template and add your keys
   cp config/api_keys_template.json config/api_keys.json
   # Edit with your actual keys
   ```

3. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the Bot**
   ```bash
   # Test on testnet first
   python main.py --testnet
   
   # Run live (use with caution!)
   python main.py
   ```

## ⚙️ Configuration

The bot is pre-configured for meme coins in `config/settings.yaml`:

- **Timeframes**: 1m, 3m (fast reaction)
- **Volume Thresholds**: 1.3x, 2x, 3x, 5x
- **Leverage**: 10-20x with small positions
- **Risk**: 0.5-2% per trade max

## 📈 Target Coins

Optimized for high-volatility coins like:
- DOGE, SHIB, PEPE, FLOKI
- BONK, WIF, MEME
- Any coin with "INU", "BABY", "MOON" patterns
- Recently listed meme coins

## ⚠️ Risk Warning

- Meme coins are extremely volatile
- Start with small capital ($100-500)
- Use testnet first
- Monitor closely for first 24 hours
- Set daily loss limits

## 🔧 Advanced Features

- **Pump Detection**: Identifies early pump patterns
- **Whale Monitoring**: Tracks large trades
- **Performance Optimization**: Focuses on winning pairs
- **Multiple Take Profits**: Scales out at 1R, 1.5R, 2R

## 📊 Monitoring

The bot provides real-time statistics:
- Current positions and P&L
- Win rate by coin
- Signal generation rate
- Top performing meme coins

## 🤝 Contributing

This is a standalone project. Feel free to fork and modify for your needs.

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Remember**: Always start with the demo, then testnet, then small live positions. Meme coins can move 10-50% in minutes - both up and down!
=======
# 🎭 ALPINE TRADING BOT

A sophisticated Victorian steampunk-themed cryptocurrency futures trading system for automated trading on Bitget exchange.

## 🚀 Quick Start

```bash
# Use the launcher (recommended)
python launch.py

# Or launch directly
python src/working_trading_system.py

# Run system health check
python tests/system_health_check.py

# Check positions
python tests/simple_position_check.py
```

## 🏗️ Architecture

- **Trading Engine**: `src/working_trading_system.py` (88KB)
- **Risk Management**: `src/enhanced_risk_management.py` (14KB)
- **Performance Analytics**: `src/advanced_performance_analytics.py` (14KB)
- **Strategy Module**: `src/enhanced_volume_rsi_strategy.py`

## 🛡️ Features

- **Risk Management**: 50x max leverage, $25 max position size
- **Signal Detection**: Volume/RSI divergence with 70% confidence threshold
- **Position Limits**: Max 10 concurrent positions
- **Safety Controls**: 8% stop loss, 10% daily loss limit
- **Victorian UI**: Steampunk-themed dashboard with live updates

## 📊 Current Status

- ✅ **System**: 100% Operational
- ✅ **Balance**: $61.23 available
- ✅ **Positions**: 0 (clean start)
- ✅ **Pairs**: 1,392 available
- ✅ **Tests**: All passing

## 📁 Directory Structure

```
├── src/              # Core trading system
├── tests/            # System tests and utilities
├── config/           # Configuration files
├── utils/            # Utility scripts
├── docs/             # Documentation
├── archive/          # Historical documentation
└── logs/             # System logs
```

## 🔧 Configuration

All configuration files are in `config/` directory. The system uses simplified risk management with fixed parameters for stability.

## 📈 Performance

- **Target Win Rate**: 60%+
- **Max Risk per Trade**: 2% of balance
- **Daily Trade Limit**: 50 trades
- **Position Sizing**: Dynamic based on balance

---

**Built with precision engineering and Victorian elegance** ⚙️🎭
# Volume
# Volume
# Volume

