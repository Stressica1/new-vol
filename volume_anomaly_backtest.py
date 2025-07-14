#!/usr/bin/env python3
"""
Volume Anomaly Strategy Backtesting System
Advanced backtesting with multi-timeframe analysis and maximum leverage simulation
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import aiohttp
from typing import Dict, List, Tuple, Optional
import json
import time
from dataclasses import dataclass
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

# Import existing configuration
from config import TradingConfig, TRADING_PAIRS, get_exchange_config

@dataclass
class BacktestResult:
    """Results from backtesting simulation"""
    total_pnl: float
    total_pnl_percentage: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    sharpe_ratio: float
    avg_trade_duration: float
    best_trade: float
    worst_trade: float
    daily_returns: List[float]
    equity_curve: List[float]
    trade_log: List[Dict]
    timeframe_performance: Dict[str, Dict]

class VolumeAnomalyBacktester:
    """Advanced Volume Anomaly Strategy Backtester"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.exchange = None
        self.timeframes = ['30s', '1m', '3m', '5m']
        self.max_leverage = 20  # Maximum leverage for simulation
        self.initial_balance = 1000  # Starting balance in USDT
        self.current_balance = self.initial_balance
        self.positions = {}
        self.trade_history = []
        self.equity_curve = []
        self.daily_pnl = []
        
    def setup_exchange(self):
        """Setup exchange connection for data fetching"""
        try:
            exchange_config = get_exchange_config()
            self.exchange = ccxt.bitget({
                'apiKey': exchange_config['api_key'],
                'secret': exchange_config['secret'],
                'password': exchange_config['passphrase'],
                'sandbox': exchange_config['sandbox'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'
                }
            })
            logger.info("Exchange connection established for backtesting")
        except Exception as e:
            logger.error(f"Failed to setup exchange: {e}")
            
    async def fetch_historical_data(self, symbol: str, timeframe: str, days: int = 7) -> pd.DataFrame:
        """Fetch historical OHLCV data for backtesting"""
        try:
            # Calculate the time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Convert to milliseconds
            since = int(start_time.timestamp() * 1000)
            
            # Fetch data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def calculate_volume_anomaly(self, df: pd.DataFrame, lookback: int = 100) -> pd.DataFrame:
        """Calculate volume anomaly indicators"""
        df = df.copy()
        
        # Calculate volume moving average and standard deviation
        df['volume_ma'] = df['volume'].rolling(window=lookback).mean()
        df['volume_std'] = df['volume'].rolling(window=lookback).std()
        
        # Calculate volume anomaly score (z-score)
        df['volume_zscore'] = (df['volume'] - df['volume_ma']) / df['volume_std']
        
        # Calculate volume percentile
        df['volume_percentile'] = df['volume'].rolling(window=lookback).rank(pct=True)
        
        # Calculate price change
        df['price_change'] = df['close'].pct_change()
        df['price_change_abs'] = df['price_change'].abs()
        
        # Volume anomaly conditions
        df['high_volume_anomaly'] = (df['volume_percentile'] > 0.95) & (df['volume_zscore'] > 2)
        df['extreme_volume_anomaly'] = (df['volume_percentile'] > 0.99) & (df['volume_zscore'] > 3)
        
        # Price momentum
        df['price_momentum'] = df['close'].pct_change(periods=3)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on volume anomalies"""
        df = df.copy()
        
        # Initialize signal columns
        df['signal'] = 0  # 0: no signal, 1: long, -1: short
        df['signal_strength'] = 0.0
        df['signal_reason'] = ''
        
        # Long signals: High volume + positive price momentum
        long_condition = (
            (df['high_volume_anomaly']) &
            (df['price_momentum'] > 0.001) &  # Positive momentum
            (df['price_change'] > 0)  # Current candle is green
        )
        
        # Short signals: High volume + negative price momentum
        short_condition = (
            (df['high_volume_anomaly']) &
            (df['price_momentum'] < -0.001) &  # Negative momentum
            (df['price_change'] < 0)  # Current candle is red
        )
        
        # Extreme signals (higher strength)
        extreme_long = (
            (df['extreme_volume_anomaly']) &
            (df['price_momentum'] > 0.002) &
            (df['price_change'] > 0.005)
        )
        
        extreme_short = (
            (df['extreme_volume_anomaly']) &
            (df['price_momentum'] < -0.002) &
            (df['price_change'] < -0.005)
        )
        
        # Set signals
        df.loc[long_condition, 'signal'] = 1
        df.loc[short_condition, 'signal'] = -1
        df.loc[extreme_long, 'signal'] = 1
        df.loc[extreme_short, 'signal'] = -1
        
        # Set signal strength
        df.loc[long_condition, 'signal_strength'] = 0.5
        df.loc[short_condition, 'signal_strength'] = 0.5
        df.loc[extreme_long, 'signal_strength'] = 1.0
        df.loc[extreme_short, 'signal_strength'] = 1.0
        
        # Set signal reasons
        df.loc[long_condition, 'signal_reason'] = 'Volume Anomaly + Positive Momentum'
        df.loc[short_condition, 'signal_reason'] = 'Volume Anomaly + Negative Momentum'
        df.loc[extreme_long, 'signal_reason'] = 'EXTREME Volume Anomaly + Strong Positive Momentum'
        df.loc[extreme_short, 'signal_reason'] = 'EXTREME Volume Anomaly + Strong Negative Momentum'
        
        return df
    
    def calculate_position_size(self, balance: float, signal_strength: float, leverage: int) -> float:
        """Calculate position size based on signal strength and risk management"""
        # Base position size as percentage of balance
        base_size_pct = 0.02  # 2% of balance per trade
        
        # Adjust based on signal strength
        adjusted_size_pct = base_size_pct * (0.5 + signal_strength)
        
        # Apply leverage
        position_size = balance * adjusted_size_pct * leverage
        
        # Maximum position size limit (10% of balance with leverage)
        max_position_size = balance * 0.1 * leverage
        
        return min(position_size, max_position_size)
    
    def simulate_trade(self, symbol: str, signal: int, price: float, signal_strength: float, 
                      timestamp: datetime, timeframe: str) -> Optional[Dict]:
        """Simulate a single trade execution"""
        
        # Calculate position size
        position_size = self.calculate_position_size(self.current_balance, signal_strength, self.max_leverage)
        
        # Calculate quantity
        quantity = position_size / price
        
        # Risk management: Stop loss and take profit
        if signal == 1:  # Long
            stop_loss = price * 0.97  # 3% stop loss
            take_profit = price * 1.06  # 6% take profit
        else:  # Short
            stop_loss = price * 1.03  # 3% stop loss
            take_profit = price * 0.94  # 6% take profit
        
        trade = {
            'symbol': symbol,
            'side': 'long' if signal == 1 else 'short',
            'entry_price': price,
            'quantity': quantity,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': timestamp,
            'timeframe': timeframe,
            'signal_strength': signal_strength,
            'leverage': self.max_leverage,
            'status': 'open'
        }
        
        return trade
    
    def update_open_positions(self, current_data: Dict[str, pd.DataFrame], current_time: datetime):
        """Update open positions and check for exits"""
        positions_to_close = []
        
        for pos_id, position in self.positions.items():
            symbol = position['symbol']
            if symbol not in current_data:
                continue
                
            # Get current price
            current_price = current_data[symbol]['close'].iloc[-1]
            
            # Check stop loss and take profit
            should_close = False
            exit_reason = ''
            
            if position['side'] == 'long':
                if current_price <= position['stop_loss']:
                    should_close = True
                    exit_reason = 'Stop Loss'
                elif current_price >= position['take_profit']:
                    should_close = True
                    exit_reason = 'Take Profit'
            else:  # short
                if current_price >= position['stop_loss']:
                    should_close = True
                    exit_reason = 'Stop Loss'
                elif current_price <= position['take_profit']:
                    should_close = True
                    exit_reason = 'Take Profit'
            
            # Time-based exit (maximum 4 hours)
            if (current_time - position['entry_time']).total_seconds() > 4 * 3600:
                should_close = True
                exit_reason = 'Time Exit'
            
            if should_close:
                # Calculate PnL
                if position['side'] == 'long':
                    pnl = (current_price - position['entry_price']) * position['quantity']
                else:
                    pnl = (position['entry_price'] - current_price) * position['quantity']
                
                # Update balance
                self.current_balance += pnl
                
                # Record trade
                trade_record = {
                    **position,
                    'exit_price': current_price,
                    'exit_time': current_time,
                    'exit_reason': exit_reason,
                    'pnl': pnl,
                    'pnl_percentage': (pnl / position['position_size']) * 100,
                    'duration_minutes': (current_time - position['entry_time']).total_seconds() / 60,
                    'status': 'closed'
                }
                
                self.trade_history.append(trade_record)
                positions_to_close.append(pos_id)
        
        # Remove closed positions
        for pos_id in positions_to_close:
            del self.positions[pos_id]
    
    async def run_backtest(self, days: int = 7) -> BacktestResult:
        """Run the complete backtesting simulation"""
        logger.info(f"Starting Volume Anomaly Strategy Backtest for {days} days")
        
        # Setup exchange
        self.setup_exchange()
        
        # Fetch historical data for all pairs and timeframes
        all_data = {}
        
        for symbol in TRADING_PAIRS[:10]:  # Limit to first 10 pairs for faster testing
            try:
                symbol_data = {}
                for timeframe in self.timeframes:
                    df = await self.fetch_historical_data(symbol, timeframe, days)
                    if not df.empty:
                        # Calculate volume anomalies and generate signals
                        df = self.calculate_volume_anomaly(df)
                        df = self.generate_signals(df)
                        symbol_data[timeframe] = df
                
                if symbol_data:
                    all_data[symbol] = symbol_data
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        logger.info(f"Fetched data for {len(all_data)} trading pairs")
        
        # Create unified timeline for simulation
        all_timestamps = set()
        for symbol_data in all_data.values():
            for timeframe_data in symbol_data.values():
                all_timestamps.update(timeframe_data.index)
        
        timeline = sorted(all_timestamps)
        logger.info(f"Created timeline with {len(timeline)} timestamps")
        
        # Run simulation
        trade_id = 0
        
        for i, timestamp in enumerate(timeline):
            # Update equity curve
            self.equity_curve.append(self.current_balance)
            
            # Get current market data
            current_data = {}
            for symbol, symbol_data in all_data.items():
                for timeframe, df in symbol_data.items():
                    if timestamp in df.index:
                        current_data[f"{symbol}_{timeframe}"] = df.loc[df.index <= timestamp].tail(1)
            
            # Update open positions
            symbol_data_for_update = {}
            for symbol in all_data.keys():
                for timeframe in self.timeframes:
                    if f"{symbol}_{timeframe}" in current_data:
                        symbol_data_for_update[symbol] = all_data[symbol][timeframe].loc[all_data[symbol][timeframe].index <= timestamp]
                        break
            
            self.update_open_positions(symbol_data_for_update, timestamp)
            
            # Check for new signals
            for data_key, df in current_data.items():
                if df.empty:
                    continue
                    
                symbol, timeframe = data_key.rsplit('_', 1)
                current_row = df.iloc[-1]
                
                if current_row['signal'] != 0:  # Signal detected
                    # Limit concurrent positions
                    if len(self.positions) < 5:  # Maximum 5 concurrent positions
                        trade = self.simulate_trade(
                            symbol=symbol,
                            signal=current_row['signal'],
                            price=current_row['close'],
                            signal_strength=current_row['signal_strength'],
                            timestamp=timestamp,
                            timeframe=timeframe
                        )
                        
                        if trade:
                            self.positions[trade_id] = trade
                            trade_id += 1
            
            # Log progress
            if i % 1000 == 0:
                logger.info(f"Processed {i}/{len(timeline)} timestamps, Balance: ${self.current_balance:.2f}")
        
        # Close any remaining positions
        final_timestamp = timeline[-1]
        for symbol in all_data.keys():
            for timeframe in self.timeframes:
                if symbol in all_data and timeframe in all_data[symbol]:
                    symbol_data_for_update[symbol] = all_data[symbol][timeframe]
                    break
        
        # Force close remaining positions
        for pos_id, position in list(self.positions.items()):
            symbol = position['symbol']
            if symbol in symbol_data_for_update:
                current_price = symbol_data_for_update[symbol]['close'].iloc[-1]
                
                if position['side'] == 'long':
                    pnl = (current_price - position['entry_price']) * position['quantity']
                else:
                    pnl = (position['entry_price'] - current_price) * position['quantity']
                
                self.current_balance += pnl
                
                trade_record = {
                    **position,
                    'exit_price': current_price,
                    'exit_time': final_timestamp,
                    'exit_reason': 'Backtest End',
                    'pnl': pnl,
                    'pnl_percentage': (pnl / position['position_size']) * 100,
                    'duration_minutes': (final_timestamp - position['entry_time']).total_seconds() / 60,
                    'status': 'closed'
                }
                
                self.trade_history.append(trade_record)
        
        # Calculate results
        return self.calculate_backtest_results()
    
    def calculate_backtest_results(self) -> BacktestResult:
        """Calculate comprehensive backtest results"""
        
        if not self.trade_history:
            return BacktestResult(
                total_pnl=0, total_pnl_percentage=0, win_rate=0, total_trades=0,
                winning_trades=0, losing_trades=0, max_drawdown=0, sharpe_ratio=0,
                avg_trade_duration=0, best_trade=0, worst_trade=0, daily_returns=[],
                equity_curve=self.equity_curve, trade_log=[], timeframe_performance={}
            )
        
        # Basic metrics
        total_pnl = self.current_balance - self.initial_balance
        total_pnl_percentage = (total_pnl / self.initial_balance) * 100
        total_trades = len(self.trade_history)
        
        # Win/Loss metrics
        winning_trades = len([t for t in self.trade_history if t['pnl'] > 0])
        losing_trades = len([t for t in self.trade_history if t['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Trade performance
        pnls = [t['pnl'] for t in self.trade_history]
        best_trade = max(pnls) if pnls else 0
        worst_trade = min(pnls) if pnls else 0
        
        # Duration
        durations = [t['duration_minutes'] for t in self.trade_history]
        avg_trade_duration = sum(durations) / len(durations) if durations else 0
        
        # Drawdown calculation
        peak = self.initial_balance
        max_drawdown = 0
        for balance in self.equity_curve:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Daily returns
        daily_returns = []
        if len(self.equity_curve) > 1:
            daily_returns = [(self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1] * 100 
                           for i in range(1, len(self.equity_curve))]
        
        # Timeframe performance
        timeframe_performance = {}
        for timeframe in self.timeframes:
            tf_trades = [t for t in self.trade_history if t['timeframe'] == timeframe]
            if tf_trades:
                tf_pnl = sum(t['pnl'] for t in tf_trades)
                tf_win_rate = len([t for t in tf_trades if t['pnl'] > 0]) / len(tf_trades) * 100
                timeframe_performance[timeframe] = {
                    'trades': len(tf_trades),
                    'pnl': tf_pnl,
                    'win_rate': tf_win_rate
                }
        
        return BacktestResult(
            total_pnl=total_pnl,
            total_pnl_percentage=total_pnl_percentage,
            win_rate=win_rate,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            avg_trade_duration=avg_trade_duration,
            best_trade=best_trade,
            worst_trade=worst_trade,
            daily_returns=daily_returns,
            equity_curve=self.equity_curve,
            trade_log=self.trade_history,
            timeframe_performance=timeframe_performance
        )

async def main():
    """Main backtesting execution"""
    backtester = VolumeAnomalyBacktester()
    
    logger.info("🚀 Starting Volume Anomaly Strategy Backtest")
    logger.info(f"📊 Initial Balance: ${backtester.initial_balance}")
    logger.info(f"⚡ Max Leverage: {backtester.max_leverage}x")
    logger.info(f"⏱️ Timeframes: {backtester.timeframes}")
    
    # Run backtest
    results = await backtester.run_backtest(days=7)
    
    # Print results
    print("\n" + "="*80)
    print("📈 VOLUME ANOMALY STRATEGY BACKTEST RESULTS")
    print("="*80)
    print(f"🎯 Strategy: Volume Anomaly Detection with {backtester.max_leverage}x Leverage")
    print(f"📅 Period: 7 days")
    print(f"⏱️ Timeframes: {', '.join(backtester.timeframes)}")
    print(f"💰 Initial Balance: ${backtester.initial_balance:,.2f}")
    print(f"💰 Final Balance: ${backtester.current_balance:,.2f}")
    print(f"📊 Total P&L: ${results.total_pnl:,.2f} ({results.total_pnl_percentage:.2f}%)")
    print(f"📈 Total Trades: {results.total_trades}")
    print(f"✅ Winning Trades: {results.winning_trades}")
    print(f"❌ Losing Trades: {results.losing_trades}")
    print(f"🎯 Win Rate: {results.win_rate:.2f}%")
    print(f"📉 Max Drawdown: {results.max_drawdown:.2f}%")
    print(f"📊 Sharpe Ratio: {results.sharpe_ratio:.3f}")
    print(f"⏱️ Avg Trade Duration: {results.avg_trade_duration:.1f} minutes")
    print(f"🚀 Best Trade: ${results.best_trade:,.2f}")
    print(f"💥 Worst Trade: ${results.worst_trade:,.2f}")
    
    print("\n📊 TIMEFRAME PERFORMANCE:")
    for timeframe, performance in results.timeframe_performance.items():
        print(f"  {timeframe}: {performance['trades']} trades, "
              f"${performance['pnl']:,.2f} P&L, {performance['win_rate']:.1f}% win rate")
    
    print("\n📋 RECENT TRADES:")
    for trade in results.trade_log[-10:]:  # Show last 10 trades
        print(f"  {trade['symbol']} {trade['side'].upper()} | "
              f"Entry: ${trade['entry_price']:.4f} | "
              f"Exit: ${trade['exit_price']:.4f} | "
              f"P&L: ${trade['pnl']:,.2f} | "
              f"Duration: {trade['duration_minutes']:.1f}m | "
              f"Reason: {trade['exit_reason']}")
    
    print("="*80)
    
    # Save results to file
    with open('backtest_results.json', 'w') as f:
        json.dump({
            'summary': {
                'initial_balance': backtester.initial_balance,
                'final_balance': backtester.current_balance,
                'total_pnl': results.total_pnl,
                'total_pnl_percentage': results.total_pnl_percentage,
                'win_rate': results.win_rate,
                'total_trades': results.total_trades,
                'max_drawdown': results.max_drawdown,
                'sharpe_ratio': results.sharpe_ratio
            },
            'timeframe_performance': results.timeframe_performance,
            'trade_log': results.trade_log
        }, f, indent=2, default=str)
    
    logger.info("📁 Results saved to backtest_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 