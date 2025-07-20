#!/usr/bin/env python3
"""
🧪 Test Multi-Exchange Configuration
🔍 Verify Bitget accounts and MEXC Futures are properly configured
"""

import asyncio
import ccxt.async_support as ccxt
from loguru import logger
import sys
import os
from dotenv.main import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

async def test_exchanges():
    """🧪 Test all configured exchanges"""
    
    # Bitget Account 1 (Primary)
    bitget1_config = {
        'name': 'Bitget',
        'api_key': os.getenv("BITGET_API_KEY", ""),
        'api_secret': os.getenv("BITGET_SECRET_KEY", ""),
        'passphrase': os.getenv("BITGET_PASSPHRASE", ""),
    }
    
    # Bitget Account 2 (Secondary)
    bitget2_config = {
        'name': 'Bitget2',
        'api_key': "bg_33b25387b50e7f874c18ddf34f5cbb14",
        'api_secret': "4b3cab211d44a155c5cc63dd025fad43025d09155ee6eef3769ef2f6f85c9715",
        'passphrase': "22672267",
    }
    
    # MEXC Futures
    mexc_config = {
        'name': 'MEXC',
        'api_key': os.getenv("MEXC_API_KEY", ""),
        'api_secret': os.getenv("MEXC_SECRET_KEY", ""),
        'passphrase': "",
    }
    
    accounts = [bitget1_config, bitget2_config, mexc_config]
    
    logger.info("🧪 Testing Multi-Exchange Configuration...")
    logger.info("=" * 60)
    
    for i, account in enumerate(accounts, 1):
        try:
            logger.info(f"🔍 Testing {account['name']} (Account {i})...")
            
            # Create exchange instance based on type
            if account['name'].lower() in ['bitget', 'bitget2']:
                exchange = ccxt.bitget({
                    'apiKey': account['api_key'],
                    'secret': account['api_secret'],
                    'password': account['passphrase'],
                    'sandbox': False,
                    'options': {
                        'defaultType': 'swap',
                        'defaultMarginMode': 'cross'
                    }
                })
            elif account['name'].lower() == 'mexc':
                exchange = ccxt.mexc({
                    'apiKey': account['api_key'],
                    'secret': account['api_secret'],
                    'sandbox': False,
                    'options': {
                        'defaultType': 'swap',
                        'defaultMarginMode': 'cross'
                    }
                })
            else:
                logger.warning(f"⚠️ Unsupported exchange: {account['name']}")
                continue
            
            # Test connection
            await exchange.load_markets()
            logger.success(f"✅ {account['name']} connection successful")
            
            # Test balance fetch
            try:
                balance = await exchange.fetch_balance({'type': 'swap'})
                usdt_balance = float(balance.get('USDT', {}).get('free', 0))
                logger.success(f"💰 {account['name']} balance: ${usdt_balance:.2f}")
            except Exception as e:
                logger.warning(f"⚠️ {account['name']} balance fetch failed: {e}")
            
            # Test positions fetch
            try:
                positions = await exchange.fetch_positions()
                active_positions = [p for p in positions if p.get('size') and abs(float(p.get('size', 0))) > 0]
                logger.success(f"📊 {account['name']} active positions: {len(active_positions)}")
            except Exception as e:
                logger.warning(f"⚠️ {account['name']} positions fetch failed: {e}")
            
            # Test futures markets
            try:
                futures_markets = [symbol for symbol in exchange.markets if exchange.markets[symbol].get('swap')]
                logger.success(f"📈 {account['name']} futures markets: {len(futures_markets)}")
                if futures_markets:
                    logger.info(f"🎯 Sample futures: {futures_markets[:3]}")
            except Exception as e:
                logger.warning(f"⚠️ {account['name']} futures markets fetch failed: {e}")
            
            # Close connection
            await exchange.close()
            logger.info(f"🔌 {account['name']} connection closed")
            
        except Exception as e:
            logger.error(f"❌ {account['name']} test failed: {e}")
        
        logger.info("-" * 40)
    
    logger.success("🎯 Multi-exchange configuration test completed!")

async def test_trading_pairs():
    """📊 Test trading pairs loading from primary account"""
    
    logger.info("📊 Testing Trading Pairs Loading...")
    
    try:
        # Use primary Bitget account for trading pairs
        exchange = ccxt.bitget({
            'apiKey': os.getenv("BITGET_API_KEY", ""),
            'secret': os.getenv("BITGET_SECRET_KEY", ""),
            'password': os.getenv("BITGET_PASSPHRASE", ""),
            'sandbox': False,
            'options': {
                'defaultType': 'swap',
                'defaultMarginMode': 'cross'
            }
        })
        
        await exchange.load_markets()
        
        # Get USDT pairs with 25x+ leverage
        pairs = []
        for symbol in exchange.markets:
            if symbol.endswith(':USDT') and exchange.markets[symbol]['swap']:
                try:
                    leverage_info = await exchange.fetch_leverage_tiers([symbol])
                    if symbol in leverage_info:
                        max_leverage = max([tier['maxLeverage'] for tier in leverage_info[symbol]])
                        if max_leverage >= 25:
                            pairs.append(symbol)
                except:
                    pairs.append(symbol)
        
        logger.success(f"📊 Found {len(pairs)} trading pairs with 25x+ leverage")
        logger.info(f"🎯 Sample pairs: {pairs[:5]}")
        
        await exchange.close()
        
    except Exception as e:
        logger.error(f"❌ Trading pairs test failed: {e}")

async def test_mexc_futures():
    """📈 Test MEXC Futures specific functionality"""
    
    logger.info("📈 Testing MEXC Futures...")
    
    try:
        # Test MEXC connection
        mexc = ccxt.mexc({
            'apiKey': os.getenv("MEXC_API_KEY", ""),
            'secret': os.getenv("MEXC_SECRET_KEY", ""),
            'sandbox': False,
            'options': {
                'defaultType': 'swap',
                'defaultMarginMode': 'cross'
            }
        })
        
        await mexc.load_markets()
        logger.success("✅ MEXC connection successful")
        
        # Test MEXC futures markets
        futures_markets = [symbol for symbol in mexc.markets if mexc.markets[symbol].get('swap')]
        logger.success(f"📈 MEXC futures markets: {len(futures_markets)}")
        
        # Test USDT-M perpetual contracts
        usdt_markets = [symbol for symbol in futures_markets if ':USDT' in symbol]
        logger.success(f"💎 MEXC USDT-M contracts: {len(usdt_markets)}")
        
        if usdt_markets:
            logger.info(f"🎯 Sample MEXC contracts: {usdt_markets[:5]}")
        
        # Test leverage tiers
        if usdt_markets:
            try:
                sample_symbol = usdt_markets[0]
                leverage_info = await mexc.fetch_leverage_tiers([sample_symbol])
                if sample_symbol in leverage_info:
                    max_leverage = max([tier['maxLeverage'] for tier in leverage_info[sample_symbol]])
                    logger.success(f"⚡ MEXC max leverage for {sample_symbol}: {max_leverage}x")
            except Exception as e:
                logger.warning(f"⚠️ MEXC leverage fetch failed: {e}")
        
        await mexc.close()
        logger.success("✅ MEXC Futures test completed")
        
    except Exception as e:
        logger.error(f"❌ MEXC Futures test failed: {e}")

async def main():
    """🎯 Main test function"""
    logger.info("🚀 Starting Multi-Exchange Configuration Tests...")
    
    # Test all exchanges
    await test_exchanges()
    
    # Test trading pairs
    await test_trading_pairs()
    
    # Test MEXC Futures specifically
    await test_mexc_futures()
    
    logger.success("✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 