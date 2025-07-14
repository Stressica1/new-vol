import os
import joblib
from typing import Tuple, Optional

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
try:
    from xgboost import XGBRegressor  # type: ignore
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False
try:
    import lightgbm as lgb  # type: ignore
    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False
try:
    from catboost import CatBoostRegressor  # type: ignore
    _HAS_CAT = True
except ImportError:
    _HAS_CAT = False
from sklearn.preprocessing import StandardScaler

import ta

from config import TradingConfig


class AIStopLossTakeProfit:
    """AI/ML-driven stop-loss and take-profit engine ⚡️

    This module trains a lightweight machine-learning model (RandomForestRegressor)
    to predict the short-term volatility of a trading pair.  The predicted one-step
    absolute return is converted into dynamic stop-loss (SL) and take-profit (TP)
    percentages.  Position sizing continues to follow a conventional fixed-risk-per-trade
    approach – *only SL / TP are determined with AI* as requested.
    """

    MODEL_VERSION = "1.0"

    def __init__(
        self,
        model_path: str = "models/ai_sl_tp_rf.joblib",
        lookahead: int = 5,
        n_estimators: int = 150,
        sl_multiplier: float = 0.8,
        tp_multiplier: float = 2.5,
        random_state: int = 42,
    ):
        self.model_path = model_path
        self.lookahead = lookahead  # bars to look ahead when training target
        self.sl_multiplier = sl_multiplier
        self.tp_multiplier = tp_multiplier
        self.random_state = random_state
        self.n_estimators = n_estimators

        self.config = TradingConfig()

        # ML components
        self.scaler: Optional[StandardScaler] = None
        self.rf_model: Optional[RandomForestRegressor] = None
        self.gbr_model: Optional[GradientBoostingRegressor] = None
        self.xgb_model: Optional['XGBRegressor'] = None  # type: ignore
        self.lgb_model: Optional['lgb.LGBMRegressor'] = None  # type: ignore
        self.cat_model: Optional['CatBoostRegressor'] = None  # type: ignore
        self.model_weights: Optional[np.ndarray] = None

        # Try to load an existing model
        self._load_model()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def train(self, df: pd.DataFrame) -> None:
        """Train / update the underlying ML model.

        Parameters
        ----------
        df : pd.DataFrame
            Historical OHLCV market data with *open, high, low, close, volume* columns.
        """
        logger.info("🧠 Training AI SL/TP model – this should only take a moment ...")

        features, target = self._prepare_training_data(df)
        if len(features) < 100:
            logger.warning("⚠️   Not enough samples ({} rows) to train the model – need at least 100. "
                           "Falling back to ATR/static stops.".format(len(features)))
            return

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(features)

        self.rf_model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=None,
            n_jobs=-1,
            random_state=self.random_state,
        )
        self.rf_model.fit(X_scaled, target)

        # Gradient Boosting (adds bias-variance diversity)
        self.gbr_model = GradientBoostingRegressor(random_state=self.random_state)
        self.gbr_model.fit(X_scaled, target)

        if _HAS_XGB:
            self.xgb_model = XGBRegressor(objective='reg:squarederror', n_estimators=200, learning_rate=0.05, random_state=self.random_state)
            self.xgb_model.fit(X_scaled, target)
        # Fit LightGBM
        if _HAS_LGB:
            self.lgb_model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, objective='regression', random_state=self.random_state)
            self.lgb_model.fit(X_scaled, target)
        if _HAS_CAT:
            self.cat_model = CatBoostRegressor(iterations=200, learning_rate=0.05, depth=6, loss_function='MAE', verbose=False, random_state=self.random_state)
            self.cat_model.fit(X_scaled, target)
        # Determine model weights based on training MAE
        preds_rf = self.rf_model.predict(X_scaled)
        preds_gbr = self.gbr_model.predict(X_scaled)
        errs = [np.mean(np.abs(preds_rf - target)), np.mean(np.abs(preds_gbr - target))]
        if _HAS_XGB:
            preds_xgb = self.xgb_model.predict(X_scaled)
            errs.append(np.mean(np.abs(preds_xgb - target)))
        if _HAS_LGB:
            preds_lgb = self.lgb_model.predict(X_scaled)
            errs.append(np.mean(np.abs(preds_lgb - target)))
        if _HAS_CAT:
            preds_cat = self.cat_model.predict(X_scaled)
            errs.append(np.mean(np.abs(preds_cat - target)))
        inv_errs = 1 / np.array(errs)
        self.model_weights = inv_errs / inv_errs.sum()
        logger.success("✅ AI SL/TP model trained on %d samples", len(target))

        # Persist to disk for future sessions
        self._save_model()

    def calculate_sl_tp(
        self,
        entry_price: float,
        side: str,
        market_data: pd.DataFrame,
    ) -> Tuple[float, float]:
        """Return AI-based (sl_price, tp_price).

        If the model is unavailable or cannot generate a prediction, the function
        falls back to ATR-driven stops (see TradingConfig) or static pct stops.
        """
        # 1) Derive volatility prediction (absolute return percentage)
        predicted_move = self._predict_volatility(market_data)

        # Apply config bounds and multipliers
        if predicted_move is None:
            # Fallback path – ATR or static
            atr_pct = self._atr_pct(market_data)
            predicted_move = atr_pct or (self.config.stop_loss_pct / 100)

        sl_pct = np.clip(
            predicted_move * self.sl_multiplier,
            self.config.min_stop_loss_pct / 100,
            self.config.max_stop_loss_pct / 100,
        )
        tp_pct = predicted_move * self.tp_multiplier

        if side.lower() in {"long", "buy", "open_long"}:
            sl_price = entry_price * (1 - sl_pct)
            tp_price = entry_price * (1 + tp_pct)
        else:  # SHORT
            sl_price = entry_price * (1 + sl_pct)
            tp_price = entry_price * (1 - tp_pct)

        logger.debug(
            "AI SL/TP – side=%s entry=%.5f → sl_pct=%.2f%% tp_pct=%.2f%% sl=%.5f tp=%.5f",
            side,
            entry_price,
            sl_pct * 100,
            tp_pct * 100,
            sl_price,
            tp_price,
        )

        return sl_price, tp_price

    def calculate_position_size(
        self,
        account_equity: float,
        entry_price: float,
        sl_price: float,
    ) -> float:
        """Conventional position sizing based on fixed risk-per-trade."""
        risk_amount = account_equity * self.config.risk_per_trade
        price_diff = abs(entry_price - sl_price)
        if price_diff <= 0:
            logger.warning("Price difference between entry and SL is zero. Returning size 0.")
            return 0.0
        size = risk_amount / price_diff

        # Respect min / max order constraints
        size = max(size, self.config.min_order_size / entry_price)
        size = min(size, self.config.max_position_size / entry_price)
        return size

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prepare_training_data(self, df: pd.DataFrame):
        df = df.copy().dropna()
        # Ensure we have at least some rows; otherwise return empty arrays
        if len(df) < 20:
            return np.empty((0, 6)), np.empty((0,))

        # FEATURES ------------------------------------------------------
        df_feats = pd.DataFrame(index=df.index)
        df_feats["return_1"] = df["close"].pct_change()
        df_feats["sma_10"] = df["close"].rolling(10).mean()
        df_feats["sma_30"] = df["close"].rolling(30).mean()
        df_feats["sma_ratio"] = df_feats["sma_10"] / df_feats["sma_30"] - 1

        # MACD components
        macd = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, window_sign=9)
        df_feats["macd"] = macd.macd()
        df_feats["macd_signal"] = macd.macd_signal()
        df_feats["macd_diff"] = macd.macd_diff()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df_feats["bb_high"] = bb.bollinger_hband() / df["close"] - 1
        df_feats["bb_low"] = df["close"] / bb.bollinger_lband() - 1

        # Stochastic RSI
        stoch = ta.momentum.StochRSIIndicator(df["close"], window=14)
        df_feats["stoch_rsi_k"] = stoch.stochrsi_k()
        df_feats["stoch_rsi_d"] = stoch.stochrsi_d()

        rsi_indicator = ta.momentum.RSIIndicator(close=df["close"], window=14)
        df_feats["rsi"] = rsi_indicator.rsi()

        if len(df) >= 14:
            atr_indicator = ta.volatility.AverageTrueRange(
                high=df["high"], low=df["low"], close=df["close"], window=14
            )
            df_feats["atr_pct"] = atr_indicator.average_true_range() / df["close"]
        else:
            df_feats["atr_pct"] = 0.01  # default 1% if insufficient data

        df_feats["volume_norm"] = df["volume"] / df["volume"].rolling(20).mean()

        df_feats = df_feats.fillna(method="bfill").fillna(method="ffill")

        # TARGET --------------------------------------------------------
        forward_returns = (
            df["close"].shift(-self.lookahead) - df["close"]
        ) / df["close"]
        target_volatility = forward_returns.abs()

        # Align indices
        df_feats = df_feats.iloc[:-self.lookahead]
        target_volatility = target_volatility.iloc[:-self.lookahead]

        return df_feats.values, target_volatility.values

    def _predict_volatility(self, market_data: pd.DataFrame) -> Optional[float]:
        # Ensure we have a fitted model & scaler
        if len(market_data) < 30:
            return None  # Not enough data yet

        if (self.rf_model is None or self.gbr_model is None or self.scaler is None):
            logger.info("AI SL/TP model unavailable – trying to train on provided data ...")
            self.train(market_data)
            if self.rf_model is None:
                return None

        # Build feature row from latest market_data
        latest_feats_df, _ = self._prepare_training_data(market_data.tail(100))
        if latest_feats_df.size == 0:
            logger.warning("Feature extraction failed – no data.")
            return None

        latest_feats = latest_feats_df[-1].reshape(1, -1)
        latest_scaled = self.scaler.transform(latest_feats)
        preds = []
        weights = []
        pred_rf = float(self.rf_model.predict(latest_scaled)[0])
        preds.append(pred_rf)
        weights.append(self.model_weights[0] if self.model_weights is not None else 1)
        pred_gbr = float(self.gbr_model.predict(latest_scaled)[0])
        preds.append(pred_gbr)
        weights.append(self.model_weights[1] if self.model_weights is not None else 1)
        if _HAS_XGB and self.xgb_model is not None:
            pred_xgb = float(self.xgb_model.predict(latest_scaled)[0])
            preds.append(pred_xgb)
            weights.append(self.model_weights[len(weights)] if self.model_weights is not None else 1)
        if _HAS_LGB and self.lgb_model is not None:
            pred_lgb = float(self.lgb_model.predict(latest_scaled)[0])
            preds.append(pred_lgb)
            weights.append(self.model_weights[len(weights)] if self.model_weights is not None else 1)
        if _HAS_CAT and self.cat_model is not None:
            pred_cat = float(self.cat_model.predict(latest_scaled)[0])
            preds.append(pred_cat)
            weights.append(self.model_weights[len(weights)] if self.model_weights is not None else 1)
        pred = float(np.average(preds, weights=weights))
        return max(pred, 0)

    def _atr_pct(self, df: pd.DataFrame) -> Optional[float]:
        try:
            atr_indicator = ta.volatility.AverageTrueRange(
                high=df["high"], low=df["low"], close=df["close"], window=self.config.atr_period
            )
            atr_val = atr_indicator.average_true_range().iloc[-1]
            current_price = df["close"].iloc[-1]
            if current_price > 0:
                return atr_val / current_price
        except Exception as e:
            logger.error("ATR calculation failed: %s", e)
        return None

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save_model(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(
                {
                    "version": self.MODEL_VERSION,
                    "rf_model": self.rf_model,
                    "gbr_model": self.gbr_model,
                    "xgb_model": self.xgb_model if _HAS_XGB else None,
                    "lgb_model": self.lgb_model if _HAS_LGB else None,
                    "scaler": self.scaler,
                    "model_weights": self.model_weights,
                    "cat_model": self.cat_model if _HAS_CAT else None,
                },
                self.model_path,
            )
            logger.debug("Saved AI SL/TP model to %s", self.model_path)
        except Exception as e:
            logger.error("Could not save model: %s", e)

    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.info("AI SL/TP model file not found – will train a new model when needed.")
            return
        try:
            data = joblib.load(self.model_path)
            if data.get("version") != self.MODEL_VERSION:
                logger.info("Model version mismatch – retraining required.")
                return
            self.rf_model = data.get("rf_model")
            self.gbr_model = data.get("gbr_model")
            self.xgb_model = data.get("xgb_model") if _HAS_XGB else None
            self.lgb_model = data.get("lgb_model") if _HAS_LGB else None
            self.cat_model = data.get("cat_model") if _HAS_CAT else None
            self.scaler = data["scaler"]
            self.model_weights = data.get("model_weights")
            logger.success("✨ Loaded pre-trained AI SL/TP model from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load AI SL/TP model: %s", e)