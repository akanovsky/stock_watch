"""
yfinance service layer for fetching stock data from Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_monthly_data(ticker_symbol: str) -> pd.DataFrame:
    """
    Fetch monthly stock data for the last 3 months from Yahoo Finance.
    Starts from today to include the most recent data.

    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        DataFrame with OHLCV data indexed by date
    """
    ticker = yf.Ticker(ticker_symbol)
    # Fetch 3 months of daily data, starting from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    df = ticker.history(start=start_date, end=end_date + timedelta(days=1), interval='1d')

    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker_symbol}")

    return df


def get_current_low_high(ticker_symbol: str) -> dict:
    """
    Get the latest low and high prices for a ticker.

    Args:
        ticker_symbol: Stock ticker symbol

    Returns:
        Dictionary with 'low' and 'high' prices
    """
    df = fetch_monthly_data(ticker_symbol)
    # Use the last row with valid Close price (skip today if market not closed yet)
    valid_rows = df[df['Close'].notna()]
    if valid_rows.empty:
        raise ValueError(f"No valid price data for ticker: {ticker_symbol}")
    latest = valid_rows.iloc[-1]

    return {
        'low': safe_float(latest['Low']),
        'high': safe_float(latest['High']),
        'close': safe_float(latest['Close']),
        'open': safe_float(latest['Open']),
        'volume': safe_int(latest['Volume']),
        'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name)
    }


import math

def safe_float(value, default=0.0):
    """Convert NaN/Inf to default value."""
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Convert NaN/Inf to default value."""
    try:
        i = int(value)
        if math.isnan(i) or math.isinf(i):
            return default
        return i
    except (ValueError, TypeError):
        return default

def get_full_monthly_history(ticker_symbol: str) -> list[dict]:
    """
    Get full monthly history as a list of dictionaries.

    Args:
        ticker_symbol: Stock ticker symbol

    Returns:
        List of dictionaries with OHLCV data
    """
    df = fetch_monthly_data(ticker_symbol)

    history = []
    for date, row in df.iterrows():
        close_price = safe_float(row['Close'])
        # Skip rows with invalid/missing close prices (e.g., weekends, holidays)
        if close_price == 0:
            continue
        history.append({
            'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
            'open': safe_float(row['Open']),
            'high': safe_float(row['High']),
            'low': safe_float(row['Low']),
            'close': close_price,
            'volume': safe_int(row['Volume'])
        })

    return history
