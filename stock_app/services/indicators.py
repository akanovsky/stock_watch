"""
Technical indicators module for calculating MACD and RSI.
"""
import pandas as pd
import numpy as np


def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        df: DataFrame with 'Close' column
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)

    Returns:
        DataFrame with MACD line, signal line, and histogram
    """
    df = df.copy()

    # Calculate EMAs
    ema_fast = df['Close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow_period, adjust=False).mean()

    # MACD line
    df['MACD'] = ema_fast - ema_slow

    # Signal line (EMA of MACD)
    df['Signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()

    # Histogram
    df['Histogram'] = df['MACD'] - df['Signal']

    return df


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        df: DataFrame with 'Close' column
        period: RSI period (default 14)

    Returns:
        DataFrame with RSI column
    """
    df = df.copy()

    # Calculate price changes
    delta = df['Close'].diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    # Calculate average gains and losses using EMA
    avg_gain = gains.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = losses.ewm(com=period - 1, min_periods=period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df


def get_recommendation(macd_df: pd.DataFrame, rsi_value: float) -> str:
    """
    Generate buy/sell/hold recommendation based on MACD crossover and RSI.

    Args:
        macd_df: DataFrame with MACD and Signal columns
        rsi_value: Current RSI value

    Returns:
        Recommendation string: 'BUY', 'SELL', or 'HOLD'
    """
    if len(macd_df) < 2:
        return 'HOLD'

    # Get the last two rows for crossover detection
    recent = macd_df.tail(2)
    prev_macd = recent.iloc[0]['MACD']
    curr_macd = recent.iloc[1]['MACD']
    prev_signal = recent.iloc[0]['Signal']
    curr_signal = recent.iloc[1]['Signal']

    # Detect crossover
    bullish_crossover = (prev_macd <= prev_signal) and (curr_macd > curr_signal)
    bearish_crossover = (prev_macd >= prev_signal) and (curr_macd < curr_signal)

    # RSI thresholds
    oversold = rsi_value < 30
    overbought = rsi_value > 70

    # Decision logic
    if bullish_crossover and oversold:
        return 'BUY'
    elif bearish_crossover and overbought:
        return 'SELL'
    elif bullish_crossover:
        return 'BUY'
    elif bearish_crossover:
        return 'SELL'
    elif curr_macd > curr_signal:
        return 'HOLD'  # Bullish but no strong signal
    else:
        return 'HOLD'  # Bearish but no strong signal


def analyze_stock(ticker_symbol: str) -> dict:
    """
    Perform complete technical analysis for a stock.

    Args:
        ticker_symbol: Stock ticker symbol

    Returns:
        Dictionary with analysis results
    """
    from .yfinance_service import fetch_monthly_data

    df = fetch_monthly_data(ticker_symbol)

    # Calculate indicators
    df = calculate_macd(df)
    df = calculate_rsi(df)

    latest = df.iloc[-1]

    # Get recommendation
    recommendation = get_recommendation(df, latest['RSI'])

    return {
        'symbol': ticker_symbol,
        'current_price': float(latest['Close']),
        'low': float(latest['Low']),
        'high': float(latest['High']),
        'open': float(latest['Open']),
        'volume': int(latest['Volume']),
        'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
        'macd': float(latest['MACD']),
        'signal': float(latest['Signal']),
        'histogram': float(latest['Histogram']),
        'rsi': float(latest['RSI']),
        'recommendation': recommendation
    }
