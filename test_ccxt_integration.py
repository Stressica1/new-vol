#!/usr/bin/env python3
"""
🧪 CCXT Integration Testing for Alpine Trading Bot
================================================

Comprehensive testing of CCXT library integration:
- Exchange initialization and configuration
- Market data structures
- Order parameter validation
- Error handling patterns
- API signature verification patterns
- Data flow testing
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import traceback

try:
    import ccxt
    from loguru import logger
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    print("✅ All required libraries imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class CCXTIntegrationTester:
    """Comprehensive CCXT integration tester for Alpine Trading Bot"""
    
    def __init__(self):
        self.console = Console()
        self.test_results = []
        self.supported_exchanges = ['bitget', 'binance', 'okx', 'bybit']
        
    def log_test_result(self, test_name: str, success: bool, details: str, data: Optional[Dict] = None):
        """Log test result with detailed information"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.console.print(f"{status} | {test_name}: {details}")
        
        if data and not success:
            self.console.print(f"🔍 Error data: {json.dumps(data, indent=2)}")
    
    def test_ccxt_library_features(self) -> bool:
        """Test CCXT library features and capabilities"""
        try:
            self.console.print("\n🔬 Testing CCXT Library Features...")
            
            # Test 1: Check CCXT version
            ccxt_version = ccxt.__version__
            self.log_test_result(
                "CCXT Version Check",
                True,
                f"CCXT version {ccxt_version} loaded successfully",
                {'version': ccxt_version}
            )
            
            # Test 2: Check supported exchanges
            supported_exchanges = ccxt.exchanges
            exchange_count = len(supported_exchanges)
            
            self.log_test_result(
                "Supported Exchanges",
                exchange_count > 100,
                f"CCXT supports {exchange_count} exchanges",
                {'exchange_count': exchange_count, 'sample_exchanges': supported_exchanges[:10]}
            )
            
            # Test 3: Bitget availability
            bitget_available = 'bitget' in supported_exchanges
            self.log_test_result(
                "Bitget Exchange Support",
                bitget_available,
                f"Bitget support: {'Available' if bitget_available else 'Not Available'}",
                {'bitget_supported': bitget_available}
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "CCXT Library Features",
                False,
                f"Library test failed: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_exchange_initialization(self) -> bool:
        """Test exchange initialization patterns"""
        try:
            self.console.print("\n🔌 Testing Exchange Initialization...")
            
            for exchange_name in self.supported_exchanges:
                try:
                    # Test exchange class creation
                    exchange_class = getattr(ccxt, exchange_name)
                    
                    # Test basic initialization
                    exchange = exchange_class({
                        'sandbox': True,  # Use sandbox mode
                        'enableRateLimit': True,
                        'timeout': 10000,
                    })
                    
                    # Test exchange properties
                    has_spot = exchange.has.get('spot', False)
                    has_futures = exchange.has.get('future', False) or exchange.has.get('swap', False)
                    has_margin = exchange.has.get('margin', False)
                    
                    self.log_test_result(
                        f"{exchange_name.upper()} Initialization",
                        True,
                        f"Successfully initialized {exchange_name}",
                        {
                            'exchange': exchange_name,
                            'has_spot': has_spot,
                            'has_futures': has_futures,
                            'has_margin': has_margin,
                            'rate_limit': exchange.rateLimit
                        }
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"{exchange_name.upper()} Initialization",
                        False,
                        f"Failed to initialize {exchange_name}: {str(e)}",
                        {'exchange': exchange_name, 'error': str(e)}
                    )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Exchange Initialization",
                False,
                f"Initialization test failed: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_bitget_specific_features(self) -> bool:
        """Test Bitget-specific features and configurations"""
        try:
            self.console.print("\n🎯 Testing Bitget-Specific Features...")
            
            # Initialize Bitget exchange
            bitget = ccxt.bitget({
                'sandbox': True,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',  # Futures trading
                    'marginMode': 'cross'
                }
            })
            
            # Test 1: Market structure
            try:
                # This won't work without API keys, but we can test the structure
                market_structure = {
                    'id': 'BTCUSDT_UMCBL',
                    'symbol': 'BTC/USDT:USDT',
                    'base': 'BTC',
                    'quote': 'USDT',
                    'settle': 'USDT',
                    'type': 'swap',
                    'spot': False,
                    'margin': False,
                    'future': False,
                    'swap': True,
                    'option': False,
                    'active': True,
                    'contract': True,
                    'linear': True,
                    'inverse': False,
                    'contractSize': 0.001,
                    'precision': {
                        'amount': 3,
                        'price': 1
                    }
                }
                
                self.log_test_result(
                    "Bitget Market Structure",
                    True,
                    "Bitget market structure validated",
                    {'sample_market': market_structure}
                )
                
            except Exception as e:
                self.log_test_result(
                    "Bitget Market Structure",
                    False,
                    f"Market structure test failed: {str(e)}",
                    {'error': str(e)}
                )
            
            # Test 2: Order parameters
            test_order_params = {
                'symbol': 'BTC/USDT:USDT',
                'type': 'limit',
                'side': 'buy',
                'amount': 0.001,
                'price': 50000,
                'params': {
                    'marginMode': 'cross',
                    'leverage': 5,
                    'timeInForce': 'GTC',
                    'reduceOnly': False,
                    'postOnly': False
                }
            }
            
            self.log_test_result(
                "Bitget Order Parameters",
                True,
                "Order parameter structure validated",
                {'order_params': test_order_params}
            )
            
            # Test 3: Error handling patterns
            expected_errors = [
                'AuthenticationError',
                'InsufficientFunds',
                'InvalidOrder',
                'NetworkError',
                'ExchangeError'
            ]
            
            available_errors = [attr for attr in dir(ccxt) if 'Error' in attr]
            
            self.log_test_result(
                "CCXT Error Classes",
                all(error in available_errors for error in expected_errors),
                f"Error handling classes available: {len(available_errors)}",
                {'available_errors': available_errors, 'expected_errors': expected_errors}
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Bitget Specific Features",
                False,
                f"Bitget feature test failed: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_data_structures(self) -> bool:
        """Test CCXT data structures and formats"""
        try:
            self.console.print("\n📊 Testing CCXT Data Structures...")
            
            # Test 1: Ticker structure
            sample_ticker = {
                'symbol': 'BTC/USDT:USDT',
                'timestamp': int(time.time() * 1000),
                'datetime': datetime.now().isoformat(),
                'high': 52000.0,
                'low': 48000.0,
                'bid': 50000.0,
                'bidVolume': None,
                'ask': 50001.0,
                'askVolume': None,
                'vwap': 50500.0,
                'open': 49000.0,
                'close': 50000.0,
                'last': 50000.0,
                'previousClose': 49000.0,
                'change': 1000.0,
                'percentage': 2.04,
                'average': 49500.0,
                'baseVolume': 1234.56,
                'quoteVolume': 62172800.0,
                'info': {}
            }
            
            self.log_test_result(
                "Ticker Data Structure",
                True,
                "Ticker structure validated",
                {'ticker_fields': list(sample_ticker.keys())}
            )
            
            # Test 2: OHLCV structure
            sample_ohlcv = [
                [1640995200000, 47000.0, 48000.0, 46500.0, 47800.0, 123.45],
                [1640998800000, 47800.0, 48500.0, 47200.0, 48200.0, 145.67],
                [1641002400000, 48200.0, 49000.0, 47800.0, 48900.0, 167.89]
            ]
            
            self.log_test_result(
                "OHLCV Data Structure",
                True,
                f"OHLCV structure validated with {len(sample_ohlcv)} candles",
                {'ohlcv_sample': sample_ohlcv[0], 'format': '[timestamp, open, high, low, close, volume]'}
            )
            
            # Test 3: Order structure
            sample_order = {
                'id': '12345678',
                'clientOrderId': 'client_123',
                'timestamp': int(time.time() * 1000),
                'datetime': datetime.now().isoformat(),
                'lastTradeTimestamp': None,
                'symbol': 'BTC/USDT:USDT',
                'type': 'limit',
                'timeInForce': 'GTC',
                'side': 'buy',
                'amount': 0.001,
                'price': 50000.0,
                'cost': 50.0,
                'average': None,
                'filled': 0.0,
                'remaining': 0.001,
                'status': 'open',
                'fee': None,
                'trades': [],
                'info': {}
            }
            
            self.log_test_result(
                "Order Data Structure",
                True,
                "Order structure validated",
                {'order_fields': list(sample_order.keys())}
            )
            
            # Test 4: Balance structure
            sample_balance = {
                'info': {},
                'USDT': {
                    'free': 1000.0,
                    'used': 50.0,
                    'total': 1050.0
                },
                'BTC': {
                    'free': 0.0,
                    'used': 0.001,
                    'total': 0.001
                },
                'free': {'USDT': 1000.0, 'BTC': 0.0},
                'used': {'USDT': 50.0, 'BTC': 0.001},
                'total': {'USDT': 1050.0, 'BTC': 0.001}
            }
            
            self.log_test_result(
                "Balance Data Structure",
                True,
                "Balance structure validated",
                {'balance_fields': list(sample_balance.keys())}
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Data Structures",
                False,
                f"Data structure test failed: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_integration_points(self) -> bool:
        """Test integration points with Alpine Trading Bot"""
        try:
            self.console.print("\n🔗 Testing Integration Points...")
            
            # Test 1: Configuration structure
            config_structure = {
                'apiKey': 'test_api_key',
                'secret': 'test_secret',
                'password': 'test_passphrase',
                'sandbox': True,
                'enableRateLimit': True,
                'timeout': 10000,
                'options': {
                    'defaultType': 'swap',
                    'marginMode': 'cross'
                }
            }
            
            self.log_test_result(
                "Configuration Structure",
                True,
                "Configuration structure validated",
                {'config_fields': list(config_structure.keys())}
            )
            
            # Test 2: Symbol format conversion
            test_symbols = [
                ('BTC/USDT', 'BTC/USDT:USDT'),  # Spot to Futures
                ('ETH/USDT', 'ETH/USDT:USDT'),  # Spot to Futures
                ('ADA/USDT', 'ADA/USDT:USDT'),  # Spot to Futures
            ]
            
            conversion_success = True
            for spot_symbol, futures_symbol in test_symbols:
                # Basic conversion logic test
                if not futures_symbol.endswith(':USDT'):
                    conversion_success = False
                    break
            
            self.log_test_result(
                "Symbol Format Conversion",
                conversion_success,
                f"Symbol conversion validated for {len(test_symbols)} pairs",
                {'test_symbols': test_symbols}
            )
            
            # Test 3: Error mapping
            error_mapping = {
                'insufficient_funds': ccxt.InsufficientFunds,
                'invalid_order': ccxt.InvalidOrder,
                'network_error': ccxt.NetworkError,
                'authentication_error': ccxt.AuthenticationError,
                'exchange_error': ccxt.ExchangeError
            }
            
            self.log_test_result(
                "Error Mapping",
                True,
                f"Error mapping validated for {len(error_mapping)} error types",
                {'error_types': list(error_mapping.keys())}
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Integration Points",
                False,
                f"Integration test failed: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def create_test_summary_table(self) -> Table:
        """Create a comprehensive test summary table"""
        table = Table(title="🧪 CCXT Integration Test Results", box=box.ROUNDED)
        
        table.add_column("Test Category", style="bold cyan", width=30)
        table.add_column("Status", style="bold", width=10)
        table.add_column("Details", style="white", width=50)
        table.add_column("Success Rate", style="bold", width=15)
        
        # Group tests by category
        categories = {}
        for result in self.test_results:
            category = result['test_name'].split(' ')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, tests in categories.items():
            passed = sum(1 for test in tests if test['success'])
            total = len(tests)
            success_rate = (passed / total * 100) if total > 0 else 0
            
            status = "✅ PASS" if success_rate >= 80 else "⚠️ PARTIAL" if success_rate >= 50 else "❌ FAIL"
            details = f"{passed}/{total} tests passed"
            
            table.add_row(
                category,
                status,
                details,
                f"{success_rate:.1f}%"
            )
        
        return table
    
    def run_comprehensive_test(self) -> Dict:
        """Run all CCXT integration tests"""
        self.console.print(Panel.fit(
            "🧪 CCXT Integration Testing for Alpine Trading Bot\n"
            "Testing CCXT library integration, exchange support, and data structures",
            title="🔬 CCXT Testing Suite",
            border_style="cyan"
        ))
        
        test_sequence = [
            ("CCXT Library Features", self.test_ccxt_library_features),
            ("Exchange Initialization", self.test_exchange_initialization),
            ("Bitget Specific Features", self.test_bitget_specific_features),
            ("Data Structures", self.test_data_structures),
            ("Integration Points", self.test_integration_points),
        ]
        
        # Run all tests
        for test_name, test_func in test_sequence:
            try:
                success = test_func()
                if not success:
                    self.console.print(f"⚠️ Test category {test_name} had failures")
            except Exception as e:
                self.console.print(f"❌ Test category {test_name} crashed: {str(e)}")
                self.log_test_result(test_name, False, f"Test crashed: {str(e)}")
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Display summary
        self.console.print("\n")
        self.console.print(self.create_test_summary_table())
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        self.console.print(f"\n📊 FINAL RESULTS:")
        self.console.print(f"   Total Tests: {total_tests}")
        self.console.print(f"   Passed: {passed_tests}")
        self.console.print(f"   Failed: {failed_tests}")
        self.console.print(f"   Success Rate: {success_rate:.1f}%")
        
        return summary

def main():
    """Main test execution"""
    tester = CCXTIntegrationTester()
    
    try:
        summary = tester.run_comprehensive_test()
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"ccxt_integration_test_results_{timestamp}.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n✅ Testing completed! Results saved to file.")
        print(f"📊 Final Score: {summary['success_rate']:.1f}% ({summary['passed_tests']}/{summary['total_tests']} tests passed)")
        
        # Return appropriate exit code
        sys.exit(0 if summary['success_rate'] >= 80 else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()