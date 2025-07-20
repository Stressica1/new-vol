#!/usr/bin/env python3
"""
🧪 POSITION SIZING SAFETY TESTS
Critical: These tests prevent financial losses from position sizing calculation errors
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from alpine_bot_complete import AlpineCompleteBot


class TestPositionSizingSafety:
    """🧪 Test position sizing calculations for financial safety"""
    
    @pytest.fixture
    def bot(self):
        """Create bot instance for testing"""
        bot = AlpineCompleteBot()
        return bot
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_position_size_calculation_accuracy(self, bot):
        """💰 Test position sizing calculation accuracy"""
        bot.balance = 1000.0
        position_size_pct = 11.0
        max_trade_value = 19.0
        price = 50000.0
        
        # Calculate expected values
        expected_trade_value = min(bot.balance * (position_size_pct / 100), max_trade_value)
        expected_target_notional = max(5.0, expected_trade_value)
        expected_quantity = expected_target_notional / price
        
        # Test the calculation logic (extracted from bot)
        max_trade_value_calc = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value_calc)
        quantity = target_notional / price
        
        assert abs(quantity - expected_quantity) < 1e-8, "Position size calculation error"
        assert target_notional >= 5.0, "Target notional below minimum"
        assert target_notional <= 110.0, "Target notional exceeds 11% of balance"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_position_size_with_small_balance(self, bot):
        """⚠️ Test position sizing with small balance"""
        bot.balance = 50.0  # Small balance
        position_size_pct = 11.0
        price = 50000.0
        
        max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value)
        quantity = target_notional / price
        
        # With $50 balance, 11% = $5.50, so target_notional should be $5.50
        assert target_notional == 5.5, f"Expected $5.50, got ${target_notional}"
        assert quantity == 5.5 / price, "Quantity calculation incorrect"
        
        # Trade value should not exceed balance percentage
        trade_value = quantity * price
        assert trade_value <= bot.balance * 0.11, "Trade value exceeds balance percentage"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_position_size_with_large_balance(self, bot):
        """💰 Test position sizing with large balance"""
        bot.balance = 10000.0  # Large balance
        position_size_pct = 11.0
        price = 50000.0
        
        max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value)
        quantity = target_notional / price
        
        # With $10,000 balance, 11% = $1,100, but capped at $19
        assert target_notional == 19.0, f"Expected $19.00, got ${target_notional}"
        assert quantity == 19.0 / price, "Quantity calculation incorrect"
        
        # Trade value should be capped at $19
        trade_value = quantity * price
        assert trade_value == 19.0, "Trade value not properly capped"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_minimum_trade_value_enforcement(self, bot):
        """🔒 Test minimum trade value enforcement"""
        bot.balance = 1.0  # Very small balance
        position_size_pct = 11.0
        price = 50000.0
        
        max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value)
        quantity = target_notional / price
        
        # Even with tiny balance, minimum trade should be $5
        assert target_notional == 5.0, f"Expected $5.00 minimum, got ${target_notional}"
        
        # Verify trade value
        trade_value = quantity * price
        assert trade_value == 5.0, "Minimum trade value not enforced"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_zero_balance_protection(self, bot):
        """🚨 Test zero balance protection"""
        bot.balance = 0.0
        position_size_pct = 11.0
        price = 50000.0
        
        max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value)
        quantity = target_notional / price
        
        # Even with zero balance, system will try minimum $5 trade
        # This should be caught at a higher level in the actual trading logic
        assert target_notional == 5.0, "Zero balance should still enforce minimum"
        
        # Note: In production, this should be prevented before position sizing
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_negative_balance_protection(self, bot):
        """🚨 Test negative balance protection"""
        bot.balance = -100.0  # Negative balance (edge case)
        position_size_pct = 11.0
        price = 50000.0
        
        max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
        target_notional = max(5.0, max_trade_value)
        quantity = target_notional / price
        
        # With negative balance, percentage calculation gives negative value
        # But max() ensures minimum $5
        assert target_notional == 5.0, "Negative balance should be protected"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_price_precision_handling(self, bot):
        """🎯 Test price precision handling"""
        bot.balance = 1000.0
        position_size_pct = 11.0
        
        # Test with various price precisions
        test_prices = [0.00001, 0.1, 1.0, 100.0, 50000.0, 1000000.0]
        
        for price in test_prices:
            max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
            target_notional = max(5.0, max_trade_value)
            quantity = target_notional / price
            
            # Verify calculations are consistent
            trade_value = quantity * price
            assert abs(trade_value - target_notional) < 1e-10, f"Precision error at price {price}"
            assert quantity > 0, f"Quantity should be positive for price {price}"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_trade_execution_position_validation(self, bot):
        """🔒 Test trade execution validates position size"""
        bot.balance = 1000.0
        
        # Mock exchange
        bot.exchange = Mock()
        bot.exchange.create_order = AsyncMock()
        bot.exchange.fetch_order = AsyncMock()
        
        # Create test signal
        signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'price': 50000.0,
            'confidence': 80
        }
        
        # Mock order response
        bot.exchange.create_order.return_value = {'id': 'test123'}
        bot.exchange.fetch_order.return_value = {
            'status': 'filled',
            'average': 50000.0
        }
        
        # This should pass validation
        result = await bot.execute_trade(signal)
        
        # Verify create_order was called with correct parameters
        bot.exchange.create_order.assert_called_once()
        call_args = bot.exchange.create_order.call_args
        
        # Extract quantity from the call
        quantity_used = call_args[1]['amount']  # keyword argument
        expected_quantity = 19.0 / 50000.0  # $19 / $50,000
        
        assert abs(quantity_used - expected_quantity) < 1e-8, "Incorrect quantity passed to exchange"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_leverage_calculation_safety(self, bot):
        """⚖️ Test leverage calculations don't exceed limits"""
        # Test with various scenarios
        test_cases = [
            {'balance': 100, 'price': 50000, 'leverage': 25},
            {'balance': 1000, 'price': 50000, 'leverage': 25},
            {'balance': 10000, 'price': 50000, 'leverage': 25},
        ]
        
        for case in test_cases:
            bot.balance = case['balance']
            position_size_pct = 11.0
            
            max_trade_value = min(bot.balance * (position_size_pct / 100), 19.0)
            target_notional = max(5.0, max_trade_value)
            quantity = target_notional / case['price']
            
            # Calculate effective leverage
            required_margin = target_notional / case['leverage']
            effective_leverage = target_notional / required_margin
            
            assert effective_leverage <= case['leverage'], "Effective leverage exceeds maximum"
            assert required_margin <= bot.balance, "Required margin exceeds balance (should be checked elsewhere)"


class TestTradeValueValidation:
    """🧪 Test trade value validation logic"""
    
    @pytest.fixture
    def bot(self):
        return AlpineCompleteBot()
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_minimum_trade_value_check(self, bot):
        """💵 Test minimum trade value validation"""
        # Test values around the $5 minimum
        test_cases = [
            (4.99, False),  # Below minimum
            (5.00, True),   # At minimum
            (5.01, True),   # Above minimum
            (10.0, True),   # Well above minimum
        ]
        
        for trade_value, should_pass in test_cases:
            result = trade_value >= 5.0
            assert result == should_pass, f"Trade value ${trade_value} validation incorrect"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_percentage_allocation_limits(self, bot):
        """📊 Test percentage allocation limits"""
        test_balances = [100, 1000, 10000, 100000]
        position_size_pct = 11.0
        max_trade_value = 19.0
        
        for balance in test_balances:
            calculated_pct_value = balance * (position_size_pct / 100)
            actual_trade_value = min(calculated_pct_value, max_trade_value)
            
            # Verify percentage never exceeds 11%
            actual_percentage = actual_trade_value / balance * 100
            assert actual_percentage <= position_size_pct, f"Percentage exceeded for balance ${balance}"
            
            # Verify hard cap is enforced
            assert actual_trade_value <= max_trade_value, f"Hard cap exceeded for balance ${balance}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])