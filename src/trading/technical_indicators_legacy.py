from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:

    @staticmethod
    def calculate_atr(high_prices: List[float], low_prices: List[float], close_prices: List[float], period: int) -> List[float]:
        # ATR calculation logic (not provided in the code block)
        pass

    @staticmethod
    def calculate_supertrend(high_prices: List[float], low_prices: List[float], close_prices: List[float], 
                           atr_period: int = 10, multiplier: float = 3.0) -> Tuple[List[float], List[int]]:
        """
        Calculate SuperTrend indicator
        
        SuperTrend is a trend-following indicator that uses Average True Range (ATR) 
        to calculate dynamic support and resistance levels.
        
        Returns:
            Tuple[List[float], List[int]]: (supertrend_values, trend_direction)
            trend_direction: 1 for bullish, -1 for bearish
        """
        try:
            if len(high_prices) < atr_period or len(low_prices) < atr_period or len(close_prices) < atr_period:
                return [close_prices[-1] if close_prices else 0.0] * len(close_prices), [1] * len(close_prices)
            
            # Calculate ATR
            atr = TechnicalIndicators.calculate_atr(high_prices, low_prices, close_prices, atr_period)
            if atr == 0:
                return [close_prices[-1]] * len(close_prices), [1] * len(close_prices)
            
            # Calculate HL2 (typical price)
            hl2 = [(high_prices[i] + low_prices[i]) / 2 for i in range(len(high_prices))]
            
            # Calculate basic upper and lower bands
            upper_band = [hl2[i] + (multiplier * atr) for i in range(len(hl2))]
            lower_band = [hl2[i] - (multiplier * atr) for i in range(len(hl2))]
            
            # Initialize SuperTrend arrays
            supertrend = [0.0] * len(close_prices)
            direction = [1] * len(close_prices)
            
            # Calculate SuperTrend values
            for i in range(len(close_prices)):
                if i == 0:
                    supertrend[i] = upper_band[i]
                    direction[i] = -1
                    continue
                
                # Calculate final upper and lower bands
                final_upper = upper_band[i] if (upper_band[i] < upper_band[i-1] or close_prices[i-1] > upper_band[i-1]) else upper_band[i-1]
                final_lower = lower_band[i] if (lower_band[i] > lower_band[i-1] or close_prices[i-1] < lower_band[i-1]) else lower_band[i-1]
                
                # Determine trend direction
                if close_prices[i] <= final_lower:
                    supertrend[i] = final_lower
                    direction[i] = 1  # Bullish
                elif close_prices[i] >= final_upper:
                    supertrend[i] = final_upper
                    direction[i] = -1  # Bearish
                else:
                    supertrend[i] = supertrend[i-1]
                    direction[i] = direction[i-1]
                
                # Override for trend changes
                if direction[i] == 1 and direction[i-1] == -1:
                    supertrend[i] = final_lower
                elif direction[i] == -1 and direction[i-1] == 1:
                    supertrend[i] = final_upper
            
            return supertrend, direction
            
        except Exception as e:
            logger.error(f"Error calculating SuperTrend: {e}")
            return [close_prices[-1] if close_prices else 0.0] * len(close_prices), [1] * len(close_prices)

    @staticmethod
    def calculate_vhma(high_prices: List[float], low_prices: List[float], close_prices: List[float], 
                      volume: List[float], period: int = 14) -> List[float]:
        """
        Calculate Volume Weighted Hull Moving Average (VHMA)
        
        VHMA combines Hull Moving Average with volume weighting for more accurate
        trend detection with volume consideration.
        """
        try:
            if len(close_prices) < period:
                return close_prices
            
            # Calculate typical price
            typical_prices = [(high_prices[i] + low_prices[i] + close_prices[i]) / 3 for i in range(len(close_prices))]
            
            # Volume weighted typical price
            vwap = []
            for i in range(len(typical_prices)):
                if i < period:
                    vwap.append(typical_prices[i])
                else:
                    numerator = sum(typical_prices[j] * volume[j] for j in range(i - period + 1, i + 1))
                    denominator = sum(volume[j] for j in range(i - period + 1, i + 1))
                    vwap.append(numerator / denominator if denominator > 0 else typical_prices[i])
            
            # Hull MA calculation
            half_period = period // 2
            sqrt_period = int(period ** 0.5)
            
            # WMA calculations
            wma_half = TechnicalIndicators.calculate_wma(vwap, half_period)
            wma_full = TechnicalIndicators.calculate_wma(vwap, period)
            
            # Hull calculation
            hull_raw = [2 * wma_half[i] - wma_full[i] for i in range(len(wma_half))]
            vhma = TechnicalIndicators.calculate_wma(hull_raw, sqrt_period)
            
            return vhma
            
        except Exception as e:
            logger.error(f"Error calculating VHMA: {e}")
            return close_prices
    
    @staticmethod
    def calculate_mfi(high_prices: List[float], low_prices: List[float], close_prices: List[float], 
                     volume: List[float], period: int = 14) -> List[float]:
        """
        Calculate Money Flow Index (MFI)
        
        MFI is a momentum oscillator that uses price and volume to identify
        overbought/oversold conditions and money flow direction.
        """
        try:
            if len(close_prices) < period + 1:
                return [50.0] * len(close_prices)
            
            # Calculate typical price
            typical_prices = [(high_prices[i] + low_prices[i] + close_prices[i]) / 3 for i in range(len(close_prices))]
            
            # Calculate raw money flow
            raw_money_flow = [typical_prices[i] * volume[i] for i in range(len(typical_prices))]
            
            # Calculate positive and negative money flow
            positive_flows = []
            negative_flows = []
            
            for i in range(1, len(typical_prices)):
                if typical_prices[i] > typical_prices[i-1]:
                    positive_flows.append(raw_money_flow[i])
                    negative_flows.append(0)
                elif typical_prices[i] < typical_prices[i-1]:
                    positive_flows.append(0)
                    negative_flows.append(raw_money_flow[i])
                else:
                    positive_flows.append(0)
                    negative_flows.append(0)
            
            # Calculate MFI
            mfi = [50.0]  # Initial value
            
            for i in range(period, len(positive_flows)):
                positive_mf = sum(positive_flows[i-period:i])
                negative_mf = sum(negative_flows[i-period:i])
                
                if negative_mf == 0:
                    mfi.append(100.0)
                else:
                    money_flow_ratio = positive_mf / negative_mf
                    mfi_value = 100 - (100 / (1 + money_flow_ratio))
                    mfi.append(mfi_value)
            
            # Fill initial values
            while len(mfi) < len(close_prices):
                mfi.insert(0, 50.0)
            
            return mfi
            
        except Exception as e:
            logger.error(f"Error calculating MFI: {e}")
            return [50.0] * len(close_prices)
    
    @staticmethod
    def calculate_bollinger_bands(close_prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """
        Calculate Bollinger Bands
        
        Returns:
            Tuple[List[float], List[float], List[float]]: (upper_band, middle_band, lower_band)
        """
        try:
            if len(close_prices) < period:
                return close_prices, close_prices, close_prices
            
            # Calculate middle band (SMA)
            middle_band = TechnicalIndicators.calculate_sma(close_prices, period)
            
            # Calculate standard deviation
            upper_band = []
            lower_band = []
            
            for i in range(len(close_prices)):
                if i < period - 1:
                    upper_band.append(close_prices[i])
                    lower_band.append(close_prices[i])
                else:
                    # Calculate standard deviation for current period
                    period_prices = close_prices[i-period+1:i+1]
                    mean_price = sum(period_prices) / period
                    variance = sum((price - mean_price) ** 2 for price in period_prices) / period
                    std = variance ** 0.5
                    
                    upper_band.append(middle_band[i] + (std * std_dev))
                    lower_band.append(middle_band[i] - (std * std_dev))
            
            return upper_band, middle_band, lower_band
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return close_prices, close_prices, close_prices
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return prices
            
            sma = []
            for i in range(len(prices)):
                if i < period - 1:
                    sma.append(prices[i])
                else:
                    sma.append(sum(prices[i-period+1:i+1]) / period)
            
            return sma
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return prices
    
    @staticmethod
    def calculate_wma(prices: List[float], period: int) -> List[float]:
        """Calculate Weighted Moving Average"""
        try:
            if len(prices) < period:
                return prices
            
            wma = []
            for i in range(len(prices)):
                if i < period - 1:
                    wma.append(prices[i])
                else:
                    weights = list(range(1, period + 1))
                    weighted_sum = sum(prices[i-period+1+j] * weights[j] for j in range(period))
                    weight_sum = sum(weights)
                    wma.append(weighted_sum / weight_sum)
            
            return wma
            
        except Exception as e:
            logger.error(f"Error calculating WMA: {e}")
            return prices