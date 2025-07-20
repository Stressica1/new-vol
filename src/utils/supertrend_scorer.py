import numpy as np
import talib

class SupertrendScorer:
    def __init__(self, atr_period=10, multiplier=3):
        self.atr_period = atr_period
        self.multiplier = multiplier

    def score(self, market_data):
        kline_data = market_data.get("kline_data")
        if not kline_data or len(kline_data) < self.atr_period + 2:
            return 0
        highs = np.array([k.high for k in kline_data])
        lows = np.array([k.low for k in kline_data])
        closes = np.array([k.close for k in kline_data])

        atr = talib.ATR(highs, lows, closes, timeperiod=self.atr_period)
        hl2 = (highs + lows) / 2
        final_upperband = hl2 - (self.multiplier * atr)
        final_lowerband = hl2 + (self.multiplier * atr)
        close = closes[-1]
        prev_close = closes[-2]
        # Simple supertrend logic: if close crosses above lowerband, bullish; below upperband, bearish
        if prev_close < final_lowerband[-2] and close > final_lowerband[-1]:
            return 50  # bullish
        elif prev_close > final_upperband[-2] and close < final_upperband[-1]:
            return -50  # bearish
        return 0
