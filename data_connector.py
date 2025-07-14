import requests
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import asdict

from crypto_scoring_system import CoinMetrics
from technical_indicators import TechnicalIndicators, VolumeAnalyzer

logger = logging.getLogger(__name__)

class CryptoDataConnector:
    """
    Data connector for fetching crypto market data from multiple sources
    
    Supports:
    - CoinGecko API (free tier)
    - CoinMarketCap API (requires API key)
    - Binance API (public endpoints)
    - Mock data for testing
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.session = None
        
        # API endpoints
        self.endpoints = {
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'markets': '/coins/markets',
                'historical': '/coins/{coin_id}/market_chart',
                'rate_limit': 50  # calls per minute
            },
            'coinmarketcap': {
                'base_url': 'https://pro-api.coinmarketcap.com/v1',
                'listings': '/cryptocurrency/listings/latest',
                'quotes': '/cryptocurrency/quotes/latest',
                'rate_limit': 333  # calls per minute for basic plan
            },
            'binance': {
                'base_url': 'https://api.binance.com/api/v3',
                'ticker': '/ticker/24hr',
                'klines': '/klines',
                'rate_limit': 1200  # calls per minute
            }
        }
        
        # Rate limiting
        self.last_request_time = {}
        self.request_counts = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _check_rate_limit(self, source: str) -> bool:
        """Check if we can make a request based on rate limits"""
        current_time = time.time()
        
        if source not in self.last_request_time:
            self.last_request_time[source] = current_time
            self.request_counts[source] = 1
            return True
        
        # Reset counter if more than a minute has passed
        if current_time - self.last_request_time[source] > 60:
            self.request_counts[source] = 1
            self.last_request_time[source] = current_time
            return True
        
        # Check if we're within rate limit
        if self.request_counts[source] < self.endpoints[source]['rate_limit']:
            self.request_counts[source] += 1
            return True
        
        return False
    
    async def _make_request(self, url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    async def fetch_coingecko_data(self, limit: int = 100) -> List[Dict]:
        """Fetch data from CoinGecko API"""
        try:
            if not self._check_rate_limit('coingecko'):
                logger.warning("CoinGecko rate limit exceeded, skipping...")
                return []
            
            base_url = self.endpoints['coingecko']['base_url']
            url = f"{base_url}{self.endpoints['coingecko']['markets']}"
            
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h,7d'
            }
            
            data = await self._make_request(url, params=params)
            
            if data:
                logger.info(f"Successfully fetched {len(data)} coins from CoinGecko")
                return data
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            return []
    
    async def fetch_binance_data(self, limit: int = 100) -> List[Dict]:
        """Fetch data from Binance API"""
        try:
            if not self._check_rate_limit('binance'):
                logger.warning("Binance rate limit exceeded, skipping...")
                return []
            
            base_url = self.endpoints['binance']['base_url']
            url = f"{base_url}{self.endpoints['binance']['ticker']}"
            
            data = await self._make_request(url)
            
            if data:
                # Filter for USDT pairs and convert to standard format
                usdt_pairs = [item for item in data if item['symbol'].endswith('USDT')]
                
                # Sort by volume and take top N
                usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
                
                logger.info(f"Successfully fetched {len(usdt_pairs[:limit])} USDT pairs from Binance")
                return usdt_pairs[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching Binance data: {e}")
            return []
    
    async def fetch_historical_data(self, coin_id: str, days: int = 30) -> Optional[Dict]:
        """Fetch historical price data for technical indicators"""
        try:
            if not self._check_rate_limit('coingecko'):
                logger.warning("CoinGecko rate limit exceeded for historical data")
                return None
            
            base_url = self.endpoints['coingecko']['base_url']
            url = f"{base_url}{self.endpoints['coingecko']['historical'].format(coin_id=coin_id)}"
            
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 7 else 'daily'
            }
            
            data = await self._make_request(url, params=params)
            
            if data and 'prices' in data:
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            return None
    
    def _normalize_coingecko_data(self, coin_data: Dict) -> Optional[Dict]:
        """Normalize CoinGecko data to standard format"""
        try:
            return {
                'symbol': coin_data['symbol'].upper(),
                'name': coin_data['name'],
                'price': float(coin_data['current_price'] or 0),
                'market_cap': float(coin_data['market_cap'] or 0),
                'volume_24h': float(coin_data['total_volume'] or 0),
                'price_change_24h': float(coin_data.get('price_change_percentage_24h', 0)),
                'price_change_7d': float(coin_data.get('price_change_percentage_7d', 0)),
                'high_24h': float(coin_data.get('high_24h', coin_data['current_price'])),
                'low_24h': float(coin_data.get('low_24h', coin_data['current_price'])),
                'circulating_supply': float(coin_data.get('circulating_supply', 0)),
                'total_supply': float(coin_data.get('total_supply', 0)),
                'coin_id': coin_data['id']
            }
        except Exception as e:
            logger.error(f"Error normalizing CoinGecko data: {e}")
            return None
    
    def _normalize_binance_data(self, coin_data: Dict) -> Optional[Dict]:
        """Normalize Binance data to standard format"""
        try:
            symbol = coin_data['symbol'].replace('USDT', '')
            price = float(coin_data['lastPrice'])
            volume_24h = float(coin_data['quoteVolume'])
            
            # Estimate market cap based on volume (rough approximation)
            # High volume coins typically have higher market caps
            estimated_market_cap = max(volume_24h * 10, 50000000)  # Minimum 50M estimation
            
            return {
                'symbol': symbol,
                'name': symbol,
                'price': price,
                'market_cap': estimated_market_cap,  # Estimated market cap
                'volume_24h': volume_24h,
                'price_change_24h': float(coin_data['priceChangePercent']),
                'price_change_7d': 0,  # Not available in 24hr ticker
                'high_24h': float(coin_data['highPrice']),
                'low_24h': float(coin_data['lowPrice']),
                'circulating_supply': 0,
                'total_supply': 0,
                'coin_id': symbol.lower()
            }
        except Exception as e:
            logger.error(f"Error normalizing Binance data: {e}")
            return None
    
    def _create_mock_historical_data(self, current_price: float, days: int = 30) -> List[float]:
        """Create mock historical data for testing"""
        np = __import__('numpy')
        
        # Generate realistic price movement
        base_price = current_price * 0.95  # Start slightly lower
        price_history = [base_price]
        
        for i in range(days * 24):  # Hourly data
            # Random walk with slight upward bias
            change = np.random.normal(0.001, 0.02)  # Small positive bias with 2% volatility
            new_price = price_history[-1] * (1 + change)
            price_history.append(max(new_price, current_price * 0.5))  # Prevent extreme drops
        
        return price_history
    
    async def get_coin_metrics(self, coin_data: Dict, fetch_historical: bool = True) -> Optional[CoinMetrics]:
        """Convert normalized coin data to CoinMetrics object with technical indicators"""
        try:
            # Get historical data for technical indicators
            historical_data = None
            if fetch_historical and 'coin_id' in coin_data:
                historical_data = await self.fetch_historical_data(coin_data['coin_id'], days=30)
            
            # Extract price history
            if historical_data and 'prices' in historical_data:
                price_history = [price[1] for price in historical_data['prices']]
                volume_history = [vol[1] for vol in historical_data.get('total_volumes', [])]
            else:
                # Use mock data if historical data not available
                price_history = self._create_mock_historical_data(coin_data['price'])
                volume_history = [coin_data['volume_24h'] * (0.8 + 0.4 * __import__('random').random()) for _ in range(len(price_history))]
            
            # Calculate technical indicators
            indicators = TechnicalIndicators.calculate_all_indicators(
                prices=price_history,
                high_prices=[p * 1.02 for p in price_history],  # Approximate highs
                low_prices=[p * 0.98 for p in price_history],   # Approximate lows
                volumes=volume_history
            )
            
            # Calculate volume analysis
            volume_analysis = VolumeAnalyzer.detect_volume_anomaly(volume_history)
            
            # Create CoinMetrics object
            metrics = CoinMetrics(
                symbol=coin_data['symbol'],
                price=coin_data['price'],
                volume_24h=coin_data['volume_24h'],
                volume_7d_avg=volume_analysis.get('avg_volume', coin_data['volume_24h']),
                market_cap=coin_data['market_cap'],
                price_change_24h=coin_data['price_change_24h'],
                price_change_7d=coin_data['price_change_7d'],
                high_24h=coin_data['high_24h'],
                low_24h=coin_data['low_24h'],
                rsi=indicators['rsi'],
                macd=indicators['macd'],
                macd_signal=indicators['macd_signal'],
                bollinger_upper=indicators['bollinger_upper'],
                bollinger_lower=indicators['bollinger_lower'],
                ema_12=indicators['ema_12'],
                ema_26=indicators['ema_26'],
                sma_50=indicators['sma_50'],
                sma_200=indicators['sma_200'],
                atr=indicators['atr'],
                timestamp=datetime.now()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error creating CoinMetrics for {coin_data.get('symbol', 'Unknown')}: {e}")
            return None
    
    async def fetch_all_coin_data(self, limit: int = 500) -> List[CoinMetrics]:
        """Fetch and process data from all available sources"""
        all_metrics = []
        
        try:
            # Fetch from multiple sources concurrently
            tasks = [
                self.fetch_coingecko_data(limit=min(limit, 250)),
                self.fetch_binance_data(limit=min(limit, 250))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process CoinGecko data
            coingecko_data = results[0] if not isinstance(results[0], Exception) else []
            for coin_data in coingecko_data:
                normalized = self._normalize_coingecko_data(coin_data)
                if normalized:
                    metrics = await self.get_coin_metrics(normalized, fetch_historical=False)
                    if metrics:
                        all_metrics.append(metrics)
            
            # Process Binance data
            binance_data = results[1] if not isinstance(results[1], Exception) else []
            for coin_data in binance_data:
                normalized = self._normalize_binance_data(coin_data)
                if normalized:
                    # Skip if we already have this coin from CoinGecko
                    if not any(m.symbol == normalized['symbol'] for m in all_metrics):
                        metrics = await self.get_coin_metrics(normalized, fetch_historical=False)
                        if metrics:
                            all_metrics.append(metrics)
            
            logger.info(f"Successfully processed {len(all_metrics)} coins from all sources")
            return all_metrics
            
        except Exception as e:
            logger.error(f"Error fetching all coin data: {e}")
            return []
    
    def create_mock_data(self, count: int = 100) -> List[CoinMetrics]:
        """Create mock data for testing when APIs are unavailable"""
        import random
        
        mock_coins = [
            'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE', 'AVAX', 'SHIB',
            'MATIC', 'UNI', 'LINK', 'ATOM', 'LTC', 'BCH', 'ALGO', 'XLM', 'VET', 'ICP',
            'FIL', 'TRX', 'ETC', 'THETA', 'AAVE', 'COMP', 'MKR', 'SUSHI', 'YFI', 'SNX',
            'SAND', 'MANA', 'CRV', 'BAL', 'KSM', 'NEAR', 'FLOW', 'EGLD', 'RUNE', 'CAKE',
            'ALPHA', 'KAVA', 'BAND', 'SRM', 'RAY', 'PERP', 'DYDX', 'ENJ', 'CHZ', 'BAT'
        ]
        
        mock_metrics = []
        
        for i in range(min(count, len(mock_coins))):
            symbol = mock_coins[i]
            base_price = random.uniform(0.1, 50000)
            
            # Create realistic mock data
            metrics = CoinMetrics(
                symbol=symbol,
                price=base_price,
                volume_24h=random.uniform(1000000, 50000000000),
                volume_7d_avg=random.uniform(1000000, 40000000000),
                market_cap=random.uniform(10000000, 1000000000000),
                price_change_24h=random.uniform(-10, 15),
                price_change_7d=random.uniform(-20, 30),
                high_24h=base_price * random.uniform(1.0, 1.15),
                low_24h=base_price * random.uniform(0.85, 1.0),
                rsi=random.uniform(20, 80),
                macd=random.uniform(-50, 50),
                macd_signal=random.uniform(-45, 45),
                bollinger_upper=base_price * random.uniform(1.05, 1.2),
                bollinger_lower=base_price * random.uniform(0.8, 0.95),
                ema_12=base_price * random.uniform(0.95, 1.05),
                ema_26=base_price * random.uniform(0.9, 1.1),
                sma_50=base_price * random.uniform(0.85, 1.15),
                sma_200=base_price * random.uniform(0.7, 1.3),
                atr=base_price * random.uniform(0.01, 0.08),
                timestamp=datetime.now()
            )
            
            mock_metrics.append(metrics)
        
        logger.info(f"Created {len(mock_metrics)} mock coin metrics")
        return mock_metrics

# Utility functions for easy integration
async def fetch_market_data(limit: int = 500, use_mock: bool = False) -> List[CoinMetrics]:
    """Convenience function to fetch market data"""
    
    if use_mock:
        connector = CryptoDataConnector()
        return connector.create_mock_data(limit)
    
    async with CryptoDataConnector() as connector:
        return await connector.fetch_all_coin_data(limit)

def get_top_volume_coins(metrics_list: List[CoinMetrics], top_n: int = 100) -> List[CoinMetrics]:
    """Get top N coins by volume"""
    return sorted(metrics_list, key=lambda x: x.volume_24h, reverse=True)[:top_n]

def filter_by_market_cap(metrics_list: List[CoinMetrics], min_market_cap: float = 10000000) -> List[CoinMetrics]:
    """Filter coins by minimum market cap"""
    return [m for m in metrics_list if m.market_cap >= min_market_cap]

# Test the data connector
if __name__ == "__main__":
    async def test_data_connector():
        print("=== TESTING CRYPTO DATA CONNECTOR ===")
        
        # Test with mock data
        print("\n1. Testing with mock data...")
        mock_metrics = await fetch_market_data(limit=10, use_mock=True)
        print(f"Created {len(mock_metrics)} mock coins")
        
        for i, metrics in enumerate(mock_metrics[:3]):
            print(f"\n{i+1}. {metrics.symbol}:")
            print(f"   Price: ${metrics.price:.2f}")
            print(f"   Volume 24h: ${metrics.volume_24h:,.0f}")
            print(f"   Market Cap: ${metrics.market_cap:,.0f}")
            print(f"   RSI: {metrics.rsi:.2f}")
            print(f"   Price Change 24h: {metrics.price_change_24h:.2f}%")
        
        # Test with real APIs (uncomment to test)
        # print("\n2. Testing with real APIs...")
        # real_metrics = await fetch_market_data(limit=5, use_mock=False)
        # print(f"Fetched {len(real_metrics)} real coins")
        
        print("\n=== TEST COMPLETED ===")
    
    asyncio.run(test_data_connector())