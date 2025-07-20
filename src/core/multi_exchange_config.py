#!/usr/bin/env python3
"""
🔌 Multi-Exchange Configuration for Alpine Trading Bot
📊 Easy configuration for adding new exchanges
"""

from dataclasses import dataclass
from typing import List
import os
from dotenv.main import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ExchangeConfig:
    """🔌 Exchange configuration for multi-API support"""
    name: str
    api_key: str
    api_secret: str
    passphrase: str = ""
    sandbox: bool = False
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    max_positions: int = 3  # Per exchange limit
    capital_allocation: float = 50.0  # Percentage of total capital for this exchange

def get_multi_exchange_config() -> List[ExchangeConfig]:
    """🔌 Get multi-exchange configuration"""
    
    # Bitget Configuration (Primary)
    bitget_config = ExchangeConfig(
        name="Bitget",
        api_key=os.getenv("BITGET_API_KEY", ""),
        api_secret=os.getenv("BITGET_SECRET_KEY", ""),
        passphrase=os.getenv("BITGET_PASSPHRASE", ""),
        sandbox=False,
        enabled=True,
        priority=1,
        max_positions=3,
        capital_allocation=25.0
    )
    
    # Bitget Configuration (Secondary Account)
    bitget2_config = ExchangeConfig(
        name="Bitget2",
        api_key=os.getenv("BITGET2_API_KEY", "bg_33b25387b50e7f874c18ddf34f5cbb14"),
        api_secret=os.getenv("BITGET2_SECRET_KEY", "4b3cab211d44a155c5cc63dd025fad43025d09155ee6eef3769ef2f6f85c9715"),
        passphrase=os.getenv("BITGET2_PASSPHRASE", "22672267"),
        sandbox=False,
        enabled=True,
        priority=2,
        max_positions=3,
        capital_allocation=25.0
    )
    
    # MEXC Configuration (Futures Trading)
    mexc_config = ExchangeConfig(
        name="MEXC",
        api_key=os.getenv("MEXC_API_KEY", ""),
        api_secret=os.getenv("MEXC_SECRET_KEY", ""),
        passphrase="",  # MEXC doesn't use passphrase
        sandbox=False,
        enabled=True,
        priority=3,
        max_positions=3,
        capital_allocation=20.0
    )
    
    # Binance Configuration (Quaternary)
    binance_config = ExchangeConfig(
        name="Binance",
        api_key=os.getenv("BINANCE_API_KEY", ""),
        api_secret=os.getenv("BINANCE_SECRET_KEY", ""),
        passphrase="",  # Binance doesn't use passphrase
        sandbox=False,
        enabled=True,
        priority=4,
        max_positions=2,
        capital_allocation=15.0
    )
    
    # OKX Configuration (Quinary)
    okx_config = ExchangeConfig(
        name="OKX",
        api_key=os.getenv("OKX_API_KEY", ""),
        api_secret=os.getenv("OKX_SECRET_KEY", ""),
        passphrase=os.getenv("OKX_PASSPHRASE", ""),
        sandbox=False,
        enabled=True,
        priority=5,
        max_positions=2,
        capital_allocation=15.0
    )
    
    # Bybit Configuration (Optional)
    bybit_config = ExchangeConfig(
        name="Bybit",
        api_key=os.getenv("BYBIT_API_KEY", ""),
        api_secret=os.getenv("BYBIT_SECRET_KEY", ""),
        passphrase="",  # Bybit doesn't use passphrase
        sandbox=False,
        enabled=False,  # Disabled by default
        priority=6,
        max_positions=2,
        capital_allocation=10.0
    )
    
    # Gate.io Configuration (Optional)
    gate_config = ExchangeConfig(
        name="Gate",
        api_key=os.getenv("GATE_API_KEY", ""),
        api_secret=os.getenv("GATE_SECRET_KEY", ""),
        passphrase="",  # Gate.io doesn't use passphrase
        sandbox=False,
        enabled=False,  # Disabled by default
        priority=7,
        max_positions=2,
        capital_allocation=10.0
    )
    
    # Return only enabled exchanges
    all_exchanges = [bitget_config, bitget2_config, mexc_config, binance_config, okx_config, bybit_config, gate_config]
    enabled_exchanges = [ex for ex in all_exchanges if ex.enabled and ex.api_key and ex.api_secret]
    
    return enabled_exchanges

def print_exchange_status():
    """📊 Print exchange configuration status"""
    exchanges = get_multi_exchange_config()
    
    print("🔌 Multi-Exchange Configuration Status:")
    print("=" * 50)
    
    for exchange in exchanges:
        status = "✅ ENABLED" if exchange.enabled and exchange.api_key and exchange.api_secret else "❌ DISABLED"
        print(f"{exchange.name:10} | {status:12} | Priority: {exchange.priority} | Positions: {exchange.max_positions} | Capital: {exchange.capital_allocation}%")
    
    print(f"\n📊 Total Enabled Exchanges: {len(exchanges)}")
    print(f"💰 Total Capital Allocation: {sum(ex.capital_allocation for ex in exchanges):.1f}%")

if __name__ == "__main__":
    print_exchange_status() 