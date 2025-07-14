import ccxt
from typing import Dict, Any, Optional, List
from loguru import logger
from config import get_exchange_config

class BitgetClient:
    """Enhanced Bitget Client with full trading functionality"""
    
    def __init__(self):
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize the Bitget client"""
        try:
            exchange_config = get_exchange_config()
            self.client = ccxt.bitget(exchange_config)
            logger.info("Bitget client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Bitget client: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Bitget API connection and credentials"""
        if not self.client:
            if not self.initialize():
                return False
        
        try:
            # Test connection with markets
            markets = self.client.load_markets()
            logger.info(f"Markets loaded: {len(markets)} pairs available")
            
            # Test account info
            balance = self.client.fetch_balance()
            logger.info(f"Account balance retrieved successfully")
            
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_account_info(self) -> Optional[List[Dict]]:
        """Get account information"""
        try:
            if not self.client:
                return None
            
            balance = self.client.fetch_balance()
            return [balance] if balance else None
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return None
    
    def get_balance(self) -> Optional[Dict]:
        """Get account balance"""
        try:
            if not self.client:
                return None
            
            balance = self.client.fetch_balance()
            if balance and 'USDT' in balance:
                usdt_balance = balance['USDT']
                return {
                    'usdtEquity': usdt_balance.get('total', 0),
                    'available': usdt_balance.get('free', 0),
                    'locked': usdt_balance.get('used', 0),
                    'unrealizedPL': 0,  # Will be calculated from positions
                    'marginCoin': 'USDT',
                    'leverage': '1'
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get ticker data for symbol"""
        try:
            if not self.client:
                return None
            
            ticker = self.client.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            if not self.client:
                return []
            
            positions = self.client.fetch_positions()
            return positions if positions else []
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def place_order(self, symbol: str, order_type: str, side: str, size: float, 
                   price: Optional[float] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Place an order"""
        try:
            if not self.client:
                return None
            
            # Default params for futures trading
            if params is None:
                params = {}
            
            if order_type.lower() == 'market':
                order = self.client.create_market_order(symbol, side, size, None, params)
            elif order_type.lower() == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = self.client.create_limit_order(symbol, side, size, price, params)
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            logger.info(f"Order placed: {order.get('id', 'Unknown')} - {side} {size} {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            if not self.client:
                return False
            
            result = self.client.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Get order status"""
        try:
            if not self.client:
                return None
            
            order = self.client.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Failed to get order status for {order_id}: {e}")
            return None

# Global instance
bitget_client = BitgetClient()