import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BISTDataManager:
    """
    Data Manager for Stock Analysis.
    Originally designed for BIST, now adapted for general usage (S&P 500 support) via yfinance.
    """
    def __init__(self):
        self.cache = {}

    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetches historical stock data for the given symbol and period.
        """
        try:
            # yfinance periodic strings: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            
            if history.empty:
                print(f"Warning: No data found for {symbol}")
                return pd.DataFrame()
            
            # Ensure standard columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in history.columns for col in required_cols):
                 return pd.DataFrame()

            return history

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_financials(self, symbol: str):
        """
        Fetches financial data (balance sheet, financials, etc.)
        """
        try:
            ticker = yf.Ticker(symbol)
            # Fetching data can be slow, so we cache it lightly if needed, but for now direct call
            return {
                'info': ticker.info,
                'balance_sheet': ticker.balance_sheet,
                'financials': ticker.financials,
                'cashflow': ticker.cashflow
            }
        except Exception as e:
            print(f"Error fetching financials for {symbol}: {e}")
            return None
