import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoreCategory(Enum):
    """Categories for different scoring components"""
    VOLUME = "volume"
    TECHNICAL = "technical"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    MARKET_STRUCTURE = "market_structure"
    TREND = "trend"

@dataclass
class CoinMetrics:
    """Data structure for coin metrics"""
    symbol: str
    price: float
    volume_24h: float
    volume_7d_avg: float
    market_cap: float
    price_change_24h: float
    price_change_7d: float
    high_24h: float
    low_24h: float
    rsi: float
    macd: float
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
    ema_12: float
    ema_26: float
    sma_50: float
    sma_200: float
    atr: float
    timestamp: datetime

@dataclass
class ScoringResult:
    """Result of scoring calculation"""
    symbol: str
    total_score: float
    category_scores: Dict[ScoreCategory, float]
    confidence_level: float
    trading_signals: List[str]
    risk_level: str
    recommended_position_size: float

class CryptoScoringSystem:
    """Advanced crypto scoring system for volume anomaly trading bot"""
    
    def __init__(self):
        self.weights = {
            ScoreCategory.VOLUME: 0.25,        # High weight for volume anomaly bot
            ScoreCategory.TECHNICAL: 0.20,     # Technical indicators
            ScoreCategory.MOMENTUM: 0.20,      # Price momentum
            ScoreCategory.VOLATILITY: 0.15,    # Volatility analysis
            ScoreCategory.MARKET_STRUCTURE: 0.10,  # Market cap, liquidity
            ScoreCategory.TREND: 0.10          # Trend analysis
        }
        
        # Minimum requirements for trading
        self.min_volume_24h = 1000000  # $1M minimum daily volume
        self.min_market_cap = 10000000  # $10M minimum market cap
        self.max_volatility_threshold = 0.15  # 15% max volatility for risk management
        
    def calculate_volume_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate volume-based score (most important for volume anomaly bot)
        
        Factors:
        - Volume anomaly (current vs average)
        - Volume consistency
        - Volume trend
        """
        try:
            # Volume anomaly ratio
            volume_ratio = metrics.volume_24h / max(metrics.volume_7d_avg, 1)
            
            # Score based on volume anomaly (1.5x to 5x average is optimal)
            if volume_ratio >= 5.0:
                volume_anomaly_score = 90  # Extreme volume spike
            elif volume_ratio >= 3.0:
                volume_anomaly_score = 95  # High volume anomaly (best)
            elif volume_ratio >= 2.0:
                volume_anomaly_score = 85  # Good volume anomaly
            elif volume_ratio >= 1.5:
                volume_anomaly_score = 70  # Moderate volume increase
            elif volume_ratio >= 1.0:
                volume_anomaly_score = 50  # Normal volume
            else:
                volume_anomaly_score = 20  # Low volume (risky)
                
            # Absolute volume check
            if metrics.volume_24h < self.min_volume_24h:
                volume_anomaly_score *= 0.5  # Penalize low absolute volume
                
            # Volume consistency bonus
            consistency_bonus = min(20, metrics.volume_24h / metrics.volume_7d_avg * 5)
            
            total_score = min(100, volume_anomaly_score + consistency_bonus)
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating volume score for {metrics.symbol}: {e}")
            return 0.0
    
    def calculate_technical_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate technical indicators score
        
        Factors:
        - RSI (Relative Strength Index)
        - MACD
        - Bollinger Bands position
        """
        try:
            score = 0.0
            
            # RSI Score (30-70 range is optimal for trading)
            if 35 <= metrics.rsi <= 65:
                rsi_score = 100  # Optimal range
            elif 30 <= metrics.rsi <= 35 or 65 <= metrics.rsi <= 70:
                rsi_score = 80   # Good range
            elif 25 <= metrics.rsi <= 30 or 70 <= metrics.rsi <= 75:
                rsi_score = 60   # Acceptable range
            else:
                rsi_score = 30   # Overbought/oversold (risky)
                
            # MACD Score
            macd_score = 50  # Default neutral
            if metrics.macd > metrics.macd_signal:
                if metrics.macd > 0:
                    macd_score = 85  # Bullish momentum
                else:
                    macd_score = 70  # Recovering from bearish
            else:
                if metrics.macd < 0:
                    macd_score = 25  # Bearish momentum
                else:
                    macd_score = 40  # Weakening bullish momentum
                    
            # Bollinger Bands Score
            bb_position = (metrics.price - metrics.bollinger_lower) / (metrics.bollinger_upper - metrics.bollinger_lower)
            
            if 0.2 <= bb_position <= 0.8:
                bb_score = 90  # Good position within bands
            elif 0.1 <= bb_position <= 0.2 or 0.8 <= bb_position <= 0.9:
                bb_score = 70  # Near bands but not touching
            else:
                bb_score = 40  # Near or touching bands (potential reversal)
                
            # Weighted technical score
            score = (rsi_score * 0.4 + macd_score * 0.35 + bb_score * 0.25)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {metrics.symbol}: {e}")
            return 0.0
    
    def calculate_momentum_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate momentum score based on price movements
        
        Factors:
        - Short-term momentum (24h)
        - Medium-term momentum (7d)
        - EMA crossovers
        """
        try:
            # Short-term momentum (24h)
            momentum_24h = metrics.price_change_24h
            if momentum_24h > 10:
                momentum_24h_score = 95
            elif momentum_24h > 5:
                momentum_24h_score = 85
            elif momentum_24h > 2:
                momentum_24h_score = 75
            elif momentum_24h > 0:
                momentum_24h_score = 60
            elif momentum_24h > -2:
                momentum_24h_score = 45
            elif momentum_24h > -5:
                momentum_24h_score = 30
            else:
                momentum_24h_score = 15
                
            # Medium-term momentum (7d)
            momentum_7d = metrics.price_change_7d
            if momentum_7d > 20:
                momentum_7d_score = 90
            elif momentum_7d > 10:
                momentum_7d_score = 80
            elif momentum_7d > 5:
                momentum_7d_score = 70
            elif momentum_7d > 0:
                momentum_7d_score = 55
            elif momentum_7d > -5:
                momentum_7d_score = 40
            else:
                momentum_7d_score = 20
                
            # EMA crossover signals
            ema_score = 50  # Default neutral
            if metrics.ema_12 > metrics.ema_26:
                if metrics.price > metrics.ema_12:
                    ema_score = 85  # Strong bullish signal
                else:
                    ema_score = 70  # Moderate bullish signal
            else:
                if metrics.price < metrics.ema_12:
                    ema_score = 25  # Bearish signal
                else:
                    ema_score = 40  # Weak/mixed signal
                    
            # Weighted momentum score
            score = (momentum_24h_score * 0.4 + momentum_7d_score * 0.3 + ema_score * 0.3)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating momentum score for {metrics.symbol}: {e}")
            return 0.0
    
    def calculate_volatility_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate volatility score (optimal volatility for trading)
        
        Factors:
        - ATR (Average True Range)
        - 24h price range
        - Volatility sustainability
        """
        try:
            # Calculate 24h volatility
            volatility_24h = (metrics.high_24h - metrics.low_24h) / metrics.price
            
            # Optimal volatility range for trading (3-12%)
            if 0.03 <= volatility_24h <= 0.12:
                volatility_score = 90  # Optimal volatility
            elif 0.02 <= volatility_24h <= 0.15:
                volatility_score = 75  # Good volatility
            elif 0.01 <= volatility_24h <= 0.20:
                volatility_score = 60  # Acceptable volatility
            else:
                volatility_score = 30  # Too low or too high volatility
                
            # ATR normalization
            atr_normalized = metrics.atr / metrics.price
            if 0.02 <= atr_normalized <= 0.08:
                atr_score = 85
            elif 0.01 <= atr_normalized <= 0.12:
                atr_score = 70
            else:
                atr_score = 40
                
            # Combine volatility metrics
            score = (volatility_score * 0.6 + atr_score * 0.4)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating volatility score for {metrics.symbol}: {e}")
            return 0.0
    
    def calculate_market_structure_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate market structure score
        
        Factors:
        - Market cap adequacy
        - Liquidity indicators
        - Price stability
        """
        try:
            # Market cap score
            if metrics.market_cap >= 1e9:  # $1B+
                market_cap_score = 95
            elif metrics.market_cap >= 500e6:  # $500M+
                market_cap_score = 85
            elif metrics.market_cap >= 100e6:  # $100M+
                market_cap_score = 75
            elif metrics.market_cap >= 50e6:   # $50M+
                market_cap_score = 60
            elif metrics.market_cap >= self.min_market_cap:  # $10M+
                market_cap_score = 45
            else:
                market_cap_score = 20  # Too small
                
            # Liquidity score (volume to market cap ratio)
            liquidity_ratio = metrics.volume_24h / metrics.market_cap
            if liquidity_ratio >= 0.1:
                liquidity_score = 95  # Excellent liquidity
            elif liquidity_ratio >= 0.05:
                liquidity_score = 85  # Good liquidity
            elif liquidity_ratio >= 0.02:
                liquidity_score = 70  # Acceptable liquidity
            else:
                liquidity_score = 40  # Poor liquidity
                
            # Combine market structure metrics
            score = (market_cap_score * 0.5 + liquidity_score * 0.5)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating market structure score for {metrics.symbol}: {e}")
            return 0.0
    
    def calculate_trend_score(self, metrics: CoinMetrics) -> float:
        """
        Calculate trend score based on moving averages
        
        Factors:
        - Price vs SMA50/SMA200
        - Moving average alignment
        - Trend strength
        """
        try:
            # Price vs moving averages
            if metrics.price > metrics.sma_50 > metrics.sma_200:
                trend_score = 90  # Strong uptrend
            elif metrics.price > metrics.sma_50:
                trend_score = 70  # Moderate uptrend
            elif metrics.price > metrics.sma_200:
                trend_score = 60  # Weak uptrend
            elif metrics.sma_50 > metrics.sma_200:
                trend_score = 40  # Mixed signals
            else:
                trend_score = 25  # Downtrend
                
            # Moving average convergence/divergence
            ma_convergence = abs(metrics.sma_50 - metrics.sma_200) / metrics.price
            if ma_convergence > 0.05:
                trend_strength = 85  # Strong trend
            elif ma_convergence > 0.02:
                trend_strength = 70  # Moderate trend
            else:
                trend_strength = 50  # Weak trend
                
            # Combine trend metrics
            score = (trend_score * 0.7 + trend_strength * 0.3)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating trend score for {metrics.symbol}: {e}")
            return 0.0
    
    def generate_trading_signals(self, metrics: CoinMetrics, category_scores: Dict[ScoreCategory, float]) -> List[str]:
        """Generate trading signals based on scoring results"""
        signals = []
        
        try:
            # Volume signals
            if category_scores[ScoreCategory.VOLUME] >= 80:
                signals.append("STRONG_VOLUME_ANOMALY")
            elif category_scores[ScoreCategory.VOLUME] >= 60:
                signals.append("MODERATE_VOLUME_INCREASE")
                
            # Technical signals
            if metrics.rsi <= 30:
                signals.append("OVERSOLD_RSI")
            elif metrics.rsi >= 70:
                signals.append("OVERBOUGHT_RSI")
                
            if metrics.macd > metrics.macd_signal:
                signals.append("BULLISH_MACD")
                
            # Momentum signals
            if category_scores[ScoreCategory.MOMENTUM] >= 75:
                signals.append("STRONG_MOMENTUM")
            elif category_scores[ScoreCategory.MOMENTUM] <= 30:
                signals.append("WEAK_MOMENTUM")
                
            # Trend signals
            if metrics.price > metrics.sma_50 > metrics.sma_200:
                signals.append("UPTREND_CONFIRMED")
                
            # Volatility signals
            volatility_24h = (metrics.high_24h - metrics.low_24h) / metrics.price
            if volatility_24h > 0.15:
                signals.append("HIGH_VOLATILITY")
                
        except Exception as e:
            logger.error(f"Error generating trading signals for {metrics.symbol}: {e}")
            
        return signals
    
    def calculate_risk_level(self, total_score: float, metrics: CoinMetrics) -> str:
        """Calculate risk level based on score and metrics"""
        try:
            volatility_24h = (metrics.high_24h - metrics.low_24h) / metrics.price
            
            if total_score >= 80 and volatility_24h <= 0.10:
                return "LOW"
            elif total_score >= 60 and volatility_24h <= 0.15:
                return "MEDIUM"
            elif total_score >= 40:
                return "HIGH"
            else:
                return "VERY_HIGH"
                
        except Exception as e:
            logger.error(f"Error calculating risk level for {metrics.symbol}: {e}")
            return "VERY_HIGH"
    
    def calculate_position_size(self, total_score: float, risk_level: str) -> float:
        """Calculate recommended position size as percentage of portfolio"""
        try:
            base_size = min(0.05, total_score / 2000)  # Max 5% per position
            
            risk_multipliers = {
                "LOW": 1.0,
                "MEDIUM": 0.7,
                "HIGH": 0.4,
                "VERY_HIGH": 0.2
            }
            
            return base_size * risk_multipliers.get(risk_level, 0.2)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.01  # Conservative default
    
    def score_coin(self, metrics: CoinMetrics) -> ScoringResult:
        """
        Score a single coin using all metrics
        
        Returns:
            ScoringResult with total score and category breakdown
        """
        try:
            # Calculate category scores
            category_scores = {
                ScoreCategory.VOLUME: self.calculate_volume_score(metrics),
                ScoreCategory.TECHNICAL: self.calculate_technical_score(metrics),
                ScoreCategory.MOMENTUM: self.calculate_momentum_score(metrics),
                ScoreCategory.VOLATILITY: self.calculate_volatility_score(metrics),
                ScoreCategory.MARKET_STRUCTURE: self.calculate_market_structure_score(metrics),
                ScoreCategory.TREND: self.calculate_trend_score(metrics)
            }
            
            # Calculate weighted total score
            total_score = sum(
                score * self.weights[category] 
                for category, score in category_scores.items()
            )
            
            # Apply minimum requirements penalty
            if metrics.volume_24h < self.min_volume_24h:
                total_score *= 0.5
            if metrics.market_cap < self.min_market_cap:
                total_score *= 0.7
                
            # Calculate confidence level
            score_variance = np.var(list(category_scores.values()))
            confidence_level = max(0.1, 1 - (score_variance / 10000))
            
            # Generate trading signals
            trading_signals = self.generate_trading_signals(metrics, category_scores)
            
            # Calculate risk level
            risk_level = self.calculate_risk_level(total_score, metrics)
            
            # Calculate recommended position size
            position_size = self.calculate_position_size(total_score, risk_level)
            
            return ScoringResult(
                symbol=metrics.symbol,
                total_score=total_score,
                category_scores=category_scores,
                confidence_level=confidence_level,
                trading_signals=trading_signals,
                risk_level=risk_level,
                recommended_position_size=position_size
            )
            
        except Exception as e:
            logger.error(f"Error scoring coin {metrics.symbol}: {e}")
            return ScoringResult(
                symbol=metrics.symbol,
                total_score=0.0,
                category_scores={cat: 0.0 for cat in ScoreCategory},
                confidence_level=0.0,
                trading_signals=[],
                risk_level="VERY_HIGH",
                recommended_position_size=0.0
            )
    
    def get_top_coins(self, coin_metrics_list: List[CoinMetrics], top_n: int = 50) -> List[ScoringResult]:
        """
        Score all coins and return top N for trading
        
        Args:
            coin_metrics_list: List of coin metrics
            top_n: Number of top coins to return (default 50)
            
        Returns:
            List of top scoring coins sorted by total score
        """
        try:
            # Score all coins
            scoring_results = []
            for metrics in coin_metrics_list:
                result = self.score_coin(metrics)
                scoring_results.append(result)
            
            # Sort by total score (descending)
            scoring_results.sort(key=lambda x: x.total_score, reverse=True)
            
            # Filter out coins with very low scores or high risk
            filtered_results = [
                result for result in scoring_results 
                if result.total_score >= 30 and result.risk_level != "VERY_HIGH"
            ]
            
            # Return top N coins
            return filtered_results[:top_n]
            
        except Exception as e:
            logger.error(f"Error getting top coins: {e}")
            return []
    
    def get_trading_recommendations(self, top_coins: List[ScoringResult]) -> Dict:
        """
        Generate trading recommendations for the next 3 hours
        
        Returns:
            Dictionary with trading recommendations
        """
        try:
            recommendations = {
                "timestamp": datetime.now().isoformat(),
                "total_coins": len(top_coins),
                "high_priority": [],
                "medium_priority": [],
                "low_priority": [],
                "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY_HIGH": 0},
                "total_portfolio_allocation": 0.0,
                "strategy_notes": []
            }
            
            for coin in top_coins:
                coin_data = {
                    "symbol": coin.symbol,
                    "score": coin.total_score,
                    "confidence": coin.confidence_level,
                    "position_size": coin.recommended_position_size,
                    "risk_level": coin.risk_level,
                    "signals": coin.trading_signals,
                    "category_scores": {cat.value: score for cat, score in coin.category_scores.items()}
                }
                
                # Categorize by score
                if coin.total_score >= 70:
                    recommendations["high_priority"].append(coin_data)
                elif coin.total_score >= 50:
                    recommendations["medium_priority"].append(coin_data)
                else:
                    recommendations["low_priority"].append(coin_data)
                
                # Update risk distribution
                recommendations["risk_distribution"][coin.risk_level] += 1
                
                # Update total allocation
                recommendations["total_portfolio_allocation"] += coin.recommended_position_size
            
            # Generate strategy notes
            if len(recommendations["high_priority"]) > 20:
                recommendations["strategy_notes"].append("High number of high-priority targets - consider increasing position sizes")
            
            if recommendations["risk_distribution"]["HIGH"] > 10:
                recommendations["strategy_notes"].append("High risk exposure - consider reducing position sizes")
                
            if recommendations["total_portfolio_allocation"] > 0.8:
                recommendations["strategy_notes"].append("High portfolio allocation - consider scaling down positions")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating trading recommendations: {e}")
            return {}

# Example usage and testing
def create_sample_metrics() -> List[CoinMetrics]:
    """Create sample coin metrics for testing"""
    return [
        CoinMetrics(
            symbol="BTC",
            price=45000.0,
            volume_24h=25000000000,
            volume_7d_avg=20000000000,
            market_cap=850000000000,
            price_change_24h=2.5,
            price_change_7d=8.2,
            high_24h=46000.0,
            low_24h=44000.0,
            rsi=58.5,
            macd=120.5,
            macd_signal=115.2,
            bollinger_upper=47000.0,
            bollinger_lower=43000.0,
            ema_12=45200.0,
            ema_26=44800.0,
            sma_50=44500.0,
            sma_200=42000.0,
            atr=1800.0,
            timestamp=datetime.now()
        ),
        CoinMetrics(
            symbol="ETH",
            price=3200.0,
            volume_24h=15000000000,
            volume_7d_avg=8000000000,
            market_cap=380000000000,
            price_change_24h=4.2,
            price_change_7d=12.8,
            high_24h=3300.0,
            low_24h=3150.0,
            rsi=65.2,
            macd=25.8,
            macd_signal=22.1,
            bollinger_upper=3400.0,
            bollinger_lower=3000.0,
            ema_12=3220.0,
            ema_26=3180.0,
            sma_50=3100.0,
            sma_200=2900.0,
            atr=120.0,
            timestamp=datetime.now()
        )
    ]

if __name__ == "__main__":
    # Example usage
    scoring_system = CryptoScoringSystem()
    sample_metrics = create_sample_metrics()
    
    # Get top coins
    top_coins = scoring_system.get_top_coins(sample_metrics, top_n=2)
    
    # Generate recommendations
    recommendations = scoring_system.get_trading_recommendations(top_coins)
    
    print("=== CRYPTO SCORING SYSTEM RESULTS ===")
    print(f"Total coins analyzed: {len(sample_metrics)}")
    print(f"Top coins selected: {len(top_coins)}")
    
    for coin in top_coins:
        print(f"\n{coin.symbol}:")
        print(f"  Total Score: {coin.total_score:.2f}")
        print(f"  Risk Level: {coin.risk_level}")
        print(f"  Position Size: {coin.recommended_position_size:.3f}")
        print(f"  Signals: {coin.trading_signals}")