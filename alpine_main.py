#!/usr/bin/env python3
"""
🌿 Alpine Trading Bot - macOS Executable Entry Point
High-performance volume anomaly trading system with 75%+ confidence signals
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def get_bot_pid():
    """Get the PID of the running trading bot"""
    try:
        result = subprocess.run(['pgrep', '-f', 'start_trading.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        return None

def is_bot_running():
    """Check if the trading bot is currently running"""
    return get_bot_pid() is not None

def print_banner():
    """Print the Alpine Trading Bot banner"""
    print("\033[0;32m🌿 Alpine Trading Bot - macOS Edition\033[0m")
    print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")

def show_help():
    """Display help menu"""
    print_banner()
    print()
    print("\033[1;33mTRADING COMMANDS:\033[0m")
    print("  start           🚀 Start the trading bot with live trading")
    print("  demo            📊 Start the bot in demo/simulation mode")
    print("  stop            ⏹️  Stop the running trading bot")
    print("  restart         🔄 Restart the trading bot")
    print()
    print("\033[1;33mMONITORING COMMANDS:\033[0m")
    print("  status          📈 Check bot status and running processes")
    print("  logs            📝 View recent trading logs")
    print("  balance         💰 Check account balance")
    print("  signals         🎯 Show recent trading signals")
    print()
    print("\033[1;33mTESTING COMMANDS:\033[0m")
    print("  test            🧪 Run system tests")
    print("  connection      🔌 Test Bitget connection")
    print("  config          ⚙️  Validate configuration")
    print()
    print("\033[1;33mEXAMPLES:\033[0m")
    print("  alpine start           # Start live trading")
    print("  alpine demo            # Run in simulation mode")
    print("  alpine logs            # View recent logs")
    print("  alpine status          # Check if bot is running")
    print()
    print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")

def start_bot(demo_mode=False):
    """Start the trading bot"""
    mode = "Demo" if demo_mode else "Live Trading"
    print(f"\033[0;32m🚀 Starting Alpine Trading Bot ({mode})...\033[0m")
    
    if is_bot_running():
        pid = get_bot_pid()
        print(f"\033[1;33m⚠️  Bot is already running (PID: {pid})\033[0m")
        print("Use 'alpine restart' to restart or 'alpine stop' to stop")
        return False
    
    print("\033[0;34m📊 Configuration: 3m signals only, 75%+ confidence\033[0m")
    
    # Start the bot
    cmd = [sys.executable, 'start_trading.py']
    if demo_mode:
        cmd.append('--demo')
    else:
        cmd.append('--trade')
    
    try:
        # Start the process in the background
        subprocess.Popen(cmd, cwd=current_dir)
        time.sleep(3)  # Give it time to start
        
        if is_bot_running():
            pid = get_bot_pid()
            print(f"\033[0;32m✅ Trading bot started successfully (PID: {pid})\033[0m")
            print("Use 'alpine logs' to monitor activity")
            return True
        else:
            print("\033[0;31m❌ Failed to start trading bot\033[0m")
            return False
    except Exception as e:
        print(f"\033[0;31m❌ Error starting bot: {e}\033[0m")
        return False

def stop_bot():
    """Stop the trading bot"""
    print("\033[1;33m⏹️  Stopping Alpine Trading Bot...\033[0m")
    
    if not is_bot_running():
        print("\033[1;33mℹ️  No trading bot is currently running\033[0m")
        return True
    
    try:
        subprocess.run(['pkill', '-f', 'start_trading.py'], check=False)
        time.sleep(2)
        
        if not is_bot_running():
            print("\033[0;32m✅ Trading bot stopped successfully\033[0m")
            return True
        else:
            print("\033[0;31m❌ Failed to stop trading bot\033[0m")
            return False
    except Exception as e:
        print(f"\033[0;31m❌ Error stopping bot: {e}\033[0m")
        return False

def show_status():
    """Show bot status"""
    print("\033[0;32m📈 Alpine Trading Bot Status\033[0m")
    print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    
    if is_bot_running():
        pid = get_bot_pid()
        print("\033[0;32m🟢 Status: RUNNING\033[0m")
        print(f"\033[0;34m📍 Process ID: {pid}\033[0m")
        
        try:
            # Get process start time
            result = subprocess.run(['ps', '-o', 'lstart=', '-p', pid], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                start_time = result.stdout.strip()
                print(f"\033[0;34m⏰ Started: {start_time}\033[0m")
        except:
            pass
    else:
        print("\033[0;31m🔴 Status: STOPPED\033[0m")
    
    # Show configuration
    print("\033[1;33m⚙️  Configuration:\033[0m")
    print("   • Timeframes: 3m only")
    print("   • Min Confidence: 75%")
    print("   • Risk per Trade: 2%")
    print("   • Max Positions: 20")

def show_balance():
    """Show account balance"""
    print("\033[0;32m💰 Account Balance\033[0m")
    print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    
    try:
        # Import and run balance check
        from bitget_client import BitgetClient
        client = BitgetClient()
        balance = client.get_balance()
        
        print(f'💰 Available: ${balance["available"]:.2f} USDT')
        print(f'📊 Equity: ${balance["usdtEquity"]:.2f} USDT')
        print(f'🔒 Locked: ${balance["locked"]:.2f} USDT')
        print(f'📈 Unrealized P&L: ${balance["unrealizedPL"]:.2f} USDT')
    except Exception as e:
        print(f'❌ Error fetching balance: {e}')

def run_command(cmd_args):
    """Run a system command and return output"""
    try:
        result = subprocess.run(cmd_args, cwd=current_dir, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    """Main CLI entry point"""
    # Change to the bot directory
    os.chdir(current_dir)
    
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if command in ['start', 'trade']:
        start_bot(demo_mode=False)
    elif command in ['demo', 'sim', 'simulation']:
        start_bot(demo_mode=True)
    elif command == 'stop':
        stop_bot()
    elif command == 'restart':
        stop_bot()
        time.sleep(2)
        start_bot(demo_mode=False)
    elif command == 'status':
        show_status()
    elif command == 'balance':
        show_balance()
    elif command in ['logs', 'log']:
        print("\033[0;32m📝 Alpine Trading Bot Logs\033[0m")
        print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        
        from datetime import datetime
        log_file = f"logs/alpine_bot_{datetime.now().strftime('%Y-%m-%d')}.log"
        if os.path.exists(log_file):
            print("\033[1;33m🎯 Recent Signals (Last 10):\033[0m")
            run_command(['grep', '-E', '(Signal|confidence|CONFLUENCE)', log_file])
            print()
            print("\033[1;33m📊 Recent Activity (Last 20 lines):\033[0m")
            run_command(['tail', '-20', log_file])
        else:
            print("No log file found for today")
    elif command == 'signals':
        print("\033[0;32m🎯 Recent Trading Signals\033[0m")
        print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        
        from datetime import datetime
        log_file = f"logs/alpine_bot_{datetime.now().strftime('%Y-%m-%d')}.log"
        if os.path.exists(log_file):
            run_command(['grep', '-E', '(Signal.*Confidence:|CONFLUENCE SIGNAL)', log_file])
        else:
            print("No signals found today")
    elif command == 'test':
        print("\033[0;32m🧪 Running System Tests\033[0m")
        print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        run_command([sys.executable, 'check_status.py'])
    elif command in ['connection', 'conn']:
        print("\033[0;32m🔌 Testing Bitget Connection\033[0m")
        print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        run_command([sys.executable, 'test_connection.py'])
    elif command == 'config':
        print("\033[0;32m⚙️  Configuration Status\033[0m")
        print("\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        try:
            from config import TradingConfig
            config = TradingConfig()
            print(f'🎯 Timeframes: {config.timeframes}')
            print(f'📊 Min Signal Confidence: {config.min_signal_confidence}%')
            print(f'💰 Risk per Trade: {config.risk_per_trade}%')
            print(f'📈 Max Positions: {config.max_position_size}')
            print(f'⏰ Primary Timeframe: {config.primary_timeframe}')
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    elif command in ['help', '--help', '-h']:
        show_help()
    else:
        print(f"\033[0;31m❌ Unknown command: {command}\033[0m")
        print()
        show_help()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[1;33m⚠️  Operation cancelled by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[0;31m❌ Error: {e}\033[0m")
        sys.exit(1) 