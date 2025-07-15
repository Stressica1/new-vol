import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
from enum import Enum
import json
import pandas as pd
import numpy as np
import ta

from config import TradingConfig
from bitget_client import bitget_client

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    margin_coin: str
    leverage: int
    timestamp: datetime
    
    @property
    def notional_value(self) -> float:
        return self.size * self.current_price
    
    @property
    def pnl_percentage(self) -> float:
        if self.entry_price == 0:
            return 0
        return (self.unrealized_pnl / (self.size * self.entry_price)) * 100

@dataclass
class RiskMetrics:
    total_equity: float
    available_balance: float
    total_margin_used: float
    unrealized_pnl: float
    daily_pnl: float
    open_positions: int
    total_exposure: float
    max_drawdown: float
    risk_level: RiskLevel
    
@dataclass
class VolatilityMetrics:
    """📊 Volatility metrics for dynamic risk management"""
    atr: float
    volatility_score: float
    risk_adjustment: float
    dynamic_stop_pct: float
    
class RiskManager:
    """Comprehensive Risk Management System with Dynamic Volatility Analysis"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.trading_config = TradingConfig()
        self.daily_start_balance = 0.0
        self.daily_high_balance = 0.0
        self.daily_low_balance = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        self.risk_metrics: Optional[RiskMetrics] = None
        self.emergency_stop = False
        
        # 📊 Volatility tracking for dynamic stops
        self.volatility_cache: Dict[str, VolatilityMetrics] = {}
        self.price_data_cache: Dict[str, pd.DataFrame] = {}
        
        logger.info("🛡️ Enhanced Risk Manager with Dynamic Volatility Analysis initialized")
    
    def calculate_atr_volatility(self, df: pd.DataFrame, period: int = 14) -> float:
        """📈 Calculate Average True Range for volatility measurement"""
        try:
            if len(df) < period:
                logger.warning(f"⚠️ Insufficient data for ATR calculation: {len(df)} < {period}")
                return 0.02  # Default 2% volatility
            
            # Calculate ATR using ta library
            atr = ta.volatility.AverageTrueRange(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=period
            ).average_true_range()
            
            current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.02
            
            # Convert ATR to percentage of current price
            current_price = df['close'].iloc[-1]
            atr_percentage = (current_atr / current_price) if current_price > 0 else 0.02
            
            logger.debug(f"📊 ATR calculated: {current_atr:.4f} ({atr_percentage:.2%})")
            return atr_percentage
            
        except Exception as e:
            logger.error(f"❌ Error calculating ATR: {e}")
            return 0.02  # Default 2% volatility
    
    def calculate_dynamic_stop_loss(self, symbol: str, entry_price: float, side: str, 
                                  market_data: pd.DataFrame = None) -> float:
        """🎯 Calculate dynamic stop loss based on volatility (ATR)"""
        try:
            # Get current volatility metrics
            volatility_metrics = self.get_volatility_metrics(symbol, market_data)
            
            # Use dynamic stop percentage based on volatility
            stop_loss_pct = volatility_metrics.dynamic_stop_pct
            
            logger.info(f"🎯 Dynamic stop loss for {symbol}: {stop_loss_pct:.2%} (ATR-based)")
            
            if side.lower() in ['long', 'open_long', 'buy']:
                stop_loss_price = entry_price * (1 - stop_loss_pct)
            else:  # short position
                stop_loss_price = entry_price * (1 + stop_loss_pct)
            
            logger.info(f"🛡️ Dynamic stop loss price: {stop_loss_price:.4f} for {symbol}")
            return stop_loss_price
            
        except Exception as e:
            logger.error(f"❌ Error calculating dynamic stop loss: {e}")
            # Fallback to static stop loss
            return self.calculate_stop_loss_price(symbol, entry_price, side)
    
    def get_volatility_metrics(self, symbol: str, market_data: pd.DataFrame = None) -> VolatilityMetrics:
        """📊 Get or calculate volatility metrics for a symbol"""
        try:
            # Use provided data or get from cache
            if market_data is not None and len(market_data) > 0:
                df = market_data
            elif symbol in self.price_data_cache:
                df = self.price_data_cache[symbol]
            else:
                # Create default data if none available
                logger.warning(f"⚠️ No market data available for {symbol}, using defaults")
                return VolatilityMetrics(
                    atr=0.02,
                    volatility_score=1.0,
                    risk_adjustment=1.0,
                    dynamic_stop_pct=self.trading_config.stop_loss_pct / 100
                )
            
            # Calculate ATR
            atr = self.calculate_atr_volatility(df, self.trading_config.atr_period)
            
            # Calculate volatility score (normalized)
            volatility_score = min(max(atr / 0.02, 0.5), 3.0)  # Normalize between 0.5-3.0
            
            # Calculate risk adjustment
            risk_adjustment = 1.0 + (volatility_score - 1.0) * 0.5
            
            # Calculate dynamic stop loss percentage
            base_stop = self.trading_config.min_stop_loss_pct / 100
            max_stop = self.trading_config.max_stop_loss_pct / 100
            
            # ATR-based dynamic stop
            atr_multiplier = self.trading_config.atr_multiplier
            dynamic_stop_pct = min(max(atr * atr_multiplier, base_stop), max_stop)
            
            volatility_metrics = VolatilityMetrics(
                atr=atr,
                volatility_score=volatility_score,
                risk_adjustment=risk_adjustment,
                dynamic_stop_pct=dynamic_stop_pct
            )
            
            # Cache the metrics
            self.volatility_cache[symbol] = volatility_metrics
            
            logger.debug(f"📊 Volatility metrics for {symbol}: ATR={atr:.3%}, Stop={dynamic_stop_pct:.2%}")
            return volatility_metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating volatility metrics: {e}")
            return VolatilityMetrics(
                atr=0.02,
                volatility_score=1.0,
                risk_adjustment=1.0,
                dynamic_stop_pct=0.015  # 1.5% default
            )
    
    def calculate_confluence_position_size(self, symbol: str, entry_price: float, 
                                         is_confluence_signal: bool = False,
                                         stop_loss_price: float = None) -> float:
        """💰 Enhanced position sizing with confluence boost"""
        try:
            # Get account metrics
            risk_metrics = self.calculate_risk_metrics()
            total_equity = max(risk_metrics.total_equity, 1000.0)  # Minimum for calculation
            
            # Base position size calculation
            base_position_value = total_equity * (self.trading_config.position_size_pct / 100)
            
            # Apply confluence multiplier if this is a confluence signal
            if is_confluence_signal:
                position_value = base_position_value * self.trading_config.confluence_position_multiplier
                logger.info(f"🚀 Confluence signal detected! Position size boosted by {self.trading_config.confluence_position_multiplier:.1%}")
            else:
                position_value = base_position_value
            
            # Get volatility adjustment
            volatility_metrics = self.get_volatility_metrics(symbol)
            
            # Adjust position size based on volatility (higher volatility = smaller position)
            volatility_adjustment = 1.0 / volatility_metrics.risk_adjustment
            adjusted_position_value = position_value * volatility_adjustment
            
            # Calculate position size in contracts/units
            position_size = adjusted_position_value / entry_price
            
            # Ensure minimum order size
            min_size = self.trading_config.min_order_size / entry_price
            if position_size < min_size:
                position_size = min_size
            
            logger.info(f"💰 Position size calculated: {position_size:.4f} for {symbol}")
            logger.info(f"   📊 Base value: ${base_position_value:.2f}")
            if is_confluence_signal:
                logger.info(f"   🚀 Confluence boost: +{(self.trading_config.confluence_position_multiplier-1)*100:.0f}%")
            logger.info(f"   📈 Volatility adj: {volatility_adjustment:.2f}x")
            logger.info(f"   💵 Final value: ${adjusted_position_value:.2f}")
            
            return position_size
            
        except Exception as e:
            logger.error(f"❌ Error calculating confluence position size: {e}")
            # Fallback to basic calculation
            return self.calculate_position_size(symbol, entry_price, stop_loss_price)

    def update_daily_metrics(self, current_balance: float):
        """Update daily metrics"""
        current_date = datetime.now().date()
        
        # Reset daily metrics if new day
        if current_date > self.last_reset_date:
            self.daily_start_balance = current_balance
            self.daily_high_balance = current_balance
            self.daily_low_balance = current_balance
            self.daily_trades = 0
            self.last_reset_date = current_date
            logger.info(f"Daily metrics reset for {current_date}")
        
        # Update daily highs and lows
        self.daily_high_balance = max(self.daily_high_balance, current_balance)
        self.daily_low_balance = min(self.daily_low_balance, current_balance)
    
    def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate current risk metrics"""
        try:
            # Get account info
            account_info = bitget_client.get_balance()
            if not account_info:
                logger.error("Failed to get account info for risk calculation")
                return self._create_default_risk_metrics()
            
            # Get positions
            positions = bitget_client.get_positions()
            
            # Filter for active positions only (non-zero contracts)
            active_positions = [
                pos for pos in positions 
                if pos.get('contracts', 0) > 0 or pos.get('contractSize', 0) > 0
            ]
            
            # Extract key metrics
            total_equity = float(account_info.get('usdtEquity', 0))
            available_balance = float(account_info.get('available', 0))
            total_margin_used = float(account_info.get('locked', 0))
            unrealized_pnl = float(account_info.get('unrealizedPL', 0))
            
            # Update daily metrics
            self.update_daily_metrics(total_equity)
            
            # Calculate daily PnL
            daily_pnl = total_equity - self.daily_start_balance if self.daily_start_balance > 0 else 0
            
            # Calculate total exposure (using active positions)
            total_exposure = sum(float(pos.get('total', 0)) for pos in active_positions)
            
            # Calculate max drawdown
            max_drawdown = 0
            if self.daily_high_balance > 0:
                max_drawdown = (self.daily_high_balance - total_equity) / self.daily_high_balance
            
            # Determine risk level (using active positions count)
            risk_level = self._determine_risk_level(
                daily_pnl, max_drawdown, total_exposure, total_equity, len(active_positions)
            )
            
            self.risk_metrics = RiskMetrics(
                total_equity=total_equity,
                available_balance=available_balance,
                total_margin_used=total_margin_used,
                unrealized_pnl=unrealized_pnl,
                daily_pnl=daily_pnl,
                open_positions=len(active_positions),
                total_exposure=total_exposure,
                max_drawdown=max_drawdown,
                risk_level=risk_level
            )
            
            logger.info(f"Risk metrics updated: {risk_level.value} risk level")
            return self.risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            return self._create_default_risk_metrics()
    
    def _create_default_risk_metrics(self) -> RiskMetrics:
        """Create default risk metrics"""
        return RiskMetrics(
            total_equity=0.0,
            available_balance=0.0,
            total_margin_used=0.0,
            unrealized_pnl=0.0,
            daily_pnl=0.0,
            open_positions=0,
            total_exposure=0.0,
            max_drawdown=0.0,
            risk_level=RiskLevel.HIGH
        )
    
    def _determine_risk_level(self, daily_pnl: float, max_drawdown: float, 
                            total_exposure: float, total_equity: float, 
                            open_positions: int) -> RiskLevel:
        """Determine current risk level"""
        
        # Check for critical conditions
        if (daily_pnl < -self.config.max_daily_loss or 
            max_drawdown > self.config.max_drawdown or
            open_positions > self.config.max_open_positions):
            return RiskLevel.CRITICAL
        
        # Check for high risk
        if (daily_pnl < -self.config.max_daily_loss * 0.7 or
            max_drawdown > self.config.max_drawdown * 0.7 or
            total_exposure > total_equity * 0.8):
            return RiskLevel.HIGH
        
        # Check for medium risk
        if (daily_pnl < -self.config.max_daily_loss * 0.4 or
            max_drawdown > self.config.max_drawdown * 0.4 or
            total_exposure > total_equity * 0.5):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def can_open_position(self, symbol: str, side: str, size: float, price: float) -> Tuple[bool, str]:
        """Check if a position can be opened"""
        
        # Check emergency stop
        if self.emergency_stop:
            return False, "Emergency stop activated"
        
        # Update risk metrics
        risk_metrics = self.calculate_risk_metrics()
        
        # Check critical risk level
        if risk_metrics.risk_level == RiskLevel.CRITICAL:
            return False, "Critical risk level - no new positions allowed"
        
        # Check maximum open positions
        if risk_metrics.open_positions >= self.config.max_open_positions:
            return False, f"Maximum open positions ({self.config.max_open_positions}) reached"
        
        # Check daily loss limit
        if risk_metrics.daily_pnl < -self.config.max_daily_loss:
            return False, f"Daily loss limit ({self.config.max_daily_loss}) exceeded"
        
        # Check maximum drawdown
        if risk_metrics.max_drawdown > self.config.max_drawdown:
            return False, f"Maximum drawdown ({self.config.max_drawdown:.2%}) exceeded"
        
        # Check position size
        notional_value = size * price
        if notional_value > self.config.max_position_size:
            return False, f"Position size ({notional_value:.2f}) exceeds maximum ({self.config.max_position_size})"
        
        # Check available balance
        required_margin = notional_value / self.trading_config.leverage
        if required_margin > risk_metrics.available_balance:
            return False, f"Insufficient balance for position (required: {required_margin:.2f}, available: {risk_metrics.available_balance:.2f})"
        
        # Check minimum order size
        if notional_value < self.trading_config.min_order_size:
            return False, f"Position size ({notional_value:.2f}) below minimum ({self.trading_config.min_order_size})"
        
        return True, "Position can be opened"
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss_price: float = None) -> float:
        """Calculate optimal position size based on risk parameters"""
        
        risk_metrics = self.calculate_risk_metrics()
        
        if risk_metrics.total_equity <= 0:
            logger.warning("No equity available for position sizing")
            return 0.0
        
        # Calculate risk amount
        risk_amount = risk_metrics.total_equity * self.config.risk_per_trade
        
        # If stop loss is provided, calculate size based on stop loss distance
        if stop_loss_price and stop_loss_price > 0:
            price_diff = abs(entry_price - stop_loss_price)
            if price_diff > 0:
                position_size = risk_amount / price_diff
            else:
                position_size = risk_amount / entry_price
        else:
            # Use default risk percentage
            position_size = risk_amount / entry_price
        
        # Apply maximum position size limit
        max_size_by_value = self.config.max_position_size / entry_price
        position_size = min(position_size, max_size_by_value)
        
        # Ensure minimum order size
        min_size = self.trading_config.min_order_size / entry_price
        if position_size < min_size:
            position_size = min_size
        
        logger.info(f"Calculated position size: {position_size:.4f} for {symbol}")
        return position_size
    
    def calculate_stop_loss_price(self, symbol: str, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        
        if side.lower() == 'long' or side.lower() == 'open_long':
            stop_loss_price = entry_price * (1 - self.config.stop_loss_percentage)
        else:  # short position
            stop_loss_price = entry_price * (1 + self.config.stop_loss_percentage)
        
        logger.info(f"Stop loss price calculated: {stop_loss_price:.4f} for {symbol}")
        return stop_loss_price
    
    def calculate_take_profit_price(self, symbol: str, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        
        if side.lower() == 'long' or side.lower() == 'open_long':
            take_profit_price = entry_price * (1 + self.config.take_profit_percentage)
        else:  # short position
            take_profit_price = entry_price * (1 - self.config.take_profit_percentage)
        
        logger.info(f"Take profit price calculated: {take_profit_price:.4f} for {symbol}")
        return take_profit_price
    
    def should_close_position(self, position: Position) -> Tuple[bool, str]:
        """Check if a position should be closed"""
        
        # Check emergency stop
        if self.emergency_stop:
            return True, "Emergency stop activated"
        
        # Check stop loss
        if self.config.enable_stop_loss:
            if position.side.lower() in ['long', 'open_long']:
                if position.current_price <= position.entry_price * (1 - self.config.stop_loss_percentage):
                    return True, "Stop loss triggered"
            else:  # short position
                if position.current_price >= position.entry_price * (1 + self.config.stop_loss_percentage):
                    return True, "Stop loss triggered"
        
        # Check take profit
        if self.config.enable_take_profit:
            if position.side.lower() in ['long', 'open_long']:
                if position.current_price >= position.entry_price * (1 + self.config.take_profit_percentage):
                    return True, "Take profit triggered"
            else:  # short position
                if position.current_price <= position.entry_price * (1 - self.config.take_profit_percentage):
                    return True, "Take profit triggered"
        
        return False, "No exit conditions met"
    
    def activate_emergency_stop(self, reason: str = "Manual activation"):
        """Activate emergency stop"""
        self.emergency_stop = True
        logger.critical(f"Emergency stop activated: {reason}")
    
    def deactivate_emergency_stop(self):
        """Deactivate emergency stop"""
        self.emergency_stop = False
        logger.info("Emergency stop deactivated")
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        
        risk_metrics = self.calculate_risk_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'emergency_stop': self.emergency_stop,
            'risk_level': risk_metrics.risk_level.value,
            'account_metrics': {
                'total_equity': risk_metrics.total_equity,
                'available_balance': risk_metrics.available_balance,
                'total_margin_used': risk_metrics.total_margin_used,
                'unrealized_pnl': risk_metrics.unrealized_pnl
            },
            'daily_metrics': {
                'daily_pnl': risk_metrics.daily_pnl,
                'daily_start_balance': self.daily_start_balance,
                'daily_high_balance': self.daily_high_balance,
                'daily_low_balance': self.daily_low_balance,
                'daily_trades': self.daily_trades
            },
            'position_metrics': {
                'open_positions': risk_metrics.open_positions,
                'total_exposure': risk_metrics.total_exposure,
                'max_drawdown': risk_metrics.max_drawdown
            },
            'risk_limits': {
                'max_position_size': self.config.max_position_size,
                'max_daily_loss': self.config.max_daily_loss,
                'max_drawdown': self.config.max_drawdown,
                'max_open_positions': self.config.max_open_positions,
                'risk_per_trade': self.config.risk_per_trade
            }
        }
    
    def monitor_positions(self):
        """Monitor all open positions for risk management"""
        
        try:
            positions = bitget_client.get_positions()
            
            for pos_data in positions:
                if float(pos_data.get('total', 0)) == 0:
                    continue
                    
                # Create position object
                position = Position(
                    symbol=pos_data.get('symbol', ''),
                    side=pos_data.get('side', ''),
                    size=float(pos_data.get('total', 0)),
                    entry_price=float(pos_data.get('averageOpenPrice', 0)),
                    current_price=float(pos_data.get('markPrice', 0)),
                    unrealized_pnl=float(pos_data.get('unrealizedPL', 0)),
                    margin_coin=pos_data.get('marginCoin', 'USDT'),
                    leverage=int(pos_data.get('leverage', 1)),
                    timestamp=datetime.now()
                )
                
                # Check if position should be closed
                should_close, reason = self.should_close_position(position)
                
                if should_close:
                    logger.warning(f"Position {position.symbol} should be closed: {reason}")
                    # Note: Actual closing logic would be implemented in the trading engine
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {str(e)}")

# Global risk manager instance
risk_manager = RiskManager()