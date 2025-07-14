# 🤖 Alpine Bot Restart/Reload System

## Overview
Implemented automatic process management so that every Alpine bot automatically kills all other Alpine bot processes when starting, ensuring only one bot runs at a time.

## Features Added

### 🔧 Bot Manager (`bot_manager.py`)
- **Process Detection**: Automatically finds all running Alpine bot processes
- **Graceful Termination**: Uses SIGTERM first, then SIGKILL if needed
- **Log Cleanup**: Clears old log files when starting new bots
- **Process Exclusion**: Excludes current process when killing others

### 🤖 Automatic Process Management
All Alpine bots now automatically:
1. **Kill other processes** before starting
2. **Clear old logs** for fresh start
3. **Display startup message** with process management info

## Usage

### Method 1: Direct Bot Execution (NEW - Automatic Process Management)
```bash
# Each bot now automatically kills others before starting
python3 simple_alpine.py              # Kills all others, starts Simple Alpine
python3 simple_alpine_trader.py       # Kills all others, starts Live Trader  
python3 alpine_bot.py                 # Kills all others, starts Full Alpine Bot
```

### Method 2: Bot Manager (Manual Control)
```bash
# Start specific bot with explicit process management
python3 bot_manager.py simple_alpine
python3 bot_manager.py simple_alpine_trader
python3 bot_manager.py alpine_bot

# Kill all Alpine bot processes manually
python3 bot_manager.py kill
```

## Process Management Features

### ✅ **Automatic Detection**
Detects all Alpine bot processes:
- `alpine_bot.py`
- `simple_alpine.py` 
- `simple_alpine_trader.py`
- `trading_dashboard.py`
- `volume_anom_bot.py`

### ✅ **Graceful Shutdown**
1. Sends SIGTERM (graceful shutdown)
2. Waits 1 second for cleanup
3. Sends SIGKILL if still running
4. Provides detailed status feedback

### ✅ **Log Management**
- Automatically clears old `.log` files
- Fresh logs for each bot session
- Prevents log file conflicts

### ✅ **Error Handling**
- Permission denied errors handled
- Process already terminated detection
- Clear error messages and status

## Bot Startup Messages

### Simple Alpine Bot
```
🤖 SIMPLE ALPINE BOT STARTING
🔍 Found X Alpine bot processes:
  • PID XXXX: other_bot.py
✅ Killed 1 Alpine bot processes
🧹 Cleared old log files
```

### Simple Alpine Trader (Live Trading)
```
🤖 SIMPLE ALPINE TRADER STARTING - LIVE TRADING!
🔍 Found X Alpine bot processes:
  • PID XXXX: other_bot.py
✅ Killed 1 Alpine bot processes
🚨 WARNING: This is LIVE TRADING mode!
```

### Alpine Bot V2.0
```
🤖 ALPINE BOT V2.0 STARTING
🔍 Found X Alpine bot processes:
  • PID XXXX: other_bot.py
✅ Killed 1 Alpine bot processes
```

## Benefits

1. **No Conflicts**: Only one bot runs at a time
2. **Clean Startup**: Fresh logs and cleared state
3. **Easy Switching**: Just run the bot you want
4. **Error Prevention**: No port conflicts or API conflicts
5. **Resource Management**: No hanging processes

## Implementation Details

### Process Detection
```python
# Finds all Python processes running Alpine bot scripts
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if script_name in self.alpine_processes:
        # Add to kill list
```

### Graceful Termination
```python
# Try graceful shutdown first
os.kill(proc['pid'], signal.SIGTERM)
time.sleep(1)

# Force kill if still running
if process_still_exists():
    os.kill(proc['pid'], signal.SIGKILL)
```

### Bot Integration
Each bot now includes:
```python
from bot_manager import AlpineBotManager

# In main function:
manager = AlpineBotManager()
manager.kill_alpine_processes(exclude_current=True)
```

**Now every Alpine bot automatically manages processes - just run the bot you want! 🚀** 