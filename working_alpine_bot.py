#!/usr/bin/env python3
"""
🏔️ Working Alpine Trading Bot - Simplified Version
"""

import sys
import os
import time
import threading
import ccxt
import json
from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from config import TradingConfig, get_exchange_config, TRADING_PAIRS
from strategy import VolumeAnomalyStrategy
from risk_manager import AlpineRiskManager
from bot_manager import AlpineBotManager

# Import trading execution components
try:
    from src.trading.trade_executor import OptimizedTradeExecutor
    from src.trading.trading_engine import TradingEngine
    TRADING_ENABLED = True
except ImportError:
    TRADING_ENABLED = False
    print("⚠️ Trading execution disabled - components not found")

class WorkingAlpineBot:
    """Working Alpine Trading Bot with Real Signal Generation"""
    
    def __init__(self):
        self.console = Console(width=140, legacy_windows=False)
        self.config = TradingConfig()
        self.exchange_config = get_exchange_config()
        self.strategy = VolumeAnomalyStrategy()
        self.risk_manager = AlpineRiskManager()
        self.bot_manager = AlpineBotManager()
        
        self.running = False
        self.exchange = None
        self.account_data = {'balance': 0.0, 'equity': 0.0, 'free_margin': 0.0}
        self.positions = []
        self.signals = []
        self.logs = []
        self.market_data = {}
        self.trading_pairs = []  # Will be populated dynamically
        self.coin_rankings = []  # Ranked by volatility and tick size
        
        # Historical data tracking
        self.historical_data = {
            'balance_history': [],
            'signal_history': [],
            'trade_history': [],
            'performance_metrics': {},
            'hourly_stats': defaultdict(list),
            'daily_stats': defaultdict(list),
            'symbol_performance': defaultdict(list)
        }
        
        # Trading execution components
        self.trade_executor = None
        self.trading_engine = None
        self.auto_trade_enabled = True  # Enable automatic trading
        
        # Clean up existing processes
        self.bot_manager.kill_alpine_processes(exclude_current=True)
        
        # Initialize exchange and get trading pairs
        self.initialize_exchange()
        self.load_trading_pairs()
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical backtest and performance data"""
        try:
            # Load backtest results
            backtest_files = [
                '/workspaces/volume-anom/data/results/full_backtest_summary.json',
                '/workspaces/volume-anom/data/results/day_75pairs_100usdt_summary.json',
                '/workspaces/volume-anom/data/results/volume_anomaly_backtest_results.json'
            ]
            
            for file_path in backtest_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                        # Store performance metrics
                        filename = os.path.basename(file_path)
                        self.historical_data['performance_metrics'][filename] = {
                            'total_pnl': data.get('total_pnl', 0),
                            'total_trades': data.get('total_trades', 0),
                            'win_rate': data.get('win_rate', 0),
                            'timeframe_performance': data.get('timeframe_performance', {}),
                            'sample_trades': data.get('sample_trades', [])[:10]  # Keep last 10 trades
                        }
            
            # Initialize balance tracking
            self.historical_data['balance_history'].append({
                'timestamp': datetime.now(),
                'balance': self.account_data.get('balance', 0)
            })
            
            self.log("📊 Historical data loaded successfully")
            
        except Exception as e:
            self.log(f"⚠️ Error loading historical data: {e}")
    
    def update_historical_data(self, signal_data=None, trade_data=None):
        """Update historical tracking data"""
        try:
            current_time = datetime.now()
            
            # Update balance history
            current_balance = self.account_data.get('balance', 0)
            if not self.historical_data['balance_history'] or \
               current_balance != self.historical_data['balance_history'][-1]['balance']:
                self.historical_data['balance_history'].append({
                    'timestamp': current_time,
                    'balance': current_balance
                })
                
                # Keep only last 100 balance records
                if len(self.historical_data['balance_history']) > 100:
                    self.historical_data['balance_history'] = self.historical_data['balance_history'][-100:]
            
            # Update signal history
            if signal_data:
                signal_record = {
                    'timestamp': current_time,
                    'symbol': signal_data.get('symbol', ''),
                    'type': signal_data.get('type', ''),
                    'confidence': signal_data.get('confidence', 0),
                    'score': signal_data.get('signal_score', 0),
                    'volume_spike': signal_data.get('volume_spike_pct', 0),
                    'executed': signal_data.get('confidence', 0) >= 80 and signal_data.get('signal_score', 0) >= 60
                }
                self.historical_data['signal_history'].append(signal_record)
                
                # Keep only last 50 signals
                if len(self.historical_data['signal_history']) > 50:
                    self.historical_data['signal_history'] = self.historical_data['signal_history'][-50:]
                
                # Update hourly stats
                hour_key = current_time.strftime('%Y-%m-%d %H:00')
                self.historical_data['hourly_stats'][hour_key].append(signal_record)
                
                # Update symbol performance
                symbol = signal_data.get('base', signal_data.get('symbol', '').replace('/USDT:USDT', ''))
                self.historical_data['symbol_performance'][symbol].append(signal_record)
            
            # Update trade history
            if trade_data:
                trade_record = {
                    'timestamp': current_time,
                    'symbol': trade_data.get('symbol', ''),
                    'type': trade_data.get('type', ''),
                    'result': trade_data.get('result', 'pending'),
                    'pnl': trade_data.get('pnl', 0)
                }
                self.historical_data['trade_history'].append(trade_record)
                
                # Keep only last 30 trades
                if len(self.historical_data['trade_history']) > 30:
                    self.historical_data['trade_history'] = self.historical_data['trade_history'][-30:]
                    
        except Exception as e:
            self.log(f"⚠️ Error updating historical data: {e}")
    
    def get_performance_summary(self):
        """Get current session performance summary"""
        try:
            current_time = datetime.now()
            
            # Calculate session stats
            session_start = current_time - timedelta(hours=1)  # Last hour
            recent_signals = [s for s in self.historical_data['signal_history'] 
                            if s['timestamp'] >= session_start]
            
            # Performance metrics
            total_signals = len(recent_signals)
            premium_signals = len([s for s in recent_signals if s['executed']])
            avg_confidence = sum(s['confidence'] for s in recent_signals) / max(total_signals, 1)
            avg_score = sum(s['score'] for s in recent_signals) / max(total_signals, 1)
            
            # Balance change
            balance_change = 0
            if len(self.historical_data['balance_history']) >= 2:
                balance_change = (self.historical_data['balance_history'][-1]['balance'] - 
                                self.historical_data['balance_history'][0]['balance'])
            
            # Top performing symbols
            symbol_stats = {}
            for symbol, signals in self.historical_data['symbol_performance'].items():
                recent_symbol_signals = [s for s in signals if s['timestamp'] >= session_start]
                if recent_symbol_signals:
                    symbol_stats[symbol] = {
                        'count': len(recent_symbol_signals),
                        'avg_confidence': sum(s['confidence'] for s in recent_symbol_signals) / len(recent_symbol_signals),
                        'avg_score': sum(s['score'] for s in recent_symbol_signals) / len(recent_symbol_signals),
                        'premium_count': len([s for s in recent_symbol_signals if s['executed']])
                    }
            
            # Sort by premium signal count
            top_symbols = sorted(symbol_stats.items(), 
                               key=lambda x: x[1]['premium_count'], 
                               reverse=True)[:5]
            
            return {
                'session_duration': '1 hour',
                'total_signals': total_signals,
                'premium_signals': premium_signals,
                'avg_confidence': avg_confidence,
                'avg_score': avg_score,
                'balance_change': balance_change,
                'top_symbols': top_symbols,
                'execution_rate': (premium_signals / max(total_signals, 1)) * 100
            }
            
        except Exception as e:
            self.log(f"⚠️ Error calculating performance: {e}")
            return {}
    
    def __init__(self):
        self.console = Console(width=140, legacy_windows=False)
        self.config = TradingConfig()
        self.exchange_config = get_exchange_config()
        self.strategy = VolumeAnomalyStrategy()
        self.risk_manager = AlpineRiskManager()
        self.bot_manager = AlpineBotManager()
        
        self.running = False
        self.exchange = None
        self.account_data = {'balance': 0.0, 'equity': 0.0, 'free_margin': 0.0}
        self.positions = []
        self.signals = []
        self.logs = []
        self.market_data = {}
        self.trading_pairs = []  # Will be populated dynamically
        self.coin_rankings = []  # Ranked by volatility and tick size
        
        # Historical data tracking
        self.historical_data = {
            'balance_history': [],
            'signal_history': [],
            'trade_history': [],
            'performance_metrics': {},
            'hourly_stats': defaultdict(list),
            'daily_stats': defaultdict(list),
            'symbol_performance': defaultdict(list)
        }
        
        # Trading execution components
        self.trade_executor = None
        self.trading_engine = None
        self.auto_trade_enabled = True  # Enable automatic trading
        
        # Clean up existing processes
        self.bot_manager.kill_alpine_processes(exclude_current=True)
        
        # Initialize exchange and get trading pairs
        self.initialize_exchange()
        self.load_trading_pairs()
        self.load_historical_data()
    
    def initialize_exchange(self):
        """Initialize Bitget exchange connection"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': self.exchange_config['apiKey'],
                'secret': self.exchange_config['secret'], 
                'password': self.exchange_config['password'],
                'sandbox': self.exchange_config.get('sandbox', False),
                'enableRateLimit': True,
                'options': self.exchange_config.get('options', {})
            })
            
            # Test connection
            balance = self.exchange.fetch_balance({'type': 'swap'})
            usdt_info = balance.get('USDT', {})
            total_balance = float(usdt_info.get('total', 0) or 0)
            
            self.log(f"✅ Connected to Bitget - Ready to trade with ${total_balance:.2f}!")
            self.account_data['balance'] = total_balance
            
            # Initialize trading components
            if TRADING_ENABLED:
                try:
                    self.trade_executor = OptimizedTradeExecutor(self.exchange)
                    self.trading_engine = TradingEngine()  # No parameters needed
                    self.log("🚀 Trading execution system initialized - AUTO-TRADING ENABLED!")
                except Exception as e:
                    self.log(f"⚠️ Trading execution failed to initialize: {e}")
                    self.trade_executor = None
                    self.trading_engine = None
            else:
                self.log("⚠️ Trading execution disabled - display mode only")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exchange connection failed: {str(e)}")
            return False
    
    def log(self, message: str):
        """Add log message with timestamp"""
        log_entry = {
            'timestamp': datetime.now(),
            'message': message,
            'level': 'INFO'
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]
        
        # Also print to console for debugging
        time_str = log_entry['timestamp'].strftime("%H:%M:%S")
        print(f"[{time_str}] {message}")
    
    def load_trading_pairs(self):
        """Load and rank trading pairs by leverage, volatility, and tick size"""
        try:
            if not self.exchange:
                self.log("❌ Exchange not initialized")
                return
            
            self.log("🔍 Discovering high-leverage trading opportunities...")
            
            # Get all markets
            markets = self.exchange.load_markets()
            
            # Filter for USDT perpetual futures with high leverage
            suitable_pairs = []
            
            for symbol, market in markets.items():
                try:
                    # Must be USDT perpetual futures
                    if (market.get('type') == 'swap' and 
                        market.get('quote') == 'USDT' and
                        market.get('active', False) and
                        '/USDT:USDT' in symbol):
                        
                        # Check leverage - must support 50x or higher
                        max_leverage = market.get('limits', {}).get('leverage', {}).get('max', 1)
                        if max_leverage >= 50:
                            
                            # Get additional market info
                            base_currency = market.get('base', '')
                            tick_size = market.get('precision', {}).get('price', 0.0001)
                            min_notional = market.get('limits', {}).get('cost', {}).get('min', 0)
                            
                            suitable_pairs.append({
                                'symbol': symbol,
                                'base': base_currency,
                                'max_leverage': max_leverage,
                                'tick_size': tick_size,
                                'min_notional': min_notional,
                                'market_info': market
                            })
                            
                except Exception as e:
                    continue
            
            self.log(f"📊 Found {len(suitable_pairs)} exciting pairs with 50x+ leverage")
            
            # Get 24h tickers for volatility ranking
            self.log("📈 Analyzing market volatility patterns...")
            
            try:
                tickers = self.exchange.fetch_tickers()
                
                # Add volatility data to pairs
                for pair in suitable_pairs:
                    symbol = pair['symbol']
                    if symbol in tickers:
                        ticker = tickers[symbol]
                        
                        # Calculate volatility metrics
                        price = ticker.get('last', 0)
                        high_24h = ticker.get('high', 0)
                        low_24h = ticker.get('low', 0)
                        volume_24h = ticker.get('quoteVolume', 0)
                        change_24h = ticker.get('percentage', 0)
                        
                        # Calculate volatility score
                        price_range = (high_24h - low_24h) / price if price > 0 else 0
                        volatility_score = abs(change_24h) + (price_range * 100)
                        
                        pair.update({
                            'price': price,
                            'volume_24h': volume_24h,
                            'volatility_score': volatility_score,
                            'price_change_24h': change_24h,
                            'price_range_24h': price_range
                        })
                    else:
                        pair.update({
                            'price': 0,
                            'volume_24h': 0,
                            'volatility_score': 0,
                            'price_change_24h': 0,
                            'price_range_24h': 0
                        })
                
                # Sort by volatility score (highest first) and volume
                suitable_pairs.sort(key=lambda x: (x['volatility_score'], x['volume_24h']), reverse=True)
                
                # Take top 250 pairs
                self.coin_rankings = suitable_pairs[:250]
                self.trading_pairs = [pair['symbol'] for pair in self.coin_rankings]
                
                self.log(f"🎯 Selected top {len(self.trading_pairs)} most promising opportunities")
                
                # Log top 10 for reference
                self.log("🏆 Top 10 most dynamic pairs:")
                for i, pair in enumerate(self.coin_rankings[:10]):
                    self.log(f"  {i+1}. {pair['base']} - {pair['volatility_score']:.2f}% volatility - {pair['max_leverage']}x leverage")
                
            except Exception as e:
                self.log(f"❌ Error fetching tickers: {e}")
                # Fallback to basic list
                self.trading_pairs = [pair['symbol'] for pair in suitable_pairs[:250]]
                self.coin_rankings = suitable_pairs[:250]
                
        except Exception as e:
            self.log(f"❌ Error loading trading pairs: {e}")
            # Fallback to basic pairs
            self.trading_pairs = [
                'BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT',
                'SOL/USDT:USDT', 'ADA/USDT:USDT', 'XRP/USDT:USDT',
                'DOGE/USDT:USDT', 'MATIC/USDT:USDT', 'AVAX/USDT:USDT',
                'DOT/USDT:USDT'
            ]
    
    def log(self, message):
        """Add log message with timestamp"""
        log_entry = {
            'timestamp': datetime.now(),
            'message': message,
            'level': 'INFO'
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]
        
        # Also print to console for debugging
        time_str = log_entry['timestamp'].strftime("%H:%M:%S")
        print(f"[{time_str}] {message}")
    
    def update_account_data(self):
        """Update account data"""
        try:
            if self.exchange:
                balance = self.exchange.fetch_balance({'type': 'swap'})
                usdt_info = balance.get('USDT', {})
                
                self.account_data.update({
                    'balance': float(usdt_info.get('total', 0) or 0),
                    'equity': float(usdt_info.get('total', 0) or 0),
                    'free_margin': float(usdt_info.get('free', 0) or 0)
                })
                
                # Update historical balance tracking
                self.update_historical_data()
                
        except Exception as e:
            self.log(f"❌ Error updating account: {str(e)}")
    
    def scan_for_signals(self):
        """Scan trading pairs for volume anomaly signals"""
        try:
            signal_count = 0
            
            # Scan top 50 pairs each cycle (rotate through all 250)
            pairs_to_scan = self.trading_pairs[:50] if self.trading_pairs else ['BTC/USDT:USDT', 'ETH/USDT:USDT']
            
            for pair in pairs_to_scan:
                try:
                    # Get market data (3m timeframe only)
                    ohlcv = self.exchange.fetch_ohlcv(pair, '3m', limit=100)
                    
                    if len(ohlcv) < 20:
                        continue
                    
                    # Convert to DataFrame
                    import pandas as pd
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Calculate indicators first
                    df = self.strategy.calculate_indicators(df)
                    
                    # Get current price and volume info
                    current_price = df['close'].iloc[-1]
                    current_volume = df['volume'].iloc[-1]
                    avg_volume = df['volume'].tail(20).mean()
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                    
                    # Calculate volume change statistics with enhanced scalping detection
                    volume_change_24h = ((current_volume - df['volume'].iloc[-2]) / df['volume'].iloc[-2] * 100) if len(df) > 1 and df['volume'].iloc[-2] > 0 else 0
                    volume_spike = max(df['volume'].tail(5)) / avg_volume if avg_volume > 0 else 0
                    
                    # Enhanced volume spike percentage for scalping (400%+ target)
                    volume_spike_pct = ((current_volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
                    
                    # Get technical indicators for scoring
                    # SuperTrend signals (REPLACED RSI)
                    supertrend_direction = df['supertrend_direction'].iloc[-1] if 'supertrend_direction' in df.columns else 1
                    supertrend_strength = df['supertrend_strength'].iloc[-1] if 'supertrend_strength' in df.columns else 0
                    supertrend_quality = df['supertrend_quality'].iloc[-1] if 'supertrend_quality' in df.columns else 'WEAK'
                    
                    bb_position = ((current_price - df['bb_lower'].iloc[-1]) / (df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1])) if 'bb_upper' in df.columns and 'bb_lower' in df.columns else 0.5
                    macd_signal = df['macd'].iloc[-1] - df['macd_signal'].iloc[-1] if 'macd' in df.columns and 'macd_signal' in df.columns else 0
                    
                    # SuperTrend calculation for trend direction
                    supertrend_upper = df['supertrend_upper'].iloc[-1] if 'supertrend_upper' in df.columns else current_price * 1.02
                    supertrend_lower = df['supertrend_lower'].iloc[-1] if 'supertrend_lower' in df.columns else current_price * 0.98
                    
                    # Determine SuperTrend signal
                    if current_price > supertrend_upper:
                        supertrend_signal = 'bullish'
                    elif current_price < supertrend_lower:
                        supertrend_signal = 'bearish'
                    else:
                        supertrend_signal = 'neutral'
                    
                    # Calculate SuperTrend strength (how far price is from bands)
                    supertrend_strength = 0
                    if supertrend_signal == 'bullish':
                        supertrend_strength = ((current_price - supertrend_upper) / supertrend_upper * 100)
                    elif supertrend_signal == 'bearish':
                        supertrend_strength = ((supertrend_lower - current_price) / supertrend_lower * 100)
                    else:
                        # Neutral - check distance from nearest band
                        upper_distance = abs(current_price - supertrend_upper) / supertrend_upper * 100
                        lower_distance = abs(current_price - supertrend_lower) / supertrend_lower * 100
                        supertrend_strength = min(upper_distance, lower_distance)
                    
                    # Calculate price change
                    price_change_pct = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) > 1 else 0
                    
                    # Enhanced signal score for scalping (0-100) - MORE GENEROUS SCORING
                    signal_score = 0
                    
                    # Volume spike scoring (50% weight) - Enhanced for scalping
                    if volume_spike_pct >= 800:
                        signal_score += 50  # Extreme spike
                    elif volume_spike_pct >= 600:
                        signal_score += 45  # Massive spike
                    elif volume_spike_pct >= 400:
                        signal_score += 40  # Huge spike
                    elif volume_spike_pct >= 300:
                        signal_score += 35  # High spike (scalping threshold)
                    elif volume_spike_pct >= 200:
                        signal_score += 30  # Good spike
                    elif volume_spike_pct >= 100:
                        signal_score += 25  # Moderate spike
                    elif volume_spike_pct >= 50:
                        signal_score += 20  # Small spike
                    else:
                        signal_score += 15  # Base score
                    
                    # SuperTrend momentum for scalping (25% weight) - ENHANCED TREND FOLLOWING
                    if supertrend_direction == 1:  # Bullish trend
                        if supertrend_strength >= 2.0:  # Strong bullish trend
                            signal_score += 25
                        elif supertrend_strength >= 1.0:  # Good bullish trend
                            signal_score += 22
                        elif supertrend_strength >= 0.5:  # Moderate bullish trend
                            signal_score += 20
                        else:  # Weak bullish trend
                            signal_score += 18
                    elif supertrend_direction == -1:  # Bearish trend
                        if supertrend_strength >= 2.0:  # Strong bearish trend
                            signal_score += 25
                        elif supertrend_strength >= 1.0:  # Good bearish trend
                            signal_score += 22
                        elif supertrend_strength >= 0.5:  # Moderate bearish trend
                            signal_score += 20
                        else:  # Weak bearish trend
                            signal_score += 18
                    else:  # Neutral - consolidation
                        if supertrend_strength <= 0.5:  # Tight consolidation (good for breakout)
                            signal_score += 15
                        else:  # Wide consolidation
                            signal_score += 10
                    
                    # Price momentum for scalping (25% weight) - MORE GENEROUS
                    if abs(price_change_pct) >= 3:
                        signal_score += 25  # Strong momentum
                    elif abs(price_change_pct) >= 2:
                        signal_score += 20  # Good momentum
                    elif abs(price_change_pct) >= 1:
                        signal_score += 15  # Moderate momentum
                    else:
                        signal_score += 10  # Base momentum score
                    
                    # MACD confirmation (10% weight)
                    if abs(macd_signal) > 0.001:
                        signal_score += 10
                    elif abs(macd_signal) > 0.0005:
                        signal_score += 5
                    
                    # Get leverage info for this pair
                    leverage_info = next((p for p in self.coin_rankings if p['symbol'] == pair), {})
                    max_leverage = leverage_info.get('max_leverage', 1)
                    volatility_score = leverage_info.get('volatility_score', 0)
                    
                    # Store market data with SuperTrend instead of RSI
                    self.market_data[pair] = {
                        'price': current_price,
                        'volume': current_volume,
                        'volume_ratio': volume_ratio,
                        'volume_change_24h': volume_change_24h,
                        'volume_spike': volume_spike,
                        'volume_spike_pct': volume_spike_pct,  # New: Volume spike percentage
                        'price_change_pct': price_change_pct,
                        'supertrend_direction': supertrend_direction,  # REPLACED RSI
                        'supertrend_strength': supertrend_strength,  # REPLACED RSI
                        'supertrend_quality': supertrend_quality,  # REPLACED RSI
                        'supertrend_upper': supertrend_upper,
                        'supertrend_lower': supertrend_lower,
                        'bb_position': bb_position,
                        'macd_signal': macd_signal,
                        'signal_score': signal_score,
                        'max_leverage': max_leverage,
                        'volatility_score': volatility_score,
                        'is_scalp_ready': volume_spike_pct >= 400 and signal_score >= 60  # Scalping flag
                    }
                    
                    # Generate signal using strategy
                    signal = self.strategy.detect_volume_anomaly(df, max_leverage)
                    
                    if signal and signal.get('signal') and signal.get('confidence', 0) >= self.config.min_signal_confidence:
                        signal_count += 1
                        signal_type = signal.get('signal', 'UNKNOWN')
                        
                        # Enhanced logging with scalping volume spike info
                        base_symbol = pair.replace('/USDT:USDT', '')
                        scalp_indicator = " 🎯 SCALP READY!" if volume_spike_pct >= 400 else ""
                        self.log(f"🎯 Great opportunity found! {base_symbol} - {signal_type} ({signal['confidence']:.1f}%) | Score: {signal_score:.0f} | {max_leverage}x leverage | Vol: {volume_spike_pct:.0f}%{scalp_indicator}")
                        
                        # **EXECUTE TRADE ONLY IF MEETS STRICT CRITERIA: 80%+ CONFIDENCE AND 60+ SCORE**
                        if (self.auto_trade_enabled and self.trade_executor and 
                            signal.get('confidence', 0) >= 80 and signal_score >= 60):
                            try:
                                # Prepare trading signal
                                trading_signal = {
                                    'symbol': pair,
                                    'type': signal_type,  # BUY/SELL
                                    'action': signal_type,  # BUY/SELL
                                    'confidence': signal['confidence'],
                                    'price': current_price,
                                    'volume_spike_pct': volume_spike_pct,
                                    'signal_score': signal_score,
                                    'max_leverage': max_leverage,
                                    'timestamp': datetime.now()
                                }
                                
                                # Execute the trade
                                self.log(f"🔥 EXECUTING TRADE: {base_symbol} {signal_type} - Confidence: {signal['confidence']:.1f}% | Score: {signal_score:.0f} | PREMIUM SIGNAL!")
                                order_result = self.trade_executor.execute_signal(trading_signal)
                                
                                if order_result:
                                    self.log(f"✅ TRADE EXECUTED: {base_symbol} {signal_type} - Order ID: {order_result.get('id', 'N/A')}")
                                else:
                                    self.log(f"❌ TRADE FAILED: {base_symbol} {signal_type} - Execution error")
                                    
                            except Exception as trade_error:
                                self.log(f"❌ TRADE ERROR: {base_symbol} - {str(trade_error)}")
                        else:
                            # Log why trade was skipped
                            reasons = []
                            if not self.auto_trade_enabled:
                                reasons.append("Auto-trade disabled")
                            if not self.trade_executor:
                                reasons.append("Trade executor not initialized")
                            if signal.get('confidence', 0) < 80:
                                reasons.append(f"Confidence too low ({signal.get('confidence', 0):.1f}% < 80%)")
                            if signal_score < 60:
                                reasons.append(f"Score too low ({signal_score:.0f} < 60)")
                            
                            self.log(f"⚠️ TRADE SKIPPED: {base_symbol} {signal_type} - {' | '.join(reasons)}")
                        
                        # Prepare signal data for historical tracking
                        signal_data = {
                            'symbol': pair,
                            'base': base_symbol,
                            'type': signal_type,
                            'confidence': signal['confidence'],
                            'price': current_price,
                            'volume_ratio': volume_ratio,
                            'volume_change_24h': volume_change_24h,
                            'volume_spike_pct': volume_spike_pct,  # New: Volume spike percentage
                            'signal_score': signal_score,
                            'max_leverage': max_leverage,
                            'volatility_score': volatility_score,
                            'is_scalp_ready': volume_spike_pct >= 400 and signal_score >= 60,  # Scalping flag
                            'timestamp': datetime.now()
                        }
                        
                        # Add to signals list with scalping info
                        self.signals.append(signal_data)
                        
                        # Update historical data tracking
                        self.update_historical_data(signal_data=signal_data)
                        
                        # Keep only last 20 signals
                        if len(self.signals) > 20:
                            self.signals = self.signals[-20:]
                    
                except Exception as e:
                    self.log(f"⚠️ Error scanning {pair}: {str(e)}")
                    continue
            
            if signal_count == 0:
                self.log(f"📊 Analyzed {len(pairs_to_scan)} markets - Still searching for the perfect setup...")
            else:
                self.log(f"🎯 Amazing! Found {signal_count} promising signals from {len(pairs_to_scan)} markets")
                    
        except Exception as e:
            self.log(f"❌ Signal scan error: {str(e)}")
    
    def trading_loop(self):
        """Background trading loop"""
        scan_counter = 0
        
        while self.running:
            try:
                # Update account data every 5 scans
                if scan_counter % 5 == 0:
                    self.update_account_data()
                
                # Scan for signals
                self.scan_for_signals()
                
                scan_counter += 1
                time.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                self.log(f"❌ Trading loop error: {str(e)}")
                time.sleep(10)
    
    def create_display(self):
        """Create the display layout"""
        # Header
        header = Panel(
            Text("🏔️  ALPINE TRADING BOT - Your Smart Trading Companion", style="bold bright_cyan", justify="center"),
            style="bold bright_blue"
        )
        
        # Account info
        account_table = Table(show_header=False, expand=True)
        account_table.add_column("Label", style="bold")
        account_table.add_column("Value", justify="right")
        
        account_table.add_row("💰 Available Balance:", f"${self.account_data['balance']:.2f}")
        account_table.add_row("🆓 Trading Margin:", f"${self.account_data['free_margin']:.2f}")
        account_table.add_row("🎯 Signals Found:", f"{len(self.signals)}")
        account_table.add_row("📊 Markets Tracked:", f"{len(self.market_data)} pairs")
        account_table.add_row("🏔️ Total Opportunities:", f"{len(self.coin_rankings)}")
        account_table.add_row("📈 High-Leverage Coins:", f"{len([c for c in self.coin_rankings if c.get('max_leverage', 0) >= 50])}")
        
        # Add trading status
        if TRADING_ENABLED and self.trade_executor:
            if self.auto_trade_enabled:
                account_table.add_row("🚀 Auto-Trading:", "[bold green]ENABLED[/bold green]")
                account_table.add_row("🎯 Trade Criteria:", "[bold yellow]80%+ Confidence & 60+ Score[/bold yellow]")
            else:
                account_table.add_row("🚀 Auto-Trading:", "[bold red]DISABLED[/bold red]")
        else:
            account_table.add_row("🚀 Auto-Trading:", "[bold yellow]NOT AVAILABLE[/bold yellow]")
        
        account_panel = Panel(account_table, title="💼 Account Overview", border_style="bright_blue")
        
        # Recent signals
        signal_table = Table(show_header=True, expand=True)
        signal_table.add_column("Time", style="bright_black", width=8)
        signal_table.add_column("Symbol", style="bold bright_cyan", width=7)
        signal_table.add_column("Signal", style="bright_green", width=6)
        signal_table.add_column("Conf%", style="bright_yellow", width=6)
        signal_table.add_column("Score", style="bright_green", width=5)
        signal_table.add_column("Vol%", style="bright_magenta", width=7)
        signal_table.add_column("Lev", style="bright_red", width=5)
        
        recent_signals = self.signals[-8:] if self.signals else []
        for signal in recent_signals:
            time_str = signal['timestamp'].strftime("%H:%M:%S")
            confidence_str = f"{signal['confidence']:.0f}%"
            symbol = signal.get('base', signal['symbol'].replace('/USDT:USDT', ''))
            score_str = f"{signal.get('signal_score', 0):.0f}"
            
            # Enhanced volume spike display for scalping
            vol_spike_pct = signal.get('volume_spike_pct', 0)
            if vol_spike_pct >= 1000:
                vol_change_str = f"🔥{vol_spike_pct:+.0f}%"
            elif vol_spike_pct >= 700:
                vol_change_str = f"🚀{vol_spike_pct:+.0f}%"
            elif vol_spike_pct >= 500:
                vol_change_str = f"💥{vol_spike_pct:+.0f}%"
            elif vol_spike_pct >= 400:
                vol_change_str = f"⚡{vol_spike_pct:+.0f}%"
            else:
                vol_change_str = f"{vol_spike_pct:+.0f}%"
            
            leverage_str = f"{signal.get('max_leverage', 1):.0f}x"
            
            # Color coding for score
            score_val = signal.get('signal_score', 0)
            confidence_val = signal.get('confidence', 0)
            
            # Mark premium signals that meet trading criteria
            if confidence_val >= 80 and score_val >= 60:
                score_display = f"[bold bright_green]⭐{score_str}[/bold bright_green]"
            elif score_val >= 70:
                score_display = f"[bold bright_green]{score_str}[/bold bright_green]"
            elif score_val >= 50:
                score_display = f"[bold bright_yellow]{score_str}[/bold bright_yellow]"
            else:
                score_display = f"[bright_black]{score_str}[/bright_black]"
            
            signal_table.add_row(time_str, symbol, signal['type'], confidence_str, score_display, vol_change_str, leverage_str)
        
        if not recent_signals:
            signal_table.add_row("--", "🔍 Searching for opportunities...", "--", "--", "--", "--", "--")
        
        signal_panel = Panel(signal_table, title="🎯 Recent Trading Signals", border_style="bright_green")
        
        # Market data
        market_table = Table(show_header=True, expand=True)
        market_table.add_column("Symbol", style="bold bright_white", width=7)
        market_table.add_column("Price", style="bright_white", width=9)
        market_table.add_column("Vol%", style="bright_yellow", width=7)
        market_table.add_column("Spike", style="bright_magenta", width=6)
        market_table.add_column("SuperTrend", style="bright_cyan", width=8)
        market_table.add_column("Score", style="bright_green", width=5)
        market_table.add_column("Lev", style="bright_red", width=5)
        
        # Sort by signal score
        sorted_pairs = sorted(self.market_data.items(), 
                            key=lambda x: x[1].get('signal_score', 0), 
                            reverse=True)
        
        for pair, data in sorted_pairs[:10]:  # Show top 10 pairs by signal score
            symbol = pair.replace('/USDT:USDT', '')
            price = f"${data['price']:.4f}"
            
            # Enhanced volume spike display for scalping
            vol_spike_pct = data.get('volume_spike_pct', 0)
            vol_spike = f"{data.get('volume_spike', 0):.1f}x"
            
            # Format volume change with scalping indicators
            if vol_spike_pct >= 1000:
                vol_change = f"🔥{vol_spike_pct:+.0f}%"
                vol_style = "bold bright_red"
            elif vol_spike_pct >= 700:
                vol_change = f"🚀{vol_spike_pct:+.0f}%"
                vol_style = "bold bright_magenta"
            elif vol_spike_pct >= 500:
                vol_change = f"💥{vol_spike_pct:+.0f}%"
                vol_style = "bold bright_yellow"
            elif vol_spike_pct >= 400:
                vol_change = f"⚡{vol_spike_pct:+.0f}%"
                vol_style = "bold bright_green"
            elif vol_spike_pct >= 200:
                vol_change = f"{vol_spike_pct:+.0f}%"
                vol_style = "bright_cyan"
            elif vol_spike_pct >= 100:
                vol_change = f"{vol_spike_pct:+.0f}%"
                vol_style = "bright_white"
            else:
                vol_change = f"{vol_spike_pct:+.0f}%"
                vol_style = "bright_black"
            
            # Format SuperTrend signal
            supertrend_signal = data.get('supertrend_signal', 'neutral')
            supertrend_strength = data.get('supertrend_strength', 0)
            
            if supertrend_signal == 'bullish':
                supertrend_display = f"🟢{supertrend_strength:.1f}%"
            elif supertrend_signal == 'bearish':
                supertrend_display = f"🔴{supertrend_strength:.1f}%"
            else:
                supertrend_display = f"🟡{supertrend_strength:.1f}%"
            signal_score = f"{data.get('signal_score', 0):.0f}"
            leverage = f"{data.get('max_leverage', 1):.0f}x"
            
            # Color coding for signal score
            score_val = data.get('signal_score', 0)
            
            # Mark premium signals that would trigger trades
            if score_val >= 70:
                score_style = "bold bright_green"
            elif score_val >= 60:
                score_style = "bold bright_yellow"
            elif score_val >= 30:
                score_style = "bold bright_magenta"
            else:
                score_style = "bright_black"
            
            # Add star for premium signals (this would need confidence check from actual signal)
            if score_val >= 60:
                signal_score_display = f"⭐{signal_score}"
            else:
                signal_score_display = signal_score
            
            market_table.add_row(
                symbol, price, 
                f"[{vol_style}]{vol_change}[/{vol_style}]", 
                vol_spike, supertrend_display, 
                f"[{score_style}]{signal_score_display}[/{score_style}]", leverage
            )
        
        if not self.market_data:
            market_table.add_row("🔍 Scanning", "markets...", "--", "--", "--", "--", "--")
        
        market_panel = Panel(market_table, title="📊 Market Opportunities", border_style="bright_magenta")
        
        # Detailed statistics table
        stats_table = Table(show_header=True, expand=True)
        stats_table.add_column("Symbol", style="bold bright_white", width=7)
        stats_table.add_column("BB", style="bright_cyan", width=6)
        stats_table.add_column("MACD", style="bright_blue", width=8)
        stats_table.add_column("Price", style="bright_white", width=7)
        stats_table.add_column("Vol", style="bright_yellow", width=6)
        
        # Show top 5 pairs with detailed stats
        for pair, data in sorted_pairs[:5]:
            symbol = pair.replace('/USDT:USDT', '')
            bb_pos = f"{data.get('bb_position', 0.5):.2f}"
            macd = f"{data.get('macd_signal', 0):.4f}"
            price_change = f"{data.get('price_change_pct', 0):+.2f}%"
            vol_ratio = f"{data.get('volume_ratio', 0):.2f}x"
            
            # Color coding for BB position
            bb_val = data.get('bb_position', 0.5)
            if bb_val < 0.2 or bb_val > 0.8:
                bb_style = "bold bright_red"
            elif bb_val < 0.3 or bb_val > 0.7:
                bb_style = "bright_yellow"
            else:
                bb_style = "bright_black"
            
            stats_table.add_row(
                symbol, 
                f"[{bb_style}]{bb_pos}[/{bb_style}]", 
                macd, 
                price_change, 
                vol_ratio
            )
        
        if not self.market_data:
            stats_table.add_row("🔍 Analyzing", "tech", "indicators", "--", "--")
        
        stats_panel = Panel(stats_table, title="📈 Technical Analysis", border_style="bright_blue")
        
        # Recent logs
        log_text = Text()
        recent_logs = self.logs[-6:] if self.logs else []
        for log in recent_logs:
            time_str = log['timestamp'].strftime("%H:%M:%S")
            log_text.append(f"[{time_str}] {log['message']}\n", style="bright_cyan")
        
        if not recent_logs:
            log_text.append("🚀 Getting ready to find amazing opportunities...\n", style="bright_black")
        
        log_panel = Panel(log_text, title="🔔 Activity Updates", border_style="bright_yellow")
        
        # Status
        status_text = Text()
        status_text.append(f"Status: {'🟢 Active & Ready' if self.running else '🔴 Offline'}\n", style="bright_green" if self.running else "bright_red")
        status_text.append(f"Exchange: Bitget Futures\n", style="bright_blue")
        status_text.append(f"Strategy: Volume Anomaly\n", style="bright_blue")
        status_text.append(f"Timeframe: 3m (Fixed)\n", style="bright_yellow")
        status_text.append(f"Time: {datetime.now().strftime('%H:%M:%S')}", style="bright_black")
        
        status_panel = Panel(status_text, title="🔧 System Status", border_style="bright_blue")
        
        # Combine everything with balanced responsive design
        from rich.columns import Columns
        from rich.console import Group
        
        # Create balanced columns with proper spacing
        top_row = Columns([account_panel, status_panel], equal=True, expand=True)
        middle_row = Columns([signal_panel, market_panel], equal=True, expand=True)
        bottom_row = Columns([stats_panel, log_panel], equal=True, expand=True)
        
        # Add historical data section
        historical_panel = self.create_historical_panel()
        historical_row = Columns([historical_panel], equal=True, expand=True)
        
        display = Group(
            header,
            "",
            top_row,
            "",
            middle_row,
            "",
            bottom_row,
            "",
            historical_row
        )
        
        return display
    
    def create_historical_panel(self):
        """Create historical data display panel"""
        try:
            # Get performance summary
            perf_summary = self.get_performance_summary()
            
            # Create main historical table
            hist_table = Table(show_header=True, expand=True)
            hist_table.add_column("📈 Performance Metrics", style="bold bright_cyan", width=25)
            hist_table.add_column("Current Session", style="bright_white", width=20)
            hist_table.add_column("📊 Signal Analysis", style="bold bright_yellow", width=25)
            hist_table.add_column("Historical Data", style="bright_white", width=20)
            hist_table.add_column("🎯 Top Performers", style="bold bright_green", width=25)
            hist_table.add_column("Stats", style="bright_white", width=15)
            
            # Session performance
            session_signals = perf_summary.get('total_signals', 0)
            premium_signals = perf_summary.get('premium_signals', 0)
            avg_confidence = perf_summary.get('avg_confidence', 0)
            avg_score = perf_summary.get('avg_score', 0)
            balance_change = perf_summary.get('balance_change', 0)
            execution_rate = perf_summary.get('execution_rate', 0)
            
            # Format balance change
            balance_color = "bright_green" if balance_change >= 0 else "bright_red"
            balance_display = f"[{balance_color}]{balance_change:+.2f}[/{balance_color}]"
            
            # Top performing symbols
            top_symbols = perf_summary.get('top_symbols', [])
            
            # Historical backtest data
            backtest_data = self.historical_data['performance_metrics']
            
            # Add rows with different data categories
            hist_table.add_row(
                "🔍 Total Signals Found", f"{session_signals}",
                "⭐ Premium Signals (80%+)", f"{premium_signals}",
                "🏆 Best Symbol (Recent)", f"{top_symbols[0][0] if top_symbols else 'N/A'}",
                f"{top_symbols[0][1]['premium_count'] if top_symbols else 0} trades"
            )
            
            hist_table.add_row(
                "💰 Balance Change", balance_display,
                "📊 Execution Rate", f"{execution_rate:.1f}%",
                "🎯 High Confidence Avg", f"{avg_confidence:.1f}%",
                f"{avg_score:.0f} score"
            )
            
            hist_table.add_row(
                "⚡ Average Confidence", f"{avg_confidence:.1f}%",
                "🔥 Average Score", f"{avg_score:.0f}",
                "📈 Signal Quality", "Premium Focus" if execution_rate > 20 else "Standard",
                f"{len(self.historical_data['signal_history'])} total"
            )
            
            # Add backtest results if available
            if backtest_data:
                best_backtest = max(backtest_data.items(), key=lambda x: x[1]['win_rate'])
                hist_table.add_row(
                    "🏆 Best Backtest", f"{best_backtest[0][:15]}...",
                    "📊 Win Rate", f"{best_backtest[1]['win_rate']:.1f}%",
                    "💹 Total PnL", f"{best_backtest[1]['total_pnl']:.2f}",
                    f"{best_backtest[1]['total_trades']} trades"
                )
            
            # Recent signal patterns
            recent_signals = self.historical_data['signal_history'][-10:]
            if recent_signals:
                buy_signals = len([s for s in recent_signals if s['type'] == 'BUY'])
                sell_signals = len([s for s in recent_signals if s['type'] == 'SELL'])
                
                hist_table.add_row(
                    "🟢 Recent BUY Signals", f"{buy_signals}",
                    "🔴 Recent SELL Signals", f"{sell_signals}",
                    "📊 Signal Balance", "Bullish" if buy_signals > sell_signals else "Bearish",
                    f"{len(recent_signals)} recent"
                )
            
            # Create balance history mini-chart
            balance_history = self.historical_data['balance_history']
            if len(balance_history) >= 2:
                balance_trend = "📈 Growing" if balance_history[-1]['balance'] > balance_history[0]['balance'] else "📉 Declining"
                balance_change_pct = ((balance_history[-1]['balance'] - balance_history[0]['balance']) / 
                                    max(balance_history[0]['balance'], 1)) * 100
                
                hist_table.add_row(
                    "📊 Balance Trend", balance_trend,
                    "📈 Change %", f"{balance_change_pct:+.2f}%",
                    "⏰ Tracking Since", f"{balance_history[0]['timestamp'].strftime('%H:%M')}",
                    f"{len(balance_history)} points"
                )
            
            # Create historical panel
            historical_panel = Panel(hist_table, title="📈 Historical Performance & Analysis", border_style="bright_magenta")
            
            return historical_panel
            
        except Exception as e:
            self.log(f"⚠️ Error creating historical panel: {e}")
            # Fallback simple panel
            simple_table = Table(show_header=False, expand=True)
            simple_table.add_column("Info", style="bright_white")
            simple_table.add_row("📊 Historical data loading...")
            return Panel(simple_table, title="📈 Historical Data", border_style="bright_magenta")
    
    def run(self):
        """Run the bot"""
        self.running = True
        self.log("🚀 Alpine Bot is ready to discover amazing trading opportunities!")
        
        # Start trading thread
        trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        trading_thread.start()
        
        try:
            # Use Rich Live for proper display
            with Live(self.create_display(), console=self.console, refresh_per_second=1) as live:
                while self.running:
                    live.update(self.create_display())
                    time.sleep(1)
                
        except KeyboardInterrupt:
            self.running = False
            self.log("⏹️ Bot stopped by user")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False

def main():
    """Main entry point"""
    try:
        bot = WorkingAlpineBot()
        bot.run()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
