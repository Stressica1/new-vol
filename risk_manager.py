"""
🏔️ Alpine Trading Bot - Risk Management System
Comprehensive risk management with stop losses, position sizing, and drawdown protection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from config import TradingConfig

class AlpineRiskManager:
    """🛡️ Alpine Risk Management System"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # Risk tracking
        self.daily_start_balance = 0.0
        self.daily_pnl = 0.0
        self.session_start_time = datetime.now().date()
        self.total_drawdown = 0.0
        self.peak_balance = 0.0
        
        # Position tracking
        self.active_positions = []
        self.closed_positions = []
        
        # Risk flags
        self.daily_loss_exceeded = False
        self.max_drawdown_exceeded = False
        self.trading_halted = False
        
    def initialize_session(self, account_balance: float):
        """Initialize trading session with starting balance 🚀"""
        
        current_date = datetime.now().date()
        
        # Reset daily tracking if new day
        if current_date != self.session_start_time:
            self.daily_start_balance = account_balance
            self.daily_pnl = 0.0
            self.session_start_time = current_date
            self.daily_loss_exceeded = False
        
        # Initialize peak balance if not set
        if self.peak_balance == 0.0:
            self.peak_balance = account_balance
        else:
            self.peak_balance = max(self.peak_balance, account_balance)
    
    def can_open_position(self, signal: Dict, account_balance: float) -> Tuple[bool, str]:
        """Check if we can open a new position 🎯"""
        
        # Check if trading is halted
        if self.trading_halted:
            return False, "🛑 Trading halted due to risk limits"
        
        # Check daily loss limit
        if self.daily_loss_exceeded:
            return False, f"🚫 Daily loss limit exceeded: {self.config.max_daily_loss_pct}%"
        
        # Check max drawdown
        if self.max_drawdown_exceeded:
            return False, f"🚫 Max drawdown exceeded: {self.config.max_drawdown_pct}%"
        
        # Check maximum positions
        if len(self.active_positions) >= self.config.max_positions:
            return False, f"📊 Max positions reached: {self.config.max_positions}"
        
        # Check if we already have a position in this symbol
        for pos in self.active_positions:
            if pos['symbol'] == signal['symbol']:
                return False, f"📋 Position already exists for {signal['symbol']}"
        
        # Calculate proposed position size and required margin
        base_position_value = account_balance * (self.config.position_size_pct / 100)
        confidence_multiplier = signal.get('confidence', 75) / 100
        adjusted_position_value = base_position_value * confidence_multiplier
        
        # Required margin with leverage
        required_margin = adjusted_position_value / self.config.leverage
        
        # Check if we have enough margin
        if required_margin > account_balance:
            return False, f"💰 Insufficient account balance (need ${required_margin:.2f} margin, have ${account_balance:.2f})"
        
        # Check minimum trade value (reduced for smaller accounts)
        min_trade_value = 5.0  # Minimum $5 trade value
        if adjusted_position_value < min_trade_value:
            return False, f"📉 Position too small (${adjusted_position_value:.2f} < ${min_trade_value} minimum)"
        
        return True, "✅ Position approved"
    
    def calculate_position_size(self, signal: Dict, account_balance: float, current_price: float) -> Tuple[float, Dict]:
        """Calculate optimal position size with risk management 💰"""
        
        # Base position size from config
        base_position_value = account_balance * (self.config.position_size_pct / 100)
        
        # Adjust based on signal confidence
        confidence_multiplier = signal.get('confidence', 75) / 100
        adjusted_position_value = base_position_value * confidence_multiplier
        
        # Adjust based on current drawdown
        current_drawdown = self.calculate_current_drawdown(account_balance)
        if current_drawdown > 10:  # Reduce size if in drawdown
            drawdown_reduction = 1 - (current_drawdown / 100 * 0.5)  # Reduce by 50% at max drawdown
            adjusted_position_value *= drawdown_reduction
        
        # Calculate position size in contracts
        position_size = adjusted_position_value / current_price
        
        # Risk metrics
        risk_info = {
            'base_value': base_position_value,
            'adjusted_value': adjusted_position_value,
            'position_size': position_size,
            'confidence_multiplier': confidence_multiplier,
            'drawdown_adjustment': current_drawdown,
            'risk_per_trade': adjusted_position_value * (self.config.stop_loss_pct / 100)
        }
        
        return position_size, risk_info
    
    def calculate_stop_loss_take_profit(self, signal: Dict, entry_price: float, position_size: float) -> Dict:
        """Calculate stop loss and take profit levels 🎯"""
        
        if signal['type'] == 'LONG':
            stop_loss = entry_price * (1 - self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 + self.config.take_profit_pct / 100)
            
            # Trailing stop
            if self.config.trailing_stop:
                trailing_stop_distance = entry_price * (self.config.trailing_stop_pct / 100)
            else:
                trailing_stop_distance = None
                
        else:  # SHORT
            stop_loss = entry_price * (1 + self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 - self.config.take_profit_pct / 100)
            
            # Trailing stop
            if self.config.trailing_stop:
                trailing_stop_distance = entry_price * (self.config.trailing_stop_pct / 100)
            else:
                trailing_stop_distance = None
        
        # Calculate potential P&L
        max_loss = position_size * abs(entry_price - stop_loss)
        max_profit = position_size * abs(take_profit - entry_price)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop_distance': trailing_stop_distance,
            'max_loss': max_loss,
            'max_profit': max_profit,
            'risk_reward_ratio': max_profit / max_loss if max_loss > 0 else 0
        }
    
    def should_update_trailing_stop(self, position: Dict, current_price: float) -> Tuple[bool, float]:
        """Check if trailing stop should be updated 📈"""
        
        if not self.config.trailing_stop or not position.get('trailing_stop_distance'):
            return False, position.get('stop_loss', 0)
        
        side = position['side']
        entry_price = position['entry_price']
        current_stop = position.get('stop_loss', 0)
        trailing_distance = position['trailing_stop_distance']
        
        if side == 'long':
            # For long positions, move stop up as price increases
            new_stop = current_price - trailing_distance
            if new_stop > current_stop:
                return True, new_stop
        else:
            # For short positions, move stop down as price decreases
            new_stop = current_price + trailing_distance
            if new_stop < current_stop:
                return True, new_stop
        
        return False, current_stop
    
    def add_position(self, position: Dict):
        """Add a new position to tracking 📋"""
        
        position['opened_at'] = datetime.now()
        position['status'] = 'OPEN'
        self.active_positions.append(position)
    
    def update_position(self, symbol: str, current_price: float, unrealized_pnl: float) -> Optional[Dict]:
        """Update position with current market data 🔄"""
        
        for i, pos in enumerate(self.active_positions):
            if pos['symbol'] == symbol:
                pos['current_price'] = current_price
                pos['unrealized_pnl'] = unrealized_pnl
                pos['last_update'] = datetime.now()
                
                # Check trailing stop
                should_update, new_stop = self.should_update_trailing_stop(pos, current_price)
                if should_update:
                    pos['stop_loss'] = new_stop
                    pos['trailing_stop_updated'] = True
                
                return pos
        
        return None
    
    def close_position(self, symbol: str, close_price: float, realized_pnl: float, reason: str) -> Optional[Dict]:
        """Close a position and update tracking 💰"""
        
        for i, pos in enumerate(self.active_positions):
            if pos['symbol'] == symbol:
                # Move to closed positions
                pos['closed_at'] = datetime.now()
                pos['close_price'] = close_price
                pos['realized_pnl'] = realized_pnl
                pos['close_reason'] = reason
                pos['status'] = 'CLOSED'
                
                # Calculate hold time
                hold_time = pos['closed_at'] - pos['opened_at']
                pos['hold_time'] = hold_time
                
                self.closed_positions.append(pos)
                self.active_positions.pop(i)
                
                # Update daily P&L
                self.daily_pnl += realized_pnl
                
                return pos
        
        return None
    
    def calculate_current_drawdown(self, current_balance: float) -> float:
        """Calculate current drawdown percentage 📉"""
        
        if self.peak_balance == 0:
            return 0.0
        
        drawdown = ((self.peak_balance - current_balance) / self.peak_balance) * 100
        return max(0, drawdown)
    
    def check_risk_limits(self, account_balance: float) -> Dict[str, bool]:
        """Check all risk limits and update flags 🛡️"""
        
        # Update peak balance
        self.peak_balance = max(self.peak_balance, account_balance)
        
        # Check daily loss limit
        if self.daily_start_balance > 0:
            daily_loss_pct = abs(self.daily_pnl / self.daily_start_balance) * 100
            if daily_loss_pct >= self.config.max_daily_loss_pct:
                self.daily_loss_exceeded = True
        
        # Check max drawdown
        current_drawdown = self.calculate_current_drawdown(account_balance)
        if current_drawdown >= self.config.max_drawdown_pct:
            self.max_drawdown_exceeded = True
        
        # Halt trading if any major limit exceeded
        if self.daily_loss_exceeded or self.max_drawdown_exceeded:
            self.trading_halted = True
        
        return {
            'daily_loss_exceeded': self.daily_loss_exceeded,
            'max_drawdown_exceeded': self.max_drawdown_exceeded,
            'trading_halted': self.trading_halted
        }
    
    def get_risk_metrics(self, account_balance: float) -> Dict:
        """Get comprehensive risk metrics for display 📊"""
        
        current_drawdown = self.calculate_current_drawdown(account_balance)
        daily_loss_pct = 0.0
        
        if self.daily_start_balance > 0:
            daily_loss_pct = (self.daily_pnl / self.daily_start_balance) * 100
        
        # Calculate position exposure
        total_exposure = sum(pos.get('position_value', 0) for pos in self.active_positions)
        exposure_pct = (total_exposure / account_balance * 100) if account_balance > 0 else 0
        
        # Calculate unrealized P&L
        total_unrealized = sum(pos.get('unrealized_pnl', 0) for pos in self.active_positions)
        
        return {
            'account_balance': account_balance,
            'peak_balance': self.peak_balance,
            'daily_start_balance': self.daily_start_balance,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': daily_loss_pct,
            'current_drawdown': current_drawdown,
            'total_exposure': total_exposure,
            'exposure_pct': exposure_pct,
            'total_unrealized': total_unrealized,
            'active_positions': len(self.active_positions),
            'max_positions': self.config.max_positions,
            'positions_available': self.config.max_positions - len(self.active_positions),
            'risk_flags': {
                'daily_loss_exceeded': self.daily_loss_exceeded,
                'max_drawdown_exceeded': self.max_drawdown_exceeded,
                'trading_halted': self.trading_halted
            }
        }
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions 📋"""
        
        if not self.closed_positions:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_pnl': 0
            }
        
        winning_trades = [pos for pos in self.closed_positions if pos['realized_pnl'] > 0]
        losing_trades = [pos for pos in self.closed_positions if pos['realized_pnl'] < 0]
        
        total_trades = len(self.closed_positions)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([pos['realized_pnl'] for pos in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([pos['realized_pnl'] for pos in losing_trades]) if losing_trades else 0
        
        total_profits = sum(pos['realized_pnl'] for pos in winning_trades)
        total_losses = sum(abs(pos['realized_pnl']) for pos in losing_trades)
        profit_factor = (total_profits / total_losses) if total_losses > 0 else 0
        
        total_pnl = sum(pos['realized_pnl'] for pos in self.closed_positions)
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl
        }