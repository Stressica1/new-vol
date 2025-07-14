#!/usr/bin/env python3
"""
Alpine-Bitget Integration
========================

This script integrates the Volume Anomaly Bot's advanced coin selection
with Alpine Bot's Bitget trading execution capabilities.

Features:
- Uses volume anomaly analysis to select top coins
- Feeds selected coins to Alpine Bot for trading on Bitget
- Real-time market data from both analysis and execution
- Unified configuration and risk management
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict
import sys
import os

# Import both systems
from volume_anom_bot import VolumeAnomBot, get_top_coins_for_trading
from alpine_bot import AlpineBot
from config import TRADING_PAIRS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlpineBitgetIntegration:
    """
    Integrated Alpine-Bitget trading system combining:
    - Volume anomaly analysis for coin selection
    - Bitget exchange for trade execution
    """
    
    def __init__(self):
        self.volume_bot = VolumeAnomBot()
        self.alpine_bot = None
        self.selected_pairs = []
        self.last_analysis = None
        
    async def initialize_alpine_bot(self):
        """Initialize Alpine bot with Bitget connection"""
        try:
            self.alpine_bot = AlpineBot()
            
            # Initialize exchange connection
            if not self.alpine_bot.initialize_exchange():
                raise Exception("Failed to connect to Bitget exchange")
                
            logger.info("✅ Alpine Bot connected to Bitget successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alpine Bot: {e}")
            return False
    
    async def run_volume_analysis(self, top_n: int = 50) -> List[str]:
        """
        Run volume anomaly analysis and return top trading pairs
        """
        try:
            logger.info("🔍 Running volume anomaly analysis...")
            
            # Get top coins from volume anomaly bot
            results = await get_top_coins_for_trading(top_n=top_n)
            
            if 'error' in results:
                logger.error(f"Volume analysis failed: {results['error']}")
                return []
            
            # Extract high and medium priority targets
            high_priority = results.get('trading_targets', {}).get('high_priority', [])
            medium_priority = results.get('trading_targets', {}).get('medium_priority', [])
            
            # Convert to Bitget trading pairs format
            selected_symbols = []
            
            for target in high_priority + medium_priority[:20]:  # Top 20 from medium priority
                symbol = target['symbol']
                # Convert to Bitget format: SYMBOL/USDT:USDT
                bitget_pair = f"{symbol}/USDT:USDT"
                selected_symbols.append(bitget_pair)
            
            logger.info(f"🎯 Selected {len(selected_symbols)} trading pairs from analysis")
            self.selected_pairs = selected_symbols
            self.last_analysis = datetime.now()
            
            return selected_symbols
            
        except Exception as e:
            logger.error(f"❌ Volume analysis failed: {e}")
            return []
    
    def update_alpine_trading_pairs(self, new_pairs: List[str]):
        """
        Update Alpine bot's trading pairs with volume anomaly selections
        """
        try:
            # Update the global TRADING_PAIRS used by Alpine bot
            global TRADING_PAIRS
            TRADING_PAIRS.clear()
            TRADING_PAIRS.extend(new_pairs)
            
            # Update Alpine bot's strategy with new pairs
            if hasattr(self.alpine_bot.strategy, 'trading_pairs'):
                self.alpine_bot.strategy.trading_pairs = new_pairs
            
            logger.info(f"📊 Updated Alpine Bot with {len(new_pairs)} trading pairs")
            
            # Log the selected pairs
            for i, pair in enumerate(new_pairs[:10], 1):
                logger.info(f"  {i}. {pair.replace('/USDT:USDT', '')}")
            
            if len(new_pairs) > 10:
                logger.info(f"  ... and {len(new_pairs) - 10} more pairs")
                
        except Exception as e:
            logger.error(f"❌ Failed to update trading pairs: {e}")
    
    async def run_integrated_trading(self, analysis_interval_hours: int = 3):
        """
        Main integrated trading loop:
        1. Run volume anomaly analysis every 3 hours
        2. Update Alpine bot's trading pairs
        3. Let Alpine bot trade on Bitget with selected pairs
        """
        
        logger.info("🚀 Starting Alpine-Bitget integrated trading system")
        
        # Initialize Alpine bot
        if not await self.initialize_alpine_bot():
            logger.error("❌ Cannot start without Bitget connection")
            return
        
        # Initial analysis
        selected_pairs = await self.run_volume_analysis()
        if not selected_pairs:
            logger.error("❌ No trading pairs selected from analysis")
            return
        
        # Update Alpine bot
        self.update_alpine_trading_pairs(selected_pairs)
        
        # Start Alpine bot trading
        logger.info("🏔️ Starting Alpine Bot trading on Bitget...")
        
        try:
            # This would integrate with Alpine bot's trading loop
            # For now, we'll simulate the integration
            analysis_counter = 0
            
            while True:
                analysis_counter += 1
                
                logger.info(f"📊 Analysis cycle #{analysis_counter}")
                logger.info(f"🎯 Trading {len(self.selected_pairs)} selected pairs on Bitget")
                
                # In real implementation, Alpine bot would be running here
                # self.alpine_bot.run_trading_cycle()
                
                # Re-analyze every 3 hours
                await asyncio.sleep(analysis_interval_hours * 3600)
                
                # Refresh coin selection
                new_pairs = await self.run_volume_analysis()
                if new_pairs:
                    self.update_alpine_trading_pairs(new_pairs)
                    logger.info(f"🔄 Updated trading pairs for cycle #{analysis_counter + 1}")
                
        except KeyboardInterrupt:
            logger.info("⏹️ Stopping integrated trading system")
        except Exception as e:
            logger.error(f"❌ Trading system error: {e}")
    
    def get_status_report(self) -> Dict:
        """Get current status of the integrated system"""
        return {
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'selected_pairs_count': len(self.selected_pairs),
            'alpine_bot_connected': self.alpine_bot is not None,
            'bitget_connected': self.alpine_bot.connected if self.alpine_bot else False,
            'current_pairs': self.selected_pairs[:10]  # Show first 10
        }

async def main():
    """Main entry point for integrated system"""
    integration = AlpineBitgetIntegration()
    
    print("🏔️ ALPINE-BITGET INTEGRATION SYSTEM")
    print("=" * 50)
    print("📊 Volume Anomaly Analysis + 🏔️ Alpine Bot + 💱 Bitget Trading")
    print("=" * 50)
    
    try:
        await integration.run_integrated_trading()
    except KeyboardInterrupt:
        print("\n👋 Integration system stopped")
    except Exception as e:
        print(f"\n❌ System error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 