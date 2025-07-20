import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Patch all external dependencies
@patch('working_alpine_bot.ccxt')
@patch('working_alpine_bot.VolumeAnomalyStrategy')
@patch('working_alpine_bot.AlpineRiskManager')
@patch('working_alpine_bot.AlpineBotManager')
@patch('working_alpine_bot.OptimizedTradeExecutor', create=True)
@patch('working_alpine_bot.TradingEngine', create=True)
class TestWorkingAlpineBot(unittest.TestCase):
    def setUp(self):
        # Patch config and exchange config
        patcher_config = patch('working_alpine_bot.TradingConfig')
        patcher_get_exchange_config = patch('working_alpine_bot.get_exchange_config', return_value={
            'apiKey': 'test', 'secret': 'test', 'password': 'test', 'sandbox': True, 'options': {}
        })
        self.addCleanup(patcher_config.stop)
        self.addCleanup(patcher_get_exchange_config.stop)
        self.mock_config = patcher_config.start()
        self.mock_get_exchange_config = patcher_get_exchange_config.start()

    def test_initialization(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        bot = WorkingAlpineBot()
        self.assertIsNotNone(bot)
        self.assertTrue(hasattr(bot, 'console'))
        self.assertTrue(hasattr(bot, 'config'))
        self.assertTrue(hasattr(bot, 'exchange_config'))
        self.assertTrue(hasattr(bot, 'strategy'))
        self.assertTrue(hasattr(bot, 'risk_manager'))
        self.assertTrue(hasattr(bot, 'bot_manager'))
        self.assertTrue(hasattr(bot, 'historical_data'))

    def test_initialize_exchange_success(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {'USDT': {'total': 100}}
        mock_ccxt.bitget.return_value = mock_exchange
        bot = WorkingAlpineBot()
        result = bot.initialize_exchange()
        self.assertTrue(result)
        self.assertEqual(bot.account_data['balance'], 100)

    def test_initialize_exchange_failure(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        mock_ccxt.bitget.side_effect = Exception('fail')
        bot = WorkingAlpineBot()
        result = bot.initialize_exchange()
        self.assertFalse(result)

    def test_load_trading_pairs(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'BTC/USDT:USDT': {'type': 'swap', 'quote': 'USDT', 'active': True, 'limits': {'leverage': {'max': 50}}, 'base': 'BTC', 'precision': {'price': 0.01}},
            'ETH/USDT:USDT': {'type': 'swap', 'quote': 'USDT', 'active': True, 'limits': {'leverage': {'max': 100}}, 'base': 'ETH', 'precision': {'price': 0.01}}
        }
        mock_exchange.fetch_tickers.return_value = {
            'BTC/USDT:USDT': {'last': 100, 'high': 110, 'low': 90, 'quoteVolume': 1000, 'percentage': 5},
            'ETH/USDT:USDT': {'last': 200, 'high': 220, 'low': 180, 'quoteVolume': 2000, 'percentage': 10}
        }
        mock_ccxt.bitget.return_value = mock_exchange
        bot = WorkingAlpineBot()
        bot.exchange = mock_exchange
        bot.load_trading_pairs()
        self.assertIn('BTC/USDT:USDT', bot.trading_pairs)
        self.assertIn('ETH/USDT:USDT', bot.trading_pairs)
        self.assertGreater(len(bot.coin_rankings), 0)

    def test_scan_for_signals(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        mock_exchange = MagicMock()
        mock_exchange.fetch_ohlcv.return_value = [[0,1,2,3,4,5]]*100
        mock_ccxt.bitget.return_value = mock_exchange
        mock_strategy.return_value.calculate_indicators.return_value = MagicMock()
        mock_strategy.return_value.detect_volume_anomaly.return_value = {'signal': 'BUY', 'confidence': 90}
        bot = WorkingAlpineBot()
        bot.exchange = mock_exchange
        bot.trading_pairs = ['BTC/USDT:USDT']
        bot.trade_executor = MagicMock()
        bot.scan_for_signals()
        self.assertGreaterEqual(len(bot.signals), 1)

    def test_update_historical_data(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        bot = WorkingAlpineBot()
        signal_data = {'symbol': 'BTC/USDT:USDT', 'type': 'BUY', 'confidence': 90, 'signal_score': 80, 'volume_spike_pct': 500}
        trade_data = {'symbol': 'BTC/USDT:USDT', 'type': 'BUY', 'result': 'win', 'pnl': 10}
        bot.update_historical_data(signal_data=signal_data, trade_data=trade_data)
        self.assertGreaterEqual(len(bot.historical_data['signal_history']), 1)
        self.assertGreaterEqual(len(bot.historical_data['trade_history']), 1)

    def test_create_display(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        bot = WorkingAlpineBot()
        # Should not raise
        display = bot.create_display()
        self.assertIsNotNone(display)

    def test_error_handling_in_scan_for_signals(self, mock_engine, mock_executor, mock_manager, mock_risk, mock_strategy, mock_ccxt):
        from working_alpine_bot import WorkingAlpineBot
        mock_exchange = MagicMock()
        mock_exchange.fetch_ohlcv.side_effect = Exception('fail')
        mock_ccxt.bitget.return_value = mock_exchange
        bot = WorkingAlpineBot()
        bot.exchange = mock_exchange
        bot.trading_pairs = ['BTC/USDT:USDT']
        bot.scan_for_signals()  # Should not raise

if __name__ == '__main__':
    unittest.main() 