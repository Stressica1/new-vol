# 🤖 Alpine Bot Management Guide

## 🛑 Process Management Features

The Alpine Bot system now includes **comprehensive process management** to ensure only one bot instance runs at a time.

### 🔧 Enhanced Features

✅ **Auto-Kill System**: Automatically terminates all existing bot processes before starting  
✅ **Smart Detection**: Finds processes by script name AND command line keywords  
✅ **Force Termination**: Uses SIGKILL for stubborn processes  
✅ **Comprehensive Scanning**: Detects Python processes with alpine/trading/bot/bitget/ccxt keywords  
✅ **Safe Exclusions**: Avoids killing pip, conda, jupyter, and other system processes  

## 🚀 How to Start the Bot

### Method 1: Standard Start (with auto-kill)
```bash
python3 alpine_bot.py
```
- Displays startup banner with "🛑 AUTO-KILL OTHER BOTS ENABLED"
- Automatically scans and kills existing bot processes
- Starts fresh Alpine Bot instance

### Method 2: Clean Start (maximum safety)
```bash
python3 clean_start_alpine.py
```
- Step-by-step process termination with visual feedback
- Double verification of process cleanup
- Force kills any remaining stubborn processes
- Guaranteed clean startup

### Method 3: Kill Only (no restart)
```bash
python3 kill_all_bots.py
```
- Only kills existing bot processes
- Does not start a new bot
- Useful for complete shutdown

## 🔍 What Gets Detected and Killed

### Specific Bot Scripts
- `alpine_bot.py`
- `simple_alpine.py`
- `simple_alpine_trader.py`
- `trading_dashboard.py`
- `volume_anom_bot.py`
- `alpine_main.py`
- `alpine_bitget_integration.py`
- `alpine_bot_launcher.py`
- `run_alpine_bot.py`
- `launch_alpine.py`
- `start_trading.py`
- `main.py`
- `demo_test.py`
- And all test/verification scripts

### Keyword-Based Detection
Any Python process containing these keywords in the command line:
- `alpine`
- `trading`
- `bot`
- `bitget`
- `ccxt`

### Safe Exclusions
These processes are NOT killed:
- `pip install`
- `conda`
- `jupyter`
- `setup.py`

## 🔄 Process Flow

1. **🔍 Scan**: Find all existing bot processes
2. **🛑 Terminate**: Send SIGTERM for graceful shutdown
3. **⏳ Wait**: Allow time for graceful termination
4. **⚡ Force Kill**: Use SIGKILL for remaining processes
5. **✅ Verify**: Double-check no processes remain
6. **🚀 Start**: Launch new Alpine Bot instance

## ⚙️ Configuration

The bot manager automatically handles:
- Current process exclusion (when exclude_current=True)
- Multiple termination attempts
- Process verification
- Error handling for access denied/process not found

## 🎯 User Benefits

✅ **No Manual Cleanup**: Never worry about killing old bot processes manually  
✅ **Guaranteed Single Instance**: Only one bot runs at a time  
✅ **Clean State**: Each startup begins with a fresh environment  
✅ **Error Prevention**: Eliminates conflicts from multiple bot instances  
✅ **User-Friendly**: Clear messages about what's being killed and why  

## 🚨 Important Notes

- **This kills ALL trading bot processes** - make sure you want to stop everything
- The system is designed to be aggressive to ensure clean operation
- Processes are given a chance to shut down gracefully before force termination
- The current process is excluded when `exclude_current=True` is used

---

*🏔️ Alpine Trading Bot V2.0 - Next-Generation Process Management* 