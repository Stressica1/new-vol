#!/usr/bin/env python3
"""
🏔️ ALPINE TRADING BOT - COMPREHENSIVE SIGNAL ANALYSIS
Validate Monte Carlo parameters with actual trading pairs and detailed analysis
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from loguru import logger
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Configure logging
logger.add("signal_analysis.log", rotation="1 day", retention="7 days")

@dataclass
class SignalResult:
    """📊 Signal result tracking"""
    symbol: str
    side: str
    entry_price: float
    entry_time: datetime
    volume_spike: float
    rsi_value: float
    confidence: float
    trend_strength: float
    exit_price: float = 0.0
    exit_time: datetime = None
    pnl: float = 0.0
    pnl_percent: float = 0.0
    status: str = "OPEN"
    exit_reason: str = ""

class SignalAnalyzer:
    """🔬 Comprehensive signal analyzer for Alpine Trading Bot"""
    
    def __init__(self):
        # Monte Carlo Optimized Parameters
        self.volume_spike_threshold = 2.0
        self.volume_sma_period = 20
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.rsi_trend_threshold = 50
        self.confidence_threshold = 72
        self.stop_loss_pct = 1.25
        self.take_profit_pct = 1.5
        self.leverage = 25
        
        # Pullback Detection
        self.pullback_threshold = 1.2
        self.momentum_threshold = 0.5
        self.volume_pullback_threshold = 1.3
        
        # Trend Analysis
        self.sma_short = 8
        self.sma_long = 25
        
        # Initialize exchange
        self.exchange = ccxt.bitget({
            'apiKey': 'bg_33b25387b50e7f874c18ddf34f5cbb14',
            'secret': '4b3cab211d44a155c5cc63dd025fad43025d09155ee6eef3769ef2f6f85c9715',
            'password': '22672267',
            'options': {
                'defaultType': 'swap',
                'defaultMarginMode': 'cross'
            }
        })
        
        # Results tracking
        self.signals = []
        self.wins = 0
        self.losses = 0
        self.total_trades = 0
        self.total_pnl = 0.0
        
        logger.info("🔬 Signal Analyzer initialized with Monte Carlo parameters")

    def fetch_market_data(self, symbol: str, hours: int = 24) -> pd.DataFrame:
        """📊 Fetch market data for analysis"""
        try:
            # Calculate timeframes
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Fetch 5-minute candles
            timeframe = '5m'
            limit = (hours * 60) // 5
            
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, 
                timeframe, 
                limit=limit,
                since=int(start_time.timestamp() * 1000)
            )
            
            if not ohlcv:
                return pd.DataFrame()
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """📈 Calculate technical indicators"""
        try:
            # Volume SMA
            df['volume_sma'] = df['volume'].rolling(window=self.volume_sma_period).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Moving Averages
            df['sma_short'] = df['close'].rolling(window=self.sma_short).mean()
            df['sma_long'] = df['close'].rolling(window=self.sma_long).mean()
            
            # Volume spike
            df['volume_spike'] = df['volume'] / df['volume_sma']
            
            # Price momentum
            df['momentum'] = df['close'].pct_change()
            
            # High/Low tracking
            df['high_20'] = df['high'].rolling(window=20).max()
            df['low_20'] = df['low'].rolling(window=20).min()
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Indicator calculation failed: {e}")
            return df

    def detect_pullback(self, df: pd.DataFrame, current_idx: int) -> bool:
        """🔍 Detect pullback to avoid false signals"""
        try:
            if current_idx < 5:
                return False
                
            current_price = df.iloc[current_idx]['close']
            recent_high = df.iloc[current_idx-5:current_idx]['high'].max()
            
            pullback_pct = ((recent_high - current_price) / recent_high) * 100
            
            if pullback_pct > self.pullback_threshold:
                current_momentum = df.iloc[current_idx]['momentum']
                avg_momentum = df.iloc[current_idx-3:current_idx]['momentum'].mean()
                current_volume_spike = df.iloc[current_idx]['volume_spike']
                
                if (current_momentum < avg_momentum and 
                    current_volume_spike < self.volume_pullback_threshold):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Pullback detection failed: {e}")
            return False

    def calculate_trend_strength(self, df: pd.DataFrame, current_idx: int) -> float:
        """📊 Calculate trend strength for signal confirmation"""
        try:
            if current_idx < self.sma_long:
                return 0.0
                
            current_price = df.iloc[current_idx]['close']
            sma_short = df.iloc[current_idx]['sma_short']
            sma_long = df.iloc[current_idx]['sma_long']
            
            price_vs_short = (current_price - sma_short) / sma_short
            price_vs_long = (current_price - sma_long) / sma_long
            trend_direction = 1 if sma_short > sma_long else -1
            
            trend_strength = (
                abs(price_vs_short) * 0.4 +
                abs(price_vs_long) * 0.3 +
                abs(trend_direction) * 0.3
            ) * 100
            
            return min(trend_strength, 100.0)
            
        except Exception as e:
            logger.error(f"❌ Trend strength calculation failed: {e}")
            return 0.0

    def generate_signal(self, df: pd.DataFrame, current_idx: int) -> Dict:
        """🎯 Generate trading signal with Monte Carlo optimized parameters"""
        try:
            if current_idx < 25:
                return None
                
            current_data = df.iloc[current_idx]
            prev_data = df.iloc[current_idx-1]
            
            # Check for pullback
            if self.detect_pullback(df, current_idx):
                return None
            
            # Volume spike detection
            volume_spike = current_data['volume_spike']
            if volume_spike < self.volume_spike_threshold:
                return None
            
            # RSI conditions
            rsi = current_data['rsi']
            prev_rsi = prev_data['rsi']
            
            # Buy signal conditions
            buy_signal = (
                rsi > self.rsi_oversold and 
                rsi < self.rsi_overbought and
                rsi > prev_rsi and
                rsi > self.rsi_trend_threshold
            )
            
            # Sell signal conditions
            sell_signal = (
                rsi < self.rsi_overbought and
                rsi > self.rsi_oversold and
                rsi < prev_rsi and
                rsi < self.rsi_trend_threshold
            )
            
            if not (buy_signal or sell_signal):
                return None
            
            # Calculate trend strength
            trend_strength = self.calculate_trend_strength(df, current_idx)
            
            # Calculate confidence score
            volume_score = min(volume_spike / 3.0, 1.0) * 30
            rsi_score = (abs(rsi - 50) / 50) * 25
            trend_score = (trend_strength / 100) * 25
            momentum_score = abs(current_data['momentum']) * 100 * 20
            
            confidence = volume_score + rsi_score + trend_score + momentum_score
            
            if confidence < self.confidence_threshold:
                return None
            
            side = 'buy' if buy_signal else 'sell'
            
            return {
                'symbol': 'TEST_SYMBOL',
                'side': side,
                'price': current_data['close'],
                'volume_spike': volume_spike,
                'rsi': rsi,
                'confidence': confidence,
                'trend_strength': trend_strength,
                'timestamp': current_data.name,
                'volume_score': volume_score,
                'rsi_score': rsi_score,
                'trend_score': trend_score,
                'momentum_score': momentum_score
            }
            
        except Exception as e:
            logger.error(f"❌ Signal generation failed: {e}")
            return None

    def simulate_trade(self, signal: Dict, df: pd.DataFrame, signal_idx: int) -> SignalResult:
        """💰 Simulate trade execution and track P&L"""
        try:
            entry_price = signal['price']
            entry_time = signal['timestamp']
            side = signal['side']
            
            # Calculate SL/TP levels
            if side == 'buy':
                sl_price = entry_price * (1 - self.stop_loss_pct / 100)
                tp_price = entry_price * (1 + self.take_profit_pct / 100)
            else:
                sl_price = entry_price * (1 + self.stop_loss_pct / 100)
                tp_price = entry_price * (1 - self.take_profit_pct / 100)
            
            # Track the trade through subsequent candles
            exit_price = entry_price
            exit_time = entry_time
            exit_reason = "OPEN"
            pnl = 0.0
            pnl_percent = 0.0
            
            for i in range(signal_idx + 1, len(df)):
                current_price = df.iloc[i]['close']
                current_time = df.index[i]
                
                if side == 'buy':
                    if current_price >= tp_price:
                        exit_price = tp_price
                        exit_time = current_time
                        exit_reason = "TAKE_PROFIT"
                        pnl = (tp_price - entry_price) / entry_price * 100
                        pnl_percent = pnl
                        break
                    elif current_price <= sl_price:
                        exit_price = sl_price
                        exit_time = current_time
                        exit_reason = "STOP_LOSS"
                        pnl = (sl_price - entry_price) / entry_price * 100
                        pnl_percent = pnl
                        break
                else:  # sell/short
                    if current_price <= tp_price:
                        exit_price = tp_price
                        exit_time = current_time
                        exit_reason = "TAKE_PROFIT"
                        pnl = (entry_price - tp_price) / entry_price * 100
                        pnl_percent = pnl
                        break
                    elif current_price >= sl_price:
                        exit_price = sl_price
                        exit_time = current_time
                        exit_reason = "STOP_LOSS"
                        pnl = (entry_price - sl_price) / entry_price * 100
                        pnl_percent = pnl
                        break
            
            # Create signal result
            signal_result = SignalResult(
                symbol=signal['symbol'],
                side=side,
                entry_price=entry_price,
                entry_time=entry_time,
                volume_spike=signal['volume_spike'],
                rsi_value=signal['rsi'],
                confidence=signal['confidence'],
                trend_strength=signal['trend_strength'],
                exit_price=exit_price,
                exit_time=exit_time,
                pnl=pnl,
                pnl_percent=pnl_percent,
                status="CLOSED" if exit_reason != "OPEN" else "OPEN",
                exit_reason=exit_reason
            )
            
            return signal_result
            
        except Exception as e:
            logger.error(f"❌ Trade simulation failed: {e}")
            return None

    def analyze_signals(self, symbols: List[str]) -> Dict:
        """🔬 Analyze signals across multiple symbols"""
        logger.info(f"🔬 Starting comprehensive signal analysis on {len(symbols)} symbols...")
        
        start_time = time.time()
        total_signals = 0
        valid_signals = 0
        
        for symbol in symbols:
            try:
                logger.info(f"📊 Analyzing {symbol}...")
                
                # Fetch market data
                df = self.fetch_market_data(symbol, hours=24)
                if df.empty:
                    continue
                
                # Calculate indicators
                df = self.calculate_indicators(df)
                if df.empty:
                    continue
                
                # Generate signals for each candle
                for i in range(25, len(df)):
                    signal = self.generate_signal(df, i)
                    
                    if signal:
                        total_signals += 1
                        signal['symbol'] = symbol
                        
                        # Simulate trade
                        signal_result = self.simulate_trade(signal, df, i)
                        
                        if signal_result and signal_result.status == "CLOSED":
                            valid_signals += 1
                            self.signals.append(signal_result)
                            
                            # Track results
                            if signal_result.pnl > 0:
                                self.wins += 1
                            else:
                                self.losses += 1
                            
                            self.total_pnl += signal_result.pnl
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Analysis failed for {symbol}: {e}")
                continue
        
        # Calculate final statistics
        execution_time = time.time() - start_time
        win_rate = (self.wins / valid_signals * 100) if valid_signals > 0 else 0
        avg_pnl = self.total_pnl / valid_signals if valid_signals > 0 else 0
        
        results = {
            'total_signals_generated': total_signals,
            'valid_signals': valid_signals,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'avg_pnl': avg_pnl,
            'execution_time': execution_time,
            'symbols_tested': len(symbols),
            'signals': self.signals
        }
        
        return results

    def print_detailed_results(self, results: Dict):
        """📊 Print detailed analysis results"""
        print("\n" + "="*100)
        print("🏔️ ALPINE TRADING BOT - COMPREHENSIVE SIGNAL ANALYSIS RESULTS")
        print("="*100)
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   ⏱️  Execution Time: {results['execution_time']:.2f} seconds")
        print(f"   📈 Symbols Tested: {results['symbols_tested']}")
        print(f"   🎯 Total Signals Generated: {results['total_signals_generated']}")
        print(f"   ✅ Valid Signals: {results['valid_signals']}")
        
        print(f"\n💰 TRADING PERFORMANCE:")
        print(f"   🏆 Wins: {results['wins']}")
        print(f"   ❌ Losses: {results['losses']}")
        print(f"   📈 Win Rate: {results['win_rate']:.2f}%")
        print(f"   💰 Total P&L: {results['total_pnl']:.2f}%")
        print(f"   📊 Average P&L per Trade: {results['avg_pnl']:.2f}%")
        
        print(f"\n🎯 MONTE CARLO PARAMETERS VALIDATION:")
        print(f"   📊 Volume Spike Threshold: {self.volume_spike_threshold}x")
        print(f"   📈 RSI Period: {self.rsi_period}")
        print(f"   🎯 Confidence Threshold: {self.confidence_threshold}%")
        print(f"   🛑 Stop Loss: {self.stop_loss_pct}%")
        print(f"   🎯 Take Profit: {self.take_profit_pct}%")
        print(f"   ⚡ Leverage: {self.leverage}x")
        
        if results['signals']:
            print(f"\n📋 DETAILED SIGNAL ANALYSIS (Last 15):")
            print(f"{'Symbol':<15} {'Side':<4} {'Entry':<10} {'Exit':<10} {'P&L%':<8} {'Conf%':<8} {'Volume':<8} {'RSI':<6} {'Status':<12}")
            print("-" * 100)
            
            for signal in results['signals'][-15:]:
                status_emoji = "✅" if signal.pnl > 0 else "❌"
                print(f"{signal.symbol:<15} {signal.side.upper():<4} "
                      f"${signal.entry_price:<9.4f} ${signal.exit_price:<9.4f} "
                      f"{signal.pnl:<7.2f}% {signal.confidence:<7.1f}% "
                      f"{signal.volume_spike:<7.1f}x {signal.rsi_value:<5.1f} "
                      f"{status_emoji} {signal.exit_reason}")
        
        print("\n" + "="*100)

def main():
    """🚀 Main analysis execution"""
    try:
        # Initialize analyzer
        analyzer = SignalAnalyzer()
        
        # Test symbols (actual trading pairs from our bot)
        test_symbols = [
            'BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'ADA/USDT:USDT',
            'AVAX/USDT:USDT', 'DOT/USDT:USDT', 'LINK/USDT:USDT', 'ATOM/USDT:USDT',
            'LTC/USDT:USDT', 'BCH/USDT:USDT', 'XRP/USDT:USDT', 'BNB/USDT:USDT',
            'DOGE/USDT:USDT', 'SHIB/USDT:USDT', 'TRX/USDT:USDT', 'NEAR/USDT:USDT',
            'ALGO/USDT:USDT', 'IOTA/USDT:USDT', 'ROSE/USDT:USDT', 'HBAR/USDT:USDT'
        ]
        
        logger.info("🚀 Starting comprehensive signal analysis...")
        
        # Run analysis
        results = analyzer.analyze_signals(test_symbols)
        
        # Print results
        analyzer.print_detailed_results(results)
        
        # Save detailed results
        with open("signal_analysis_results.txt", "w") as f:
            f.write("ALPINE TRADING BOT - SIGNAL ANALYSIS RESULTS\n")
            f.write("="*50 + "\n")
            f.write(f"Win Rate: {results['win_rate']:.2f}%\n")
            f.write(f"Total P&L: {results['total_pnl']:.2f}%\n")
            f.write(f"Valid Signals: {results['valid_signals']}\n")
            f.write(f"Execution Time: {results['execution_time']:.2f}s\n")
        
        logger.success("✅ Signal analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 