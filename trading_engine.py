import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from config import TradingConfig
from bitget_client import bitget_client
from risk_management import risk_manager, RiskLevel

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"

@dataclass
class Order:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    order_type: OrderType
    size: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_size: float = 0.0
    filled_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    def update_status(self, status: OrderStatus, error_message: str = None):
        """Update order status"""
        self.status = status
        self.updated_at = datetime.now()
        if error_message:
            self.error_message = error_message

@dataclass
class Trade:
    trade_id: str
    order_id: str
    symbol: str
    side: str
    size: float
    price: float
    timestamp: datetime
    commission: float = 0.0
    commission_asset: str = "USDT"

class TradingEngine:
    """Main Trading Engine"""
    
    def __init__(self):
        self.config = config.trading
        self.is_running = False
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.position_monitor_thread: Optional[threading.Thread] = None
        self.order_monitor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._stop_event = threading.Event()
        
        logger.info("Trading Engine initialized")
    
    def start(self):
        """Start the trading engine"""
        if self.is_running:
            logger.warning("Trading engine is already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start monitoring threads
        self.position_monitor_thread = threading.Thread(target=self._monitor_positions)
        self.order_monitor_thread = threading.Thread(target=self._monitor_orders)
        
        self.position_monitor_thread.daemon = True
        self.order_monitor_thread.daemon = True
        
        self.position_monitor_thread.start()
        self.order_monitor_thread.start()
        
        logger.info("Trading engine started")
    
    def stop(self):
        """Stop the trading engine"""
        if not self.is_running:
            logger.warning("Trading engine is not running")
            return
        
        self.is_running = False
        self._stop_event.set()
        
        # Wait for threads to finish
        if self.position_monitor_thread:
            self.position_monitor_thread.join(timeout=5)
        if self.order_monitor_thread:
            self.order_monitor_thread.join(timeout=5)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Trading engine stopped")
    
    def place_market_order(self, symbol: str, side: str, size: float, 
                          reduce_only: bool = False) -> Optional[Order]:
        """Place a market order"""
        
        # Get current price for validation
        ticker = bitget_client.get_ticker(symbol)
        if not ticker:
            logger.error(f"Failed to get ticker for {symbol}")
            return None
        
        current_price = float(ticker.get('last', 0))
        if current_price <= 0:
            logger.error(f"Invalid price for {symbol}: {current_price}")
            return None
        
        # Check risk management
        can_open, reason = risk_manager.can_open_position(symbol, side, size, current_price)
        if not can_open:
            logger.warning(f"Order rejected by risk manager: {reason}")
            return None
        
        # Create order
        client_order_id = f"market_{uuid.uuid4().hex[:8]}"
        order = Order(
            order_id="",
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            size=size,
            price=current_price
        )
        
        # Submit order
        return self._submit_order(order, reduce_only=reduce_only)
    
    def place_limit_order(self, symbol: str, side: str, size: float, price: float,
                         reduce_only: bool = False) -> Optional[Order]:
        """Place a limit order"""
        
        # Check risk management
        can_open, reason = risk_manager.can_open_position(symbol, side, size, price)
        if not can_open:
            logger.warning(f"Order rejected by risk manager: {reason}")
            return None
        
        # Create order
        client_order_id = f"limit_{uuid.uuid4().hex[:8]}"
        order = Order(
            order_id="",
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            size=size,
            price=price
        )
        
        # Submit order
        return self._submit_order(order, reduce_only=reduce_only)
    
    def place_stop_order(self, symbol: str, side: str, size: float, stop_price: float,
                        order_type: str = "market", reduce_only: bool = True) -> Optional[Order]:
        """Place a stop order"""
        
        # Create order
        client_order_id = f"stop_{uuid.uuid4().hex[:8]}"
        order = Order(
            order_id="",
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=OrderType.STOP_MARKET,
            size=size,
            stop_price=stop_price
        )
        
        # Submit stop order
        try:
            result = bitget_client.place_stop_order(
                symbol=symbol,
                side=side,
                size=str(size),
                stop_price=str(stop_price),
                order_type=order_type
            )
            
            if result and result.get('orderId'):
                order.order_id = result['orderId']
                order.status = OrderStatus.SUBMITTED
                self.orders[order.order_id] = order
                logger.info(f"Stop order submitted: {order.order_id}")
                return order
            else:
                logger.error(f"Failed to submit stop order: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting stop order: {str(e)}")
            return None
    
    def _submit_order(self, order: Order, reduce_only: bool = False) -> Optional[Order]:
        """Submit order to exchange"""
        
        try:
            # Submit to exchange
            result = bitget_client.place_order(
                symbol=order.symbol,
                side=order.side,
                order_type=order.order_type.value,
                size=str(order.size),
                price=str(order.price) if order.price else None,
                reduce_only=reduce_only,
                time_in_force=self.config.time_in_force,
                client_order_id=order.client_order_id
            )
            
            if result and result.get('orderId'):
                order.order_id = result['orderId']
                order.status = OrderStatus.SUBMITTED
                self.orders[order.order_id] = order
                logger.info(f"Order submitted: {order.order_id} ({order.side} {order.size} {order.symbol})")
                return order
            else:
                error_msg = f"Failed to submit order: {result}"
                order.update_status(OrderStatus.FAILED, error_msg)
                logger.error(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Error submitting order: {str(e)}"
            order.update_status(OrderStatus.FAILED, error_msg)
            logger.error(error_msg)
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        
        try:
            result = bitget_client.cancel_order(order.symbol, order_id)
            
            if result:
                order.update_status(OrderStatus.CANCELLED)
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                logger.error(f"Failed to cancel order: {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            return False
    
    def cancel_all_orders(self, symbol: str = None) -> bool:
        """Cancel all orders"""
        
        try:
            if symbol:
                result = bitget_client.cancel_all_orders(symbol)
                # Update local orders
                for order in self.orders.values():
                    if order.symbol == symbol and order.status == OrderStatus.SUBMITTED:
                        order.update_status(OrderStatus.CANCELLED)
            else:
                # Cancel all orders for all symbols
                symbols = set(order.symbol for order in self.orders.values())
                for sym in symbols:
                    bitget_client.cancel_all_orders(sym)
                
                # Update local orders
                for order in self.orders.values():
                    if order.status == OrderStatus.SUBMITTED:
                        order.update_status(OrderStatus.CANCELLED)
            
            logger.info(f"All orders cancelled{' for ' + symbol if symbol else ''}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling all orders: {str(e)}")
            return False
    
    def close_position(self, symbol: str, size: float = None) -> bool:
        """Close a position"""
        
        try:
            # Get current position
            positions = bitget_client.get_positions(symbol)
            if not positions:
                logger.warning(f"No position found for {symbol}")
                return False
            
            position = positions[0]
            position_size = float(position.get('total', 0))
            
            if position_size == 0:
                logger.warning(f"No open position for {symbol}")
                return False
            
            # Determine close side
            position_side = position.get('side', '')
            if position_side.lower() in ['long', 'open_long']:
                close_side = 'close_long'
            else:
                close_side = 'close_short'
            
            # Use provided size or full position size
            close_size = size if size else abs(position_size)
            
            # Place market order to close position
            order = self.place_market_order(
                symbol=symbol,
                side=close_side,
                size=close_size,
                reduce_only=True
            )
            
            if order:
                logger.info(f"Position close order placed: {order.order_id}")
                return True
            else:
                logger.error(f"Failed to place position close order for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {str(e)}")
            return False
    
    def close_all_positions(self) -> bool:
        """Close all open positions"""
        
        try:
            positions = bitget_client.get_positions()
            
            for position in positions:
                position_size = float(position.get('total', 0))
                if position_size != 0:
                    symbol = position.get('symbol', '')
                    self.close_position(symbol)
            
            logger.info("All positions closed")
            return True
            
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")
            return False
    
    def get_position_summary(self) -> Dict[str, Any]:
        """Get position summary"""
        
        try:
            positions = bitget_client.get_positions()
            balance = bitget_client.get_balance()
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'account_balance': {
                    'total_equity': float(balance.get('usdtEquity', 0)),
                    'available_balance': float(balance.get('available', 0)),
                    'margin_used': float(balance.get('locked', 0)),
                    'unrealized_pnl': float(balance.get('unrealizedPL', 0))
                },
                'positions': [],
                'total_positions': 0,
                'total_unrealized_pnl': 0.0
            }
            
            for pos in positions:
                position_size = float(pos.get('total', 0))
                if position_size != 0:
                    position_info = {
                        'symbol': pos.get('symbol', ''),
                        'side': pos.get('side', ''),
                        'size': position_size,
                        'entry_price': float(pos.get('averageOpenPrice', 0)),
                        'current_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedPL', 0)),
                        'margin_coin': pos.get('marginCoin', ''),
                        'leverage': int(pos.get('leverage', 1))
                    }
                    summary['positions'].append(position_info)
                    summary['total_unrealized_pnl'] += position_info['unrealized_pnl']
            
            summary['total_positions'] = len(summary['positions'])
            return summary
            
        except Exception as e:
            logger.error(f"Error getting position summary: {str(e)}")
            return {}
    
    def _monitor_positions(self):
        """Monitor positions in background thread"""
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Update risk metrics and monitor positions
                risk_manager.monitor_positions()
                
                # Check for emergency conditions
                risk_summary = risk_manager.get_risk_summary()
                if risk_summary.get('risk_level') == 'critical':
                    logger.warning("Critical risk level detected")
                    
                    # Consider emergency actions here
                    if risk_summary.get('daily_pnl', 0) < -config.risk_management.max_daily_loss:
                        logger.critical("Daily loss limit exceeded - considering emergency stop")
                        # risk_manager.activate_emergency_stop("Daily loss limit exceeded")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in position monitoring: {str(e)}")
                time.sleep(10)
    
    def _monitor_orders(self):
        """Monitor orders in background thread"""
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Update order statuses
                for order_id, order in list(self.orders.items()):
                    if order.status == OrderStatus.SUBMITTED:
                        self._update_order_status(order)
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in order monitoring: {str(e)}")
                time.sleep(5)
    
    def _update_order_status(self, order: Order):
        """Update order status from exchange"""
        
        try:
            # Get open orders
            open_orders = bitget_client.get_open_orders(order.symbol)
            
            # Check if order is still open
            order_found = False
            for open_order in open_orders:
                if open_order.get('orderId') == order.order_id:
                    order_found = True
                    break
            
            if not order_found:
                # Order is no longer open, check if it was filled
                fills = bitget_client.get_fills(order.symbol, limit=50)
                
                for fill in fills:
                    if fill.get('orderId') == order.order_id:
                        # Order was filled
                        order.status = OrderStatus.FILLED
                        order.filled_size = float(fill.get('baseVolume', 0))
                        order.filled_price = float(fill.get('price', 0))
                        order.updated_at = datetime.now()
                        
                        # Create trade record
                        trade = Trade(
                            trade_id=fill.get('tradeId', ''),
                            order_id=order.order_id,
                            symbol=order.symbol,
                            side=order.side,
                            size=order.filled_size,
                            price=order.filled_price,
                            timestamp=datetime.now(),
                            commission=float(fill.get('fee', 0)),
                            commission_asset=fill.get('feeMarginCoin', 'USDT')
                        )
                        self.trades.append(trade)
                        
                        logger.info(f"Order filled: {order.order_id} at {order.filled_price}")
                        break
                else:
                    # Order was cancelled or failed
                    order.status = OrderStatus.CANCELLED
                    order.updated_at = datetime.now()
                    
        except Exception as e:
            logger.error(f"Error updating order status for {order.order_id}: {str(e)}")
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Get comprehensive trading summary"""
        
        position_summary = self.get_position_summary()
        risk_summary = risk_manager.get_risk_summary()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'engine_status': {
                'running': self.is_running,
                'total_orders': len(self.orders),
                'total_trades': len(self.trades),
                'active_orders': len([o for o in self.orders.values() if o.status == OrderStatus.SUBMITTED])
            },
            'positions': position_summary,
            'risk_metrics': risk_summary,
            'recent_orders': [
                {
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'size': order.size,
                    'price': order.price,
                    'status': order.status.value,
                    'created_at': order.created_at.isoformat()
                }
                for order in sorted(self.orders.values(), 
                                  key=lambda x: x.created_at, reverse=True)[:10]
            ],
            'recent_trades': [
                {
                    'trade_id': trade.trade_id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'size': trade.size,
                    'price': trade.price,
                    'timestamp': trade.timestamp.isoformat()
                }
                for trade in sorted(self.trades, 
                                  key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }

# Global trading engine instance
trading_engine = TradingEngine()