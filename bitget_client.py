import time
import hmac
import hashlib
import base64
import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger
from pybitget import Client
from pybitget.enums import *
from config import config

class BitgetClient:
    """Enhanced Bitget API Client for Futures Trading"""
    
    def __init__(self):
        """Initialize the Bitget client"""
        self.api_key = config.bitget.api_key
        self.api_secret = config.bitget.api_secret
        self.passphrase = config.bitget.passphrase
        self.base_url = config.bitget.base_url
        self.sandbox = config.bitget.sandbox
        
        # Initialize pybitget client
        self.client = Client(
            api_key=self.api_key,
            api_secret_key=self.api_secret,
            passphrase=self.passphrase,
            use_server_time=True
        )
        
        logger.info("Bitget client initialized successfully")
    
    def test_connection(self) -> bool:
        """Test API connection and credentials"""
        try:
            # Test connection with server time
            result = self.client.public_get_time()
            logger.info(f"Server time: {result}")
            
            # Test account info
            account_info = self.client.mix_get_accounts(productType='UMCBL')
            logger.info(f"Account info retrieved: {len(account_info)} accounts")
            
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_account_info(self, product_type: str = 'UMCBL') -> Dict[str, Any]:
        """Get account information"""
        try:
            result = self.client.mix_get_accounts(productType=product_type)
            logger.info(f"Account info retrieved for {product_type}")
            return result
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return {}
    
    def get_positions(self, symbol: str = None, product_type: str = 'UMCBL') -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            if symbol:
                result = self.client.mix_get_single_position(symbol=symbol, marginCoin='USDT')
            else:
                result = self.client.mix_get_all_positions(productType=product_type, marginCoin='USDT')
            
            logger.info(f"Positions retrieved: {len(result) if isinstance(result, list) else 1}")
            return result if isinstance(result, list) else [result]
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            return []
    
    def get_balance(self, margin_coin: str = 'USDT') -> Dict[str, Any]:
        """Get account balance"""
        try:
            accounts = self.client.mix_get_accounts(productType='UMCBL')
            
            for account in accounts:
                if account.get('marginCoin') == margin_coin:
                    return account
            
            logger.warning(f"No balance found for {margin_coin}")
            return {}
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return {}
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information"""
        try:
            result = self.client.mix_get_ticker(symbol=symbol)
            logger.debug(f"Ticker retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {str(e)}")
            return {}
    
    def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get orderbook depth"""
        try:
            result = self.client.mix_get_depth(symbol=symbol, limit=str(limit))
            logger.debug(f"Orderbook retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to get orderbook for {symbol}: {str(e)}")
            return {}
    
    def place_order(self, symbol: str, side: str, order_type: str, size: str, 
                   price: str = None, reduce_only: bool = False, 
                   time_in_force: str = 'normal', client_order_id: str = None) -> Dict[str, Any]:
        """Place a futures order"""
        try:
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'marginCoin': 'USDT',
                'side': side,
                'orderType': order_type,
                'size': size,
                'timeInForceValue': time_in_force
            }
            
            if price:
                order_params['price'] = price
            
            if reduce_only:
                order_params['reduceOnly'] = 'YES'
            
            if client_order_id:
                order_params['clientOrderId'] = client_order_id
            
            # Place order
            result = self.client.mix_place_order(**order_params)
            logger.info(f"Order placed: {side} {size} {symbol} at {price if price else 'market'}")
            return result
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return {}
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            result = self.client.mix_cancel_order(symbol=symbol, orderId=order_id, marginCoin='USDT')
            logger.info(f"Order cancelled: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            return {}
    
    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """Cancel all orders for a symbol"""
        try:
            result = self.client.mix_cancel_all_orders(symbol=symbol, marginCoin='USDT')
            logger.info(f"All orders cancelled for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel all orders for {symbol}: {str(e)}")
            return {}
    
    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        try:
            if symbol:
                result = self.client.mix_get_open_orders(symbol=symbol)
            else:
                result = self.client.mix_get_open_orders()
            
            logger.info(f"Open orders retrieved: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Failed to get open orders: {str(e)}")
            return []
    
    def get_order_history(self, symbol: str, start_time: str = None, 
                         end_time: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get order history"""
        try:
            params = {'symbol': symbol, 'pageSize': str(limit)}
            
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            result = self.client.mix_get_order_history(**params)
            logger.info(f"Order history retrieved: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Failed to get order history: {str(e)}")
            return []
    
    def get_fills(self, symbol: str, start_time: str = None, 
                  end_time: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trade fills"""
        try:
            params = {'symbol': symbol, 'pageSize': str(limit)}
            
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            result = self.client.mix_get_fills(**params)
            logger.info(f"Fills retrieved: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Failed to get fills: {str(e)}")
            return []
    
    def set_leverage(self, symbol: str, leverage: int, hold_side: str = 'long') -> Dict[str, Any]:
        """Set leverage for a symbol"""
        try:
            result = self.client.mix_change_leverage(
                symbol=symbol,
                marginCoin='USDT',
                leverage=str(leverage),
                holdSide=hold_side
            )
            logger.info(f"Leverage set to {leverage}x for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to set leverage: {str(e)}")
            return {}
    
    def set_margin_mode(self, symbol: str, margin_mode: str = 'isolated') -> Dict[str, Any]:
        """Set margin mode"""
        try:
            result = self.client.mix_change_margin_mode(
                symbol=symbol,
                marginCoin='USDT',
                marginMode=margin_mode
            )
            logger.info(f"Margin mode set to {margin_mode} for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to set margin mode: {str(e)}")
            return {}
    
    def place_stop_order(self, symbol: str, side: str, size: str, 
                        stop_price: str, trigger_type: str = 'fill_price',
                        order_type: str = 'market') -> Dict[str, Any]:
        """Place a stop order"""
        try:
            result = self.client.mix_place_stop_order(
                symbol=symbol,
                marginCoin='USDT',
                side=side,
                orderType=order_type,
                size=size,
                triggerPrice=stop_price,
                triggerType=trigger_type
            )
            logger.info(f"Stop order placed: {side} {size} {symbol} at {stop_price}")
            return result
        except Exception as e:
            logger.error(f"Failed to place stop order: {str(e)}")
            return {}
    
    def place_take_profit_order(self, symbol: str, side: str, size: str, 
                               trigger_price: str, trigger_type: str = 'fill_price',
                               order_type: str = 'market') -> Dict[str, Any]:
        """Place a take profit order"""
        try:
            result = self.client.mix_place_stop_order(
                symbol=symbol,
                marginCoin='USDT',
                side=side,
                orderType=order_type,
                size=size,
                triggerPrice=trigger_price,
                triggerType=trigger_type
            )
            logger.info(f"Take profit order placed: {side} {size} {symbol} at {trigger_price}")
            return result
        except Exception as e:
            logger.error(f"Failed to place take profit order: {str(e)}")
            return {}
    
    def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Get current funding rate"""
        try:
            result = self.client.mix_get_current_funding_rate(symbol=symbol)
            logger.debug(f"Funding rate retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to get funding rate for {symbol}: {str(e)}")
            return {}
    
    def get_contract_info(self, symbol: str) -> Dict[str, Any]:
        """Get contract information"""
        try:
            result = self.client.mix_get_contract_info(symbol=symbol)
            logger.debug(f"Contract info retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to get contract info for {symbol}: {str(e)}")
            return {}

# Global client instance
bitget_client = BitgetClient()