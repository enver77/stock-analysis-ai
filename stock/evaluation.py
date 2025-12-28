import argparse
from data_layer import BISTDataManager
import pandas as pd
import numpy as np

def evaluate_strategy(symbol: str):
    """
    Simple backtest: Buy if Price > SMA20, Sell if Price < SMA20.
    """
    dm = BISTDataManager()
    # Get 2 years of data for evaluation
    df = dm.get_stock_data(symbol, period="2y")
    
    if df.empty:
        print("No data.")
        return

    # Calculate indicators
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # Strategy: 1 if Price > SMA20 else 0
    df['Signal'] = np.where(df['Close'] > df['SMA20'], 1, 0)
    df['Position'] = df['Signal'].shift() # Enter next day
    
    df['Daily_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Position'] * df['Daily_Return']
    
    # Cumulative Return
    df['Cum_Market'] = (1 + df['Daily_Return']).cumprod()
    df['Cum_Strategy'] = (1 + df['Strategy_Return']).cumprod()
    
    total_market_return = (df['Cum_Market'].iloc[-1] - 1) * 100
    total_strategy_return = (df['Cum_Strategy'].iloc[-1] - 1) * 100
    
    print(f"--- Performance Evaluation: {symbol} ---")
    print(f"Period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Market Return: {total_market_return:.2f}%")
    print(f"Strategy Return (SMA20 Trend): {total_strategy_return:.2f}%")
    
    # Validation vs Training (Split 80/20)
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]
    
    train_ret = (1 + train_df['Strategy_Return']).cumprod().iloc[-1] - 1
    val_ret = (1 + val_df['Strategy_Return']).cumprod().iloc[-1] - 1
    
    print(f"Training Return: {train_ret*100:.2f}%")
    print(f"Validation Return: {val_ret*100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str)
    args = parser.parse_args()
    evaluate_strategy(args.symbol)
