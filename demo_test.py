#!/usr/bin/env python3
"""
Demo test script for the Volume Anomaly Bot
This script demonstrates the key concepts without requiring external dependencies.
"""

import json
import random
from datetime import datetime
from typing import Dict, List

# Mock numpy functions for demonstration
def mean(values):
    return sum(values) / len(values) if values else 0

def std(values):
    if not values or len(values) < 2:
        return 0
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance ** 0.5

def random_normal(mean_val, std_val):
    # Simple Box-Muller transform
    import math
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean_val + z * std_val

# Mock data structures
class MockCoinMetrics:
    def __init__(self, **kwargs):
        self.symbol = kwargs.get('symbol', 'BTC')
        self.price = kwargs.get('price', 45000.0)
        self.volume_24h = kwargs.get('volume_24h', 25000000000)
        self.volume_7d_avg = kwargs.get('volume_7d_avg', 20000000000)
        self.market_cap = kwargs.get('market_cap', 850000000000)
        self.price_change_24h = kwargs.get('price_change_24h', 2.5)
        self.price_change_7d = kwargs.get('price_change_7d', 8.2)
        self.high_24h = kwargs.get('high_24h', 46000.0)
        self.low_24h = kwargs.get('low_24h', 44000.0)
        self.rsi = kwargs.get('rsi', 58.5)
        self.macd = kwargs.get('macd', 120.5)
        self.macd_signal = kwargs.get('macd_signal', 115.2)
        self.bollinger_upper = kwargs.get('bollinger_upper', 47000.0)
        self.bollinger_lower = kwargs.get('bollinger_lower', 43000.0)
        self.ema_12 = kwargs.get('ema_12', 45200.0)
        self.ema_26 = kwargs.get('ema_26', 44800.0)
        self.sma_50 = kwargs.get('sma_50', 44500.0)
        self.sma_200 = kwargs.get('sma_200', 42000.0)
        self.atr = kwargs.get('atr', 1800.0)
        self.timestamp = kwargs.get('timestamp', datetime.now())

class MockScoringSystem:
    """Simplified scoring system for demonstration"""
    
    def __init__(self):
        self.weights = {
            'volume': 0.25,
            'technical': 0.20,
            'momentum': 0.20,
            'volatility': 0.15,
            'market_structure': 0.10,
            'trend': 0.10
        }
        
        self.min_volume_24h = 1000000
        self.min_market_cap = 10000000
    
    def calculate_volume_score(self, metrics):
        """Calculate volume score"""
        volume_ratio = metrics.volume_24h / max(metrics.volume_7d_avg, 1)
        
        if volume_ratio >= 3.0:
            return 90
        elif volume_ratio >= 2.0:
            return 80
        elif volume_ratio >= 1.5:
            return 70
        elif volume_ratio >= 1.0:
            return 50
        else:
            return 30
    
    def calculate_technical_score(self, metrics):
        """Calculate technical score"""
        # RSI score
        if 35 <= metrics.rsi <= 65:
            rsi_score = 100
        elif 30 <= metrics.rsi <= 70:
            rsi_score = 80
        else:
            rsi_score = 40
        
        # MACD score
        macd_score = 80 if metrics.macd > metrics.macd_signal else 40
        
        # Bollinger Bands
        bb_position = (metrics.price - metrics.bollinger_lower) / (metrics.bollinger_upper - metrics.bollinger_lower)
        bb_score = 90 if 0.2 <= bb_position <= 0.8 else 50
        
        return (rsi_score * 0.4 + macd_score * 0.35 + bb_score * 0.25)
    
    def calculate_momentum_score(self, metrics):
        """Calculate momentum score"""
        if metrics.price_change_24h > 5:
            momentum_24h = 90
        elif metrics.price_change_24h > 0:
            momentum_24h = 70
        else:
            momentum_24h = 30
        
        if metrics.price_change_7d > 10:
            momentum_7d = 85
        elif metrics.price_change_7d > 0:
            momentum_7d = 65
        else:
            momentum_7d = 35
        
        return (momentum_24h * 0.6 + momentum_7d * 0.4)
    
    def calculate_volatility_score(self, metrics):
        """Calculate volatility score"""
        volatility = (metrics.high_24h - metrics.low_24h) / metrics.price
        
        if 0.03 <= volatility <= 0.12:
            return 90
        elif 0.02 <= volatility <= 0.15:
            return 75
        else:
            return 40
    
    def calculate_market_structure_score(self, metrics):
        """Calculate market structure score"""
        if metrics.market_cap >= 1e9:
            market_cap_score = 95
        elif metrics.market_cap >= 100e6:
            market_cap_score = 75
        else:
            market_cap_score = 45
        
        liquidity_ratio = metrics.volume_24h / metrics.market_cap
        liquidity_score = 90 if liquidity_ratio >= 0.05 else 60
        
        return (market_cap_score * 0.5 + liquidity_score * 0.5)
    
    def calculate_trend_score(self, metrics):
        """Calculate trend score"""
        if metrics.price > metrics.sma_50 > metrics.sma_200:
            return 90
        elif metrics.price > metrics.sma_50:
            return 70
        else:
            return 40
    
    def score_coin(self, metrics):
        """Score a single coin"""
        scores = {
            'volume': self.calculate_volume_score(metrics),
            'technical': self.calculate_technical_score(metrics),
            'momentum': self.calculate_momentum_score(metrics),
            'volatility': self.calculate_volatility_score(metrics),
            'market_structure': self.calculate_market_structure_score(metrics),
            'trend': self.calculate_trend_score(metrics)
        }
        
        total_score = sum(scores[cat] * self.weights[cat] for cat in scores)
        
        # Risk assessment
        volatility = (metrics.high_24h - metrics.low_24h) / metrics.price
        if total_score >= 80 and volatility <= 0.10:
            risk_level = "LOW"
        elif total_score >= 60 and volatility <= 0.15:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Position size calculation
        base_size = min(0.05, total_score / 2000)
        risk_multipliers = {"LOW": 1.0, "MEDIUM": 0.7, "HIGH": 0.4}
        position_size = base_size * risk_multipliers.get(risk_level, 0.2)
        
        return {
            'symbol': metrics.symbol,
            'score': total_score,
            'risk_level': risk_level,
            'position_size': position_size,
            'category_scores': scores,
            'signals': self.generate_signals(metrics, scores)
        }
    
    def generate_signals(self, metrics, scores):
        """Generate trading signals"""
        signals = []
        
        if scores['volume'] >= 80:
            signals.append("STRONG_VOLUME_ANOMALY")
        if metrics.rsi <= 30:
            signals.append("OVERSOLD_RSI")
        elif metrics.rsi >= 70:
            signals.append("OVERBOUGHT_RSI")
        if metrics.macd > metrics.macd_signal:
            signals.append("BULLISH_MACD")
        if metrics.price > metrics.sma_50 > metrics.sma_200:
            signals.append("UPTREND_CONFIRMED")
        
        return signals

def create_mock_coins(count=20):
    """Create mock cryptocurrency data"""
    coins = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE', 'AVAX', 'SHIB',
             'MATIC', 'UNI', 'LINK', 'ATOM', 'LTC', 'BCH', 'ALGO', 'XLM', 'VET', 'ICP']
    
    mock_coins = []
    for i in range(min(count, len(coins))):
        symbol = coins[i]
        base_price = random.uniform(0.1, 50000)
        
        # Create realistic volume anomaly scenarios
        volume_multiplier = random.choice([0.8, 1.2, 2.5, 4.0, 1.0, 1.5, 3.0])
        base_volume = random.uniform(10000000, 50000000000)
        
        metrics = MockCoinMetrics(
            symbol=symbol,
            price=base_price,
            volume_24h=base_volume * volume_multiplier,
            volume_7d_avg=base_volume,
            market_cap=random.uniform(50000000, 1000000000000),
            price_change_24h=random.uniform(-8, 12),
            price_change_7d=random.uniform(-15, 25),
            high_24h=base_price * random.uniform(1.02, 1.12),
            low_24h=base_price * random.uniform(0.88, 0.98),
            rsi=random.uniform(25, 75),
            macd=random.uniform(-50, 50),
            macd_signal=random.uniform(-45, 45),
            bollinger_upper=base_price * 1.1,
            bollinger_lower=base_price * 0.9,
            ema_12=base_price * random.uniform(0.98, 1.02),
            ema_26=base_price * random.uniform(0.96, 1.04),
            sma_50=base_price * random.uniform(0.90, 1.10),
            sma_200=base_price * random.uniform(0.80, 1.20),
            atr=base_price * random.uniform(0.02, 0.08)
        )
        
        mock_coins.append(metrics)
    
    return mock_coins

def run_demo():
    """Run the demonstration"""
    print("=" * 60)
    print("🚀 VOLUME ANOMALY BOT - DEMO TEST")
    print("=" * 60)
    
    # Create mock scoring system
    scoring_system = MockScoringSystem()
    
    # Create mock coin data
    print("\n📊 Creating mock cryptocurrency data...")
    coins = create_mock_coins(20)
    print(f"Created {len(coins)} mock coins")
    
    # Score coins
    print("\n🔍 Scoring coins...")
    scored_coins = []
    for coin in coins:
        score_result = scoring_system.score_coin(coin)
        scored_coins.append(score_result)
    
    # Sort by score
    scored_coins.sort(key=lambda x: x['score'], reverse=True)
    
    # Display results
    print("\n🏆 TOP 10 COINS FOR TRADING:")
    print("-" * 60)
    
    for i, coin in enumerate(scored_coins[:10], 1):
        print(f"{i:2d}. {coin['symbol']:>6} | Score: {coin['score']:5.1f} | Risk: {coin['risk_level']:>6} | Size: {coin['position_size']:5.3f}")
        if coin['signals']:
            print(f"     Signals: {', '.join(coin['signals'])}")
    
    # Summary statistics
    print("\n📈 ANALYSIS SUMMARY:")
    print(f"Total coins analyzed: {len(scored_coins)}")
    print(f"High-priority coins (score >= 70): {len([c for c in scored_coins if c['score'] >= 70])}")
    print(f"Medium-priority coins (score 50-70): {len([c for c in scored_coins if 50 <= c['score'] < 70])}")
    print(f"Low-priority coins (score < 50): {len([c for c in scored_coins if c['score'] < 50])}")
    
    # Risk distribution
    risk_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
    for coin in scored_coins:
        risk_counts[coin['risk_level']] += 1
    
    print(f"\n🎯 RISK DISTRIBUTION:")
    for risk, count in risk_counts.items():
        print(f"  {risk}: {count} coins")
    
    # Total allocation
    total_allocation = sum(coin['position_size'] for coin in scored_coins[:10])
    print(f"\n💰 TOTAL PORTFOLIO ALLOCATION: {total_allocation:.1%}")
    
    # Sample detailed analysis
    print(f"\n🔍 DETAILED ANALYSIS - {scored_coins[0]['symbol']}:")
    top_coin = scored_coins[0]
    print(f"  Overall Score: {top_coin['score']:.1f}")
    print(f"  Category Scores:")
    for category, score in top_coin['category_scores'].items():
        print(f"    {category.capitalize():15}: {score:5.1f}")
    print(f"  Risk Level: {top_coin['risk_level']}")
    print(f"  Position Size: {top_coin['position_size']:.3f} ({top_coin['position_size']*100:.1f}%)")
    print(f"  Trading Signals: {', '.join(top_coin['signals']) if top_coin['signals'] else 'None'}")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Create sample output JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_coins_analyzed': len(scored_coins),
        'top_10_coins': scored_coins[:10],
        'risk_distribution': risk_counts,
        'total_allocation': total_allocation,
        'strategy_notes': [
            f"Found {len([c for c in scored_coins if c['score'] >= 70])} high-priority targets",
            f"Total portfolio allocation: {total_allocation:.1%}",
            "Volume anomaly detection working properly"
        ]
    }
    
    print(f"\n📁 Sample JSON output saved to demo_output.json")
    with open('demo_output.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    return output

if __name__ == "__main__":
    run_demo()