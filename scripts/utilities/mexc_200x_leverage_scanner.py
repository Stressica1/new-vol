#!/usr/bin/env python3
"""
🔍 MEXC 200x Leverage Scanner
Find all MEXC Futures coins that offer 200x leverage
"""

import os
import asyncio
import ccxt
import pandas as pd
from datetime import datetime
from loguru import logger
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class MEXC200xLeverageScanner:
    """Scan MEXC Futures for all coins with 200x leverage"""
    
    def __init__(self):
        self.exchange = None
        self.results = []
        self.stats = {
            'total_pairs': 0,
            'pairs_with_200x': 0,
            'pairs_with_100x': 0,
            'pairs_with_50x': 0,
            'pairs_with_25x': 0,
            'pairs_with_10x': 0,
            'pairs_with_5x': 0,
            'pairs_with_1x': 0
        }
        
    async def setup_exchange(self):
        """Setup MEXC exchange connection"""
        try:
            # Use environment variables or default to public access
            api_key = os.getenv("MEXC_API_KEY", "")
            api_secret = os.getenv("MEXC_SECRET_KEY", "")
            
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap'  # Futures trading
                }
            })
            
            logger.info("🔌 Connecting to MEXC Futures...")
            self.exchange.load_markets()
            logger.success("✅ MEXC connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MEXC: {e}")
            raise
    
    async def scan_all_futures_pairs(self):
        """Scan all MEXC futures pairs for leverage information"""
        try:
            logger.info("🔍 Scanning MEXC Futures pairs for leverage...")
            
            # Get all futures markets
            futures_markets = []
            for symbol, market in self.exchange.markets.items():
                if market.get('swap') and market.get('quote') == 'USDT':
                    futures_markets.append(symbol)
            
            self.stats['total_pairs'] = len(futures_markets)
            logger.info(f"📊 Found {len(futures_markets)} USDT futures pairs")
            
            # Process in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(futures_markets), batch_size):
                batch = futures_markets[i:i + batch_size]
                logger.info(f"🔍 Processing batch {i//batch_size + 1}/{(len(futures_markets) + batch_size - 1)//batch_size}")
                
                for symbol in batch:
                    try:
                        # Get leverage tiers for this symbol
                        leverage_info = self.exchange.fetch_leverage_tiers([symbol])
                        
                        if leverage_info and symbol in leverage_info:
                            tiers = leverage_info[symbol]
                            max_leverage = self._get_max_leverage(tiers)
                            
                            # Store result
                            result = {
                                'symbol': symbol,
                                'max_leverage': max_leverage,
                                'has_200x': max_leverage >= 200,
                                'has_100x': max_leverage >= 100,
                                'tiers': tiers
                            }
                            self.results.append(result)
                            
                            # Update stats
                            self._update_stats(max_leverage)
                            
                            if max_leverage >= 200:
                                logger.success(f"🎯 {symbol}: {max_leverage}x leverage")
                            elif max_leverage >= 100:
                                logger.info(f"📈 {symbol}: {max_leverage}x leverage")
                            
                        else:
                            logger.warning(f"⚠️ No leverage info for {symbol}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing {symbol}: {e}")
                        continue
                
                # Rate limiting
                await asyncio.sleep(0.5)
            
            logger.success(f"✅ Scan completed! Processed {len(self.results)} pairs")
            
        except Exception as e:
            logger.error(f"❌ Error during scan: {e}")
            raise
    
    def _get_max_leverage(self, tiers):
        """Extract maximum leverage from leverage tiers"""
        try:
            if not tiers or not isinstance(tiers, list):
                return 0
            
            max_leverage = 0
            for tier in tiers:
                if isinstance(tier, dict) and 'maxLeverage' in tier:
                    leverage = int(tier['maxLeverage'])
                    max_leverage = max(max_leverage, leverage)
            
            return max_leverage
        except Exception as e:
            logger.warning(f"⚠️ Error parsing leverage tiers: {e}")
            return 0
    
    def _update_stats(self, max_leverage):
        """Update statistics based on leverage"""
        if max_leverage >= 200:
            self.stats['pairs_with_200x'] += 1
        elif max_leverage >= 100:
            self.stats['pairs_with_100x'] += 1
        elif max_leverage >= 50:
            self.stats['pairs_with_50x'] += 1
        elif max_leverage >= 25:
            self.stats['pairs_with_25x'] += 1
        elif max_leverage >= 10:
            self.stats['pairs_with_10x'] += 1
        elif max_leverage >= 5:
            self.stats['pairs_with_5x'] += 1
        else:
            self.stats['pairs_with_1x'] += 1
    
    def get_200x_pairs(self):
        """Get all pairs with 200x leverage"""
        return [result for result in self.results if result['has_200x']]
    
    def get_100x_pairs(self):
        """Get all pairs with 100x leverage"""
        return [result for result in self.results if result['has_100x']]
    
    def generate_report(self):
        """Generate comprehensive report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 MEXC FUTURES 200X LEVERAGE SCAN REPORT")
        report.append("=" * 80)
        report.append(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔌 Exchange: MEXC Futures")
        report.append("")
        
        # Statistics
        report.append("📊 LEVERAGE STATISTICS:")
        report.append("-" * 40)
        report.append(f"Total Pairs Scanned: {self.stats['total_pairs']}")
        report.append(f"Pairs with 200x Leverage: {self.stats['pairs_with_200x']}")
        report.append(f"Pairs with 100x+ Leverage: {self.stats['pairs_with_100x']}")
        report.append(f"Pairs with 50x+ Leverage: {self.stats['pairs_with_50x']}")
        report.append(f"Pairs with 25x+ Leverage: {self.stats['pairs_with_25x']}")
        report.append(f"Pairs with 10x+ Leverage: {self.stats['pairs_with_10x']}")
        report.append("")
        
        # 200x Leverage Pairs
        pairs_200x = self.get_200x_pairs()
        if pairs_200x:
            report.append("🎯 PAIRS WITH 200X LEVERAGE:")
            report.append("-" * 40)
            for result in pairs_200x:
                report.append(f"✅ {result['symbol']}: {result['max_leverage']}x")
            report.append("")
        else:
            report.append("⚠️ No pairs found with 200x leverage")
            report.append("")
        
        # 100x+ Leverage Pairs
        pairs_100x = self.get_100x_pairs()
        if pairs_100x:
            report.append("📈 PAIRS WITH 100X+ LEVERAGE:")
            report.append("-" * 40)
            for result in pairs_100x:
                if not result['has_200x']:  # Don't repeat 200x pairs
                    report.append(f"📈 {result['symbol']}: {result['max_leverage']}x")
            report.append("")
        
        # Summary
        report.append("📋 SUMMARY:")
        report.append("-" * 40)
        report.append(f"🎯 Total 200x pairs: {len(pairs_200x)}")
        report.append(f"📈 Total 100x+ pairs: {len(pairs_100x)}")
        report.append(f"📊 Coverage: {len(pairs_200x)/self.stats['total_pairs']*100:.1f}% of pairs have 200x leverage")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 40)
        if pairs_200x:
            report.append("✅ Found pairs with 200x leverage - suitable for high-risk strategies")
            report.append("⚠️ Use extreme caution with 200x leverage - high liquidation risk")
            report.append("🔒 Always use stop-losses with high leverage positions")
        else:
            report.append("⚠️ No 200x leverage pairs found - check MEXC's current offerings")
            report.append("📈 Consider 100x leverage pairs as alternative")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, filename="mexc_200x_leverage_results.txt"):
        """Save results to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_report())
            logger.success(f"💾 Results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
    
    def export_csv(self, filename="mexc_200x_leverage_pairs.csv"):
        """Export results to CSV"""
        try:
            df = pd.DataFrame(self.results)
            df = df[['symbol', 'max_leverage', 'has_200x', 'has_100x']]
            df.to_csv(filename, index=False)
            logger.success(f"📊 Results exported to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to export CSV: {e}")

async def main():
    """Main execution function"""
    logger.info("🚀 Starting MEXC 200x Leverage Scanner...")
    
    scanner = MEXC200xLeverageScanner()
    
    try:
        # Setup exchange connection
        await scanner.setup_exchange()
        
        # Scan all futures pairs
        await scanner.scan_all_futures_pairs()
        
        # Generate and display report
        report = scanner.generate_report()
        print(report)
        
        # Save results
        scanner.save_results()
        scanner.export_csv()
        
        # Return results for programmatic use
        return {
            '200x_pairs': scanner.get_200x_pairs(),
            '100x_pairs': scanner.get_100x_pairs(),
            'stats': scanner.stats,
            'total_pairs': len(scanner.results)
        }
        
    except Exception as e:
        logger.error(f"❌ Scanner failed: {e}")
        return None
    finally:
        if scanner.exchange:
            try:
                scanner.exchange.close()
            except:
                pass

if __name__ == "__main__":
    # Run the scanner
    results = asyncio.run(main())
    
    if results:
        print(f"\n🎯 Found {len(results['200x_pairs'])} pairs with 200x leverage!")
        print(f"📈 Found {len(results['100x_pairs'])} pairs with 100x+ leverage!")
    else:
        print("\n❌ Scanner failed to complete") 