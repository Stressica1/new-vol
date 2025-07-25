#!/bin/bash

# 🌿 Alpine Trading Bot Command Line Interface
# Usage: ./alpine [command] [options]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Bot directory
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_DIR"

# Function to display help
show_help() {
    echo -e "${GREEN}🌿 Alpine Trading Bot CLI${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}TRADING COMMANDS:${NC}"
    echo "  start           🚀 Start the trading bot with live trading"
    echo "  demo            📊 Start the bot in demo/simulation mode"
    echo "  stop            ⏹️  Stop the running trading bot"
    echo "  restart         🔄 Restart the trading bot"
    echo ""
    echo -e "${YELLOW}MONITORING COMMANDS:${NC}"
    echo "  status          📈 Check bot status and running processes"
    echo "  logs            📝 View recent trading logs"
    echo "  balance         💰 Check account balance"
    echo "  signals         🎯 Show recent trading signals"
    echo ""
    echo -e "${YELLOW}TESTING COMMANDS:${NC}"
    echo "  test            🧪 Run system tests"
    echo "  connection      🔌 Test Bitget connection"
    echo "  config          ⚙️  Validate configuration"
    echo ""
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo "  ./alpine start           # Start live trading"
    echo "  ./alpine demo            # Run in simulation mode"
    echo "  ./alpine logs            # View recent logs"
    echo "  ./alpine status          # Check if bot is running"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check if bot is running
is_bot_running() {
    pgrep -f "run_alpine_bot.py\|alpine_bot.py" > /dev/null 2>&1
}

# Function to get bot PID
get_bot_pid() {
    pgrep -f "run_alpine_bot.py\|alpine_bot.py" 2>/dev/null | head -1
}

# Main command handling
case "${1:-help}" in
    "start"|"trade")
        echo -e "${GREEN}🚀 Starting Alpine Trading Bot (Live Trading)...${NC}"
        if is_bot_running; then
            echo -e "${YELLOW}⚠️  Bot is already running (PID: $(get_bot_pid))${NC}"
            echo "Use './alpine restart' to restart or './alpine stop' to stop"
            exit 1
        fi
        echo -e "${BLUE}📊 Configuration: 3m signals only, 75%+ confidence${NC}"
        python3 run_alpine_bot.py &
        sleep 3
        if is_bot_running; then
            echo -e "${GREEN}✅ Trading bot started successfully (PID: $(get_bot_pid))${NC}"
            echo "Use './alpine logs' to monitor activity"
        else
            echo -e "${RED}❌ Failed to start trading bot${NC}"
            exit 1
        fi
        ;;
        
    "demo"|"sim"|"simulation")
        echo -e "${BLUE}📊 Starting Alpine Trading Bot (Demo Mode)...${NC}"
        if is_bot_running; then
            echo -e "${YELLOW}⚠️  Bot is already running (PID: $(get_bot_pid))${NC}"
            echo "Use './alpine restart' to restart or './alpine stop' to stop"
            exit 1
        fi
        python3 run_alpine_bot.py &
        sleep 3
        if is_bot_running; then
            echo -e "${GREEN}✅ Demo bot started successfully (PID: $(get_bot_pid))${NC}"
        else
            echo -e "${RED}❌ Failed to start demo bot${NC}"
            exit 1
        fi
        ;;
        
    "stop")
        echo -e "${YELLOW}⏹️  Stopping Alpine Trading Bot...${NC}"
        if is_bot_running; then
            pkill -f "run_alpine_bot.py\|alpine_bot.py"
            sleep 2
            if ! is_bot_running; then
                echo -e "${GREEN}✅ Trading bot stopped successfully${NC}"
            else
                echo -e "${RED}❌ Failed to stop trading bot${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}ℹ️  No trading bot is currently running${NC}"
        fi
        ;;
        
    "restart")
        echo -e "${BLUE}🔄 Restarting Alpine Trading Bot...${NC}"
        if is_bot_running; then
            ./alpine stop
            sleep 2
        fi
        ./alpine start
        ;;
        
    "status")
        echo -e "${GREEN}📈 Alpine Trading Bot Status${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        if is_bot_running; then
            echo -e "${GREEN}🟢 Status: RUNNING${NC}"
            echo -e "${BLUE}📍 Process ID: $(get_bot_pid)${NC}"
            echo -e "${BLUE}⏰ Started: $(ps -o lstart= -p $(get_bot_pid) 2>/dev/null || echo 'Unknown')${NC}"
        else
            echo -e "${RED}🔴 Status: STOPPED${NC}"
        fi
        
        # Show configuration
        echo -e "${YELLOW}⚙️  Configuration:${NC}"
        echo "   • Timeframes: 3m only"
        echo "   • Min Confidence: 75%"
        echo "   • Risk per Trade: 2%"
        echo "   • Max Positions: 20"
        
        # Show recent activity
        if [[ -f "logs/alpine_bot_$(date +%Y-%m-%d).log" ]]; then
            echo -e "${YELLOW}📊 Recent Activity:${NC}"
            tail -3 "logs/alpine_bot_$(date +%Y-%m-%d).log" | grep -E "(Signal|signal|complete)" | tail -2 || echo "   No recent signals"
        fi
        ;;
        
    "logs")
        echo -e "${GREEN}📝 Alpine Trading Bot Logs${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Show recent signals and activity
        if [[ -f "logs/alpine_bot_$(date +%Y-%m-%d).log" ]]; then
            echo -e "${YELLOW}🎯 Recent Signals (Last 10):${NC}"
            grep -E "(Signal|confidence|CONFLUENCE)" "logs/alpine_bot_$(date +%Y-%m-%d).log" | tail -10 || echo "No recent signals found"
            echo ""
            echo -e "${YELLOW}📊 Recent Activity (Last 20 lines):${NC}"
            tail -20 "logs/alpine_bot_$(date +%Y-%m-%d).log"
        else
            echo "No log file found for today"
        fi
        ;;
        
    "balance")
        echo -e "${GREEN}💰 Account Balance${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python3 -c "
import sys
sys.path.append('.')
from bitget_client import BitgetClient
try:
    client = BitgetClient()
    balance = client.get_balance()
    print(f'💰 Available: \${balance[\"available\"]:.2f} USDT')
    print(f'📊 Equity: \${balance[\"usdtEquity\"]:.2f} USDT')
    print(f'🔒 Locked: \${balance[\"locked\"]:.2f} USDT')
    print(f'📈 Unrealized P&L: \${balance[\"unrealizedPL\"]:.2f} USDT')
except Exception as e:
    print(f'❌ Error fetching balance: {e}')
"
        ;;
        
    "signals")
        echo -e "${GREEN}🎯 Recent Trading Signals${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        if [[ -f "logs/alpine_bot_$(date +%Y-%m-%d).log" ]]; then
            grep -E "(Signal.*Confidence:|CONFLUENCE SIGNAL)" "logs/alpine_bot_$(date +%Y-%m-%d).log" | tail -15 || echo "No signals found today"
        else
            echo "No log file found for today"
        fi
        ;;
        
    "test")
        echo -e "${GREEN}🧪 Running System Tests${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python3 check_status.py
        ;;
        
    "connection"|"conn")
        echo -e "${GREEN}🔌 Testing Bitget Connection${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python3 test_connection.py
        ;;
        
    "config")
        echo -e "${GREEN}⚙️  Configuration Status${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python3 -c "
from config import TradingConfig
config = TradingConfig()
print(f'🎯 Timeframes: {config.timeframes}')
print(f'📊 Min Signal Confidence: {config.min_signal_confidence}%')
print(f'💰 Risk per Trade: {config.risk_per_trade}%')
print(f'📈 Max Positions: {config.max_position_size}')
print(f'⏰ Primary Timeframe: {config.primary_timeframe}')
"
        ;;
        
    "help"|"--help"|"-h"|"")
        show_help
        ;;
        
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 