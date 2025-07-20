from strategies.orderbook import get_orderbook
from src.api.public.md.kline import get_kline_data
from src.models.market_depth import MarketDepth
from strategies.kline import Kline
import time
import threading
import logging

from src.executors.trading_engine import TradingEngine
from src.models.signal import TradingSignal
from src.scanners.scoring_system import ScoringSystem

class MarketScanner:
    def __init__(self, symbol, depth_limit=5, kline_interval='MINUTE_1', engine=None, scan_interval=60, scoring_system=None):
        self.symbol = symbol
        self.depth_limit = depth_limit
        self.kline_interval = kline_interval
        self.scan_interval = scan_interval

        # start trading engine
        self.engine = engine or TradingEngine(max_workers=2)
        self.engine.start()

        self._stop_event = threading.Event()
        self._thread = None

        # Setup logger
        self.logger = logging.getLogger(f"MarketScanner:{self.symbol}")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.scoring_system = scoring_system or ScoringSystem()

    def scan_market(self):
        try:
            orderbook = self.get_orderbook()
            kline_data = self.get_kline_data()
            # Analyze market conditions
            opportunities = self.analyze_market(orderbook, kline_data)
            self.logger.info(f"Scanned market: {self.symbol}, found {len(opportunities)} opportunities.")
            return opportunities
        except Exception as e:
            self.logger.error(f"Error scanning market: {e}", exc_info=True)
            return []

    def get_orderbook(self):
        orderbook_data = get_orderbook(self.symbol, self.depth_limit)
        return MarketDepth(orderbook_data)

    def get_kline_data(self):
        kline_data = get_kline_data(self.symbol, self.kline_interval)
        return [Kline(**data) for data in kline_data]

    def analyze_market(self, orderbook, kline_data):
        market_data = {
            "orderbook": orderbook,
            "kline_data": kline_data,
            # Add more as needed
        }
        score = self.scoring_system.score(market_data)
        strength = self.scoring_system.signal_strength(score)

        # Use score for action and sizing
        bids = orderbook.bids[: self.depth_limit]
        asks = orderbook.asks[: self.depth_limit]
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        mid_price = (best_bid + best_ask) / 2

        action = "buy" if score > 0 else "sell"
        qty = abs(score) / mid_price if mid_price else 0

        signal = TradingSignal(
            ticker=self.symbol,
            action=action,
            quantity=qty,
            price=mid_price,
            strength=score,
            # Optionally add: meta=strength
        )
        return [signal]

    def run(self):
        self.logger.info(f"Started market scanning for {self.symbol}.")
        while not self._stop_event.is_set():
            try:
                opportunities = self.scan_market()
                if opportunities:
                    self.execute_trades(opportunities)
            except Exception as e:
                self.logger.error(f"Error in run loop: {e}", exc_info=True)
            time.sleep(self.scan_interval)
        self.logger.info(f"Stopped market scanning for {self.symbol}.")

    def execute_trades(self, opportunities):
        for sig in opportunities:
            self.engine.submit_signal(sig)

    def start(self):
        """Start scanning in a background thread."""
        if self._thread and self._thread.is_alive():
            self.logger.warning("Scanner already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        self.logger.info("Scanner thread started.")

    def stop(self):
        """Stop the background scanning thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self.logger.info("Scanner thread stopped.")