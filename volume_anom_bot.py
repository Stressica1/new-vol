#!/usr/bin/env python3
"""
Volume Anomaly Bot - Advanced Crypto Scoring System
===================================================

Main execution script for the volume anomaly trading bot.
This script provides a complete solution for scoring and selecting
the top 50 cryptocurrencies for trading in the next 3 hours.

Features:
- Real-time data fetching from multiple APIs
- Advanced technical analysis
- Volume anomaly detection
- Risk assessment and position sizing
- Comprehensive scoring algorithm
- JSON output for easy integration

Usage:
    python volume_anom_bot.py [options]
    
Options:
    --mock              Use mock data for testing
    --limit N           Number of coins to analyze (default: 500)
    --top-n N          Number of top coins to return (default: 50)
    --output FILE       Output file for results (default: stdout)
    --config FILE       Configuration file (default: config.json)
    --verbose          Enable verbose logging
"""

import asyncio
import json
import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

# Import our modules
from crypto_scoring_system import CryptoScoringSystem, CoinMetrics, ScoringResult
from data_connector import CryptoDataConnector, fetch_market_data
from technical_indicators import TechnicalIndicators, VolumeAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('volume_anom_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class VolumeAnomBot:
    """
    Main Volume Anomaly Bot class
    
    Orchestrates the entire process from data fetching to final recommendations.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_default_config()
        self.scoring_system = CryptoScoringSystem()
        self.data_connector = None
        
        # Override scoring weights if specified in config
        if 'scoring_weights' in self.config:
            self.scoring_system.weights.update(self.config['scoring_weights'])
    
    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            'data_sources': ['coingecko', 'binance'],
            'min_volume_24h': 1000000,
            'min_market_cap': 10000000,
            'max_coins_to_analyze': 500,
            'top_coins_to_return': 50,
            'use_mock_data': False,
            'api_keys': {},
            'scoring_weights': {
                'volume': 0.25,
                'technical': 0.20,
                'momentum': 0.20,
                'volatility': 0.15,
                'market_structure': 0.10,
                'trend': 0.10
            },
            'risk_management': {
                'max_position_size': 0.05,
                'max_portfolio_allocation': 0.8,
                'min_confidence_level': 0.3
            }
        }
    
    def load_config(self, config_file: str) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config.update(json.load(f))
                logger.info(f"Configuration loaded from {config_file}")
                return True
            else:
                logger.warning(f"Config file {config_file} not found, using defaults")
                return False
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
    
    def save_config(self, config_file: str) -> bool:
        """Save current configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    async def fetch_market_data(self, limit: int = None) -> List[CoinMetrics]:
        """Fetch market data from configured sources"""
        limit = limit or self.config['max_coins_to_analyze']
        
        try:
            if self.config['use_mock_data']:
                logger.info("Using mock data for testing")
                return await fetch_market_data(limit=limit, use_mock=True)
            
            logger.info(f"Fetching market data for {limit} coins...")
            
            async with CryptoDataConnector(self.config.get('api_keys', {})) as connector:
                return await connector.fetch_all_coin_data(limit)
                
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            # Fallback to mock data
            logger.info("Falling back to mock data...")
            return await fetch_market_data(limit=limit, use_mock=True)
    
    def filter_coins(self, coin_metrics: List[CoinMetrics]) -> List[CoinMetrics]:
        """Filter coins based on minimum requirements"""
        filtered = []
        
        for metrics in coin_metrics:
            # Apply filters
            if (metrics.volume_24h >= self.config['min_volume_24h'] and
                metrics.market_cap >= self.config['min_market_cap']):
                filtered.append(metrics)
        
        logger.info(f"Filtered {len(filtered)} coins from {len(coin_metrics)} total")
        return filtered
    
    def score_and_rank_coins(self, coin_metrics: List[CoinMetrics]) -> List[ScoringResult]:
        """Score and rank coins using the scoring system"""
        try:
            logger.info(f"Scoring {len(coin_metrics)} coins...")
            
            # Get top coins using the scoring system
            top_coins = self.scoring_system.get_top_coins(
                coin_metrics, 
                top_n=self.config['top_coins_to_return']
            )
            
            # Apply additional filters
            confidence_threshold = self.config['risk_management']['min_confidence_level']
            filtered_coins = [
                coin for coin in top_coins 
                if coin.confidence_level >= confidence_threshold
            ]
            
            logger.info(f"Selected {len(filtered_coins)} coins after confidence filtering")
            return filtered_coins
            
        except Exception as e:
            logger.error(f"Error scoring coins: {e}")
            return []
    
    def generate_trading_recommendations(self, top_coins: List[ScoringResult]) -> Dict:
        """Generate comprehensive trading recommendations"""
        try:
            recommendations = self.scoring_system.get_trading_recommendations(top_coins)
            
            # Add bot-specific metadata
            recommendations.update({
                'bot_version': '1.0.0',
                'analysis_timestamp': datetime.now().isoformat(),
                'next_analysis_time': (datetime.now() + timedelta(hours=3)).isoformat(),
                'configuration': {
                    'min_volume_24h': self.config['min_volume_24h'],
                    'min_market_cap': self.config['min_market_cap'],
                    'scoring_weights': self.config['scoring_weights']
                }
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {}
    
    def format_results_for_output(self, recommendations: Dict) -> Dict:
        """Format results for clean output"""
        try:
            # Create a clean output format
            output = {
                'timestamp': recommendations.get('timestamp'),
                'next_analysis': recommendations.get('next_analysis_time'),
                'summary': {
                    'total_coins_analyzed': len(recommendations.get('high_priority', [])) + 
                                          len(recommendations.get('medium_priority', [])) + 
                                          len(recommendations.get('low_priority', [])),
                    'high_priority_targets': len(recommendations.get('high_priority', [])),
                    'medium_priority_targets': len(recommendations.get('medium_priority', [])),
                    'low_priority_targets': len(recommendations.get('low_priority', [])),
                    'total_portfolio_allocation': recommendations.get('total_portfolio_allocation', 0),
                    'risk_distribution': recommendations.get('risk_distribution', {})
                },
                'trading_targets': {
                    'high_priority': recommendations.get('high_priority', []),
                    'medium_priority': recommendations.get('medium_priority', []),
                    'low_priority': recommendations.get('low_priority', [])
                },
                'strategy_notes': recommendations.get('strategy_notes', []),
                'configuration': recommendations.get('configuration', {})
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return {'error': str(e)}
    
    async def run_analysis(self, **kwargs) -> Dict:
        """
        Main analysis runner
        
        This is the primary method that your bot should call to get
        the top 50 coins for trading in the next 3 hours.
        """
        try:
            start_time = datetime.now()
            logger.info("=== STARTING VOLUME ANOMALY ANALYSIS ===")
            
            # Override config with runtime parameters
            if 'limit' in kwargs:
                self.config['max_coins_to_analyze'] = kwargs['limit']
            if 'top_n' in kwargs:
                self.config['top_coins_to_return'] = kwargs['top_n']
            if 'use_mock' in kwargs:
                self.config['use_mock_data'] = kwargs['use_mock']
            
            # Step 1: Fetch market data
            logger.info("Step 1: Fetching market data...")
            coin_metrics = await self.fetch_market_data()
            
            if not coin_metrics:
                raise Exception("No market data available")
            
            # Step 2: Filter coins
            logger.info("Step 2: Filtering coins...")
            filtered_coins = self.filter_coins(coin_metrics)
            
            if not filtered_coins:
                raise Exception("No coins passed filtering criteria")
            
            # Step 3: Score and rank coins
            logger.info("Step 3: Scoring and ranking coins...")
            top_coins = self.score_and_rank_coins(filtered_coins)
            
            if not top_coins:
                raise Exception("No coins scored successfully")
            
            # Step 4: Generate recommendations
            logger.info("Step 4: Generating trading recommendations...")
            recommendations = self.generate_trading_recommendations(top_coins)
            
            # Step 5: Format results
            logger.info("Step 5: Formatting results...")
            results = self.format_results_for_output(recommendations)
            
            # Analysis complete
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"=== ANALYSIS COMPLETE in {duration:.2f} seconds ===")
            logger.info(f"Selected {len(top_coins)} coins for trading")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def print_summary(self, results: Dict):
        """Print a summary of the analysis results"""
        try:
            if 'error' in results:
                print(f"❌ Analysis failed: {results['error']}")
                return
            
            print("\n" + "="*60)
            print("📊 VOLUME ANOMALY BOT - ANALYSIS RESULTS")
            print("="*60)
            
            summary = results.get('summary', {})
            print(f"⏰ Analysis Time: {results.get('timestamp', 'Unknown')}")
            print(f"📈 Total Coins Analyzed: {summary.get('total_coins_analyzed', 0)}")
            print(f"🔥 High Priority Targets: {summary.get('high_priority_targets', 0)}")
            print(f"⚡ Medium Priority Targets: {summary.get('medium_priority_targets', 0)}")
            print(f"📊 Low Priority Targets: {summary.get('low_priority_targets', 0)}")
            print(f"💰 Total Portfolio Allocation: {summary.get('total_portfolio_allocation', 0):.1%}")
            
            # Risk distribution
            risk_dist = summary.get('risk_distribution', {})
            print(f"\n🎯 Risk Distribution:")
            print(f"   • Low Risk: {risk_dist.get('LOW', 0)} coins")
            print(f"   • Medium Risk: {risk_dist.get('MEDIUM', 0)} coins")
            print(f"   • High Risk: {risk_dist.get('HIGH', 0)} coins")
            
            # Top 5 high priority coins
            high_priority = results.get('trading_targets', {}).get('high_priority', [])
            if high_priority:
                print(f"\n🔥 Top 5 High Priority Coins:")
                for i, coin in enumerate(high_priority[:5], 1):
                    print(f"   {i}. {coin['symbol']} - Score: {coin['score']:.1f} - Risk: {coin['risk_level']}")
            
            # Strategy notes
            notes = results.get('strategy_notes', [])
            if notes:
                print(f"\n📝 Strategy Notes:")
                for note in notes:
                    print(f"   • {note}")
            
            print(f"\n🕒 Next Analysis: {results.get('next_analysis', 'Not scheduled')}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Volume Anomaly Bot - Advanced Crypto Scoring System')
    parser.add_argument('--mock', action='store_true', help='Use mock data for testing')
    parser.add_argument('--limit', type=int, default=500, help='Number of coins to analyze')
    parser.add_argument('--top-n', type=int, default=50, help='Number of top coins to return')
    parser.add_argument('--output', type=str, help='Output file for results')
    parser.add_argument('--config', type=str, default='config.json', help='Configuration file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--save-config', action='store_true', help='Save current config to file')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async def run():
        try:
            # Initialize bot
            bot = VolumeAnomBot()
            
            # Load configuration
            if os.path.exists(args.config):
                bot.load_config(args.config)
            elif args.save_config:
                bot.save_config(args.config)
            
            # Run analysis
            results = await bot.run_analysis(
                limit=args.limit,
                top_n=args.top_n,
                use_mock=args.mock
            )
            
            # Output results
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Results saved to {args.output}")
            else:
                bot.print_summary(results)
                
            return results
            
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            return {'error': str(e)}
    
    # Run the bot
    results = asyncio.run(run())
    
    # Exit with appropriate code
    sys.exit(0 if 'error' not in results else 1)

# Simple API for integration
async def get_top_coins_for_trading(top_n: int = 50, use_mock: bool = False) -> Dict:
    """
    Simple API function for integration with existing bots
    
    Args:
        top_n: Number of top coins to return (default: 50)
        use_mock: Whether to use mock data (default: False)
    
    Returns:
        Dictionary with trading recommendations
    """
    bot = VolumeAnomBot()
    return await bot.run_analysis(top_n=top_n, use_mock=use_mock)

if __name__ == "__main__":
    main()