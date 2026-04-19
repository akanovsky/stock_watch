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
    latest = df.iloc[-1]

    return {
        'low': float(latest['Low']),
        'high': float(latest['High']),
        'close': float(latest['Close']),
        'open': float(latest['Open']),
        'volume': int(latest['Volume']),
        'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name)
    }


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
        history.append({
            'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
            'volume': int(row['Volume'])
        })

    return history
