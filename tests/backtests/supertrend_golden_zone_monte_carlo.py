#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SUPERTREND GOLDEN ZONE MONTE CARLO BACKTEST
🎯 Comprehensive Monte Carlo optimization for SuperTrend + Golden Zone strategy
🚀 Optimized for maximum win rate and minimal drawdown
"""

from __future__ import annotations

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union, Tuple
import sys
import os
import random
import json
from dotenv import load_dotenv
from typing_extensions import TypedDict

from loguru import logger
import traceback
import sys
import os
import random
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# UNIFIED LOGGING SETUP
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/supertrend_monte_carlo.log", rotation="1 day", retention="7 days", 
          format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

@dataclass
class MonteCarloConfig:
    """🎯 Monte Carlo optimization configuration for SuperTrend Golden Zone"""
    
    # Supertrend Parameters
    supertrend_period_min: int = 8
    supertrend_period_max: int = 15
    supertrend_multiplier_min: float = 2.0
    supertrend_multiplier_max: float = 4.0
    atr_period_min: int = 10
    atr_period_max: int = 20
    
    # Golden Zone Parameters
    golden_zone_start_min: float = 0.68
    golden_zone_start_max: float = 0.76
    golden_zone_end_min: float = 0.84
    golden_zone_end_max: float = 0.92
    zone_tolerance_min: float = 0.01
    zone_tolerance_max: float = 0.03
    
    # Volume Analysis
    volume_spike_min: float = 1.3
    volume_spike_max: float = 3.0
    volume_period_min: int = 15
    volume_period_max: int = 30
    
    # RSI Configuration
    rsi_period_min: int = 10
    rsi_period_max: int = 18
    rsi_oversold_min: float = 25.0
    rsi_oversold_max: float = 40.0
    rsi_overbought_min: float = 60.0
    rsi_overbought_max: float = 75.0
    
    # Signal Quality
    min_confidence_min: float = 70.0
    min_confidence_max: float = 90.0
    min_volume_spike_min: float = 1.2
    min_volume_spike_max: float = 2.5
    
    # Risk Management
    stop_loss_min: float = 0.8
    stop_loss_max: float = 2.0
    take_profit_min: float = 1.5
    take_profit_max: float = 3.5
    position_size_min: float = 8.0
    position_size_max: float = 15.0
    
    # Optimization Targets
    target_metrics: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.target_metrics is None:
            self.target_metrics = ['win_rate', 'profit_factor', 'sharpe_ratio', 'max_drawdown']

@dataclass
class BacktestResult:
    """📊 Backtest result structure"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    profit_factor: float
    average_win: float
    average_loss: float
    max_drawdown: float
    sharpe_ratio: float
    total_return: float
    parameters: Dict[str, Any]
    trade_history: List[Dict[str, Any]]

class SupertrendCalculator:
    """📈 Enhanced Supertrend calculator"""
    
    def calculate_supertrend(self, df: pd.DataFrame, period: int, multiplier: float, atr_period: int) -> pd.DataFrame:
        """📊 Calculate Supertrend indicator with custom parameters"""
        try:
            # Calculate ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(atr_period).mean()
            
            # Calculate Supertrend
            hl2 = (df['high'] + df['low']) / 2
            basic_upperband = hl2 + (multiplier * atr)
            basic_lowerband = hl2 - (multiplier * atr)
            
            # Initialize bands
            final_upperband = basic_upperband.copy()
            final_lowerband = basic_lowerband.copy()
            supertrend = pd.Series(index=df.index, dtype=float)
            trend_direction = pd.Series(index=df.index, dtype=int)
            
            for i in range(1, len(df)):
                # Upper band logic
                if basic_upperband.iloc[i] < final_upperband.iloc[i-1] or df['close'].iloc[i-1] > final_upperband.iloc[i-1]:
                    final_upperband.iloc[i] = basic_upperband.iloc[i]
                else:
                    final_upperband.iloc[i] = final_upperband.iloc[i-1]
                
                # Lower band logic
                if basic_lowerband.iloc[i] > final_lowerband.iloc[i-1] or df['close'].iloc[i-1] < final_lowerband.iloc[i-1]:
                    final_lowerband.iloc[i] = basic_lowerband.iloc[i]
                else:
                    final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
                
                # Supertrend signal
                if supertrend.iloc[i-1] == final_upperband.iloc[i-1] and df['close'].iloc[i] <= final_upperband.iloc[i]:
                    supertrend.iloc[i] = final_upperband.iloc[i]
                    trend_direction.iloc[i] = -1
                elif supertrend.iloc[i-1] == final_upperband.iloc[i-1] and df['close'].iloc[i] > final_upperband.iloc[i]:
                    supertrend.iloc[i] = final_lowerband.iloc[i]
                    trend_direction.iloc[i] = 1
                elif supertrend.iloc[i-1] == final_lowerband.iloc[i-1] and df['close'].iloc[i] >= final_lowerband.iloc[i]:
                    supertrend.iloc[i] = final_lowerband.iloc[i]
                    trend_direction.iloc[i] = 1
                elif supertrend.iloc[i-1] == final_lowerband.iloc[i-1] and df['close'].iloc[i] < final_lowerband.iloc[i]:
                    supertrend.iloc[i] = final_upperband.iloc[i]
                    trend_direction.iloc[i] = -1
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    trend_direction.iloc[i] = trend_direction.iloc[i-1]
            
            # Add to dataframe
            df['supertrend'] = supertrend
            df['supertrend_upper'] = final_upperband
            df['supertrend_lower'] = final_lowerband
            df['supertrend_direction'] = trend_direction
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Supertrend calculation error: {e}")
            traceback.print_exc()
            return df

class GoldenZoneCalculator:
    """🎯 Enhanced Golden Zone Fibonacci calculator"""
    
    def calculate_fibonacci_levels(self, df: pd.DataFrame, golden_zone_start: float, 
                                 golden_zone_end: float, zone_tolerance: float, 
                                 lookback: int = 50) -> pd.DataFrame:
        """📊 Calculate Fibonacci retracement levels with Golden Zone"""
        try:
            # Find swing high and low
            swing_high = df['high'].rolling(lookback).max()
            swing_low = df['low'].rolling(lookback).min()
            
            # Calculate Fibonacci levels
            diff = swing_high - swing_low
            
            # Standard Fibonacci levels
            fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.72, 0.786, 0.88, 1.0]
            
            for level in fib_levels:
                fib_level = swing_low + (diff * level)
                df[f'fib_{level:.3f}'.replace('.', '_')] = fib_level
            
            # Calculate Golden Zone
            df['golden_zone_upper'] = swing_low + (diff * golden_zone_end)
            df['golden_zone_lower'] = swing_low + (diff * golden_zone_start)
            
            # Determine if price is in Golden Zone
            current_price = df['close']
            golden_zone_upper = df['golden_zone_upper']
            golden_zone_lower = df['golden_zone_lower']
            
            df['in_golden_zone'] = (
                (current_price >= golden_zone_lower - (golden_zone_lower * zone_tolerance)) &
                (current_price <= golden_zone_upper + (golden_zone_upper * zone_tolerance))
            )
            
            # Calculate Golden Zone position (0-1 scale)
            df['golden_zone_position'] = np.where(
                df['in_golden_zone'],
                (current_price - golden_zone_lower) / (golden_zone_upper - golden_zone_lower),
                0
            )
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Fibonacci calculation error: {e}")
            traceback.print_exc()
            return df

class MonteCarloSupertrendBacktester:
    """🎯 Monte Carlo backtester for SuperTrend Golden Zone strategy"""
    
    def __init__(self, config: MonteCarloConfig):
        self.config = config
        self.exchange = None
        self.best_params = None
        self.best_score = 0.0
        self.results_history = []
        
    async def initialize_exchange(self):
        """🔌 Initialize Bitget exchange"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': API_KEY,
                'secret': SECRET_KEY,
                'password': PASSPHRASE,
                'sandbox': False,
                'options': {
                    'defaultType': 'swap',
                    'defaultMarginMode': 'cross'
                }
            })
            await self.exchange.load_markets()
            logger.success("✅ Exchange initialized for Monte Carlo backtest")
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            traceback.print_exc()
            raise
    
    def generate_random_params(self) -> Dict:
        """🎲 Generate random parameters for testing"""
        params = {
            # Supertrend Parameters
            'supertrend_period': random.randint(self.config.supertrend_period_min, self.config.supertrend_period_max),
            'supertrend_multiplier': random.uniform(self.config.supertrend_multiplier_min, self.config.supertrend_multiplier_max),
            'atr_period': random.randint(self.config.atr_period_min, self.config.atr_period_max),
            
            # Golden Zone Parameters
            'golden_zone_start': random.uniform(self.config.golden_zone_start_min, self.config.golden_zone_start_max),
            'golden_zone_end': random.uniform(self.config.golden_zone_end_min, self.config.golden_zone_end_max),
            'zone_tolerance': random.uniform(self.config.zone_tolerance_min, self.config.zone_tolerance_max),
            
            # Volume Analysis
            'volume_spike_threshold': random.uniform(self.config.volume_spike_min, self.config.volume_spike_max),
            'volume_period': random.randint(self.config.volume_period_min, self.config.volume_period_max),
            
            # RSI Configuration
            'rsi_period': random.randint(self.config.rsi_period_min, self.config.rsi_period_max),
            'rsi_oversold': random.uniform(self.config.rsi_oversold_min, self.config.rsi_oversold_max),
            'rsi_overbought': random.uniform(self.config.rsi_overbought_min, self.config.rsi_overbought_max),
            
            # Signal Quality
            'min_confidence': random.uniform(self.config.min_confidence_min, self.config.min_confidence_max),
            'min_volume_spike': random.uniform(self.config.min_volume_spike_min, self.config.min_volume_spike_max),
            
            # Risk Management
            'stop_loss_pct': random.uniform(self.config.stop_loss_min, self.config.stop_loss_max),
            'take_profit_pct': random.uniform(self.config.take_profit_min, self.config.take_profit_max),
            'position_size_pct': random.uniform(self.config.position_size_min, self.config.position_size_max)
        }
        return params
    
    def calculate_rsi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """📊 Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"❌ RSI calculation error: {e}")
            return pd.Series(index=df.index, dtype=float)
    
    def calculate_volume_spike(self, df: pd.DataFrame, period: int) -> pd.Series:
        """📊 Calculate volume spike ratio"""
        try:
            volume_sma = df['volume'].rolling(period).mean()
            volume_ratio = df['volume'] / volume_sma
            return volume_ratio
        except Exception as e:
            logger.error(f"❌ Volume spike calculation error: {e}")
            return pd.Series(index=df.index, dtype=float)
    
    def generate_signal(self, df: pd.DataFrame, params: Dict) -> Dict:
        """🎯 Generate trading signal with SuperTrend + Golden Zone"""
        try:
            if len(df) < 50:
                return None
            
            # Get current values
            current_price = df['close'].iloc[-1]
            current_supertrend = df['supertrend'].iloc[-1]
            current_trend = df['supertrend_direction'].iloc[-1]
            in_golden_zone = df['in_golden_zone'].iloc[-1]
            volume_spike = df['volume_ratio'].iloc[-1]
            current_rsi = df['rsi'].iloc[-1]
            
            # Skip if any values are NaN
            if pd.isna(current_supertrend) or pd.isna(current_trend) or pd.isna(current_rsi):
                return None
            
            signal = None
            confidence = 0.0
            reasons = []
            
            # Volume condition
            volume_condition = volume_spike >= params['min_volume_spike']
            if volume_condition:
                reasons.append(f"Volume spike: {volume_spike:.2f}x")
                confidence += 25.0
            
            # RSI condition
            rsi_condition = False
            if current_rsi < params['rsi_oversold']:
                rsi_condition = True
                reasons.append(f"RSI oversold: {current_rsi:.1f}")
                confidence += 25.0
            elif current_rsi > params['rsi_overbought']:
                rsi_condition = True
                reasons.append(f"RSI overbought: {current_rsi:.1f}")
                confidence += 25.0
            
            # SuperTrend condition
            supertrend_condition = False
            if current_trend == 1 and current_price > current_supertrend:
                supertrend_condition = True
                reasons.append("SuperTrend bullish")
                confidence += 30.0
            elif current_trend == -1 and current_price < current_supertrend:
                supertrend_condition = True
                reasons.append("SuperTrend bearish")
                confidence += 30.0
            
            # Golden Zone condition
            golden_zone_condition = in_golden_zone
            if golden_zone_condition:
                reasons.append("In Golden Zone")
                confidence += 20.0
            
            # Generate signal
            if confidence >= params['min_confidence']:
                if current_trend == 1 and rsi_condition and (supertrend_condition or golden_zone_condition):
                    signal = {
                        'side': 'buy',
                        'price': current_price,
                        'confidence': confidence,
                        'reasons': reasons,
                        'timestamp': df.index[-1]
                    }
                elif current_trend == -1 and rsi_condition and (supertrend_condition or golden_zone_condition):
                    signal = {
                        'side': 'sell',
                        'price': current_price,
                        'confidence': confidence,
                        'reasons': reasons,
                        'timestamp': df.index[-1]
                    }
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return None
    
    async def fetch_historical_data(self, symbol: str, timeframe: str = '5m', limit: int = 1000) -> pd.DataFrame:
        """📊 Fetch historical data for backtesting"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"❌ Data fetch error for {symbol}: {e}")
            return pd.DataFrame()
    
    async def backtest_parameters(self, params: Dict, symbols: List[str], 
                                timeframe: str = '5m', days: int = 7) -> BacktestResult:
        """📊 Backtest parameters on historical data"""
        try:
            trades = []
            total_profit = 0.0
            total_loss = 0.0
            winning_trades = 0
            losing_trades = 0
            max_drawdown = 0.0
            peak_balance = 10000.0  # Starting balance
            current_balance = 10000.0
            
            # Calculate lookback period
            lookback_days = max(30, days * 2)  # Ensure enough data for indicators
            
            for symbol in symbols:
                try:
                    # Fetch historical data
                    df = await self.fetch_historical_data(symbol, timeframe, limit=lookback_days * 288)  # 5m candles
                    
                    if len(df) < 100:
                        continue
                    
                    # Calculate indicators
                    supertrend_calc = SupertrendCalculator()
                    df = supertrend_calc.calculate_supertrend(
                        df, 
                        params['supertrend_period'], 
                        params['supertrend_multiplier'], 
                        params['atr_period']
                    )
                    
                    golden_zone_calc = GoldenZoneCalculator()
                    df = golden_zone_calc.calculate_fibonacci_levels(
                        df,
                        params['golden_zone_start'],
                        params['golden_zone_end'],
                        params['zone_tolerance']
                    )
                    
                    # Calculate additional indicators
                    df['rsi'] = self.calculate_rsi(df, params['rsi_period'])
                    df['volume_ratio'] = self.calculate_volume_spike(df, params['volume_period'])
                    
                    # Generate signals
                    for i in range(50, len(df)):  # Start after enough data for indicators
                        signal_df = df.iloc[:i+1]
                        signal = self.generate_signal(signal_df, params)
                        
                        if signal:
                            # Simulate trade
                            entry_price = signal['price']
                            side = signal['side']
                            
                            # Calculate stop loss and take profit
                            if side == 'buy':
                                stop_loss = entry_price * (1 - params['stop_loss_pct'] / 100)
                                take_profit = entry_price * (1 + params['take_profit_pct'] / 100)
                            else:
                                stop_loss = entry_price * (1 + params['stop_loss_pct'] / 100)
                                take_profit = entry_price * (1 - params['take_profit_pct'] / 100)
                            
                            # Find exit point
                            exit_price = None
                            exit_reason = None
                            
                            for j in range(i+1, min(i+100, len(df))):  # Look ahead max 100 candles
                                future_price = df['close'].iloc[j]
                                
                                if side == 'buy':
                                    if future_price <= stop_loss:
                                        exit_price = stop_loss
                                        exit_reason = 'stop_loss'
                                        break
                                    elif future_price >= take_profit:
                                        exit_price = take_profit
                                        exit_reason = 'take_profit'
                                        break
                                else:
                                    if future_price >= stop_loss:
                                        exit_price = stop_loss
                                        exit_reason = 'stop_loss'
                                        break
                                    elif future_price <= take_profit:
                                        exit_price = take_profit
                                        exit_reason = 'take_profit'
                                        break
                            
                            if exit_price:
                                # Calculate P&L
                                if side == 'buy':
                                    pnl = (exit_price - entry_price) / entry_price * 100
                                else:
                                    pnl = (entry_price - exit_price) / entry_price * 100
                                
                                # Update statistics
                                position_size = current_balance * params['position_size_pct'] / 100
                                trade_pnl = position_size * pnl / 100
                                
                                if pnl > 0:
                                    total_profit += trade_pnl
                                    winning_trades += 1
                                else:
                                    total_loss += abs(trade_pnl)
                                    losing_trades += 1
                                
                                current_balance += trade_pnl
                                
                                # Update max drawdown
                                if current_balance > peak_balance:
                                    peak_balance = current_balance
                                else:
                                    drawdown = (peak_balance - current_balance) / peak_balance * 100
                                    max_drawdown = max(max_drawdown, drawdown)
                                
                                # Record trade
                                trade = {
                                    'symbol': symbol,
                                    'side': side,
                                    'entry_price': entry_price,
                                    'exit_price': exit_price,
                                    'pnl': pnl,
                                    'trade_pnl': trade_pnl,
                                    'exit_reason': exit_reason,
                                    'confidence': signal['confidence'],
                                    'reasons': signal['reasons'],
                                    'timestamp': signal['timestamp']
                                }
                                trades.append(trade)
                
                except Exception as e:
                    logger.warning(f"⚠️ Error backtesting {symbol}: {e}")
                    continue
            
            # Calculate final statistics
            total_trades = winning_trades + losing_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
            average_win = (total_profit / winning_trades) if winning_trades > 0 else 0
            average_loss = (total_loss / losing_trades) if losing_trades > 0 else 0
            total_return = ((current_balance - 10000) / 10000) * 100
            
            # Calculate Sharpe ratio (simplified)
            if len(trades) > 0:
                returns = [trade['pnl'] for trade in trades]
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
            
            return BacktestResult(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_profit=total_profit,
                total_loss=total_loss,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                total_return=total_return,
                parameters=params,
                trade_history=trades
            )
            
        except Exception as e:
            logger.error(f"❌ Backtest error: {e}")
            traceback.print_exc()
            return None
    
    def calculate_score(self, result: BacktestResult) -> float:
        """🎯 Calculate optimization score"""
        try:
            # Weighted scoring system
            win_rate_score = result.win_rate / 100.0
            profit_factor_score = min(result.profit_factor / 3.0, 1.0)  # Cap at 3.0
            sharpe_score = min(max(result.sharpe_ratio / 2.0, 0.0), 1.0)  # Normalize to 0-1
            drawdown_score = max(0.0, 1.0 - (result.max_drawdown / 50.0))  # Penalize high drawdown
            
            # Combined score
            score = (
                win_rate_score * 0.35 +
                profit_factor_score * 0.25 +
                sharpe_score * 0.25 +
                drawdown_score * 0.15
            )
            
            return score
            
        except Exception as e:
            logger.error(f"❌ Score calculation error: {e}")
            return 0.0
    
    async def run_monte_carlo_optimization(self, symbols: List[str], iterations: int = 1000) -> Dict:
        """🎯 Run Monte Carlo optimization"""
        try:
            logger.info(f"🚀 Starting Monte Carlo optimization with {iterations} iterations")
            
            best_result = None
            all_results = []
            
            for i in range(iterations):
                try:
                    # Generate random parameters
                    params = self.generate_random_params()
                    
                    # Run backtest
                    result = await self.backtest_parameters(params, symbols, days=7)
                    
                    if result and result.total_trades >= 10:  # Minimum trades for valid result
                        score = self.calculate_score(result)
                        result.score = score
                        all_results.append(result)
                        
                        # Update best result
                        if best_result is None or score > best_result.score:
                            best_result = result
                            logger.success(f"🎯 New best score: {score:.4f} (Win Rate: {result.win_rate:.1f}%, PF: {result.profit_factor:.2f})")
                    
                    # Progress update
                    if (i + 1) % 100 == 0:
                        logger.info(f"📊 Completed {i + 1}/{iterations} iterations")
                
                except Exception as e:
                    logger.warning(f"⚠️ Iteration {i + 1} failed: {e}")
                    continue
            
            # Sort results by score
            all_results.sort(key=lambda x: x.score, reverse=True)
            
            # Generate optimization report
            optimization_report = {
                'best_parameters': best_result.parameters if best_result else None,
                'best_score': best_result.score if best_result else 0.0,
                'best_result': best_result,
                'top_10_results': all_results[:10],
                'total_iterations': iterations,
                'valid_results': len(all_results),
                'optimization_summary': {
                    'avg_win_rate': np.mean([r.win_rate for r in all_results]),
                    'avg_profit_factor': np.mean([r.profit_factor for r in all_results]),
                    'avg_sharpe': np.mean([r.sharpe_ratio for r in all_results]),
                    'avg_drawdown': np.mean([r.max_drawdown for r in all_results])
                }
            }
            
            logger.success(f"✅ Monte Carlo optimization completed!")
            logger.info(f"📊 Best Score: {best_result.score:.4f}")
            logger.info(f"📊 Best Win Rate: {best_result.win_rate:.1f}%")
            logger.info(f"📊 Best Profit Factor: {best_result.profit_factor:.2f}")
            
            return optimization_report
            
        except Exception as e:
            logger.error(f"❌ Monte Carlo optimization error: {e}")
            traceback.print_exc()
            return None

async def main():
    """🎯 Main function to run Monte Carlo backtest"""
    try:
        # Initialize configuration
        config = MonteCarloConfig()
        
        # Initialize backtester
        backtester = MonteCarloSupertrendBacktester(config)
        await backtester.initialize_exchange()
        
        # Define symbols to test
        symbols = [
            'BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT', 'ADA/USDT:USDT',
            'SOL/USDT:USDT', 'DOT/USDT:USDT', 'AVAX/USDT:USDT', 'MATIC/USDT:USDT',
            'LINK/USDT:USDT', 'UNI/USDT:USDT', 'ATOM/USDT:USDT', 'LTC/USDT:USDT',
            'XRP/USDT:USDT', 'BCH/USDT:USDT', 'FIL/USDT:USDT', 'NEAR/USDT:USDT',
            'FTM/USDT:USDT', 'ALGO/USDT:USDT', 'VET/USDT:USDT', 'MANA/USDT:USDT'
        ]
        
        logger.info(f"🎯 Starting SuperTrend Golden Zone Monte Carlo backtest")
        logger.info(f"📊 Testing {len(symbols)} symbols")
        logger.info(f"🎲 Running 1000 Monte Carlo iterations")
        
        # Run optimization
        results = await backtester.run_monte_carlo_optimization(symbols, iterations=1000)
        
        if results:
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/supertrend_monte_carlo_results_{timestamp}.json"
            
            # Convert results to JSON-serializable format
            json_results = {
                'best_parameters': results['best_parameters'],
                'best_score': results['best_score'],
                'total_iterations': results['total_iterations'],
                'valid_results': results['valid_results'],
                'optimization_summary': results['optimization_summary'],
                'best_result': {
                    'total_trades': results['best_result'].total_trades,
                    'winning_trades': results['best_result'].winning_trades,
                    'losing_trades': results['best_result'].losing_trades,
                    'win_rate': results['best_result'].win_rate,
                    'total_profit': results['best_result'].total_profit,
                    'total_loss': results['best_result'].total_loss,
                    'profit_factor': results['best_result'].profit_factor,
                    'average_win': results['best_result'].average_win,
                    'average_loss': results['best_result'].average_loss,
                    'max_drawdown': results['best_result'].max_drawdown,
                    'sharpe_ratio': results['best_result'].sharpe_ratio,
                    'total_return': results['best_result'].total_return,
                    'score': results['best_result'].score
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(json_results, f, indent=2, default=str)
            
            logger.success(f"💾 Results saved to {filename}")
            
            # Print summary
            print("\n" + "="*80)
            print("🏔️ SUPERTREND GOLDEN ZONE MONTE CARLO BACKTEST RESULTS")
            print("="*80)
            print(f"🎯 Best Score: {results['best_score']:.4f}")
            print(f"📊 Best Win Rate: {results['best_result'].win_rate:.1f}%")
            print(f"💰 Best Profit Factor: {results['best_result'].profit_factor:.2f}")
            print(f"📈 Best Sharpe Ratio: {results['best_result'].sharpe_ratio:.2f}")
            print(f"📉 Best Max Drawdown: {results['best_result'].max_drawdown:.1f}%")
            print(f"🔄 Total Trades: {results['best_result'].total_trades}")
            print(f"✅ Valid Results: {results['valid_results']}/{results['total_iterations']}")
            print("="*80)
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 