# 🌿 Alpine Trading System - Quick Start Guide

## Overview

The Alpine Trading System now features:
- **Beautiful mint green & black terminal display** with real-time PnL tracking
- **Forced Bitget connection** with automatic retry mechanism
- **Dual bot system**: Alpine Bot + Volume Anomaly Bot
- **Optimized trade execution** with smart order management

## Quick Start

### 1. Run the Main Trading System

```bash
python start_trading.py
```

Then select option `1` to start the complete trading system with both bots and the dashboard.

### 2. Command Line Options

```bash
# Start trading directly
python start_trading.py --trade

# Test Bitget connection only
python start_trading.py --test

# Launch dashboard only
python start_trading.py --dashboard
```

### 3. Alternative Launches

```bash
# Run the beautiful mint green dashboard directly
python trading_dashboard.py

# Test connection status
python test_connection.py

# Run individual bots
python alpine_bot.py
python volume_anom_bot.py
```

## Features

### 🌿 Mint Green Terminal Display

The new dashboard features:
- **Account Info**: Real-time balance, equity, margin level
- **PnL Statistics**: Daily, weekly, monthly, and all-time PnL
- **Active Positions**: Live position tracking with unrealized PnL
- **Trading Signals**: Top signals from both bots with confidence scores
- **Activity Log**: Real-time trading activity with color coding

### 🔌 Forced Bitget Connection

- Automatic connection with exponential backoff retry
- Up to 10 retry attempts
- Connection keep-alive with periodic pings
- Automatic reconnection on connection loss

### ⚡ Optimized Trade Execution

- **Smart Position Sizing**: Based on confidence and risk parameters
- **Limit Order Priority**: Better fills with price improvement
- **Dynamic Stop Loss**: ATR-based stops for volatility adaptation
- **Order Retry Logic**: Automatic retry on failed orders
- **Slippage Protection**: Maximum slippage limits

## System Architecture

```
┌─────────────────────────────────────────┐
│      Alpine Trading Dashboard           │
│   (Beautiful Mint Green Display)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│        Trading Orchestrator             │
│    (Manages Both Trading Bots)          │
└────────────────┬────────────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
┌────┴─────┐          ┌─────┴────┐
│ Alpine   │          │ Volume   │
│   Bot    │          │ Anomaly  │
└────┬─────┘          └─────┬────┘
     │                       │
┌────┴────────────────────────┴────┐
│    Optimized Trade Executor      │
│  (Smart Order Management)        │
└──────────────┬───────────────────┘
               │
┌──────────────┴───────────────────┐
│      Bitget Exchange API         │
└──────────────────────────────────┘
```

## Configuration

Edit `config.py` to adjust:
- API credentials (already configured)
- Trading parameters (position size, stop loss, etc.)
- Risk management settings
- Trading pairs selection

## Monitoring

- **Logs**: Check `logs/` directory for detailed logs
- **Real-time Stats**: Watch the dashboard for live updates
- **PnL Tracking**: Monitor performance across all timeframes
- **Signal Quality**: Track confidence scores and win rates

## Troubleshooting

### Connection Issues

If connection fails:
1. Check API credentials in `config.py`
2. Verify internet connection
3. Check Bitget API status
4. Run `python start_trading.py --test` to diagnose

### Performance Issues

- Reduce number of trading pairs in `config.py`
- Increase refresh rate in display settings
- Check system resources (CPU/Memory)

## Safety Features

- Maximum daily loss limit: 50%
- Maximum positions: 30
- Position size limits: 2-10% per trade
- Automatic stop loss on all positions
- Connection monitoring and auto-reconnect

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in terminal
- Verify configuration settings
- Test connection independently

---

**Happy Trading! 🚀**