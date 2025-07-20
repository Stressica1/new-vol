# 🏔️ Alpine Trading Bot - Professional Volume Anomaly Trading System

[![Version](https://img.shields.io/badge/version-2.0.0-neon)](https://github.com/Stressica1/volume-anom)
[![Success Rate](https://img.shields.io/badge/success%20rate-90%25-brightgreen)](https://github.com/Stressica1/volume-anom)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A production-ready cryptocurrency trading bot implementing volume anomaly detection strategies with professional risk management, real-time monitoring, and beautiful terminal UI.

## 🚀 Quick Start

### GitHub Codespaces (Recommended)
1. Click "Code" → "Codespaces" → "Create codespace"
2. Wait for automatic setup
3. Run: `python scripts/deployment/launch_alpine.py`

### Local Installation
```bash
git clone https://github.com/Stressica1/volume-anom.git
cd volume-anom
pip install -r requirements.txt
python scripts/deployment/launch_alpine.py --test
```

## 🏗️ Reorganized Architecture

**NEW STRUCTURE**: This project has been completely reorganized for better maintainability and scalability!

```
volume-anom/
├── src/                        # 🎯 Source code (NEW)
│   ├── core/                   # Core engine components
│   │   ├── bot.py             # Main bot engine
│   │   ├── config.py          # Configuration management
│   │   ├── manager.py         # Bot lifecycle management
│   │   └── data_connector.py  # Data connection utilities
│   ├── trading/               # Trading logic
│   │   ├── strategy.py        # Volume anomaly strategy
│   │   ├── risk_manager_v2.py # Risk management (latest)
│   │   ├── risk_management_v1.py # Risk management (legacy)
│   │   ├── position_sizing.py # Position sizing logic
│   │   ├── trade_executor.py  # Trade execution
│   │   ├── trading_engine.py  # Main trading engine
│   │   └── technical_indicators.py # Technical analysis
│   ├── exchange/              # Exchange connectivity
│   │   └── bitget_client.py   # Bitget exchange client
│   ├── ui/                    # User interface
│   │   ├── display.py         # Terminal UI display
│   │   ├── trading_dashboard.py # Trading dashboard
│   │   └── ui_display.py      # UI components
│   └── utils/                 # Utilities
│       ├── crypto_scoring_system.py # Cryptocurrency scoring
│       └── bot_manager.py     # Bot management utilities
├── tests/                     # 🧪 Test suite (REORGANIZED)
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── backtests/             # Backtesting scripts
├── scripts/                   # 🛠️ Scripts (NEW)
│   ├── deployment/            # Deployment scripts
│   │   ├── alpine_launcher.sh # Main launcher
│   │   ├── launch_alpine.py   # Python launcher
│   │   └── start_*.py        # Various start scripts
│   └── utilities/             # Utility scripts
│       ├── check_status.py    # Status checker
│       ├── kill_all_bots.py   # Emergency stop
│       └── show_*.py         # Display utilities
├── data/                      # 📊 Data files (NEW)
│   ├── logs/                  # Log files
│   ├── results/               # Trading results
│   └── configs/               # Configuration files
├── docs/                      # 📚 Documentation (REORGANIZED)
│   ├── api/                   # API documentation
│   ├── guides/                # User guides
│   └── fixes/                 # Fix documentation
├── archives/                  # 📦 Archives (NEW)
│   └── old_versions/          # Deprecated files
└── .devcontainer/             # GitHub Codespaces config
```

## 📋 Features

### 🎯 Trading Strategy
- **Volume Anomaly Detection**: Advanced algorithms to identify unusual volume patterns
- **Multi-Timeframe Analysis**: Comprehensive market analysis across multiple timeframes
- **Dynamic Position Sizing**: Intelligent position sizing based on market conditions
- **Risk-First Approach**: Multiple risk management systems with versioning support

### 🔧 System Features
- **Modular Architecture**: Clean separation of concerns for easy maintenance
- **Version Control**: Proper versioning for all components
- **Comprehensive Testing**: Unit, integration, and backtesting frameworks
- **Professional Deployment**: Multiple deployment options and utilities
- **Real-time Monitoring**: Live dashboard and status monitoring
- **Emergency Controls**: Quick stop and restart capabilities

## 📚 Documentation

- **[📖 Directory Structure](DIRECTORY_STRUCTURE.md)**: Complete project organization guide
- **[🚀 API Documentation](docs/api/)**: Technical API reference
- **[📋 User Guides](docs/guides/)**: Step-by-step guides and tutorials
- **[🔧 Fix Documentation](docs/fixes/)**: System improvements and fixes

## 🛠️ Usage

### Launch Options
```bash
# Main launcher (recommended)
python scripts/deployment/launch_alpine.py

# Shell script launcher
./scripts/deployment/alpine_launcher.sh

# Clean start
python scripts/deployment/clean_start_alpine.py

# Direct run
python scripts/deployment/run_alpine_bot.py
```

### Monitoring
```bash
# Check bot status
python scripts/utilities/check_status.py

# Show statistics
python scripts/utilities/show_alpine_stats.py

# Verify functionality
python scripts/utilities/verify_bot_functionality.py
```

### Testing
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Run backtests
python tests/backtests/volume_anomaly_backtest.py
```

### Emergency Controls
```bash
# Stop all bots immediately
python scripts/utilities/kill_all_bots.py

# Force restart
python scripts/deployment/clean_start_alpine.py
```

## ⚙️ Configuration

Configuration files are now organized in `data/configs/`:
- `relaxed_config.json` - Relaxed trading parameters
- `.env` - Environment variables and API keys

## 🔄 Migration from Old Structure

If you're upgrading from the old structure:

1. **All source code** moved to `src/` directory
2. **All tests** moved to `tests/` with proper categorization
3. **All scripts** moved to `scripts/` (deployment vs utilities)
4. **All data files** moved to `data/` directory
5. **All documentation** reorganized in `docs/`
6. **Old files** preserved in `archives/old_versions/`

## 🎨 Recent Improvements

- ✅ **Complete directory restructure** for better organization
- ✅ **Version naming conventions** for all components
- ✅ **Separated test types** (unit, integration, backtests)
- ✅ **Organized deployment scripts** and utilities
- ✅ **Centralized data management** (logs, results, configs)
- ✅ **Comprehensive documentation** system
- ✅ **Archive system** for old versions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the established directory structure in `src/`
4. Add tests in appropriate `tests/` subdirectory
5. Update documentation in `docs/`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

Trading cryptocurrencies involves substantial risk. This bot is for educational and research purposes. Use at your own risk and never trade with money you can't afford to lose.

---

**📁 For detailed information about the new project structure, see [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)**
