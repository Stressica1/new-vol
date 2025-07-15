#!/usr/bin/env python3
"""
🏔️ Alpine Risk Manager - Advanced Risk Management
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AlpineRiskManager:
    """Advanced risk management for Alpine Trading Bot"""
    
    def __init__(self):
        self.name = "Alpine Risk Manager"
        self.version = "2.0"
        
        # Risk parameters
        self.max_daily_loss_pct = 50.0
        self.max_drawdown_pct = 30.0
        self.max_positions = 20
        self.position_size_pct = 20.0
        self.stop_loss_pct = 1.5
        self.take_profit_pct = 3.0
        
        # Tracking
        self.daily_pnl = 0.0
        self.peak_balance = 0.0
        self.current_drawdown = 0.0
        self.open_positions = []
        self.trade_history = []
        
        # Risk state
        self.risk_level = "LOW"
        self.trading_allowed = True
        self.last_risk_check = datetime.now()
    
    def update_balance(self, current_balance: float):
        """Update balance and calculate drawdown"""
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        if self.peak_balance > 0:
            self.current_drawdown = ((self.peak_balance - current_balance) / self.peak_balance) * 100
        else:
            self.current_drawdown = 0.0
    
    def calculate_position_size(self, account_balance: float, signal_confidence: float) -> float:
        """Calculate position size based on risk parameters"""
        try:
            # Base position size
            base_size = (account_balance * self.position_size_pct) / 100
            
            # Adjust based on confidence
            confidence_multiplier = signal_confidence / 100
            adjusted_size = base_size * confidence_multiplier
            
            # Risk adjustments
            if self.current_drawdown > 20:
                adjusted_size *= 0.5  # Reduce size during drawdown
            
            if len(self.open_positions) > 15:
                adjusted_size *= 0.8  # Reduce size when many positions open
            
            return max(adjusted_size, 10.0)  # Minimum $10
            
        except Exception as e:
            print(f"❌ Error calculating position size: {e}")
            return 10.0
    
    def check_risk_limits(self, account_balance: float) -> bool:
        """Check if trading is allowed based on risk limits"""
        try:
            # Update balance
            self.update_balance(account_balance)
            
            # Check daily loss limit
            if self.daily_pnl <= -self.max_daily_loss_pct:
                self.trading_allowed = False
                self.risk_level = "CRITICAL"
                return False
            
            # Check drawdown limit
            if self.current_drawdown >= self.max_drawdown_pct:
                self.trading_allowed = False
                self.risk_level = "HIGH"
                return False
            
            # Check position limit
            if len(self.open_positions) >= self.max_positions:
                self.trading_allowed = False
                self.risk_level = "HIGH"
                return False
            
            # Set risk level
            if self.current_drawdown > 15:
                self.risk_level = "MEDIUM"
            elif self.current_drawdown > 5:
                self.risk_level = "LOW"
            else:
                self.risk_level = "MINIMAL"
            
            self.trading_allowed = True
            return True
            
        except Exception as e:
            print(f"❌ Error checking risk limits: {e}")
            return False
    
    def calculate_stop_loss(self, entry_price: float, signal_type: str) -> float:
        """Calculate stop loss price"""
        try:
            if signal_type == "BUY":
                return entry_price * (1 - self.stop_loss_pct / 100)
            else:  # SELL
                return entry_price * (1 + self.stop_loss_pct / 100)
        except Exception as e:
            print(f"❌ Error calculating stop loss: {e}")
            return entry_price
    
    def calculate_take_profit(self, entry_price: float, signal_type: str) -> float:
        """Calculate take profit price"""
        try:
            if signal_type == "BUY":
                return entry_price * (1 + self.take_profit_pct / 100)
            else:  # SELL
                return entry_price * (1 - self.take_profit_pct / 100)
        except Exception as e:
            print(f"❌ Error calculating take profit: {e}")
            return entry_price
    
    def add_position(self, position: Dict):
        """Add a new position to tracking"""
        self.open_positions.append(position)
    
    def remove_position(self, position_id: str):
        """Remove a position from tracking"""
        self.open_positions = [p for p in self.open_positions if p.get('id') != position_id]
    
    def get_risk_summary(self) -> Dict:
        """Get risk management summary"""
        return {
            'risk_level': self.risk_level,
            'trading_allowed': self.trading_allowed,
            'current_drawdown': self.current_drawdown,
            'daily_pnl': self.daily_pnl,
            'open_positions': len(self.open_positions),
            'max_positions': self.max_positions,
            'position_utilization': (len(self.open_positions) / self.max_positions) * 100
        }

def main():
    """Test the risk manager"""
    risk_manager = AlpineRiskManager()
    print(f"✅ {risk_manager.name} v{risk_manager.version} initialized")
    
    # Test risk check
    result = risk_manager.check_risk_limits(1000.0)
    print(f"🛡️ Risk check result: {result}")
    print(f"📊 Risk summary: {risk_manager.get_risk_summary()}")

if __name__ == "__main__":
    main()
