#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all major imports"""
    
    print("🧪 Testing Alpine Trading Bot imports...")
    print("=" * 50)
    
    try:
        # Test core imports
        from src.core.bot import AlpineBot
        from src.core.config import TradingConfig, get_exchange_config
        from src.core.manager import AlpineBotManager
        print("✅ Core imports successful")
        
        # Test exchange imports
        from src.exchange.bitget_client import BitgetClient
        print("✅ Exchange imports successful")
        
        # Test trading imports
        from src.trading.trading_engine import TradingEngine
        from src.trading.risk_management_v1 import RiskManager, RiskLevel
        from src.trading.strategy import VolumeAnomalyStrategy
        from src.trading.risk_manager_v2 import AlpineRiskManager
        print("✅ Trading imports successful")
        
        # Test UI imports
        from src.ui.display import AlpineDisplay
        print("✅ UI imports successful")
        
        # Test instantiation
        config = TradingConfig()
        bitget_client = BitgetClient(config)
        risk_manager = RiskManager(bitget_client)
        trading_engine = TradingEngine()
        
        print("✅ All components can be instantiated")
        
        print("\n🎉 All imports and instantiations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
