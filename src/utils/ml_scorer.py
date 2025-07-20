import numpy as np
import logging

class MLScorer:
    """
    Industry-grade ML scorer for trading signals.
    Supports regression and classification models (scikit-learn compatible).
    """

    def __init__(self, model=None, feature_names=None, logger=None, scaler=None, postprocess_fn=None):
        """
        :param model: Trained sklearn-like model with predict() or predict_proba()
        :param feature_names: Optional list of feature names for extraction
        :param logger: Optional logger instance
        :param scaler: Optional sklearn-like scaler for feature normalization
        :param postprocess_fn: Optional function to postprocess model output
        """
        self.model = model
        self.feature_names = feature_names or ["depth_ratio", "trend"]
        self.scaler = scaler
        self.postprocess_fn = postprocess_fn
        self.logger = logger or logging.getLogger("MLScorer")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def score(self, market_data):
        """
        Score the market data using the ML model.
        Returns a float score (regression/classification probability or class).
        """
        features = self._extract_features(market_data)
        if self.model is None:
            self.logger.warning("No ML model provided.")
            return 0.0
        if features is None:
            self.logger.warning("Feature extraction failed or insufficient data.")
            return 0.0
        try:
            features = np.array(features).reshape(1, -1)
            if self.scaler is not None:
                features = self.scaler.transform(features)
            # If classifier, use probability if available
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(features)
                if proba.shape[1] == 2:
                    score = float(proba[0, 1])
                else:
                    score = float(np.max(proba[0]))
                self.logger.debug(f"Predicted probability score: {score}")
            else:
                pred = self.model.predict(features)
                score = float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
                self.logger.debug(f"Predicted value score: {score}")
            if self.postprocess_fn:
                score = self.postprocess_fn(score)
            return score
        except Exception as e:
            self.logger.error(f"MLScorer prediction error: {e}", exc_info=True)
            return 0.0

    def _extract_features(self, market_data):
        """
        Extract features for the ML model from market data.
        Extend this method for more features as needed.
        """
        try:
            orderbook = market_data.get("orderbook")
            kline_data = market_data.get("kline_data")
            if not orderbook or not kline_data or len(kline_data) < 2:
                return None
            bids = orderbook.bids[:5]
            asks = orderbook.asks[:5]
            buy_depth = sum(qty for price, qty in bids) if bids else 0
            sell_depth = sum(qty for price, qty in asks) if asks else 0
            depth_ratio = buy_depth / sell_depth if sell_depth else 1.0
            prev, curr = kline_data[-2].close, kline_data[-1].close
            trend = (curr - prev) / prev if prev else 0
            # Additional features
            high = kline_data[-1].high
            low = kline_data[-1].low
            close = kline_data[-1].close
            volume = getattr(kline_data[-1], "volume", 0)
            avg_volume = np.mean([getattr(k, "volume", 0) for k in kline_data[-10:]]) if len(kline_data) >= 10 else volume
            volatility = np.std([k.close for k in kline_data[-10:]]) if len(kline_data) >= 10 else 0
            # Example: add more features as needed
            features = [
                depth_ratio,
                trend,
                high,
                low,
                close,
                volume,
                avg_volume,
                volatility
            ]
            # If custom feature_names, align features accordingly
            if self.feature_names and len(features) != len(self.feature_names):
                self.logger.warning("Feature count does not match feature_names.")
            return features
        except Exception as e:
            self.logger.error(f"Feature extraction error: {e}", exc_info=True)
            return None
