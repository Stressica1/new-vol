"""
💰 Enhanced Position Sizing System
Properly handles budget constraints, leverage settings, and minimum position requirements
"""

import math
from typing import Dict, Tuple, Optional, Union
from dataclasses import dataclass
from config import TradingConfig

# Simple logger for this module
import logging
logger = logging.getLogger(__name__)

@dataclass
class PositionSizingConfig:
    """Position sizing configuration with leverage and budget constraints"""
    min_order_size_usdt: float = 10.0  # Minimum order size in USDT
    max_leverage: int = 35  # Maximum leverage allowed
    risk_per_trade_pct: float = 2.0  # Risk per trade as percentage of account
    max_position_size_usdt: float = 200.0  # Maximum position size in USDT
    account_balance: float = 1000.0  # Current account balance
    available_margin: float = 1000.0  # Available margin for trading
    
    def __post_init__(self):
        """Validate configuration"""
        if self.min_order_size_usdt <= 0:
            raise ValueError("Minimum order size must be positive")
        if self.max_leverage <= 0:
            raise ValueError("Maximum leverage must be positive")
        if self.risk_per_trade_pct <= 0 or self.risk_per_trade_pct > 100:
            raise ValueError("Risk per trade must be between 0 and 100%")

class PositionSizer:
    """Enhanced position sizing with leverage and budget constraints"""
    
    def __init__(self, config: PositionSizingConfig):
        self.config = config
        self.trading_config = TradingConfig()
        logger.info(f"💰 Position Sizer initialized with {config.max_leverage}x leverage")
    
    def calculate_required_capital(self, position_size_usdt: float, leverage: int) -> float:
        """Calculate the actual capital required for a position with leverage"""
        if leverage <= 0:
            raise ValueError("Leverage must be positive")
        
        required_capital = position_size_usdt / leverage
        logger.debug(f"💰 Required capital: {position_size_usdt} USDT / {leverage}x = {required_capital:.2f} USDT")
        return required_capital
    
    def calculate_max_position_with_leverage(self, available_capital: float, leverage: int) -> float:
        """Calculate maximum position size possible with given capital and leverage"""
        if leverage <= 0:
            raise ValueError("Leverage must be positive")
        
        max_position = available_capital * leverage
        logger.debug(f"💰 Max position: {available_capital} USDT * {leverage}x = {max_position:.2f} USDT")
        return max_position
    
    def calculate_optimal_leverage(self, desired_position_size: float, available_capital: float) -> int:
        """Calculate optimal leverage for desired position size with available capital"""
        if available_capital <= 0:
            raise ValueError("Available capital must be positive")
        
        required_leverage = desired_position_size / available_capital
        optimal_leverage = min(math.ceil(required_leverage), self.config.max_leverage)
        
        logger.debug(f"💰 Optimal leverage: {required_leverage:.2f} → {optimal_leverage}x (capped)")
        return optimal_leverage
    
    def calculate_position_size_with_constraints(self, 
                                              signal_confidence: float,
                                              entry_price: float,
                                              stop_loss_price: Optional[float] = None,
                                              is_confluence: bool = False) -> Dict[str, Union[float, int, bool, str, None]]:
        """Calculate position size considering all constraints"""
        try:
            # 1. Calculate base risk amount
            risk_amount = self.config.account_balance * (self.config.risk_per_trade_pct / 100)
            
            # 2. Apply confluence multiplier if applicable
            if is_confluence:
                risk_amount *= self.trading_config.confluence_position_multiplier
                logger.info(f"🚀 Confluence boost applied: {self.trading_config.confluence_position_multiplier}x")
            
            # 3. Calculate position size based on stop loss distance
            if stop_loss_price and stop_loss_price > 0:
                price_diff = abs(entry_price - stop_loss_price)
                if price_diff > 0:
                    position_size_units = risk_amount / price_diff
                else:
                    position_size_units = risk_amount / entry_price
            else:
                position_size_units = risk_amount / entry_price
            
            # 4. Convert to USDT value
            position_size_usdt = position_size_units * entry_price
            
            # 5. Apply maximum position size constraint
            position_size_usdt = min(position_size_usdt, self.config.max_position_size_usdt)
            
            # 6. Ensure minimum order size
            if position_size_usdt < self.config.min_order_size_usdt:
                logger.warning(f"⚠️ Position size ({position_size_usdt:.2f} USDT) below minimum ({self.config.min_order_size_usdt} USDT)")
                position_size_usdt = self.config.min_order_size_usdt
            
            # 7. Check if we have enough capital with leverage
            required_capital = self.calculate_required_capital(position_size_usdt, self.config.max_leverage)
            
            if required_capital > self.config.available_margin:
                max_possible_position = self.calculate_max_position_with_leverage(
                    self.config.available_margin, self.config.max_leverage
                )
                position_size_usdt = min(position_size_usdt, max_possible_position)
                required_capital = self.calculate_required_capital(position_size_usdt, self.config.max_leverage)
                logger.warning(f"⚠️ Position size reduced due to insufficient capital")
            
            # 8. Calculate optimal leverage for this position
            leverage_used = self.calculate_optimal_leverage(position_size_usdt, required_capital)
            
            # 9. Recalculate position size units
            position_size_units = position_size_usdt / entry_price
            
            result = {
                'position_size_usdt': position_size_usdt,
                'position_size_units': position_size_units,
                'required_capital': required_capital,
                'leverage_used': leverage_used,
                'risk_amount': risk_amount,
                'entry_price': entry_price,
                'stop_loss_price': stop_loss_price
            }
            
            logger.info(f"💰 Position sizing complete:")
            logger.info(f"   📊 Size: {position_size_usdt:.2f} USDT ({position_size_units:.4f} units)")
            logger.info(f"   💰 Required Capital: {required_capital:.2f} USDT")
            logger.info(f"   ⚡ Leverage: {leverage_used}x")
            logger.info(f"   🛡️ Risk Amount: {risk_amount:.2f} USDT")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            return {
                'position_size_usdt': self.config.min_order_size_usdt,
                'position_size_units': self.config.min_order_size_usdt / entry_price,
                'required_capital': self.config.min_order_size_usdt / self.config.max_leverage,
                'leverage_used': self.config.max_leverage,
                'risk_amount': self.config.account_balance * (self.config.risk_per_trade_pct / 100),
                'entry_price': entry_price,
                'stop_loss_price': stop_loss_price
            }
    
    def validate_position_viability(self, position_details: Dict[str, Union[float, int, bool, str, None]]) -> Tuple[bool, str]:
        """Validate if a position is viable given current constraints"""
        position_size_usdt = position_details.get('position_size_usdt', 0.0)
        required_capital = position_details.get('required_capital', 0.0)
        leverage_used = position_details.get('leverage_used', 0)
        
        # Type checking and validation
        if not isinstance(position_size_usdt, (int, float)) or not isinstance(required_capital, (int, float)) or not isinstance(leverage_used, (int, float)):
            return False, "Invalid position details - missing required numeric values"
        
        # Check minimum order size
        if position_size_usdt < self.config.min_order_size_usdt:
            return False, f"Position size ({position_size_usdt:.2f} USDT) below minimum ({self.config.min_order_size_usdt} USDT)"
        
        # Check available capital
        if required_capital > self.config.available_margin:
            return False, f"Insufficient capital (required: {required_capital:.2f} USDT, available: {self.config.available_margin:.2f} USDT)"
        
        # Check leverage limits
        if leverage_used > self.config.max_leverage:
            return False, f"Leverage ({leverage_used}x) exceeds maximum ({self.config.max_leverage}x)"
        
        # Check maximum position size
        if position_size_usdt > self.config.max_position_size_usdt:
            return False, f"Position size ({position_size_usdt:.2f} USDT) exceeds maximum ({self.config.max_position_size_usdt} USDT)"
        
        return True, "Position is viable"
    
    def get_position_summary(self, position_details: Dict[str, Union[float, int, bool, str, None]]) -> str:
        """Get a formatted summary of position details"""
        return (
            f"💰 Position Summary:\n"
            f"   📊 Size: {position_details['position_size_usdt']:.2f} USDT\n"
            f"   📈 Units: {position_details['position_size_units']:.4f}\n"
            f"   💰 Capital Required: {position_details['required_capital']:.2f} USDT\n"
            f"   ⚡ Leverage: {position_details['leverage_used']}x\n"
            f"   🛡️ Risk Amount: {position_details['risk_amount']:.2f} USDT\n"
            f"   🎯 Entry Price: {position_details['entry_price']:.4f}"
        )

# Example usage and testing
def create_position_sizer(account_balance: float, available_margin: Optional[float] = None) -> PositionSizer:
    """Create a position sizer with current account settings"""
    if available_margin is None:
        available_margin = account_balance
    
    config = PositionSizingConfig(
        min_order_size_usdt=10.0,
        max_leverage=35,
        risk_per_trade_pct=2.0,
        max_position_size_usdt=200.0,
        account_balance=account_balance,
        available_margin=available_margin
    )
    
    return PositionSizer(config)

# Example: How the system works with leverage
def demonstrate_leverage_calculation():
    """Demonstrate how leverage affects position sizing"""
    print("🎯 LEVERAGE POSITION SIZING DEMONSTRATION")
    print("=" * 50)
    
    # Example: Minimum position is 5 USDT, leverage is 5x
    min_position = 5.0  # USDT
    leverage = 5  # 5x leverage
    
    # Required capital = Position size / Leverage
    required_capital = min_position / leverage
    print(f"📊 Example: Minimum position {min_position} USDT with {leverage}x leverage")
    print(f"💰 Required capital: {min_position} / {leverage} = {required_capital} USDT")
    print(f"✅ This means you only need {required_capital} USDT to place a {min_position} USDT position")
    print()
    
    # Test with different scenarios
    sizer = create_position_sizer(1000.0)  # 1000 USDT account
    
    scenarios = [
        {"confidence": 80, "price": 1.0, "stop_loss": 0.98, "confluence": False},
        {"confidence": 90, "price": 2.0, "stop_loss": 1.9, "confluence": True},
        {"confidence": 70, "price": 0.5, "stop_loss": 0.48, "confluence": False},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📈 Scenario {i}:")
        print(f"   Confidence: {scenario['confidence']}%")
        print(f"   Price: ${scenario['price']}")
        print(f"   Stop Loss: ${scenario['stop_loss']}")
        print(f"   Confluence: {scenario['confluence']}")
        
        result = sizer.calculate_position_size_with_constraints(
            signal_confidence=scenario['confidence'],
            entry_price=scenario['price'],
            stop_loss_price=scenario['stop_loss'],
            is_confluence=scenario['confluence']
        )
        
        is_viable, reason = sizer.validate_position_viability(result)
        print(f"   ✅ Viable: {is_viable}")
        if not is_viable:
            print(f"   ❌ Reason: {reason}")
        print(f"   📊 Position Size: {result['position_size_usdt']:.2f} USDT")
        print(f"   💰 Required Capital: {result['required_capital']:.2f} USDT")
        print(f"   ⚡ Leverage: {result['leverage_used']}x")
        print()

if __name__ == "__main__":
    demonstrate_leverage_calculation()