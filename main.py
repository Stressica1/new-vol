#!/usr/bin/env python3
"""
Bitget Futures Trading System
Main script for testing connectivity and executing trades
"""

import time
import json
import sys
import signal
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "trading_system.log",
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

from config import config
from bitget_client import bitget_client
from risk_management import risk_manager
from trading_engine import trading_engine

class TradingSystem:
    """Main Trading System Controller"""
    
    def __init__(self):
        self.running = False
        self.setup_signal_handlers()
        logger.info("Trading System initialized")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    def test_connectivity(self) -> bool:
        """Test Bitget API connectivity"""
        logger.info("Testing Bitget API connectivity...")
        
        try:
            # Test basic connection
            if not bitget_client.test_connection():
                logger.error("Failed to connect to Bitget API")
                return False
            
            # Test account access
            account_info = bitget_client.get_account_info()
            if not account_info:
                logger.error("Failed to get account information")
                return False
            
            # Test balance retrieval
            balance = bitget_client.get_balance()
            if not balance:
                logger.error("Failed to get account balance")
                return False
            
            logger.success("✅ Bitget API connectivity test passed")
            
            # Display account summary
            self.display_account_summary(account_info, balance)
            
            return True
            
        except Exception as e:
            logger.error(f"Connectivity test failed: {str(e)}")
            return False
    
    def display_account_summary(self, account_info: List[Dict], balance: Dict):
        """Display account summary"""
        
        logger.info("\n" + "="*50)
        logger.info("ACCOUNT SUMMARY")
        logger.info("="*50)
        
        if balance:
            logger.info(f"💰 Total Equity: {float(balance.get('usdtEquity', 0)):.2f} USDT")
            logger.info(f"💳 Available Balance: {float(balance.get('available', 0)):.2f} USDT")
            logger.info(f"🔒 Margin Used: {float(balance.get('locked', 0)):.2f} USDT")
            logger.info(f"📊 Unrealized PnL: {float(balance.get('unrealizedPL', 0)):.2f} USDT")
            logger.info(f"🎯 Margin Coin: {balance.get('marginCoin', 'USDT')}")
            logger.info(f"⚖️ Leverage: {balance.get('leverage', 'N/A')}")
        
        logger.info("="*50)
    
    def test_trade_execution(self, symbol: str = "BTCUSDT_UMCBL", test_amount: float = 10.0):
        """Test trade execution with small amount"""
        
        logger.info(f"Testing trade execution for {symbol} with {test_amount} USDT...")
        
        try:
            # Get current price
            ticker = bitget_client.get_ticker(symbol)
            if not ticker:
                logger.error(f"Failed to get ticker for {symbol}")
                return False
            
            current_price = float(ticker.get('last', 0))
            logger.info(f"Current price for {symbol}: {current_price}")
            
            # Calculate test position size
            test_size = test_amount / current_price
            
            logger.info(f"Test position size: {test_size:.6f}")
            
            # Check if we can open this position
            can_open, reason = risk_manager.can_open_position(symbol, 'open_long', test_size, current_price)
            
            if not can_open:
                logger.warning(f"Cannot open test position: {reason}")
                return False
            
            logger.success("✅ Trade execution test passed (position validation)")
            logger.info("💡 Skipping actual order placement in test mode")
            
            return True
            
        except Exception as e:
            logger.error(f"Trade execution test failed: {str(e)}")
            return False
    
    def test_risk_management(self):
        """Test risk management system"""
        
        logger.info("Testing risk management system...")
        
        try:
            # Calculate risk metrics
            risk_metrics = risk_manager.calculate_risk_metrics()
            
            # Get risk summary
            risk_summary = risk_manager.get_risk_summary()
            
            logger.info("\n" + "="*50)
            logger.info("RISK MANAGEMENT SUMMARY")
            logger.info("="*50)
            
            logger.info(f"🚨 Risk Level: {risk_summary['risk_level'].upper()}")
            logger.info(f"📊 Open Positions: {risk_summary['position_metrics']['open_positions']}")
            logger.info(f"💰 Daily PnL: {risk_summary['daily_metrics']['daily_pnl']:.2f} USDT")
            logger.info(f"📉 Max Drawdown: {risk_summary['position_metrics']['max_drawdown']:.2%}")
            logger.info(f"🛑 Emergency Stop: {'ACTIVE' if risk_summary['emergency_stop'] else 'INACTIVE'}")
            
            # Display risk limits
            logger.info("\n📋 Risk Limits:")
            limits = risk_summary['risk_limits']
            logger.info(f"  • Max Position Size: {limits['max_position_size']} USDT")
            logger.info(f"  • Max Daily Loss: {limits['max_daily_loss']} USDT")
            logger.info(f"  • Max Drawdown: {limits['max_drawdown']:.2%}")
            logger.info(f"  • Max Open Positions: {limits['max_open_positions']}")
            logger.info(f"  • Risk Per Trade: {limits['risk_per_trade']:.2%}")
            
            logger.info("="*50)
            
            logger.success("✅ Risk management test passed")
            return True
            
        except Exception as e:
            logger.error(f"Risk management test failed: {str(e)}")
            return False
    
    def test_position_monitoring(self):
        """Test position monitoring"""
        
        logger.info("Testing position monitoring...")
        
        try:
            # Get current positions
            positions = bitget_client.get_positions()
            
            logger.info(f"Found {len(positions)} positions")
            
            active_positions = [p for p in positions if float(p.get('total', 0)) != 0]
            
            if active_positions:
                logger.info("\n" + "="*50)
                logger.info("CURRENT POSITIONS")
                logger.info("="*50)
                
                for pos in active_positions:
                    symbol = pos.get('symbol', '')
                    side = pos.get('side', '')
                    size = float(pos.get('total', 0))
                    entry_price = float(pos.get('averageOpenPrice', 0))
                    current_price = float(pos.get('markPrice', 0))
                    unrealized_pnl = float(pos.get('unrealizedPL', 0))
                    
                    logger.info(f"🏷️  {symbol}")
                    logger.info(f"  📊 Side: {side}")
                    logger.info(f"  📏 Size: {size}")
                    logger.info(f"  💰 Entry Price: {entry_price}")
                    logger.info(f"  💹 Current Price: {current_price}")
                    logger.info(f"  📈 Unrealized PnL: {unrealized_pnl:.2f} USDT")
                    logger.info("  " + "-"*30)
                
                logger.info("="*50)
            else:
                logger.info("No active positions found")
            
            logger.success("✅ Position monitoring test passed")
            return True
            
        except Exception as e:
            logger.error(f"Position monitoring test failed: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive system test"""
        
        logger.info("🚀 Starting comprehensive Bitget trading system test...")
        logger.info("="*60)
        
        tests = [
            ("Connectivity Test", self.test_connectivity),
            ("Risk Management Test", self.test_risk_management),
            ("Position Monitoring Test", self.test_position_monitoring),
            ("Trade Execution Test", self.test_trade_execution),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n🔍 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
                    logger.success(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} FAILED: {str(e)}")
            
            time.sleep(1)  # Small delay between tests
        
        logger.info("\n" + "="*60)
        logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            logger.success("🎉 ALL TESTS PASSED! System is ready for trading.")
        else:
            logger.error("⚠️  Some tests failed. Please check the issues above.")
        
        logger.info("="*60)
        
        return passed == total
    
    def start_trading_system(self):
        """Start the full trading system"""
        
        logger.info("Starting trading system...")
        
        if not self.test_connectivity():
            logger.error("Connectivity test failed. Cannot start trading system.")
            return
        
        # Start trading engine
        trading_engine.start()
        
        self.running = True
        logger.success("🚀 Trading system started successfully!")
        
        # Main monitoring loop
        try:
            while self.running:
                # Get and display system status
                trading_summary = trading_engine.get_trading_summary()
                
                # Log periodic status
                if int(time.time()) % 30 == 0:  # Every 30 seconds
                    self.log_system_status(trading_summary)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.shutdown()
    
    def log_system_status(self, trading_summary: Dict[str, Any]):
        """Log system status periodically"""
        
        engine_status = trading_summary.get('engine_status', {})
        positions = trading_summary.get('positions', {})
        risk_metrics = trading_summary.get('risk_metrics', {})
        
        logger.info(f"📊 System Status - "
                   f"Running: {engine_status.get('running', False)}, "
                   f"Orders: {engine_status.get('total_orders', 0)}, "
                   f"Trades: {engine_status.get('total_trades', 0)}, "
                   f"Positions: {positions.get('total_positions', 0)}, "
                   f"Risk: {risk_metrics.get('risk_level', 'unknown').upper()}")
    
    def shutdown(self):
        """Graceful shutdown"""
        
        logger.info("Shutting down trading system...")
        
        self.running = False
        
        # Stop trading engine
        trading_engine.stop()
        
        logger.info("Trading system shutdown complete")
        sys.exit(0)
    
    def interactive_mode(self):
        """Interactive mode for manual testing"""
        
        logger.info("🎮 Interactive Mode - Available Commands:")
        logger.info("  test - Run comprehensive tests")
        logger.info("  start - Start trading system")
        logger.info("  status - Show system status")
        logger.info("  balance - Show account balance")
        logger.info("  positions - Show current positions")
        logger.info("  risk - Show risk metrics")
        logger.info("  quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "test":
                    self.run_comprehensive_test()
                elif command == "start":
                    self.start_trading_system()
                elif command == "status":
                    summary = trading_engine.get_trading_summary()
                    print(json.dumps(summary, indent=2))
                elif command == "balance":
                    balance = bitget_client.get_balance()
                    print(json.dumps(balance, indent=2))
                elif command == "positions":
                    positions = bitget_client.get_positions()
                    print(json.dumps(positions, indent=2))
                elif command == "risk":
                    risk_summary = risk_manager.get_risk_summary()
                    print(json.dumps(risk_summary, indent=2))
                elif command == "quit":
                    break
                else:
                    logger.info("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
        
        logger.info("Exiting interactive mode...")

def main():
    """Main function"""
    
    # Initialize system
    system = TradingSystem()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            system.run_comprehensive_test()
        elif command == "start":
            system.start_trading_system()
        elif command == "interactive":
            system.interactive_mode()
        else:
            print("Usage: python main.py [test|start|interactive]")
            print("  test - Run comprehensive tests")
            print("  start - Start trading system")
            print("  interactive - Interactive mode")
    else:
        # Default: run comprehensive test
        system.run_comprehensive_test()

if __name__ == "__main__":
    main()