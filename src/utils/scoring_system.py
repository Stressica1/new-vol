import importlib

class ScoringSystem:
    """
    Modular scoring system for trading signals.
    Supports: depth/trend, Supertrend, ML, VORTECS.
    """

    def __init__(self, weights=None, supertrend_params=None, ml_model=None):
        self.weights = weights or {
            "depth_trend": 0.3,
            "supertrend": 0.2,
            "ml": 0.3,
            "vortecs": 0.2,
        }
        # Lazy import to avoid hard dependency if not needed
        self.supertrend = None
        try:
            supertrend_mod = importlib.import_module(".supertrend_scorer", __package__)
            self.supertrend = supertrend_mod.SupertrendScorer(**(supertrend_params or {}))
        except Exception:
            pass

        self.ml = None
        try:
            ml_mod = importlib.import_module(".ml_scorer", __package__)
            self.ml = ml_mod.MLScorer(model=ml_model)
        except Exception:
            pass

        self.vortecs = None
        try:
            vortecs_mod = importlib.import_module(".vortecs_scorer", __package__)
            self.vortecs = vortecs_mod.VortecsScorer()
        except Exception:
            pass

    def score(self, market_data):
        # Depth/Trend
        depth_trend_score = self._score_depth_trend(market_data)
        # Supertrend
        supertrend_score = self.supertrend.score(market_data) if self.supertrend else 0
        # ML
        ml_score = self.ml.score(market_data) if self.ml else 0
        # VORTECS
        vortecs_score = self.vortecs.score(market_data) if self.vortecs else 0

        total_score = (
            self.weights["depth_trend"] * depth_trend_score +
            self.weights["supertrend"] * supertrend_score +
            self.weights["ml"] * ml_score +
            self.weights["vortecs"] * vortecs_score
        )
        return total_score

    def _score_depth_trend(self, market_data):
        orderbook = market_data.get("orderbook")
        kline_data = market_data.get("kline_data")
        if not orderbook or not kline_data or len(kline_data) < 2:
            return 0
        bids = orderbook.bids[:5]
        asks = orderbook.asks[:5]
        buy_depth = sum(qty for price, qty in bids)
        sell_depth = sum(qty for price, qty in asks)
        depth_ratio = buy_depth / sell_depth if sell_depth else 1.0
        prev, curr = kline_data[-2].close, kline_data[-1].close
        trend = (curr - prev) / prev
        depth_score = (depth_ratio - 1) * 100 * 0.5
        trend_score = trend * 100 * 0.5
        return depth_score + trend_score

    def signal_strength(self, score):
        if score > 50:
            return "strong_buy"
        elif score > 10:
            return "buy"
        elif score < -50:
            return "strong_sell"
        elif score < -10:
            return "sell"
        else:
            return "neutral"
