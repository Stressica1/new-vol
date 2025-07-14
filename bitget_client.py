import ccxt
from typing import Dict, Any, Optional, List
from loguru import logger
from config import get_exchange_config

# Global bitget client instance
bitget_client = None

def initialize_bitget_client():
    """Initialize the global Bitget client"""
    global bitget_client
    try:
        exchange_config = get_exchange_config()
        bitget_client = ccxt.bitget(exchange_config)
        logger.info("Bitget client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Bitget client: {e}")
        return False

def test_bitget_connection() -> bool:
    """Test Bitget API connection and credentials"""
    global bitget_client
    if not bitget_client:
        if not initialize_bitget_client():
            return False
    
    try:
        # Test connection with markets
        markets = bitget_client.load_markets()
        logger.info(f"Markets loaded: {len(markets)} pairs available")
        
        # Test account info
        balance = bitget_client.fetch_balance()
        logger.info(f"Account balance retrieved successfully")
        
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

# Initialize client on import
initialize_bitget_client()