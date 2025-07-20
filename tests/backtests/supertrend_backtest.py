#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - SUPERTREND GOLDEN ZONE BACKTESTING
🎯 Comprehensive backtesting with Monte Carlo optimization
🚀 Advanced analysis and performance metrics
"""

import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from loguru import logger
import traceback
from supertrend_golden_zone_strategy import (
    SupertrendGoldenZoneStrategy, 
    StrategyConfig, 
    MonteCarloSupertrendOptimizer
)
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

# UNIFIED LOGGING SETUP
logger.remove()
logger.add("logs/supertrend_backtest.log", rotation="1 day", retention="7 days", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

class SupertrendGoldenZoneBacktester:
    """🎯 Comprehensive backtesting system for Supertrend Golden Zone strategy"""
    
    def __init__(self):
        self.exchange = None
        self.results = []
        self.optimization_results = {}
        
    async def initialize_exchange(self):
        """🔌 Initialize Bitget exchange"""
        try:
            self.exchange = ccxt.bitget({
                'apiKey': os.getenv("BITGET_API_KEY"),
                'secret': os.getenv("BITGET_SECRET_KEY"),
                'password': os.getenv("BITGET_PASSPHRASE"),
                'sandbox': False,
                'options': {
                    'defaultType': 'swap',
                    'defaultMarginMode': 'cross'
                }
            })
            await self.exchange.load_markets()
            logger.success("✅ Exchange initialized for backtesting")
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[str]:
        """📊 Get available trading pairs"""
        try:
            markets = await self.exchange.load_markets()
            logger.info(f"📊 Total markets loaded: {len(markets)}")
            
            # Debug: Print some market examples
            sample_markets = list(markets.keys())[:10]
            logger.info(f"📊 Sample markets: {sample_markets}")
            
            symbols = [
                symbol for symbol in markets.keys() 
                if '/USDT' in symbol and markets[symbol].get('type') == 'swap'
            ]
            
            logger.info(f"📊 Found {len(symbols)} USDT swap pairs")
            
            # If no swap pairs found, try alternative filtering
            if not symbols:
                symbols = [
                    symbol for symbol in markets.keys() 
                    if '/USDT' in symbol and 'SWAP' in symbol.upper()
                ]
                logger.info(f"📊 Found {len(symbols)} USDT pairs with SWAP in name")
            
            # If still no symbols, try basic USDT filtering
            if not symbols:
                symbols = [
                    symbol for symbol in markets.keys() 
                    if '/USDT' in symbol
                ]
                logger.info(f"📊 Found {len(symbols)} basic USDT pairs")
            
            return symbols
            
        except Exception as e:
            logger.error(f"❌ Error getting trading pairs: {e}")
            traceback.print_exc()
            return []
    
    async def get_historical_data(self, symbol: str, timeframe: str = '5m', limit: int = 1000) -> pd.DataFrame:
        """📊 Get historical OHLCV data"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_performance_metrics(self, trades: List[Dict]) -> Dict:
        """📊 Calculate comprehensive performance metrics"""
        try:
            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'total_profit': 0.0,
                    'total_loss': 0.0,
                    'net_profit': 0.0,
                    'profit_factor': 0.0,
                    'average_win': 0.0,
                    'average_loss': 0.0,
                    'largest_win': 0.0,
                    'largest_loss': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_consecutive_wins': 0,
                    'max_consecutive_losses': 0
                }
            
            # Calculate basic metrics
            total_trades = len(trades)
            winning_trades = [t for t in trades if t['profit'] > 0]
            losing_trades = [t for t in trades if t['profit'] <= 0]
            
            win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
            
            total_profit = sum(t['profit'] for t in winning_trades)
            total_loss = abs(sum(t['profit'] for t in losing_trades))
            net_profit = total_profit - total_loss
            
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            
            average_win = total_profit / len(winning_trades) if winning_trades else 0
            average_loss = total_loss / len(losing_trades) if losing_trades else 0
            
            largest_win = max(t['profit'] for t in trades) if trades else 0
            largest_loss = min(t['profit'] for t in trades) if trades else 0
            
            # Calculate drawdown
            balance = 1000.0  # Starting balance
            peak_balance = balance
            max_drawdown = 0.0
            
            for trade in trades:
                balance += trade['profit']
                if balance > peak_balance:
                    peak_balance = balance
                drawdown = (peak_balance - balance) / peak_balance * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate Sharpe ratio (simplified)
            returns = [t['profit'] / 1000.0 for t in trades]  # Normalize to starting balance
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Calculate consecutive wins/losses
            consecutive_wins = 0
            consecutive_losses = 0
            max_consecutive_wins = 0
            max_consecutive_losses = 0
            
            for trade in trades:
                if trade['profit'] > 0:
                    consecutive_wins += 1
                    consecutive_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                else:
                    consecutive_losses += 1
                    consecutive_wins = 0
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            
            return {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_loss': total_loss,
                'net_profit': net_profit,
                'profit_factor': profit_factor,
                'average_win': average_win,
                'average_loss': average_loss,
                'largest_win': largest_win,
                'largest_loss': largest_loss,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'max_consecutive_wins': max_consecutive_wins,
                'max_consecutive_losses': max_consecutive_losses
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {e}")
            return {}
    
    async def run_single_backtest(self, symbol: str, config: StrategyConfig, 
                                 timeframe: str = '5m', limit: int = 1000) -> Dict:
        """📊 Run single symbol backtest"""
        try:
            logger.info(f"📊 Running backtest for {symbol}")
            
            # Get historical data
            df = await self.get_historical_data(symbol, timeframe, limit)
            if df.empty:
                return {'symbol': symbol, 'trades': [], 'metrics': {}}
            
            # Initialize strategy
            strategy = SupertrendGoldenZoneStrategy(config)
            
            # Simulate trading
            trades = []
            position = None
            
            for i in range(100, len(df)):  # Start from 100 to have enough data for indicators
                test_df = df.iloc[:i+1].copy()
                signal = strategy.generate_signal(test_df)
                
                # Check for entry signal
                if signal['side'] and signal['confidence'] >= config.min_confidence and position is None:
                    position = {
                        'symbol': symbol,
                        'side': signal['side'],
                        'entry_price': signal['entry_price'],
                        'entry_time': test_df.index[-1],
                        'stop_loss': signal['stop_loss'],
                        'take_profit': signal['take_profit'],
                        'confidence': signal['confidence']
                    }
                
                # Check for exit
                elif position:
                    current_price = test_df['close'].iloc[-1]
                    exit_price = None
                    exit_reason = None
                    
                    if position['side'] == 'buy':
                        if current_price <= position['stop_loss']:
                            exit_price = position['stop_loss']
                            exit_reason = 'stop_loss'
                        elif current_price >= position['take_profit']:
                            exit_price = position['take_profit']
                            exit_reason = 'take_profit'
                    else:  # sell
                        if current_price >= position['stop_loss']:
                            exit_price = position['stop_loss']
                            exit_reason = 'stop_loss'
                        elif current_price <= position['take_profit']:
                            exit_price = position['take_profit']
                            exit_reason = 'take_profit'
                    
                    if exit_price:
                        # Calculate profit/loss
                        if position['side'] == 'buy':
                            profit_pct = (exit_price - position['entry_price']) / position['entry_price'] * 100
                        else:
                            profit_pct = (position['entry_price'] - exit_price) / position['entry_price'] * 100
                        
                        profit_amount = 1000 * (profit_pct / 100) * config.position_size_pct / 100
                        
                        trade = {
                            'symbol': symbol,
                            'side': position['side'],
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'entry_time': position['entry_time'],
                            'exit_time': test_df.index[-1],
                            'profit': profit_amount,
                            'profit_pct': profit_pct,
                            'exit_reason': exit_reason,
                            'confidence': position['confidence']
                        }
                        
                        trades.append(trade)
                        position = None
            
            # Calculate metrics
            metrics = self.calculate_performance_metrics(trades)
            
            return {
                'symbol': symbol,
                'trades': trades,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Backtest error for {symbol}: {e}")
            return {'symbol': symbol, 'trades': [], 'metrics': {}}
    
    async def run_comprehensive_backtest(self, symbols: List[str], config: StrategyConfig) -> Dict:
        """📊 Run comprehensive backtest across multiple symbols"""
        try:
            logger.info(f"🚀 Starting comprehensive backtest for {len(symbols)} symbols")
            
            all_trades = []
            symbol_results = []
            
            for symbol in symbols[:10]:  # Test on first 10 symbols
                result = await self.run_single_backtest(symbol, config)
                symbol_results.append(result)
                all_trades.extend(result['trades'])
            
            # Calculate overall metrics
            overall_metrics = self.calculate_performance_metrics(all_trades)
            
            return {
                'symbol_results': symbol_results,
                'overall_metrics': overall_metrics,
                'total_trades': len(all_trades),
                'config': config
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive backtest error: {e}")
            return {}
    
    async def run_monte_carlo_optimization(self, symbols: List[str], iterations: int = 500) -> Dict:
        """🎯 Run Monte Carlo optimization"""
        try:
            logger.info(f"🎯 Starting Monte Carlo optimization with {iterations} iterations")
            
            # Initialize strategy and optimizer
            base_config = StrategyConfig()
            strategy = SupertrendGoldenZoneStrategy(base_config)
            optimizer = MonteCarloSupertrendOptimizer(strategy)
            
            # Run optimization
            optimization_results = await optimizer.run_optimization(symbols, iterations)
            
            if optimization_results:
                logger.success("🎯 Optimization Results:")
                logger.info(f"Best Win Rate: {optimization_results['best_results'].get('win_rate', 0):.1f}%")
                logger.info(f"Best Profit: ${optimization_results['best_results'].get('total_profit', 0):.2f}")
                logger.info(f"Best Sharpe Ratio: {optimization_results['best_results'].get('sharpe_ratio', 0):.2f}")
                logger.info(f"Max Drawdown: {optimization_results['best_results'].get('max_drawdown', 0):.1f}%")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Monte Carlo optimization error: {e}")
            return {}
    
    def save_results(self, results: Dict, filename: str = None):
        """💾 Save backtest results to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"supertrend_golden_zone_results_{timestamp}.json"
            
            # Convert dataclass to dict for JSON serialization
            if 'config' in results:
                results['config'] = {
                    'supertrend_period': results['config'].supertrend_period,
                    'supertrend_multiplier': results['config'].supertrend_multiplier,
                    'supertrend_atr_period': results['config'].supertrend_atr_period,
                    'golden_zone_start': results['config'].golden_zone_start,
                    'golden_zone_end': results['config'].golden_zone_end,
                    'zone_tolerance': results['config'].zone_tolerance,
                    'min_confidence': results['config'].min_confidence,
                    'min_volume_spike': results['config'].min_volume_spike,
                    'min_rsi': results['config'].min_rsi,
                    'max_rsi': results['config'].max_rsi,
                    'stop_loss_pct': results['config'].stop_loss_pct,
                    'take_profit_pct': results['config'].take_profit_pct,
                    'max_positions': results['config'].max_positions,
                    'position_size_pct': results['config'].position_size_pct
                }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.success(f"💾 Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    def print_results_summary(self, results: Dict):
        """📊 Print comprehensive results summary"""
        try:
            if not results:
                logger.warning("⚠️ No results to display")
                return
            
            print("\n" + "="*80)
            print("🏔️ SUPERTREND GOLDEN ZONE BACKTEST RESULTS")
            print("="*80)
            
            if 'overall_metrics' in results:
                metrics = results['overall_metrics']
                print(f"📊 Total Trades: {metrics.get('total_trades', 0)}")
                print(f"✅ Winning Trades: {metrics.get('winning_trades', 0)}")
                print(f"❌ Losing Trades: {metrics.get('losing_trades', 0)}")
                print(f"🎯 Win Rate: {metrics.get('win_rate', 0):.1f}%")
                print(f"💰 Total Profit: ${metrics.get('total_profit', 0):.2f}")
                print(f"💸 Total Loss: ${metrics.get('total_loss', 0):.2f}")
                print(f"📈 Net Profit: ${metrics.get('net_profit', 0):.2f}")
                print(f"📊 Profit Factor: {metrics.get('profit_factor', 0):.2f}")
                print(f"📉 Max Drawdown: {metrics.get('max_drawdown', 0):.1f}%")
                print(f"📊 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                print(f"🔥 Average Win: ${metrics.get('average_win', 0):.2f}")
                print(f"💧 Average Loss: ${metrics.get('average_loss', 0):.2f}")
                print(f"🚀 Largest Win: ${metrics.get('largest_win', 0):.2f}")
                print(f"💥 Largest Loss: ${metrics.get('largest_loss', 0):.2f}")
                print(f"🔥 Max Consecutive Wins: {metrics.get('max_consecutive_wins', 0)}")
                print(f"💥 Max Consecutive Losses: {metrics.get('max_consecutive_losses', 0)}")
            
            if 'config' in results:
                config = results['config']
                print("\n" + "-"*80)
                print("🎯 STRATEGY CONFIGURATION")
                print("-"*80)
                print(f"📊 Supertrend Period: {config.get('supertrend_period', 0)}")
                print(f"📊 Supertrend Multiplier: {config.get('supertrend_multiplier', 0):.2f}")
                print(f"📊 ATR Period: {config.get('supertrend_atr_period', 0)}")
                print(f"🎯 Golden Zone Start: {config.get('golden_zone_start', 0):.2f}")
                print(f"🎯 Golden Zone End: {config.get('golden_zone_end', 0):.2f}")
                print(f"🎯 Zone Tolerance: {config.get('zone_tolerance', 0):.2f}")
                print(f"📊 Min Confidence: {config.get('min_confidence', 0):.1f}%")
                print(f"📊 Min Volume Spike: {config.get('min_volume_spike', 0):.1f}x")
                print(f"📊 RSI Range: {config.get('min_rsi', 0):.1f} - {config.get('max_rsi', 0):.1f}")
                print(f"🛑 Stop Loss: {config.get('stop_loss_pct', 0):.2f}%")
                print(f"🎯 Take Profit: {config.get('take_profit_pct', 0):.2f}%")
                print(f"📊 Position Size: {config.get('position_size_pct', 0):.1f}%")
            
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"❌ Error printing results: {e}")

async def main():
    """🚀 Main function to run comprehensive backtesting"""
    try:
        logger.info("🏔️ Starting Supertrend Golden Zone Backtesting")
        
        # Initialize backtester
        backtester = SupertrendGoldenZoneBacktester()
        await backtester.initialize_exchange()
        
        # Get trading pairs
        symbols = await backtester.get_trading_pairs()
        if not symbols:
            logger.error("❌ No trading pairs found")
            logger.info("🔧 Trying to get basic market info...")
            
            # Try to get basic market info
            try:
                markets = await backtester.exchange.load_markets()
                logger.info(f"📊 Total markets available: {len(markets)}")
                
                # Show first 20 markets for debugging
                sample_markets = list(markets.keys())[:20]
                logger.info(f"📊 Sample markets: {sample_markets}")
                
                # Try to find any USDT pairs
                usdt_pairs = [s for s in markets.keys() if '/USDT' in s]
                logger.info(f"📊 USDT pairs found: {len(usdt_pairs)}")
                if usdt_pairs:
                    symbols = usdt_pairs[:10]  # Use first 10 for testing
                    logger.info(f"🎯 Using {len(symbols)} symbols for testing")
                else:
                    logger.error("❌ No USDT pairs found")
                    return
                    
            except Exception as e:
                logger.error(f"❌ Error getting market info: {e}")
                return
        
        # Run Monte Carlo optimization
        logger.info("🎯 Running Monte Carlo optimization...")
        optimization_results = await backtester.run_monte_carlo_optimization(symbols, iterations=300)
        
        if optimization_results and 'best_params' in optimization_results:
            # Run backtest with optimized parameters
            logger.info("📊 Running backtest with optimized parameters...")
            backtest_results = await backtester.run_comprehensive_backtest(symbols, optimization_results['best_params'])
            
            # Print results
            backtester.print_results_summary(backtest_results)
            
            # Save results
            backtester.save_results(backtest_results)
            
            # Save optimization results
            backtester.save_results(optimization_results, "supertrend_optimization_results.json")
        
        # Close exchange connection
        await backtester.exchange.close()
        
        logger.success("✅ Backtesting complete!")
        
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 