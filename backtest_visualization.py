#!/usr/bin/env python3
"""
Volume Anomaly Backtest Visualization System
Advanced visualization and analysis of backtest results
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

class BacktestVisualizer:
    """Advanced visualization for backtest results"""
    
    def __init__(self, results_file: str = 'backtest_results.json'):
        self.results_file = results_file
        self.results = None
        self.load_results()
    
    def load_results(self):
        """Load backtest results from JSON file"""
        try:
            with open(self.results_file, 'r') as f:
                self.results = json.load(f)
            print(f"✅ Loaded backtest results from {self.results_file}")
        except FileNotFoundError:
            print(f"❌ Results file {self.results_file} not found. Run backtest first.")
            return
        except Exception as e:
            print(f"❌ Error loading results: {e}")
            return
    
    def create_equity_curve(self):
        """Create equity curve visualization"""
        if not self.results:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('📈 Volume Anomaly Strategy - Equity Curve Analysis', fontsize=16, fontweight='bold')
        
        # Create sample equity curve (since we don't have timestamps in results)
        trades = self.results['trade_log']
        if not trades:
            print("❌ No trades found for visualization")
            return
        
        # Calculate cumulative P&L
        cumulative_pnl = []
        running_pnl = 1000  # Initial balance
        
        for trade in trades:
            running_pnl += trade['pnl']
            cumulative_pnl.append(running_pnl)
        
        # Plot equity curve
        ax1.plot(range(len(cumulative_pnl)), cumulative_pnl, 
                color='#00ff88', linewidth=2, label='Portfolio Value')
        ax1.axhline(y=1000, color='#ff6b6b', linestyle='--', alpha=0.7, label='Initial Balance')
        ax1.fill_between(range(len(cumulative_pnl)), cumulative_pnl, 1000, 
                        alpha=0.3, color='#00ff88')
        ax1.set_title('💰 Portfolio Value Over Time', fontsize=14)
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Portfolio Value (USDT)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot drawdown
        peak = np.maximum.accumulate(cumulative_pnl)
        drawdown = (peak - cumulative_pnl) / peak * 100
        
        ax2.fill_between(range(len(drawdown)), drawdown, 0, 
                        color='#ff6b6b', alpha=0.7, label='Drawdown')
        ax2.set_title('📉 Drawdown Analysis', fontsize=14)
        ax2.set_xlabel('Trade Number')
        ax2.set_ylabel('Drawdown (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('equity_curve.png', dpi=300, bbox_inches='tight', facecolor='black')
        plt.show()
    
    def create_performance_dashboard(self):
        """Create comprehensive performance dashboard"""
        if not self.results:
            return
        
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('🎯 Volume Anomaly Strategy - Performance Dashboard', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 1. Key Metrics
        ax1 = fig.add_subplot(gs[0, :2])
        metrics = self.results['summary']
        
        metric_names = ['Total P&L', 'Win Rate', 'Total Trades', 'Max Drawdown', 'Sharpe Ratio']
        metric_values = [
            f"${metrics['total_pnl']:.2f} ({metrics['total_pnl_percentage']:.1f}%)",
            f"{metrics['win_rate']:.1f}%",
            f"{metrics['total_trades']}",
            f"{metrics['max_drawdown']:.1f}%",
            f"{metrics['sharpe_ratio']:.3f}"
        ]
        
        colors = ['#00ff88' if metrics['total_pnl'] > 0 else '#ff6b6b', 
                 '#00ff88' if metrics['win_rate'] > 50 else '#ff6b6b',
                 '#4ecdc4', '#ff6b6b', '#ffd93d']
        
        bars = ax1.barh(metric_names, [abs(float(v.split()[0].replace('$', '').replace('%', ''))) 
                                      for v in metric_values], color=colors, alpha=0.8)
        ax1.set_title('📊 Key Performance Metrics', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, metric_values)):
            ax1.text(bar.get_width() + bar.get_width()*0.01, bar.get_y() + bar.get_height()/2, 
                    value, ha='left', va='center', fontweight='bold')
        
        ax1.set_xlabel('Value')
        
        # 2. Timeframe Performance
        ax2 = fig.add_subplot(gs[0, 2:])
        tf_data = self.results['timeframe_performance']
        
        if tf_data:
            timeframes = list(tf_data.keys())
            pnls = [tf_data[tf]['pnl'] for tf in timeframes]
            win_rates = [tf_data[tf]['win_rate'] for tf in timeframes]
            
            x = np.arange(len(timeframes))
            width = 0.35
            
            ax2_twin = ax2.twinx()
            bars1 = ax2.bar(x - width/2, pnls, width, label='P&L (USDT)', 
                           color='#00ff88', alpha=0.8)
            bars2 = ax2_twin.bar(x + width/2, win_rates, width, label='Win Rate (%)', 
                               color='#4ecdc4', alpha=0.8)
            
            ax2.set_title('⏱️ Timeframe Performance', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Timeframe')
            ax2.set_ylabel('P&L (USDT)', color='#00ff88')
            ax2_twin.set_ylabel('Win Rate (%)', color='#4ecdc4')
            ax2.set_xticks(x)
            ax2.set_xticklabels(timeframes)
            
            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${height:.1f}', ha='center', va='bottom', fontweight='bold')
            
            for bar in bars2:
                height = bar.get_height()
                ax2_twin.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                            f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 3. Trade Distribution
        ax3 = fig.add_subplot(gs[1, :2])
        trades = self.results['trade_log']
        
        if trades:
            pnls = [trade['pnl'] for trade in trades]
            winning_pnls = [p for p in pnls if p > 0]
            losing_pnls = [p for p in pnls if p < 0]
            
            ax3.hist(winning_pnls, bins=20, alpha=0.7, color='#00ff88', 
                    label=f'Winning Trades ({len(winning_pnls)})', density=True)
            ax3.hist(losing_pnls, bins=20, alpha=0.7, color='#ff6b6b', 
                    label=f'Losing Trades ({len(losing_pnls)})', density=True)
            
            ax3.axvline(x=0, color='white', linestyle='--', alpha=0.7)
            ax3.set_title('📊 Trade P&L Distribution', fontsize=14, fontweight='bold')
            ax3.set_xlabel('P&L (USDT)')
            ax3.set_ylabel('Density')
            ax3.legend()
        
        # 4. Trade Duration Analysis
        ax4 = fig.add_subplot(gs[1, 2:])
        if trades:
            durations = [trade['duration_minutes'] for trade in trades]
            
            ax4.hist(durations, bins=30, color='#ffd93d', alpha=0.8, edgecolor='black')
            ax4.axvline(x=np.mean(durations), color='#ff6b6b', linestyle='--', 
                       linewidth=2, label=f'Average: {np.mean(durations):.1f} min')
            ax4.set_title('⏱️ Trade Duration Distribution', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Duration (minutes)')
            ax4.set_ylabel('Frequency')
            ax4.legend()
        
        # 5. Symbol Performance
        ax5 = fig.add_subplot(gs[2, :2])
        if trades:
            symbol_pnl = {}
            for trade in trades:
                symbol = trade['symbol']
                if symbol not in symbol_pnl:
                    symbol_pnl[symbol] = 0
                symbol_pnl[symbol] += trade['pnl']
            
            symbols = list(symbol_pnl.keys())[:10]  # Top 10 symbols
            pnls = [symbol_pnl[s] for s in symbols]
            
            colors = ['#00ff88' if p > 0 else '#ff6b6b' for p in pnls]
            bars = ax5.bar(symbols, pnls, color=colors, alpha=0.8)
            ax5.set_title('💰 Symbol Performance (Top 10)', fontsize=14, fontweight='bold')
            ax5.set_xlabel('Symbol')
            ax5.set_ylabel('P&L (USDT)')
            ax5.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 6. Risk Metrics
        ax6 = fig.add_subplot(gs[2, 2:])
        if trades:
            # Calculate risk metrics
            pnls = [trade['pnl'] for trade in trades]
            
            risk_metrics = {
                'Profit Factor': sum(p for p in pnls if p > 0) / abs(sum(p for p in pnls if p < 0)) if any(p < 0 for p in pnls) else float('inf'),
                'Average Win': np.mean([p for p in pnls if p > 0]) if any(p > 0 for p in pnls) else 0,
                'Average Loss': np.mean([p for p in pnls if p < 0]) if any(p < 0 for p in pnls) else 0,
                'Largest Win': max(pnls) if pnls else 0,
                'Largest Loss': min(pnls) if pnls else 0
            }
            
            labels = list(risk_metrics.keys())
            values = list(risk_metrics.values())
            
            # Create table
            table_data = [[label, f"${value:.2f}" if 'Factor' not in label else f"{value:.2f}"] 
                         for label, value in risk_metrics.items()]
            
            ax6.axis('tight')
            ax6.axis('off')
            table = ax6.table(cellText=table_data, 
                            colLabels=['Metric', 'Value'],
                            cellLoc='center',
                            loc='center',
                            colWidths=[0.6, 0.4])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)
            
            # Style the table
            for i in range(len(table_data) + 1):
                for j in range(2):
                    cell = table[(i, j)]
                    if i == 0:  # Header
                        cell.set_facecolor('#4ecdc4')
                        cell.set_text_props(weight='bold')
                    else:
                        cell.set_facecolor('#2d3748')
                        if j == 1 and '$' in cell.get_text().get_text():
                            value = float(cell.get_text().get_text().replace('$', ''))
                            if value > 0:
                                cell.set_facecolor('#1a4d3a')
                            elif value < 0:
                                cell.set_facecolor('#4d1a1a')
            
            ax6.set_title('⚠️ Risk Metrics', fontsize=14, fontweight='bold')
        
        plt.savefig('performance_dashboard.png', dpi=300, bbox_inches='tight', facecolor='black')
        plt.show()
    
    def create_trade_analysis(self):
        """Create detailed trade analysis"""
        if not self.results:
            return
        
        trades = self.results['trade_log']
        if not trades:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🔍 Detailed Trade Analysis', fontsize=16, fontweight='bold')
        
        # 1. P&L over time
        cumulative_pnl = np.cumsum([trade['pnl'] for trade in trades])
        ax1.plot(range(len(cumulative_pnl)), cumulative_pnl, 
                color='#00ff88', linewidth=2, marker='o', markersize=3)
        ax1.axhline(y=0, color='white', linestyle='--', alpha=0.5)
        ax1.set_title('📈 Cumulative P&L Over Trades')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Cumulative P&L (USDT)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Win/Loss streaks
        results = [1 if trade['pnl'] > 0 else 0 for trade in trades]
        streaks = []
        current_streak = 1
        
        for i in range(1, len(results)):
            if results[i] == results[i-1]:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        streaks.append(current_streak)
        
        ax2.hist(streaks, bins=min(20, len(set(streaks))), color='#4ecdc4', alpha=0.8)
        ax2.set_title('🔄 Win/Loss Streak Distribution')
        ax2.set_xlabel('Streak Length')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # 3. Entry vs Exit analysis
        entry_prices = [trade['entry_price'] for trade in trades]
        exit_prices = [trade['exit_price'] for trade in trades]
        
        ax3.scatter(entry_prices, exit_prices, 
                   c=[trade['pnl'] for trade in trades], 
                   cmap='RdYlGn', alpha=0.7, s=50)
        
        # Add diagonal line
        min_price = min(min(entry_prices), min(exit_prices))
        max_price = max(max(entry_prices), max(exit_prices))
        ax3.plot([min_price, max_price], [min_price, max_price], 
                'white', linestyle='--', alpha=0.5)
        
        ax3.set_title('💹 Entry vs Exit Price Analysis')
        ax3.set_xlabel('Entry Price')
        ax3.set_ylabel('Exit Price')
        ax3.grid(True, alpha=0.3)
        
        # 4. Signal strength vs Performance
        signal_strengths = [trade['signal_strength'] for trade in trades]
        pnls = [trade['pnl'] for trade in trades]
        
        ax4.scatter(signal_strengths, pnls, alpha=0.7, s=50, color='#ffd93d')
        ax4.axhline(y=0, color='white', linestyle='--', alpha=0.5)
        ax4.set_title('⚡ Signal Strength vs Trade Performance')
        ax4.set_xlabel('Signal Strength')
        ax4.set_ylabel('Trade P&L (USDT)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('trade_analysis.png', dpi=300, bbox_inches='tight', facecolor='black')
        plt.show()
    
    def generate_report(self):
        """Generate comprehensive backtest report"""
        if not self.results:
            return
        
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE VOLUME ANOMALY STRATEGY BACKTEST REPORT")
        print("="*100)
        
        # Summary
        summary = self.results['summary']
        print(f"\n🎯 STRATEGY OVERVIEW:")
        print(f"   • Strategy: Volume Anomaly Detection with Maximum Leverage")
        print(f"   • Timeframes: 30s, 1m, 3m, 5m")
        print(f"   • Leverage: 20x")
        print(f"   • Period: 7 days")
        print(f"   • Initial Balance: ${summary['initial_balance']:,.2f}")
        
        print(f"\n💰 PERFORMANCE SUMMARY:")
        print(f"   • Final Balance: ${summary['final_balance']:,.2f}")
        print(f"   • Total P&L: ${summary['total_pnl']:,.2f} ({summary['total_pnl_percentage']:.2f}%)")
        print(f"   • Win Rate: {summary['win_rate']:.2f}%")
        print(f"   • Total Trades: {summary['total_trades']}")
        print(f"   • Max Drawdown: {summary['max_drawdown']:.2f}%")
        print(f"   • Sharpe Ratio: {summary['sharpe_ratio']:.3f}")
        
        # Timeframe analysis
        print(f"\n⏱️ TIMEFRAME ANALYSIS:")
        tf_data = self.results['timeframe_performance']
        for tf, data in tf_data.items():
            print(f"   • {tf}: {data['trades']} trades, ${data['pnl']:,.2f} P&L, {data['win_rate']:.1f}% win rate")
        
        # Trade analysis
        trades = self.results['trade_log']
        if trades:
            winning_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] < 0]
            
            print(f"\n📈 TRADE ANALYSIS:")
            print(f"   • Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(trades)*100:.1f}%)")
            print(f"   • Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(trades)*100:.1f}%)")
            
            if winning_trades:
                avg_win = np.mean([t['pnl'] for t in winning_trades])
                print(f"   • Average Win: ${avg_win:.2f}")
            
            if losing_trades:
                avg_loss = np.mean([t['pnl'] for t in losing_trades])
                print(f"   • Average Loss: ${avg_loss:.2f}")
            
            print(f"   • Best Trade: ${max(t['pnl'] for t in trades):.2f}")
            print(f"   • Worst Trade: ${min(t['pnl'] for t in trades):.2f}")
            
            avg_duration = np.mean([t['duration_minutes'] for t in trades])
            print(f"   • Average Trade Duration: {avg_duration:.1f} minutes")
        
        # Risk analysis
        print(f"\n⚠️ RISK ANALYSIS:")
        if trades:
            pnls = [t['pnl'] for t in trades]
            winning_pnls = [p for p in pnls if p > 0]
            losing_pnls = [p for p in pnls if p < 0]
            
            if winning_pnls and losing_pnls:
                profit_factor = sum(winning_pnls) / abs(sum(losing_pnls))
                print(f"   • Profit Factor: {profit_factor:.2f}")
            
            print(f"   • Risk-Reward Ratio: {abs(np.mean(winning_pnls)/np.mean(losing_pnls)):.2f}" if winning_pnls and losing_pnls else "   • Risk-Reward Ratio: N/A")
            print(f"   • Maximum Consecutive Losses: {self.calculate_max_consecutive_losses(trades)}")
        
        print("\n" + "="*100)
        print("📊 All visualizations saved as PNG files")
        print("📁 Detailed results saved in backtest_results.json")
        print("="*100)
    
    def calculate_max_consecutive_losses(self, trades):
        """Calculate maximum consecutive losses"""
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if trade['pnl'] < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def run_all_visualizations(self):
        """Run all visualization methods"""
        if not self.results:
            print("❌ No results to visualize. Run backtest first.")
            return
        
        print("🎨 Generating visualizations...")
        
        try:
            self.create_equity_curve()
            print("✅ Equity curve created")
            
            self.create_performance_dashboard()
            print("✅ Performance dashboard created")
            
            self.create_trade_analysis()
            print("✅ Trade analysis created")
            
            self.generate_report()
            print("✅ Comprehensive report generated")
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")

if __name__ == "__main__":
    visualizer = BacktestVisualizer()
    visualizer.run_all_visualizations() 