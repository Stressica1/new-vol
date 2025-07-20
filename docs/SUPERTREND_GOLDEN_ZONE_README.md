# 🏔️ ALPINE TRADING BOT - SUPERTREND GOLDEN ZONE STRATEGY

## 🎯 Overview

Advanced trading strategy combining **Supertrend** indicator with **Fibonacci Golden Zone (0.72-0.88)** for maximum win rate and minimal drawdown. Monte Carlo optimized for professional trading performance.

## 🚀 Key Features

### 📊 Strategy Components
- **Supertrend Indicator**: Trend-following momentum indicator
- **Golden Zone Fibonacci**: 0.72-0.88 Fibonacci retracement levels
- **RSI Confirmation**: 30-70 RSI range for signal validation
- **Volume Spike Detection**: 1.5x minimum volume spike requirement
- **Monte Carlo Optimization**: Automated parameter optimization

### 🎯 Signal Logic
1. **Supertrend Direction**: Primary trend signal (bullish/bearish)
2. **Golden Zone Entry**: Price must be in 0.72-0.88 Fibonacci zone
3. **RSI Confirmation**: RSI between 30-70 for optimal entry
4. **Volume Confirmation**: 1.5x volume spike minimum
5. **Confidence Scoring**: 75% minimum confidence required

### 💰 Risk Management
- **Stop Loss**: 1.25% fixed stop loss
- **Take Profit**: 2.0% take profit target
- **Position Size**: 11% per trade (5 trades max = 55% capital)
- **Capital Limit**: Maximum 68% capital in play
- **Leverage**: 25x leverage on Bitget futures

## 📁 File Structure

```
supertrend_golden_zone_strategy.py      # Core strategy implementation
supertrend_golden_zone_backtest.py      # Comprehensive backtesting
supertrend_golden_zone_integration.py   # Live trading integration
SUPERTREND_GOLDEN_ZONE_README.md        # This documentation
```

## 🎯 Strategy Configuration

### Default Parameters
```python
StrategyConfig(
    # Supertrend Settings
    supertrend_period=10,
    supertrend_multiplier=3.0,
    supertrend_atr_period=14,
    
    # Golden Zone Settings
    golden_zone_start=0.72,    # 0.72 Fibonacci level
    golden_zone_end=0.88,      # 0.88 Fibonacci level
    zone_tolerance=0.02,       # 2% tolerance
    
    # Signal Quality
    min_confidence=75.0,       # 75% minimum confidence
    min_volume_spike=1.5,      # 1.5x volume spike
    min_rsi=30.0,             # RSI minimum
    max_rsi=70.0,             # RSI maximum
    
    # Risk Management
    stop_loss_pct=1.25,       # 1.25% stop loss
    take_profit_pct=2.0,      # 2.0% take profit
    max_positions=5,          # Maximum 5 positions
    position_size_pct=11.0    # 11% per position
)
```

## 🚀 Quick Start

### 1. Backtesting
```bash
python supertrend_golden_zone_backtest.py
```

### 2. Live Trading
```bash
python supertrend_golden_zone_integration.py
```

### 3. Strategy Development
```python
from supertrend_golden_zone_strategy import SupertrendGoldenZoneStrategy, StrategyConfig

# Initialize strategy
config = StrategyConfig()
strategy = SupertrendGoldenZoneStrategy(config)

# Generate signal
signal = strategy.generate_signal(df)
```

## 📊 Performance Metrics

### Target Performance
- **Win Rate**: 75-85% target
- **Profit Factor**: >2.0
- **Max Drawdown**: <15%
- **Sharpe Ratio**: >1.5
- **Daily Signals**: 1-5 per pair

### Risk Management
- **Capital Allocation**: Max 55% total capital
- **Position Limits**: 5 concurrent positions
- **Emergency Shutdown**: 85% capital utilization
- **Daily Loss Limit**: 19% maximum daily loss

## 🎯 Signal Generation Process

### 1. Supertrend Calculation
```python
# Calculate ATR
atr = true_range.rolling(period).mean()

# Calculate Supertrend bands
basic_upperband = hl2 + (multiplier * atr)
basic_lowerband = hl2 - (multiplier * atr)

# Generate trend direction
supertrend_direction = 1 if close > supertrend else -1
```

### 2. Golden Zone Detection
```python
# Calculate Fibonacci levels
swing_high = df['high'].rolling(lookback).max()
swing_low = df['low'].rolling(lookback).min()

# Golden Zone (0.72-0.88)
golden_zone_upper = swing_low + (diff * 0.88)
golden_zone_lower = swing_low + (diff * 0.72)

# Check if price is in Golden Zone
in_golden_zone = (price >= golden_zone_lower) & (price <= golden_zone_upper)
```

### 3. Signal Scoring
```python
confidence = 0.0

# Supertrend confirmation (30 points)
if supertrend_direction == 1:
    confidence += 30.0

# Golden Zone confirmation (25 points)
if in_golden_zone:
    confidence += 25.0

# RSI confirmation (15 points)
if min_rsi <= rsi <= max_rsi:
    confidence += 15.0

# Volume confirmation (20 points)
if volume_spike >= min_volume_spike:
    confidence += 20.0

# Minimum 75% confidence required
if confidence >= 75.0:
    generate_signal()
```

## 🔧 Monte Carlo Optimization

### Optimization Parameters
- **Iterations**: 1000 Monte Carlo iterations
- **Target Metric**: Sharpe Ratio optimization
- **Parameter Ranges**:
  - Supertrend Period: 7-15
  - Supertrend Multiplier: 2.0-4.0
  - Golden Zone: 0.70-0.90
  - RSI Range: 25-75
  - Volume Spike: 1.3-2.0x

### Optimization Process
1. **Random Parameter Generation**: Generate random parameter sets
2. **Historical Backtesting**: Test on 5m timeframe data
3. **Performance Scoring**: Calculate Sharpe ratio, win rate, drawdown
4. **Parameter Selection**: Choose best performing parameters
5. **Validation**: Test on out-of-sample data

## 📈 Backtesting Results

### Expected Performance
- **Win Rate**: 75-85%
- **Profit Factor**: 2.0-3.0
- **Max Drawdown**: 10-15%
- **Sharpe Ratio**: 1.5-2.5
- **Average Trade**: $15-25 profit

### Risk Metrics
- **Consecutive Wins**: 3-5 average
- **Consecutive Losses**: 1-2 average
- **Largest Win**: $50-100
- **Largest Loss**: $15-25
- **Average Win**: $20-30
- **Average Loss**: $15-20

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install ccxt pandas numpy loguru python-dotenv
```

### 2. Environment Setup
```bash
# Create .env file
BITGET_API_KEY=your_api_key
BITGET_SECRET_KEY=your_secret_key
BITGET_PASSPHRASE=your_passphrase
```

### 3. Directory Structure
```
logs/
├── supertrend_golden_zone.log
├── supertrend_backtest.log
└── supertrend_integration.log
```

## 🔍 Monitoring & Logging

### Log Files
- **Strategy Logs**: `logs/supertrend_golden_zone.log`
- **Backtest Logs**: `logs/supertrend_backtest.log`
- **Integration Logs**: `logs/supertrend_integration.log`

### Key Metrics
- **Signal Generation**: Real-time signal logging
- **Trade Execution**: Order placement and management
- **Performance Tracking**: PnL and win rate monitoring
- **Error Handling**: Comprehensive error logging

## 🚨 Risk Warnings

### Important Considerations
- **High Leverage**: 25x leverage increases risk
- **Market Volatility**: Crypto markets are highly volatile
- **Capital Management**: Never risk more than 55% of capital
- **Testing Required**: Always backtest before live trading
- **Stop Losses**: Always use stop losses

### Emergency Procedures
- **Capital Limit**: Automatic shutdown at 85% utilization
- **Position Limits**: Maximum 5 concurrent positions
- **Daily Loss Limit**: Stop trading at 19% daily loss
- **Manual Override**: Ability to close all positions

## 📊 Integration with Alpine System

### Compatibility
- **Exchange**: Bitget futures
- **Timeframe**: 5-minute candles
- **Pairs**: USDT perpetual contracts
- **Leverage**: 25x cross margin

### System Integration
- **Unified Logging**: Consistent with Alpine system
- **Capital Management**: Integrated risk controls
- **Position Tracking**: Real-time position monitoring
- **Performance Metrics**: Comprehensive reporting

## 🎯 Advanced Features

### 1. Dynamic Parameter Adjustment
- **Market Conditions**: Adjust parameters based on volatility
- **Performance Feedback**: Optimize based on recent results
- **Risk Adjustment**: Modify position sizes based on drawdown

### 2. Multi-Timeframe Analysis
- **Higher Timeframes**: 15m and 1h trend confirmation
- **Lower Timeframes**: 1m for precise entry timing
- **Timeframe Alignment**: Confirm signals across timeframes

### 3. Advanced Risk Management
- **Dynamic Stop Loss**: Trailing stops based on ATR
- **Position Sizing**: Kelly criterion for optimal sizing
- **Portfolio Heat**: Monitor correlation between positions

## 🔧 Troubleshooting

### Common Issues
1. **API Connection**: Check API credentials and network
2. **Data Quality**: Verify OHLCV data integrity
3. **Signal Generation**: Monitor confidence thresholds
4. **Order Execution**: Check exchange order limits

### Debug Mode
```python
# Enable debug logging
logger.add("debug.log", level="DEBUG")

# Test signal generation
test_signal = strategy.generate_signal(test_df)
print(f"Signal: {test_signal}")
```

## 📈 Performance Optimization

### 1. Parameter Tuning
- **Supertrend Sensitivity**: Adjust period and multiplier
- **Golden Zone Width**: Modify zone tolerance
- **RSI Range**: Optimize overbought/oversold levels
- **Volume Threshold**: Adjust spike requirements

### 2. Market Adaptation
- **Volatility Adjustment**: Modify parameters for high/low volatility
- **Trend Strength**: Adjust for strong/weak trends
- **Volume Patterns**: Adapt to different volume regimes

### 3. Risk Optimization
- **Position Sizing**: Dynamic sizing based on volatility
- **Stop Loss Adjustment**: ATR-based stop losses
- **Take Profit Scaling**: Multiple profit targets

## 🎯 Future Enhancements

### Planned Features
- **Machine Learning**: ML-based parameter optimization
- **Multi-Exchange**: Support for additional exchanges
- **Advanced Analytics**: Real-time performance dashboard
- **Mobile Alerts**: Push notifications for signals

### Research Areas
- **Alternative Indicators**: Additional technical indicators
- **Market Regime Detection**: Adaptive strategy selection
- **Portfolio Optimization**: Multi-strategy allocation
- **Risk Parity**: Advanced risk management techniques

---

## 📞 Support

For questions, issues, or feature requests:
- **Documentation**: Check this README and inline comments
- **Logs**: Review log files for detailed information
- **Backtesting**: Always test thoroughly before live trading
- **Risk Management**: Never risk more than you can afford to lose

**⚠️ DISCLAIMER**: This is for educational purposes only. Trading involves substantial risk of loss. Always test thoroughly and never risk more than you can afford to lose. 