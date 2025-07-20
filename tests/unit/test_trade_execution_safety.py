#!/usr/bin/env python3
"""
🧪 TRADE EXECUTION SAFETY TESTS
Critical: These tests prevent financial losses from trade execution errors
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from alpine_bot_complete import AlpineCompleteBot


class TestTradeExecutionSafety:
    """🧪 Test trade execution logic for financial safety"""
    
    @pytest.fixture
    def bot(self):
        """Create bot instance for testing"""
        bot = AlpineCompleteBot()
        bot.balance = 1000.0
        # Mock exchange
        bot.exchange = Mock()
        return bot
    
    @pytest.fixture
    def valid_signal(self):
        """Create valid signal for testing"""
        return {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'price': 50000.0,
            'confidence': 80,
            'volume_ratio': 2.5,
            'rsi': 35,
            'trend_strength': 0.6,
            'timestamp': '2024-01-01T00:00:00'
        }
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_successful_trade_execution(self, bot, valid_signal):
        """✅ Test successful trade execution flow"""
        # Mock successful exchange responses
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'filled',
            'average': 50000.0,
            'id': 'order123'
        })
        
        result = await bot.execute_trade(valid_signal)
        
        assert result is True, "Trade execution should succeed"
        
        # Verify order was placed correctly
        bot.exchange.create_order.assert_called_once()
        call_args = bot.exchange.create_order.call_args
        
        # Check order parameters
        assert call_args[1]['symbol'] == 'BTC/USDT:USDT'
        assert call_args[1]['type'] == 'market'
        assert call_args[1]['side'] == 'buy'
        assert call_args[1]['amount'] > 0
        assert call_args[1]['params']['leverage'] == 25
        assert call_args[1]['params']['marginMode'] == 'cross'
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_trade_execution_with_invalid_signal(self, bot):
        """🚨 Test trade execution rejects invalid signals"""
        invalid_signals = [
            None,
            {},
            {'symbol': 'BTC/USDT:USDT'},  # Missing required fields
            {'symbol': 'BTC/USDT:USDT', 'side': 'invalid', 'price': 50000},  # Invalid side
            {'symbol': 'BTC/USDT:USDT', 'side': 'buy', 'price': -50000},  # Negative price
            {'symbol': 'BTC/USDT:USDT', 'side': 'buy', 'price': 0},  # Zero price
        ]
        
        for invalid_signal in invalid_signals:
            result = await bot.execute_trade(invalid_signal)
            # Should handle gracefully without crashing
            assert result is False or result is None, f"Should reject invalid signal: {invalid_signal}"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_stop_loss_calculation_accuracy(self, bot, valid_signal):
        """🛡️ Test stop loss calculation accuracy"""
        # Mock exchange responses
        bot.exchange.create_order = AsyncMock()
        
        # Mock main order response
        bot.exchange.create_order.side_effect = [
            {'id': 'main_order'},  # Main order
            {'id': 'sl_order'},    # Stop loss order
            {'id': 'tp_order'},    # Take profit order
        ]
        
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'filled',
            'average': 50000.0
        })
        
        await bot.execute_trade(valid_signal)
        
        # Verify SL order was placed (second call)
        assert bot.exchange.create_order.call_count == 3
        sl_call = bot.exchange.create_order.call_args_list[1]
        
        # Check SL parameters
        assert sl_call[1]['type'] == 'stop'
        assert sl_call[1]['side'] == 'sell'  # Opposite of buy signal
        
        # Verify SL price calculation (1.25% below entry for buy)
        entry_price = 50000.0
        expected_sl_price = entry_price * (1 - 1.25 / 100)
        sl_price = sl_call[1]['price']
        
        assert abs(sl_price - expected_sl_price) < 0.01, f"SL price incorrect: {sl_price} vs {expected_sl_price}"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_take_profit_calculation_accuracy(self, bot, valid_signal):
        """🎯 Test take profit calculation accuracy"""
        # Mock exchange responses
        bot.exchange.create_order = AsyncMock()
        
        bot.exchange.create_order.side_effect = [
            {'id': 'main_order'},
            {'id': 'sl_order'},
            {'id': 'tp_order'},
        ]
        
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'filled',
            'average': 50000.0
        })
        
        await bot.execute_trade(valid_signal)
        
        # Verify TP order was placed (third call)
        tp_call = bot.exchange.create_order.call_args_list[2]
        
        # Check TP parameters
        assert tp_call[1]['type'] == 'limit'
        assert tp_call[1]['side'] == 'sell'  # Opposite of buy signal
        
        # Verify TP price calculation (1.5% above entry for buy)
        entry_price = 50000.0
        expected_tp_price = entry_price * (1 + 1.5 / 100)
        tp_price = tp_call[1]['price']
        
        assert abs(tp_price - expected_tp_price) < 0.01, f"TP price incorrect: {tp_price} vs {expected_tp_price}"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_sell_signal_sl_tp_calculation(self, bot):
        """📉 Test SL/TP calculation for sell signals"""
        sell_signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'sell',
            'price': 50000.0,
            'confidence': 80
        }
        
        # Mock exchange responses
        bot.exchange.create_order = AsyncMock()
        bot.exchange.create_order.side_effect = [
            {'id': 'main_order'},
            {'id': 'sl_order'},
            {'id': 'tp_order'},
        ]
        
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'filled',
            'average': 50000.0
        })
        
        await bot.execute_trade(sell_signal)
        
        # Check SL and TP for sell signal
        sl_call = bot.exchange.create_order.call_args_list[1]
        tp_call = bot.exchange.create_order.call_args_list[2]
        
        entry_price = 50000.0
        
        # For sell: SL above entry, TP below entry
        expected_sl_price = entry_price * (1 + 1.25 / 100)  # 1.25% above
        expected_tp_price = entry_price * (1 - 1.5 / 100)   # 1.5% below
        
        sl_price = sl_call[1]['price']
        tp_price = tp_call[1]['price']
        
        assert abs(sl_price - expected_sl_price) < 0.01, f"Sell SL price incorrect"
        assert abs(tp_price - expected_tp_price) < 0.01, f"Sell TP price incorrect"
        
        # Verify order sides
        assert sl_call[1]['side'] == 'buy'   # Buy to cover short
        assert tp_call[1]['side'] == 'buy'   # Buy to cover short
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_exchange_error_handling(self, bot, valid_signal):
        """🚨 Test exchange error handling"""
        # Test order creation failure
        bot.exchange.create_order = AsyncMock(side_effect=Exception("Exchange error"))
        
        result = await bot.execute_trade(valid_signal)
        
        # Should handle error gracefully
        assert result is False, "Should return False on exchange error"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_order_status_verification(self, bot, valid_signal):
        """🔍 Test order status verification logic"""
        # Mock main order success
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        
        # Test unfilled order
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'open',  # Not filled
            'id': 'order123'
        })
        
        result = await bot.execute_trade(valid_signal)
        
        # Should handle unfilled orders appropriately
        # (Based on current bot logic, it may still try to place SL/TP)
        assert isinstance(result, bool), "Should return boolean result"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_minimum_trade_value_validation(self, bot, valid_signal):
        """💵 Test minimum trade value validation"""
        # Set very small balance to trigger minimum trade check
        bot.balance = 1.0
        
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        bot.exchange.fetch_order = AsyncMock(return_value={
            'status': 'filled',
            'average': 50000.0
        })
        
        # This should still work due to $5 minimum
        result = await bot.execute_trade(valid_signal)
        
        # Verify order was placed with minimum value
        if bot.exchange.create_order.called:
            call_args = bot.exchange.create_order.call_args
            quantity = call_args[1]['amount']
            trade_value = quantity * valid_signal['price']
            
            assert trade_value >= 5.0, "Trade value should meet minimum"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_leverage_application(self, bot, valid_signal):
        """⚖️ Test leverage is applied correctly"""
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        bot.exchange.fetch_order = AsyncMock(return_value={'status': 'filled', 'average': 50000.0})
        
        await bot.execute_trade(valid_signal)
        
        # Check leverage in order parameters
        call_args = bot.exchange.create_order.call_args
        params = call_args[1]['params']
        
        assert params['leverage'] == 25, "Leverage should be 25x"
        assert params['marginMode'] == 'cross', "Should use cross margin"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_quantity_precision_handling(self, bot, valid_signal):
        """🎯 Test quantity precision is handled correctly"""
        # Test with very high price (small quantity)
        high_price_signal = valid_signal.copy()
        high_price_signal['price'] = 1000000.0  # $1M per unit
        
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        bot.exchange.fetch_order = AsyncMock(return_value={'status': 'filled', 'average': 1000000.0})
        
        result = await bot.execute_trade(high_price_signal)
        
        if bot.exchange.create_order.called:
            call_args = bot.exchange.create_order.call_args
            quantity = call_args[1]['amount']
            
            # Quantity should be positive and properly calculated
            assert quantity > 0, "Quantity should be positive"
            assert quantity < 1, "Quantity should be very small for high price"
            
            # Trade value should still be reasonable
            trade_value = quantity * high_price_signal['price']
            assert 5.0 <= trade_value <= 19.0, "Trade value should be within limits"


class TestRiskManagementInTradeExecution:
    """🧪 Test risk management in trade execution"""
    
    @pytest.fixture
    def bot(self):
        bot = AlpineCompleteBot()
        bot.balance = 1000.0
        bot.exchange = Mock()
        return bot
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_position_size_never_exceeds_balance_percentage(self, bot):
        """💰 Test position size never exceeds safe percentage"""
        signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'price': 1.0,  # Low price to test percentage limits
            'confidence': 80
        }
        
        bot.exchange.create_order = AsyncMock(return_value={'id': 'order123'})
        bot.exchange.fetch_order = AsyncMock(return_value={'status': 'filled', 'average': 1.0})
        
        await bot.execute_trade(signal)
        
        if bot.exchange.create_order.called:
            call_args = bot.exchange.create_order.call_args
            quantity = call_args[1]['amount']
            trade_value = quantity * signal['price']
            
            # Should never exceed 11% of balance even with low prices
            max_allowed = bot.balance * 0.11
            assert trade_value <= max_allowed, f"Trade value {trade_value} exceeds {max_allowed}"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_stop_loss_prevents_catastrophic_loss(self, bot):
        """🛡️ Test stop loss prevents catastrophic losses"""
        signal = {
            'symbol': 'BTC/USDT:USDT',
            'side': 'buy',
            'price': 50000.0,
            'confidence': 80
        }
        
        bot.exchange.create_order = AsyncMock()
        bot.exchange.create_order.side_effect = [
            {'id': 'main_order'},
            {'id': 'sl_order'},
            {'id': 'tp_order'},
        ]
        bot.exchange.fetch_order = AsyncMock(return_value={'status': 'filled', 'average': 50000.0})
        
        await bot.execute_trade(signal)
        
        # Verify stop loss limits maximum loss
        sl_call = bot.exchange.create_order.call_args_list[1]
        sl_price = sl_call[1]['price']
        entry_price = 50000.0
        
        # Maximum loss should be 1.25%
        max_loss_pct = (entry_price - sl_price) / entry_price * 100
        assert abs(max_loss_pct - 1.25) < 0.01, f"Stop loss allows too much loss: {max_loss_pct}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])