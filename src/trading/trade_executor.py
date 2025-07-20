"""
🚀 Alpine Trade Executor - Optimized Execution Engine
Handles trade execution for both Alpine and Volume Anomaly bots
with advanced order management and execution optimization
"""

import ccxt
import time
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
from ..core.config import TradingConfig, get_exchange_config

class OptimizedTradeExecutor:
    """⚡ Optimized Trade Execution Engine"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.config = TradingConfig()
        self.pending_orders = {}
        self.execution_lock = threading.Lock()
        self.order_history = []
        
        # Execution optimization settings
        self.use_limit_orders = True  # Use limit orders for better fills
        self.price_improvement_bps = 5  # 0.05% price improvement
        self.max_slippage_pct = 0.2  # Maximum allowed slippage
        self.retry_attempts = 3
        self.order_timeout = 10  # seconds
        
    def execute_signal(self, signal: Dict) -> Optional[Dict]:
        """Execute a trading signal with optimized logic"""
        with self.execution_lock:
            try:
                symbol = signal['symbol']
                # Support multiple naming conventions – bots may provide either
                # `action` (BUY/SELL) or `type` (LONG/SHORT)
                if 'action' in signal:
                    action = signal['action'].upper()
                elif 'type' in signal:
                    action = 'BUY' if signal['type'].upper() == 'LONG' else 'SELL'
                else:
                    logger.warning("Signal missing 'action'/'type' field")
                    return None
                
                confidence = signal.get('confidence', 0)
                
                # Validate signal
                if confidence < 50:
                    logger.warning(f"Signal confidence too low: {confidence}%")
                    return None
                
                # Calculate position size
                position_size = self._calculate_position_size(signal)
                if position_size <= 0:
                    logger.warning("Invalid position size calculated")
                    return None
                
                # Get current market data
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate entry price with improvement
                entry_price = self._calculate_entry_price(
                    current_price, 
                    action, 
                    self.use_limit_orders
                )
                
                # Calculate stop loss and take profit
                stop_loss, take_profit = self._calculate_risk_levels(
                    entry_price, 
                    action, 
                    signal
                )
                
                # Place the order
                order = self._place_optimized_order(
                    symbol=symbol,
                    side='buy' if action == 'BUY' else 'sell',
                    amount=position_size,
                    price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if order:
                    logger.success(f"✅ Order executed: {symbol} {action} @ {entry_price}")
                    self._record_order(order, signal)
                    return order
                
            except Exception as e:
                logger.error(f"❌ Execution error: {str(e)}")
                return None
    
    def _calculate_position_size(self, signal: Dict) -> float:
        """Calculate optimal position size based on risk and confidence"""
        try:
            # Get futures account balance
            balance = self.exchange.fetch_balance({'type': 'swap'})
            
            # Extract USDT futures balance
            free_usdt = 0
            for info in balance.get('info', []):
                if info.get('marginCoin') == 'USDT':
                    free_usdt = float(info.get('available', 0))
                    break
            
            if free_usdt == 0:
                # Fallback to regular balance
                free_usdt = balance.get('USDT', {}).get('free', 0)
            
            # Base position size (this is MARGIN not position value)
            # Target: $175 notional with 50x leverage = $3.50 margin
            target_margin = 3.50  # $3.50 margin for $175 notional at 50x
            base_margin = min(free_usdt * (self.config.position_size_pct / 100), target_margin)
            
            # Adjust for confidence
            confidence = signal.get('confidence', 50)
            confidence_multiplier = 0.8 + (confidence / 500)  # 0.8x to 1.0x (targeting $3.50 margin)
            
            # Adjust for confluence
            if signal.get('confluence', False) or signal.get('is_confluence', False):
                confidence_multiplier *= self.config.confluence_position_multiplier
            
            # Calculate final margin size
            margin_size = base_margin * confidence_multiplier
            
            # Target $175 notional, so cap margin at $3.50 for 50x leverage
            max_margin = 3.50  # $3.50 margin = $175 notional at 50x
            margin_size = min(margin_size, max_margin)
            
            # Get leverage from signal or use config default
            leverage = signal.get('max_leverage', self.config.leverage)
            leverage = max(leverage, 50)  # Minimum 50x leverage as requested
            leverage = min(leverage, 125)  # Cap at 125x leverage maximum
            
            # Calculate actual position size using leverage
            position_size = margin_size * leverage
            
            # Convert USD position size to asset amount
            symbol = signal['symbol']
            
            # Get current price to convert USD to asset amount
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                position_size_asset = position_size / current_price
            except Exception as e:
                logger.error(f"Failed to get ticker for {symbol}: {e}")
                return 0
            
            # Check minimum size requirements
            markets = self.exchange.markets
            if symbol in markets:
                min_size = markets[symbol]['limits']['amount']['min']
                if position_size_asset < min_size:
                    logger.warning(f"Position size {position_size_asset:.4f} below minimum {min_size} for {symbol}")
                    # Try to use minimum size if margin allows
                    min_position_value = min_size * current_price
                    if min_position_value / leverage <= margin_size:
                        position_size_asset = min_size
                        logger.info(f"Using minimum position size: {min_size} for {symbol}")
                    else:
                        return 0
                
                # Also check minimum notional value (this is important for leverage)
                min_notional = markets[symbol]['limits']['cost']['min']
                if min_notional and position_size < min_notional:
                    logger.warning(f"Position value ${position_size:.2f} below minimum ${min_notional} for {symbol}")
                    # Try to use minimum notional if margin allows
                    if min_notional / leverage <= margin_size:
                        position_size = min_notional
                        position_size_asset = min_notional / current_price
                        logger.info(f"Using minimum notional value: ${min_notional} for {symbol}")
                    else:
                        return 0
            
            logger.info(f"💰 Position calculation: ${margin_size:.2f} margin × {leverage}x = ${position_size:.2f} position = {position_size_asset:.4f} {symbol.split('/')[0]}")
            return position_size_asset
            
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return 0
    
    def _calculate_entry_price(self, current_price: float, action: str, use_limit: bool) -> float:
        """Calculate optimal entry price"""
        if not use_limit:
            return current_price
        
        # Apply price improvement for limit orders
        improvement = current_price * (self.price_improvement_bps / 10000)
        
        if action == 'BUY':
            # Buy slightly below market for better fill
            return current_price - improvement
        else:
            # Sell slightly above market for better fill
            return current_price + improvement
    
    def _calculate_risk_levels(self, entry_price: float, action: str, signal: Dict) -> Tuple[float, float]:
        """Calculate dynamic stop loss and take profit levels"""
        # Use ATR-based stops if available
        if self.config.use_dynamic_stop_loss and 'atr' in signal and signal['atr'] is not None:
            atr = signal['atr']
            stop_distance = atr * self.config.atr_multiplier
            
            # Ensure within min/max bounds
            stop_pct = (stop_distance / entry_price) * 100
            stop_pct = max(self.config.min_stop_loss_pct, 
                          min(stop_pct, self.config.max_stop_loss_pct))
        else:
            stop_pct = self.config.stop_loss_pct
        
        take_profit_pct = self.config.take_profit_pct
        
        if action == 'BUY':
            stop_loss = entry_price * (1 - stop_pct / 100)
            take_profit = entry_price * (1 + take_profit_pct / 100)
        else:
            stop_loss = entry_price * (1 + stop_pct / 100)
            take_profit = entry_price * (1 - take_profit_pct / 100)
        
        return stop_loss, take_profit
    
    def _place_optimized_order(self, symbol: str, side: str, amount: float, 
                              price: float, stop_loss: float, take_profit: float) -> Optional[Dict]:
        """Place order with retry logic and optimization"""
        for attempt in range(self.retry_attempts):
            try:
                # Place main order with futures-specific parameters
                params = {
                    'marginCoin': 'USDT',  # Required for Bitget futures
                    'timeInForce': 'IOC'   # Immediate or Cancel
                }
                
                if self.use_limit_orders:
                    order = self.exchange.create_limit_order(
                        symbol=symbol,
                        side=side,
                        amount=amount,
                        price=price,
                        params=params
                    )
                    
                    # Wait for fill or timeout
                    start_time = time.time()
                    while time.time() - start_time < self.order_timeout:
                        order_status = self.exchange.fetch_order(order['id'], symbol)
                        if order_status['status'] == 'closed':
                            break
                        time.sleep(0.5)
                    
                    # If not filled, cancel and use market order
                    if order_status['status'] != 'closed':
                        self.exchange.cancel_order(order['id'], symbol)
                        logger.warning("Limit order timeout, using market order")
                        order = self.exchange.create_market_order(
                            symbol=symbol,
                            side=side,
                            amount=amount,
                            params=params
                        )
                else:
                    order = self.exchange.create_market_order(
                        symbol=symbol,
                        side=side,
                        amount=amount,
                        params=params
                    )
                
                # Place stop loss order
                if stop_loss > 0:
                    stop_side = 'sell' if side == 'buy' else 'buy'
                    try:
                        # For Bitget, use 'stop' order type with proper parameters
                        stop_params = {
                            'stopPrice': stop_loss,
                            'reduceOnly': True,
                            'marginCoin': 'USDT',
                            'timeInForce': 'GTC'
                        }
                        self.exchange.create_order(
                            symbol=symbol,
                            type='stop',
                            side=stop_side,
                            amount=amount,
                            price=stop_loss,  # Use stop_loss as the trigger price
                            params=stop_params
                        )
                        logger.info(f"✅ Stop loss order placed: {stop_loss}")
                    except Exception as e:
                        logger.error(f"❌ Stop loss order failed: {e}")
                
                # Place take profit order
                if take_profit > 0:
                    tp_side = 'sell' if side == 'buy' else 'buy'
                    try:
                        # For Bitget, use 'limit' order type for take profit
                        tp_params = {
                            'reduceOnly': True,
                            'marginCoin': 'USDT',
                            'timeInForce': 'GTC'
                        }
                        self.exchange.create_order(
                            symbol=symbol,
                            type='limit',
                            side=tp_side,
                            amount=amount,
                            price=take_profit,
                            params=tp_params
                        )
                        logger.info(f"✅ Take profit order placed: {take_profit}")
                    except Exception as e:
                        logger.error(f"❌ Take profit order failed: {e}")
                
                return order
                
            except Exception as e:
                logger.error(f"Order placement error (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(1)
                else:
                    return None
    
    def _record_order(self, order: Dict, signal: Dict):
        """Record order for analysis"""
        self.order_history.append({
            'timestamp': datetime.now(),
            'order': order,
            'signal': signal
        })
        
        # Keep only last 1000 orders
        if len(self.order_history) > 1000:
            self.order_history.pop(0)
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        if not self.order_history:
            return {
                'total_orders': 0,
                'avg_fill_time': 0,
                'success_rate': 0
            }
        
        total_orders = len(self.order_history)
        successful_orders = sum(1 for o in self.order_history if o['order']['status'] == 'closed')
        
        # Calculate actual fill times
        fill_times = []
        for o in self.order_history:
            if o['order']['status'] == 'closed' and 'created_at' in o and 'filled_at' in o:
                try:
                    created_at = datetime.fromisoformat(o['created_at'].replace('Z', '+00:00'))
                    filled_at = datetime.fromisoformat(o['filled_at'].replace('Z', '+00:00'))
                    fill_time = (filled_at - created_at).total_seconds()
                    fill_times.append(fill_time)
                except (ValueError, TypeError):
                    continue
        
        avg_fill_time = sum(fill_times) / len(fill_times) if fill_times else 0
        
        return {
            'total_orders': total_orders,
            'success_rate': (successful_orders / total_orders) * 100 if total_orders > 0 else 0,
            'avg_fill_time': avg_fill_time
        }

class TradingOrchestrator:
    """🎼 Orchestrates multiple trading bots with the execution engine"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.exchange = None
        self.executor = None
        self.bots = []
        self.running = False
        
    def initialize(self) -> bool:
        """Initialize exchange and executor"""
        try:
            # Create exchange connection
            self.exchange = ccxt.bitget(get_exchange_config())
            self.exchange.load_markets()
            
            # Create executor
            self.executor = OptimizedTradeExecutor(self.exchange)
            
            logger.success("✅ Trading orchestrator initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def add_bot(self, bot):
        """Add a trading bot to the orchestrator"""
        self.bots.append(bot)
        logger.info(f"Added bot: {bot.__class__.__name__}")
    
    def start(self):
        """Start all bots"""
        self.running = True
        
        # Start bot threads
        for bot in self.bots:
            thread = threading.Thread(target=self._run_bot, args=(bot,), daemon=True)
            thread.start()
        
        logger.success("🚀 Trading orchestrator started")
    
    def _run_bot(self, bot):
        """Run a single bot (polls for new trading signals)"""
        while self.running:
            try:
                # ------------------------------------------------------------------
                # Flexible signal retrieval
                # ------------------------------------------------------------------
                if hasattr(bot, "generate_signals"):
                    signals = bot.generate_signals()
                elif hasattr(bot, "analyze_signals"):
                    # AlpineBot exposes `analyze_signals` instead – keep legacy support✅
                    signals = bot.analyze_signals()
                else:
                    logger.warning(f"{bot.__class__.__name__} has no signal generation method")
                    signals = []

                # Execute any qualifying signals
                for signal in signals:
                    if signal.get("confidence", 0) > 50:
                        self.executor.execute_signal(signal)

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Bot error ({bot.__class__.__name__}): {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop all bots"""
        self.running = False
        logger.info("Trading orchestrator stopped")