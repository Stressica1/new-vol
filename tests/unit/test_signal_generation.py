#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE SIGNAL GENERATION TESTS
Critical: These tests prevent financial losses from signal generation errors
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from alpine_bot_complete import AlpineCompleteBot


class TestSignalGeneration:
    """🧪 Test signal generation logic for financial safety"""
    
    @pytest.fixture
    def bot(self):
        """Create bot instance for testing"""
        bot = AlpineCompleteBot()
        bot.balance = 1000.0  # Mock balance
        return bot
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='5T')
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic price data
        base_price = 50000
        returns = np.random.normal(0, 0.001, 100)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.001))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.001))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 10000, 100)
        })
        df.set_index('timestamp', inplace=True)
        return df
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_signal_generation_with_valid_data(self, bot, sample_ohlcv_data):
        """✅ Test signal generation with valid market data"""
        result = await bot.generate_signal(sample_ohlcv_data, 'BTC/USDT:USDT')
        
        # Signal should be generated or None (both are valid)
        assert result is None or isinstance(result, dict)
        
        if result:
            # Validate required signal fields
            required_fields = ['symbol', 'side', 'price', 'confidence', 'timestamp']
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
            
            # Validate signal values
            assert result['side'] in ['buy', 'sell'], "Invalid signal side"
            assert 0 <= result['confidence'] <= 100, "Confidence must be 0-100%"
            assert result['price'] > 0, "Price must be positive"
            assert result['symbol'] == 'BTC/USDT:USDT', "Symbol mismatch"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_signal_generation_with_insufficient_data(self, bot):
        """🚨 Test signal generation fails safely with insufficient data"""
        # Create data with only 5 candles (insufficient for RSI)
        insufficient_data = pd.DataFrame({
            'open': [50000, 50100, 49900, 50200, 50050],
            'high': [50200, 50300, 50100, 50400, 50150],
            'low': [49800, 49900, 49700, 50000, 49950],
            'close': [50100, 49900, 50200, 50050, 50100],
            'volume': [1000, 1500, 1200, 1800, 1300]
        })
        
        result = await bot.generate_signal(insufficient_data, 'BTC/USDT:USDT')
        
        # Should return None for insufficient data
        assert result is None, "Should return None for insufficient data"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_rsi_calculation_accuracy(self, bot, sample_ohlcv_data):
        """🧮 Test RSI calculation accuracy"""
        # Calculate RSI manually for verification
        prices = sample_ohlcv_data['close']
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        expected_rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # Calculate RSI using bot method
        calculated_rsi = bot.calculate_rsi(sample_ohlcv_data['close'], 14)
        
        # Allow small floating point differences
        assert abs(calculated_rsi - expected_rsi) < 0.01, "RSI calculation inaccurate"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_confidence_calculation_bounds(self, bot, sample_ohlcv_data):
        """📊 Test confidence calculation stays within bounds"""
        # Modify data to create extreme conditions
        extreme_data = sample_ohlcv_data.copy()
        extreme_data['volume'].iloc[-1] = extreme_data['volume'].iloc[-10:-1].mean() * 10  # Huge volume spike
        
        result = await bot.generate_signal(extreme_data, 'BTC/USDT:USDT')
        
        if result:
            assert 0 <= result['confidence'] <= 100, "Confidence out of bounds"
            assert 0 <= result.get('volume_confidence', 0) <= 100, "Volume confidence out of bounds"
            assert 0 <= result.get('rsi_confidence', 0) <= 100, "RSI confidence out of bounds"
            assert 0 <= result.get('trend_confidence', 0) <= 100, "Trend confidence out of bounds"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_signal_side_logic(self, bot):
        """🔄 Test buy/sell signal logic accuracy"""
        # Create data with low RSI (should trigger buy)
        low_rsi_data = pd.DataFrame({
            'open': [50000] * 50,
            'high': [50100] * 50,
            'low': [49900] * 50,
            'close': [49000 - i * 10 for i in range(50)],  # Decreasing price for low RSI
            'volume': [1000] * 49 + [5000]  # High volume on last candle
        })
        low_rsi_data.index = pd.date_range(start='2024-01-01', periods=50, freq='5T')
        
        result = await bot.generate_signal(low_rsi_data, 'BTC/USDT:USDT')
        
        if result:
            # With decreasing price trend, should generate buy signal if RSI is low enough
            calculated_rsi = bot.calculate_rsi(low_rsi_data['close'], 14)
            if calculated_rsi < 45:  # Based on bot's threshold
                assert result['side'] == 'buy', f"Expected buy signal with RSI {calculated_rsi}"
    
    @pytest.mark.unit
    async def test_error_handling_in_signal_generation(self, bot):
        """🚨 Test error handling doesn't crash the system"""
        # Test with invalid data
        invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
        
        result = await bot.generate_signal(invalid_data, 'BTC/USDT:USDT')
        assert result is None, "Should handle invalid data gracefully"
        
        # Test with None data
        result = await bot.generate_signal(None, 'BTC/USDT:USDT')
        assert result is None, "Should handle None data gracefully"
        
        # Test with empty DataFrame
        result = await bot.generate_signal(pd.DataFrame(), 'BTC/USDT:USDT')
        assert result is None, "Should handle empty DataFrame gracefully"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_minimum_confidence_threshold(self, bot, sample_ohlcv_data):
        """⚠️ Test minimum confidence threshold prevents bad trades"""
        # Modify data to create low confidence scenario
        low_confidence_data = sample_ohlcv_data.copy()
        low_confidence_data['volume'] = 100  # Very low volume
        
        result = await bot.generate_signal(low_confidence_data, 'BTC/USDT:USDT')
        
        # Should return None if confidence is below threshold
        if result is None:
            # This is expected behavior for low confidence
            assert True
        else:
            # If signal is generated, confidence must be above threshold
            assert result['confidence'] >= 40, "Signal confidence below minimum threshold"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    async def test_volume_ratio_calculation(self, bot, sample_ohlcv_data):
        """📊 Test volume ratio calculation accuracy"""
        # Known volume pattern
        test_data = sample_ohlcv_data.copy()
        test_data['volume'].iloc[-10:] = 1000  # Set last 10 to same value
        test_data['volume'].iloc[-1] = 2000    # Last one is 2x
        
        result = await bot.generate_signal(test_data, 'BTC/USDT:USDT')
        
        if result:
            expected_ratio = 2000 / 1000  # Should be 2.0
            assert abs(result['volume_ratio'] - expected_ratio) < 0.1, "Volume ratio calculation incorrect"


class TestTrendStrengthCalculation:
    """🧪 Test trend strength calculation accuracy"""
    
    @pytest.fixture
    def bot(self):
        return AlpineCompleteBot()
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_trend_strength_with_uptrend(self, bot):
        """📈 Test trend strength with clear uptrend"""
        # Create clear uptrend data
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
        df = pd.DataFrame({'close': prices})
        
        trend_strength = bot.calculate_trend_strength(df)
        
        # Should be positive for uptrend
        assert trend_strength > 0, "Trend strength should be positive for uptrend"
        assert trend_strength <= 1.0, "Trend strength should not exceed 1.0"
    
    @pytest.mark.unit
    @pytest.mark.financial_risk
    def test_trend_strength_with_downtrend(self, bot):
        """📉 Test trend strength with clear downtrend"""
        # Create clear downtrend data
        prices = pd.Series([110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100])
        df = pd.DataFrame({'close': prices})
        
        trend_strength = bot.calculate_trend_strength(df)
        
        # Should be negative for downtrend
        assert trend_strength < 0, "Trend strength should be negative for downtrend"
        assert trend_strength >= -1.0, "Trend strength should not be less than -1.0"
    
    @pytest.mark.unit
    def test_trend_strength_with_sideways_market(self, bot):
        """➡️ Test trend strength with sideways market"""
        # Create sideways market data
        prices = pd.Series([100, 101, 99, 100, 101, 99, 100, 101, 99, 100, 101])
        df = pd.DataFrame({'close': prices})
        
        trend_strength = bot.calculate_trend_strength(df)
        
        # Should be close to zero for sideways market
        assert abs(trend_strength) < 0.3, "Trend strength should be weak for sideways market"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])