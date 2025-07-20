# Directory Structure

This document explains the reorganized directory structure for the volume-anom trading bot project.

## Root Directory Structure

```
volume-anom/
├── src/                    # Source code
├── tests/                  # All test files
├── scripts/                # Deployment and utility scripts
├── data/                   # Data files (logs, results, configs)
├── docs/                   # Documentation
├── archives/               # Old versions and deprecated files
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── README.md              # Main project documentation
```

## Source Code (`src/`)

### Core (`src/core/`)
- Core application logic and configuration
- `bot.py` - Main bot class
- `config.py` - Configuration management
- `data_connector.py` - Data connection utilities
- `manager.py` - Bot manager

### Exchange (`src/exchange/`)
- Exchange-specific clients and integrations
- `bitget_client.py` - Bitget exchange client

### Trading (`src/trading/`)
- Trading logic and algorithms
- `strategy.py` - Trading strategies
- `trade_executor.py` - Trade execution
- `trading_engine.py` - Main trading engine
- `technical_indicators.py` - Technical analysis
- `position_sizing.py` - Position sizing logic
- `risk_manager_v2.py` - Risk management (latest version)
- `risk_management_v1.py` - Risk management (legacy version)

### UI (`src/ui/`)
- User interface components
- `display.py` - Display utilities
- `trading_dashboard.py` - Trading dashboard
- `ui_display.py` - UI display components

### Utils (`src/utils/`)
- Utility functions and helpers
- `crypto_scoring_system.py` - Cryptocurrency scoring
- `bot_manager.py` - Bot management utilities

## Tests (`tests/`)

### Unit Tests (`tests/unit/`)
- Unit tests for individual components
- `test_*.py` - Various unit tests
- `demo_test.py` - Demo functionality tests
- `working_trade_test.py` - Trade functionality tests

### Integration Tests (`tests/integration/`)
- Integration test results and scripts
- `ccxt_integration_test_results_*.json` - CCXT integration results
- `bot_verification_results_*.json` - Bot verification results

### Backtests (`tests/backtests/`)
- Backtesting scripts and results
- `backtest_*.py` - Backtesting scripts
- `volume_anomaly_backtest.py` - Volume anomaly backtesting
- `simulation_equity_curve.png` - Backtest visualization

## Scripts (`scripts/`)

### Deployment (`scripts/deployment/`)
- Scripts for deploying and starting the bot
- `alpine_launcher.sh` - Main launcher script
- `launch_alpine.py` - Python launcher
- `start_*.py` - Various start scripts
- `run_*.py` - Run scripts
- `clean_start_alpine.py` - Clean start utility

### Utilities (`scripts/utilities/`)
- Utility scripts for maintenance and monitoring
- `kill_all_bots.py` - Stop all running bots
- `check_status.py` - Check bot status
- `show_*.py` - Display utilities
- `verify_bot_functionality.py` - Bot verification

## Data (`data/`)

### Logs (`data/logs/`)
- Application logs
- `*.log` - Log files

### Results (`data/results/`)
- Trading results and analysis
- `*.json` - Result files
- `ai_sl_tp_rf.joblib` - ML model files

### Configs (`data/configs/`)
- Configuration files
- `relaxed_config.json` - Relaxed configuration

## Documentation (`docs/`)

### API (`docs/api/`)
- API documentation
- `api.md` - API reference
- `configuration.md` - Configuration guide
- `installation.md` - Installation instructions

### Guides (`docs/guides/`)
- User guides and documentation
- `*_README.md` - Various README files
- `*_GUIDE.md` - User guides
- `*_CHECKLIST.md` - Checklists
- `*_SUMMARY.md` - Summary documents

### Fixes (`docs/fixes/`)
- Fix documentation and system findings
- `*_COMPLETE.md` - Completion documentation
- `*_FIXES.md` - Fix documentation
- `*_IMPROVEMENTS.md` - Improvement documentation
- `*_IMPLEMENTATION.md` - Implementation documentation

## Archives (`archives/`)

### Old Versions (`archives/old_versions/`)
- Deprecated and old version files
- `alpine_*.py` - Old Alpine versions
- `simple_*.py` - Simple implementations
- `ai_sl_tp.py` - Old AI implementation
- `volume_anom_bot.py` - Old bot version
- `main.py` - Old main file

## File Naming Conventions

1. **Versioning**: When multiple versions exist, use `_v1`, `_v2`, etc.
2. **Test Files**: All test files are in `tests/` directory, named `test_*.py` or `*_test.py`
3. **Scripts**: Deployment scripts in `scripts/deployment/`, utilities in `scripts/utilities/`
4. **Documentation**: Organized by type in `docs/` subdirectories
5. **Data Files**: Organized by type in `data/` subdirectories
6. **Archives**: Old/deprecated files moved to `archives/old_versions/`

## Benefits of This Structure

1. **Clear Separation**: Source code, tests, scripts, and data are clearly separated
2. **Scalability**: Easy to add new components in appropriate directories
3. **Maintainability**: Logical organization makes code easier to maintain
4. **Documentation**: All documentation is centralized and organized
5. **Version Control**: Old versions are preserved in archives
6. **Testing**: All tests are organized by type and purpose
