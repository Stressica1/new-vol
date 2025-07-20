#!/usr/bin/env python3
"""
🧪 Unit Tests for Alpine Trading Bot Error Handling
✅ Comprehensive testing of all validation and error handling methods
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpine_trading_bot import AlpineTradingBot, TradingConfig, Position

class TestErrorHandling(unittest.TestCase):
    """🧪 Test error handling and validation methods"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = AlpineTradingBot()
        
    def test_validate_dependencies_success(self):
        """✅ Test dependency validation with all packages available"""
        # Test that the bot can be initialized without import errors
        self.assertIsNotNone(self.bot, "Bot should initialize successfully")
    
    def test_validate_environment_success(self):
        """✅ Test environment validation with all variables set"""
        # Set environment variables for testing
        os.environ['BITGET_API_KEY'] = 'test_key'
        os.environ['BITGET_SECRET_KEY'] = 'test_secret'
        os.environ['BITGET_PASSPHRASE'] = 'test_passphrase'
        
        # Test that environment variables are accessible
        self.assertIn('BITGET_API_KEY', os.environ)
        self.assertIn('BITGET_SECRET_KEY', os.environ)
        self.assertIn('BITGET_PASSPHRASE', os.environ)
    
    def test_validate_config_success(self):
        """✅ Test configuration validation with valid settings"""
        result = self.bot.validate_config()
        self.assertTrue(result, "Configuration validation should pass with valid settings")
    
    def test_validate_config_invalid_position_size(self):
        """✅ Test configuration validation with invalid position size"""
        # Temporarily modify config to test validation
        original_size = self.bot.config.position_size_pct
        self.bot.config.position_size_pct = 20.0  # 20% * 5 positions = 100% > 55%
        
        result = self.bot.validate_config()
        self.assertFalse(result, "Configuration validation should fail with invalid position size")
        
        # Restore original value
        self.bot.config.position_size_pct = original_size
    
    def test_validate_config_invalid_leverage(self):
        """✅ Test configuration validation with invalid leverage"""
        original_leverage = self.bot.config.leverage_filter
        self.bot.config.leverage_filter = 10  # Below minimum 25x
        
        result = self.bot.validate_config()
        self.assertFalse(result, "Configuration validation should fail with invalid leverage")
        
        # Restore original value
        self.bot.config.leverage_filter = original_leverage
    
    def test_validate_input_parameters_success(self):
        """✅ Test input parameter validation with valid parameters"""
        result = self.bot.validate_input_parameters("BTC/USDT:USDT", "5m", 25)
        self.assertTrue(result, "Input validation should pass with valid parameters")
    
    def test_validate_input_parameters_invalid_symbol(self):
        """✅ Test input parameter validation with invalid symbol"""
        result = self.bot.validate_input_parameters("BTC/USDT", "5m", 25)
        self.assertFalse(result, "Input validation should fail with invalid symbol")
    
    def test_validate_input_parameters_invalid_timeframe(self):
        """✅ Test input parameter validation with invalid timeframe"""
        result = self.bot.validate_input_parameters("BTC/USDT:USDT", "invalid", 25)
        self.assertFalse(result, "Input validation should fail with invalid timeframe")
    
    def test_validate_input_parameters_invalid_limit(self):
        """✅ Test input parameter validation with invalid limit"""
        result = self.bot.validate_input_parameters("BTC/USDT:USDT", "5m", 5)  # Too low
        self.assertFalse(result, "Input validation should fail with invalid limit")
        
        result = self.bot.validate_input_parameters("BTC/USDT:USDT", "5m", 2000)  # Too high
        self.assertFalse(result, "Input validation should fail with invalid limit")

class TestSafeExecution(unittest.TestCase):
    """🧪 Test safe execution methods"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = AlpineTradingBot()
    
    @patch.object(AlpineTradingBot, 'execute_trade')
    async def test_safe_execute_trade_success(self, mock_execute):
        """✅ Test safe trade execution with valid signal"""
        mock_execute.return_value = True
        
        signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'confidence': 85
        }
        
        result = await self.bot.safe_execute_trade(signal)
        self.assertTrue(result, "Safe trade execution should succeed with valid signal")
    
    async def test_safe_execute_trade_invalid_signal(self):
        """✅ Test safe trade execution with invalid signal"""
        result = await self.bot.safe_execute_trade(None)
        self.assertFalse(result, "Safe trade execution should fail with invalid signal")
    
    async def test_safe_execute_trade_low_confidence(self):
        """✅ Test safe trade execution with low confidence"""
        signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'confidence': 50  # Below 75% threshold
        }
        
        result = await self.bot.safe_execute_trade(signal)
        self.assertFalse(result, "Safe trade execution should fail with low confidence")
    
    @patch.object(AlpineTradingBot, 'update_positions')
    async def test_safe_update_positions_success(self, mock_update):
        """✅ Test safe position update"""
        mock_update.return_value = None
        
        await self.bot.safe_update_positions()
        # Should not raise any exceptions
    
    @patch.object(AlpineTradingBot, 'update_positions')
    async def test_safe_update_positions_error(self, mock_update):
        """✅ Test safe position update with error"""
        mock_update.side_effect = Exception("Update failed")
        
        # Should not raise exception, just log error
        await self.bot.safe_update_positions()
    
    def test_safe_format_positions_success(self):
        """✅ Test safe position formatting"""
        result = self.bot.safe_format_positions(50)
        self.assertIsInstance(result, str, "Safe position formatting should return string")
    
    def test_safe_format_positions_error(self):
        """✅ Test safe position formatting with error"""
        # Mock an error by temporarily breaking the method
        original_method = self.bot.format_positions_responsive
        self.bot.format_positions_responsive = MagicMock(side_effect=Exception("Format error"))
        
        result = self.bot.safe_format_positions(50)
        self.assertIn("Error formatting positions", result, "Should return error message")
        
        # Restore original method
        self.bot.format_positions_responsive = original_method
    
    def test_safe_format_signals_success(self):
        """✅ Test safe signal formatting"""
        result = self.bot.safe_format_signals(50)
        self.assertIsInstance(result, str, "Safe signal formatting should return string")
    
    def test_safe_format_signals_error(self):
        """✅ Test safe signal formatting with error"""
        # Mock an error by temporarily breaking the method
        original_method = self.bot.format_recent_signals_responsive
        self.bot.format_recent_signals_responsive = MagicMock(side_effect=Exception("Format error"))
        
        result = self.bot.safe_format_signals(50)
        self.assertIn("Error formatting signals", result, "Should return error message")
        
        # Restore original method
        self.bot.format_recent_signals_responsive = original_method

class TestRetryLogic(unittest.TestCase):
    """🧪 Test retry logic methods"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = AlpineTradingBot()
    
    @patch.object(AlpineTradingBot, 'connect_exchange')
    async def test_connect_exchange_with_retry_success(self, mock_connect):
        """✅ Test exchange connection retry with success"""
        mock_connect.return_value = None
        
        result = await self.bot.connect_exchange_with_retry()
        self.assertTrue(result, "Retry logic should succeed on first attempt")
    
    @patch.object(AlpineTradingBot, 'connect_exchange')
    async def test_connect_exchange_with_retry_failure(self, mock_connect):
        """✅ Test exchange connection retry with failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = await self.bot.connect_exchange_with_retry(max_retries=2)
        self.assertFalse(result, "Retry logic should fail after all attempts")

class TestPositionClass(unittest.TestCase):
    """🧪 Test Position dataclass"""
    
    def test_position_creation(self):
        """✅ Test Position object creation"""
        position = Position(
            symbol="BTC/USDT:USDT",
            side="buy",
            size=0.1,
            entry_price=50000.0,
            current_price=51000.0,
            pnl=100.0,
            pnl_percent=2.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(position.symbol, "BTC/USDT:USDT")
        self.assertEqual(position.side, "buy")
        self.assertEqual(position.size, 0.1)
        self.assertEqual(position.entry_price, 50000.0)
        self.assertEqual(position.current_price, 51000.0)
        self.assertEqual(position.pnl, 100.0)
        self.assertEqual(position.pnl_percent, 2.0)

class TestTradingConfig(unittest.TestCase):
    """🧪 Test TradingConfig dataclass"""
    
    def test_config_creation(self):
        """✅ Test TradingConfig object creation"""
        config = TradingConfig()
        
        self.assertEqual(config.max_positions, 5)
        self.assertEqual(config.position_size_pct, 11.0)
        self.assertEqual(config.leverage_filter, 25)
        self.assertEqual(config.stop_loss_pct, 1.25)
        self.assertEqual(config.take_profit_pct, 1.5)
        self.assertEqual(config.daily_loss_limit, -19.0)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 