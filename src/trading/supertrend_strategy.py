#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SUPERTREND & GOLDEN ZONE STRATEGY
🎯 Advanced strategy combining Supertrend with Fibonacci Golden Zone (0.72-0.88)
🚀 Monte Carlo optimized for maximum win rate and minimal drawdown
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union, Tuple
from loguru import logger
import traceback
import sys
import os
import random
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
logger.add("logs/supertrend_golden_zone.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

@dataclass
class SupertrendConfig:
    """📊 Supertrend configuration parameters"""
    period: int = 10
    multiplier: float = 3.0
    atr_period: int = 14

@dataclass
class GoldenZoneConfig:
    """🎯 Golden Zone Fibonacci configuration"""
    fib_levels: List[float] = None
    golden_zone_start: float = 0.72  # 0.72 Fibonacci level
    golden_zone_end: float = 0.88    # 0.88 Fibonacci level
    zone_tolerance: float = 0.02     # 2% tolerance for zone entry
    
    def __post_init__(self):
        if self.fib_levels is None:
            self.fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.72, 0.786, 0.88, 1.0]

@dataclass
class StrategyConfig:
    """🎯 Complete strategy configuration"""
    # Supertrend Settings
    supertrend_period: int = 10
    supertrend_multiplier: float = 3.0
    supertrend_atr_period: int = 14
    
    # Golden Zone Settings
    golden_zone_start: float = 0.72
    golden_zone_end: float = 0.88
    zone_tolerance: float = 0.02
    
    # Signal Quality
    min_confidence: float = 75.0
    min_volume_spike: float = 1.5
    min_rsi: float = 30.0
    max_rsi: float = 70.0
    
    # Risk Management
    stop_loss_pct: float = 1.25
    take_profit_pct: float = 2.0
    max_positions: int = 5
    position_size_pct: float = 11.0
    
    # Monte Carlo Optimization
    monte_carlo_iterations: int = 1000
    optimization_target: str = "sharpe_ratio"  # sharpe_ratio, win_rate, profit_factor

class SupertrendCalculator:
    """📈 Supertrend indicator calculator"""
    
    def __init__(self, config: SupertrendConfig):
        self.config = config
    
    def calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """📊 Calculate Supertrend indicator"""
        try:
            # Calculate ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(self.config.atr_period).mean()
            
            # Calculate Supertrend
            hl2 = (df['high'] + df['low']) / 2
            basic_upperband = hl2 + (self.config.multiplier * atr)
            basic_lowerband = hl2 - (self.config.multiplier * atr)
            
            # Initialize bands
            final_upperband = basic_upperband.copy()
            final_lowerband = basic_lowerband.copy()
            supertrend = pd.Series(index=df.index, dtype=float)
            
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
                elif supertrend.iloc[i-1] == final_upperband.iloc[i-1] and df['close'].iloc[i] > final_upperband.iloc[i]:
                    supertrend.iloc[i] = final_lowerband.iloc[i]
                elif supertrend.iloc[i-1] == final_lowerband.iloc[i-1] and df['close'].iloc[i] >= final_lowerband.iloc[i]:
                    supertrend.iloc[i] = final_lowerband.iloc[i]
                elif supertrend.iloc[i-1] == final_lowerband.iloc[i-1] and df['close'].iloc[i] < final_lowerband.iloc[i]:
                    supertrend.iloc[i] = final_upperband.iloc[i]
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
            
            # Add to dataframe
            df['supertrend'] = supertrend
            df['supertrend_upper'] = final_upperband
            df['supertrend_lower'] = final_lowerband
            df['supertrend_direction'] = np.where(df['close'] > supertrend, 1, -1)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Supertrend calculation error: {e}")
            traceback.print_exc()
            return df

class GoldenZoneCalculator:
    """🎯 Golden Zone Fibonacci calculator"""
    
    def __init__(self, config: GoldenZoneConfig):
        self.config = config
    
    def calculate_fibonacci_levels(self, df: pd.DataFrame, lookback: int = 50) -> pd.DataFrame:
        """📊 Calculate Fibonacci retracement levels"""
        try:
            # Find swing high and low
            swing_high = df['high'].rolling(lookback).max()
            swing_low = df['low'].rolling(lookback).min()
            
            # Calculate Fibonacci levels
            diff = swing_high - swing_low
            
            for level in self.config.fib_levels:
                fib_level = swing_low + (diff * level)
                df[f'fib_{level:.3f}'.replace('.', '_')] = fib_level
            
            # Calculate Golden Zone
            df['golden_zone_upper'] = swing_low + (diff * self.config.golden_zone_end)
            df['golden_zone_lower'] = swing_low + (diff * self.config.golden_zone_start)
            
            # Determine if price is in Golden Zone
            current_price = df['close'].iloc[-1]
            golden_zone_upper = df['golden_zone_upper'].iloc[-1]
            golden_zone_lower = df['golden_zone_lower'].iloc[-1]
            
            df['in_golden_zone'] = (
                (current_price >= golden_zone_lower - (golden_zone_lower * self.config.zone_tolerance)) &
                (current_price <= golden_zone_upper + (golden_zone_upper * self.config.zone_tolerance))
            )
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Fibonacci calculation error: {e}")
            traceback.print_exc()
            return df
    
    def is_in_golden_zone(self, df: pd.DataFrame) -> bool:
        """🎯 Check if current price is in Golden Zone"""
        try:
            return df['in_golden_zone'].iloc[-1] if 'in_golden_zone' in df.columns else False
        except Exception as e:
            logger.warning(f"⚠️ Golden Zone check error: {e}")
            return False

class SupertrendGoldenZoneStrategy:
    """🎯 Supertrend + Golden Zone Strategy"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.supertrend_calc = SupertrendCalculator(SupertrendConfig(
            period=config.supertrend_period,
            multiplier=config.supertrend_multiplier,
            atr_period=config.supertrend_atr_period
        ))
        self.golden_zone_calc = GoldenZoneCalculator(GoldenZoneConfig(
            golden_zone_start=config.golden_zone_start,
            golden_zone_end=config.golden_zone_end,
            zone_tolerance=config.zone_tolerance
        ))
        self.exchange = None
        
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
            logger.success("✅ Exchange initialized for Supertrend Golden Zone strategy")
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            traceback.print_exc()
            raise
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
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
    
    def calculate_volume_spike(self, df: pd.DataFrame, period: int = 20) -> float:
        """📊 Calculate volume spike ratio"""
        try:
            volume_sma = df['volume'].rolling(period).mean()
            current_volume = df['volume'].iloc[-1]
            volume_spike = current_volume / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 1
            return volume_spike
        except Exception as e:
            logger.error(f"❌ Volume spike calculation error: {e}")
            return 1.0
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """🎯 Generate trading signal based on Supertrend + Golden Zone"""
        try:
            # Calculate indicators
            df = self.supertrend_calc.calculate_supertrend(df)
            df = self.golden_zone_calc.calculate_fibonacci_levels(df)
            df['rsi'] = self.calculate_rsi(df)
            
            # Get current values
            current_price = df['close'].iloc[-1]
            supertrend_direction = df['supertrend_direction'].iloc[-1]
            in_golden_zone = self.golden_zone_calc.is_in_golden_zone(df)
            rsi = df['rsi'].iloc[-1]
            volume_spike = self.calculate_volume_spike(df)
            
            # Signal logic
            signal = {
                'symbol': None,  # Will be set by caller
                'side': None,
                'confidence': 0.0,
                'entry_price': current_price,
                'stop_loss': 0.0,
                'take_profit': 0.0,
                'reason': [],
                'timestamp': datetime.now()
            }
            
            # Supertrend bullish signal
            if supertrend_direction == 1:
                signal['reason'].append("Supertrend bullish")
                signal['confidence'] += 30.0
                
                # Golden Zone confirmation
                if in_golden_zone:
                    signal['reason'].append("Price in Golden Zone (0.72-0.88)")
                    signal['confidence'] += 25.0
                
                # RSI confirmation
                if self.config.min_rsi <= rsi <= self.config.max_rsi:
                    signal['reason'].append(f"RSI in range ({rsi:.1f})")
                    signal['confidence'] += 15.0
                
                # Volume confirmation
                if volume_spike >= self.config.min_volume_spike:
                    signal['reason'].append(f"Volume spike ({volume_spike:.2f}x)")
                    signal['confidence'] += 20.0
                
                # Set signal
                if signal['confidence'] >= self.config.min_confidence:
                    signal['side'] = 'buy'
                    signal['stop_loss'] = current_price * (1 - self.config.stop_loss_pct / 100)
                    signal['take_profit'] = current_price * (1 + self.config.take_profit_pct / 100)
            
            # Supertrend bearish signal
            elif supertrend_direction == -1:
                signal['reason'].append("Supertrend bearish")
                signal['confidence'] += 30.0
                
                # Golden Zone confirmation
                if in_golden_zone:
                    signal['reason'].append("Price in Golden Zone (0.72-0.88)")
                    signal['confidence'] += 25.0
                
                # RSI confirmation
                if self.config.min_rsi <= rsi <= self.config.max_rsi:
                    signal['reason'].append(f"RSI in range ({rsi:.1f})")
                    signal['confidence'] += 15.0
                
                # Volume confirmation
                if volume_spike >= self.config.min_volume_spike:
                    signal['reason'].append(f"Volume spike ({volume_spike:.2f}x)")
                    signal['confidence'] += 20.0
                
                # Set signal
                if signal['confidence'] >= self.config.min_confidence:
                    signal['side'] = 'sell'
                    signal['stop_loss'] = current_price * (1 + self.config.stop_loss_pct / 100)
                    signal['take_profit'] = current_price * (1 - self.config.take_profit_pct / 100)
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            traceback.print_exc()
            return {
                'symbol': None,
                'side': None,
                'confidence': 0.0,
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'take_profit': 0.0,
                'reason': [f"Error: {e}"],
                'timestamp': datetime.now()
            }

class MonteCarloSupertrendOptimizer:
    """🎯 Monte Carlo optimizer for Supertrend Golden Zone strategy"""
    
    def __init__(self, strategy: SupertrendGoldenZoneStrategy):
        self.strategy = strategy
        self.best_params = None
        self.best_score = 0.0
        self.optimization_results = []
    
    def generate_random_params(self) -> StrategyConfig:
        """🎲 Generate random parameters for optimization"""
        return StrategyConfig(
            # Supertrend parameters
            supertrend_period=random.randint(7, 15),
            supertrend_multiplier=random.uniform(2.0, 4.0),
            supertrend_atr_period=random.randint(10, 20),
            
            # Golden Zone parameters
            golden_zone_start=random.uniform(0.70, 0.75),
            golden_zone_end=random.uniform(0.85, 0.90),
            zone_tolerance=random.uniform(0.01, 0.03),
            
            # Signal quality
            min_confidence=random.uniform(70.0, 85.0),
            min_volume_spike=random.uniform(1.3, 2.0),
            min_rsi=random.uniform(25.0, 35.0),
            max_rsi=random.uniform(65.0, 75.0),
            
            # Risk management
            stop_loss_pct=random.uniform(1.0, 1.5),
            take_profit_pct=random.uniform(1.8, 2.5),
            max_positions=random.randint(3, 6),
            position_size_pct=random.uniform(8.0, 15.0)
        )
    
    async def backtest_parameters(self, params: StrategyConfig, symbols: List[str], 
                                timeframe: str = '5m', limit: int = 500) -> Dict:
        """📊 Backtest parameters on historical data"""
        try:
            total_trades = 0
            winning_trades = 0
            total_profit = 0.0
            max_drawdown = 0.0
            current_drawdown = 0.0
            peak_balance = 1000.0  # Starting balance
            current_balance = 1000.0
            
            # Create strategy with test parameters
            test_strategy = SupertrendGoldenZoneStrategy(params)
            
            for symbol in symbols[:5]:  # Test on first 5 symbols
                try:
                    # Get historical data
                    ohlcv = await self.strategy.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Generate signals
                    for i in range(100, len(df)):  # Start from 100 to have enough data for indicators
                        test_df = df.iloc[:i+1].copy()
                        signal = test_strategy.generate_signal(test_df)
                        
                        if signal['side'] and signal['confidence'] >= params.min_confidence:
                            total_trades += 1
                            
                            # Simulate trade
                            entry_price = signal['entry_price']
                            stop_loss = signal['stop_loss']
                            take_profit = signal['take_profit']
                            
                            # Find exit price
                            exit_price = None
                            exit_reason = None
                            
                            for j in range(i+1, min(i+50, len(df))):  # Look ahead 50 candles max
                                current_price = df.iloc[j]['close']
                                
                                if signal['side'] == 'buy':
                                    if current_price <= stop_loss:
                                        exit_price = stop_loss
                                        exit_reason = 'stop_loss'
                                        break
                                    elif current_price >= take_profit:
                                        exit_price = take_profit
                                        exit_reason = 'take_profit'
                                        break
                                else:  # sell
                                    if current_price >= stop_loss:
                                        exit_price = stop_loss
                                        exit_reason = 'stop_loss'
                                        break
                                    elif current_price <= take_profit:
                                        exit_price = take_profit
                                        exit_reason = 'take_profit'
                                        break
                            
                            if exit_price:
                                # Calculate profit/loss
                                if signal['side'] == 'buy':
                                    profit_pct = (exit_price - entry_price) / entry_price * 100
                                else:
                                    profit_pct = (entry_price - exit_price) / entry_price * 100
                                
                                profit_amount = 1000 * (profit_pct / 100) * params.position_size_pct / 100
                                current_balance += profit_amount
                                total_profit += profit_amount
                                
                                if profit_amount > 0:
                                    winning_trades += 1
                                
                                # Update drawdown
                                if current_balance > peak_balance:
                                    peak_balance = current_balance
                                current_drawdown = (peak_balance - current_balance) / peak_balance * 100
                                max_drawdown = max(max_drawdown, current_drawdown)
                
                except Exception as e:
                    logger.warning(f"⚠️ Backtest error for {symbol}: {e}")
                    continue
            
            # Calculate metrics
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            profit_factor = abs(total_profit / (total_profit - (current_balance - 1000))) if total_profit != (current_balance - 1000) else 1
            sharpe_ratio = total_profit / max_drawdown if max_drawdown > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'final_balance': current_balance
            }
            
        except Exception as e:
            logger.error(f"❌ Backtest error: {e}")
            traceback.print_exc()
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'final_balance': 1000
            }
    
    def calculate_score(self, results: Dict) -> float:
        """📊 Calculate optimization score"""
        try:
            # Multi-factor scoring
            win_rate_score = results['win_rate'] * 0.3
            profit_factor_score = min(results['profit_factor'], 5.0) * 20  # Cap at 5.0
            sharpe_score = min(results['sharpe_ratio'], 10.0) * 10  # Cap at 10.0
            drawdown_penalty = results['max_drawdown'] * 0.5
            
            total_score = win_rate_score + profit_factor_score + sharpe_score - drawdown_penalty
            
            return total_score
            
        except Exception as e:
            logger.error(f"❌ Score calculation error: {e}")
            return 0.0
    
    async def run_optimization(self, symbols: List[str], iterations: int = 1000) -> Dict:
        """🎯 Run Monte Carlo optimization"""
        try:
            logger.info(f"🚀 Starting Monte Carlo optimization with {iterations} iterations")
            
            for i in range(iterations):
                if i % 100 == 0:
                    logger.info(f"📊 Optimization progress: {i}/{iterations}")
                
                # Generate random parameters
                params = self.generate_random_params()
                
                # Backtest parameters
                results = await self.backtest_parameters(params, symbols)
                
                # Calculate score
                score = self.calculate_score(results)
                
                # Store results
                self.optimization_results.append({
                    'params': params,
                    'results': results,
                    'score': score
                })
                
                # Update best parameters
                if score > self.best_score:
                    self.best_score = score
                    self.best_params = params
                    logger.success(f"🎯 New best score: {score:.2f} (Win Rate: {results['win_rate']:.1f}%, Profit: ${results['total_profit']:.2f})")
            
            # Sort results by score
            self.optimization_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.success(f"✅ Optimization complete! Best score: {self.best_score:.2f}")
            
            return {
                'best_params': self.best_params,
                'best_score': self.best_score,
                'best_results': self.optimization_results[0]['results'] if self.optimization_results else {},
                'all_results': self.optimization_results[:10]  # Top 10 results
            }
            
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
            traceback.print_exc()
            return {}

async def main():
    """🚀 Main function to run Supertrend Golden Zone strategy"""
    try:
        logger.info("🏔️ Starting Supertrend Golden Zone Strategy")
        
        # Initialize strategy
        config = StrategyConfig()
        strategy = SupertrendGoldenZoneStrategy(config)
        await strategy.initialize_exchange()
        
        # Get available symbols
        markets = await strategy.exchange.load_markets()
        symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol and 'SWAP' in markets[symbol]['type']]
        
        logger.info(f"📊 Found {len(symbols)} trading pairs")
        
        # Run Monte Carlo optimization
        optimizer = MonteCarloSupertrendOptimizer(strategy)
        optimization_results = await optimizer.run_optimization(symbols, iterations=500)
        
        if optimization_results:
            logger.success("🎯 Optimization Results:")
            logger.info(f"Best Win Rate: {optimization_results['best_results'].get('win_rate', 0):.1f}%")
            logger.info(f"Best Profit: ${optimization_results['best_results'].get('total_profit', 0):.2f}")
            logger.info(f"Best Sharpe Ratio: {optimization_results['best_results'].get('sharpe_ratio', 0):.2f}")
            logger.info(f"Max Drawdown: {optimization_results['best_results'].get('max_drawdown', 0):.1f}%")
        
        # Close exchange connection
        await strategy.exchange.close()
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 