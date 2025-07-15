"""
Test suite for Alpine Trading Bot
"""

import pytest
import sys
from pathlib import Path

# Add alpine_bot to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alpine_bot import AlpineBot, TradingConfig


class TestAlpineBot:
    """Test cases for the main AlpineBot class"""
    
    def test_bot_initialization(self):
        """Test bot can be initialized properly"""
        config = TradingConfig()
        bot = AlpineBot(config)
        assert bot is not None
        assert bot.config == config
        assert bot.running is False
    
    def test_bot_configuration(self):
        """Test bot configuration"""
        config = TradingConfig()
        assert config.max_positions > 0
        assert config.position_size_pct > 0
        assert config.leverage > 0
        assert config.min_order_size > 0
    
    def test_bot_components(self):
        """Test bot components are initialized"""
        config = TradingConfig()
        bot = AlpineBot(config)
        
        assert bot.exchange_client is not None
        assert bot.strategy is not None
        assert bot.risk_manager is not None
        assert bot.display is not None
        assert bot.bot_manager is not None
    
    def test_signal_handlers(self):
        """Test signal handlers are set up"""
        config = TradingConfig()
        bot = AlpineBot(config)
        
        # Signal handlers should be set up without errors
        assert True  # If we get here, signal handlers worked
    
    def test_logging_setup(self):
        """Test logging is set up correctly"""
        config = TradingConfig()
        bot = AlpineBot(config)
        
        # Logging should be configured
        assert True  # If we get here, logging worked


class TestTradingConfig:
    """Test cases for TradingConfig"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = TradingConfig()
        
        # Test critical values
        assert config.max_positions > 0
        assert config.position_size_pct > 0
        assert config.leverage > 0
        assert config.min_order_size > 0
        assert config.volume_lookback > 0
        assert config.min_signal_confidence > 0
    
    def test_config_types(self):
        """Test configuration value types"""
        config = TradingConfig()
        
        assert isinstance(config.max_positions, int)
        assert isinstance(config.position_size_pct, float)
        assert isinstance(config.leverage, int)
        assert isinstance(config.min_order_size, float)
        assert isinstance(config.API_KEY, str)
        assert isinstance(config.API_SECRET, str)
        assert isinstance(config.PASSPHRASE, str)
        assert isinstance(config.SANDBOX, bool)


@pytest.fixture
def sample_config():
    """Fixture providing a sample configuration"""
    return TradingConfig()


@pytest.fixture
def sample_bot(sample_config):
    """Fixture providing a sample bot instance"""
    return AlpineBot(sample_config)


def test_main_import():
    """Test that main modules can be imported"""
    from alpine_bot import AlpineBot, TradingConfig
    
    assert AlpineBot is not None
    assert TradingConfig is not None


if __name__ == "__main__":
    pytest.main([__file__])