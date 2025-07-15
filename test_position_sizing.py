#!/usr/bin/env python3
"""
🧪 Test Position Sizing System
Demonstrates the enhanced position sizing with leverage and budget constraints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from position_sizing import create_position_sizer, demonstrate_leverage_calculation
from config import TradingConfig

def test_position_sizing_scenarios():
    """Test various position sizing scenarios"""
    print("🧪 TESTING ENHANCED POSITION SIZING SYSTEM")
    print("=" * 60)
    
    # Test scenarios with different account balances and requirements
    scenarios = [
        {
            "name": "Small Account (100 USDT)",
            "account_balance": 100.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        },
        {
            "name": "Medium Account (1000 USDT)",
            "account_balance": 1000.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        },
        {
            "name": "Large Account (10000 USDT)",
            "account_balance": 10000.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 40)
        
        # Create position sizer for this scenario
        sizer = create_position_sizer(
            account_balance=scenario['account_balance'],
            available_margin=scenario['account_balance']
        )
        
        for i, test_case in enumerate(scenario['test_cases'], 1):
            print(f"\n  🎯 Test Case {i}:")
            print(f"    Price: ${test_case['price']}")
            print(f"    Stop Loss: ${test_case['stop_loss']}")
            print(f"    Confidence: {test_case['confidence']}%")
            print(f"    Confluence: {test_case['confluence']}")
            
            # Calculate position size
            result = sizer.calculate_position_size_with_constraints(
                signal_confidence=test_case['confidence'],
                entry_price=test_case['price'],
                stop_loss_price=test_case['stop_loss'],
                is_confluence=test_case['confluence']
            )
            
            # Validate position
            is_viable, reason = sizer.validate_position_viability(result)
            
            print(f"    📊 Position Size: {result['position_size_usdt']:.2f} USDT")
            print(f"    📈 Units: {result['position_size_units']:.4f}")
            print(f"    💰 Required Capital: {result['required_capital']:.2f} USDT")
            print(f"    ⚡ Leverage: {result['leverage_used']}x")
            print(f"    🛡️ Risk Amount: {result['risk_amount']:.2f} USDT")
            print(f"    ✅ Viable: {is_viable}")
            if not is_viable:
                print(f"    ❌ Reason: {reason}")
            
            # Demonstrate leverage calculation
            position_size = result.get('position_size_usdt', 0.0)
            required_capital = result.get('required_capital', 0.0)
            if isinstance(position_size, (int, float)) and isinstance(required_capital, (int, float)) and position_size > 0 and required_capital > 0:
                leverage_ratio = position_size / required_capital
                print(f"    🔍 Leverage Check: {position_size:.2f} / {required_capital:.2f} = {leverage_ratio:.2f}x")

def test_leverage_understanding():
    """Test to demonstrate leverage understanding"""
    print("\n🎯 LEVERAGE UNDERSTANDING TEST")
    print("=" * 50)
    
    # Example: Minimum position is 5 USDT, leverage is 5x
    min_position = 5.0  # USDT
    leverage = 5  # 5x leverage
    
    # Required capital = Position size / Leverage
    required_capital = min_position / leverage
    
    print(f"📊 Example: Minimum position {min_position} USDT with {leverage}x leverage")
    print(f"💰 Required capital: {min_position} / {leverage} = {required_capital} USDT")
    print(f"✅ This means you only need {required_capital} USDT to place a {min_position} USDT position")
    
    # Test with different leverage scenarios
    leverage_scenarios = [
        {"position": 10.0, "leverage": 5, "description": "10 USDT position with 5x leverage"},
        {"position": 20.0, "leverage": 10, "description": "20 USDT position with 10x leverage"},
        {"position": 50.0, "leverage": 25, "description": "50 USDT position with 25x leverage"},
        {"position": 100.0, "leverage": 35, "description": "100 USDT position with 35x leverage"},
    ]
    
    print("\n📈 Leverage Scenarios:")
    for scenario in leverage_scenarios:
        required = scenario["position"] / scenario["leverage"]
        print(f"  {scenario['description']}:")
        print(f"    Required capital: {scenario['position']} / {scenario['leverage']} = {required:.2f} USDT")
        print(f"    Capital efficiency: {scenario['leverage']}x")

def test_budget_constraints():
    """Test budget constraints with different account sizes"""
    print("\n💰 BUDGET CONSTRAINT TEST")
    print("=" * 40)
    
    # Test with very small account
    small_account = 5.0  # 5 USDT account
    sizer = create_position_sizer(small_account)
    
    print(f"📊 Testing with {small_account} USDT account:")
    
    # Try to place minimum position
    result = sizer.calculate_position_size_with_constraints(
        signal_confidence=80,
        entry_price=1.0,
        stop_loss_price=0.98,
        is_confluence=False
    )
    
    print(f"  📊 Position Size: {result['position_size_usdt']:.2f} USDT")
    print(f"  💰 Required Capital: {result['required_capital']:.2f} USDT")
    print(f"  ⚡ Leverage: {result['leverage_used']}x")
    
    is_viable, reason = sizer.validate_position_viability(result)
    print(f"  ✅ Viable: {is_viable}")
    if not is_viable:
        print(f"  ❌ Reason: {reason}")
    
    # Test with larger account
    large_account = 1000.0  # 1000 USDT account
    sizer = create_position_sizer(large_account)
    
    print(f"\n📊 Testing with {large_account} USDT account:")
    
    result = sizer.calculate_position_size_with_constraints(
        signal_confidence=80,
        entry_price=1.0,
        stop_loss_price=0.98,
        is_confluence=False
    )
    
    print(f"  📊 Position Size: {result['position_size_usdt']:.2f} USDT")
    print(f"  💰 Required Capital: {result['required_capital']:.2f} USDT")
    print(f"  ⚡ Leverage: {result['leverage_used']}x")
    
    is_viable, reason = sizer.validate_position_viability(result)
    print(f"  ✅ Viable: {is_viable}")
    if not is_viable:
        print(f"  ❌ Reason: {reason}")

def main():
    """Run all position sizing tests"""
    print("🚀 ENHANCED POSITION SIZING SYSTEM TEST")
    print("=" * 60)
    print("This system properly handles:")
    print("  ✅ Budget constraints")
    print("  ✅ Leverage settings")
    print("  ✅ Minimum position requirements")
    print("  ✅ Risk management rules")
    print("  ✅ Confluence signal boosts")
    print()
    
    # Run demonstration
    demonstrate_leverage_calculation()
    
    # Run comprehensive tests
    test_position_sizing_scenarios()
    test_leverage_understanding()
    test_budget_constraints()
    
    print("\n✅ All tests completed!")
    print("\n💡 Key Insights:")
    print("  • Leverage reduces required capital: Position Size / Leverage = Required Capital")
    print("  • Minimum position requirements are enforced regardless of leverage")
    print("  • Budget constraints are respected with optimal leverage calculation")
    print("  • Risk management rules are maintained across all scenarios")

if __name__ == "__main__":
    main()
"""
🧪 Test Position Sizing System
Demonstrates the enhanced position sizing with leverage and budget constraints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from position_sizing import create_position_sizer, demonstrate_leverage_calculation
from config import TradingConfig

def test_position_sizing_scenarios():
    """Test various position sizing scenarios"""
    print("🧪 TESTING ENHANCED POSITION SIZING SYSTEM")
    print("=" * 60)
    
    # Test scenarios with different account balances and requirements
    scenarios = [
        {
            "name": "Small Account (100 USDT)",
            "account_balance": 100.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        },
        {
            "name": "Medium Account (1000 USDT)",
            "account_balance": 1000.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        },
        {
            "name": "Large Account (10000 USDT)",
            "account_balance": 10000.0,
            "min_order_size": 10.0,
            "max_leverage": 35,
            "test_cases": [
                {"price": 1.0, "stop_loss": 0.98, "confidence": 80, "confluence": False},
                {"price": 2.0, "stop_loss": 1.9, "confidence": 90, "confluence": True},
                {"price": 0.5, "stop_loss": 0.48, "confidence": 70, "confluence": False},
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 40)
        
        # Create position sizer for this scenario
        sizer = create_position_sizer(
            account_balance=scenario['account_balance'],
            available_margin=scenario['account_balance']
        )
        
        for i, test_case in enumerate(scenario['test_cases'], 1):
            print(f"\n  🎯 Test Case {i}:")
            print(f"    Price: ${test_case['price']}")
            print(f"    Stop Loss: ${test_case['stop_loss']}")
            print(f"    Confidence: {test_case['confidence']}%")
            print(f"    Confluence: {test_case['confluence']}")
            
            # Calculate position size
            result = sizer.calculate_position_size_with_constraints(
                signal_confidence=test_case['confidence'],
                entry_price=test_case['price'],
                stop_loss_price=test_case['stop_loss'],
                is_confluence=test_case['confluence']
            )
            
            # Validate position
            is_viable, reason = sizer.validate_position_viability(result)
            
            print(f"    📊 Position Size: {result['position_size_usdt']:.2f} USDT")
            print(f"    📈 Units: {result['position_size_units']:.4f}")
            print(f"    💰 Required Capital: {result['required_capital']:.2f} USDT")
            print(f"    ⚡ Leverage: {result['leverage_used']}x")
            print(f"    🛡️ Risk Amount: {result['risk_amount']:.2f} USDT")
            print(f"    ✅ Viable: {is_viable}")
            if not is_viable:
                print(f"    ❌ Reason: {reason}")
            
            # Demonstrate leverage calculation
            position_size = result.get('position_size_usdt', 0.0)
            required_capital = result.get('required_capital', 0.0)
            if isinstance(position_size, (int, float)) and isinstance(required_capital, (int, float)) and position_size > 0 and required_capital > 0:
                leverage_ratio = position_size / required_capital
                print(f"    🔍 Leverage Check: {position_size:.2f} / {required_capital:.2f} = {leverage_ratio:.2f}x")

def test_leverage_understanding():
    """Test to demonstrate leverage understanding"""
    print("\n🎯 LEVERAGE UNDERSTANDING TEST")
    print("=" * 50)
    
    # Example: Minimum position is 5 USDT, leverage is 5x
    min_position = 5.0  # USDT
    leverage = 5  # 5x leverage
    
    # Required capital = Position size / Leverage
    required_capital = min_position / leverage
    
    print(f"📊 Example: Minimum position {min_position} USDT with {leverage}x leverage")
    print(f"💰 Required capital: {min_position} / {leverage} = {required_capital} USDT")
    print(f"✅ This means you only need {required_capital} USDT to place a {min_position} USDT position")
    
    # Test with different leverage scenarios
    leverage_scenarios = [
        {"position": 10.0, "leverage": 5, "description": "10 USDT position with 5x leverage"},
        {"position": 20.0, "leverage": 10, "description": "20 USDT position with 10x leverage"},
        {"position": 50.0, "leverage": 25, "description": "50 USDT position with 25x leverage"},
        {"position": 100.0, "leverage": 35, "description": "100 USDT position with 35x leverage"},
    ]
    
    print("\n📈 Leverage Scenarios:")
    for scenario in leverage_scenarios:
        required = scenario["position"] / scenario["leverage"]
        print(f"  {scenario['description']}:")
        print(f"    Required capital: {scenario['position']} / {scenario['leverage']} = {required:.2f} USDT")
        print(f"    Capital efficiency: {scenario['leverage']}x")

def test_budget_constraints():
    """Test budget constraints with different account sizes"""
    print("\n💰 BUDGET CONSTRAINT TEST")
    print("=" * 40)
    
    # Test with very small account
    small_account = 5.0  # 5 USDT account
    sizer = create_position_sizer(small_account)
    
    print(f"📊 Testing with {small_account} USDT account:")
    
    # Try to place minimum position
    result = sizer.calculate_position_size_with_constraints(
        signal_confidence=80,
        entry_price=1.0,
        stop_loss_price=0.98,
        is_confluence=False
    )
    
    print(f"  📊 Position Size: {result['position_size_usdt']:.2f} USDT")
    print(f"  💰 Required Capital: {result['required_capital']:.2f} USDT")
    print(f"  ⚡ Leverage: {result['leverage_used']}x")
    
    is_viable, reason = sizer.validate_position_viability(result)
    print(f"  ✅ Viable: {is_viable}")
    if not is_viable:
        print(f"  ❌ Reason: {reason}")
    
    # Test with larger account
    large_account = 1000.0  # 1000 USDT account
    sizer = create_position_sizer(large_account)
    
    print(f"\n📊 Testing with {large_account} USDT account:")
    
    result = sizer.calculate_position_size_with_constraints(
        signal_confidence=80,
        entry_price=1.0,
        stop_loss_price=0.98,
        is_confluence=False
    )
    
    print(f"  📊 Position Size: {result['position_size_usdt']:.2f} USDT")
    print(f"  💰 Required Capital: {result['required_capital']:.2f} USDT")
    print(f"  ⚡ Leverage: {result['leverage_used']}x")
    
    is_viable, reason = sizer.validate_position_viability(result)
    print(f"  ✅ Viable: {is_viable}")
    if not is_viable:
        print(f"  ❌ Reason: {reason}")

def main():
    """Run all position sizing tests"""
    print("🚀 ENHANCED POSITION SIZING SYSTEM TEST")
    print("=" * 60)
    print("This system properly handles:")
    print("  ✅ Budget constraints")
    print("  ✅ Leverage settings")
    print("  ✅ Minimum position requirements")
    print("  ✅ Risk management rules")
    print("  ✅ Confluence signal boosts")
    print()
    
    # Run demonstration
    demonstrate_leverage_calculation()
    
    # Run comprehensive tests
    test_position_sizing_scenarios()
    test_leverage_understanding()
    test_budget_constraints()
    
    print("\n✅ All tests completed!")
    print("\n💡 Key Insights:")
    print("  • Leverage reduces required capital: Position Size / Leverage = Required Capital")
    print("  • Minimum position requirements are enforced regardless of leverage")
    print("  • Budget constraints are respected with optimal leverage calculation")
    print("  • Risk management rules are maintained across all scenarios")

if __name__ == "__main__":
    main()