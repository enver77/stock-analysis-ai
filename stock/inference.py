import argparse
import json
from data_layer import BISTDataManager
from analysis_layer import FinancialAnalyzer

def predict(symbol: str):
    """
    Inference: Predicts next movement based on simple heuristic (e.g. Price vs SMA).
    Returns JSON.
    """
    dm = BISTDataManager()
    analyzer = FinancialAnalyzer(dm)
    
    # Get recent data
    df = dm.get_stock_data(symbol, period="3mo")
    if df.empty:
        print(json.dumps({"error": "No data"}))
        return

    # Calculate basic features
    last_close = df['Close'].iloc[-1]
    sma20 = df['Close'].rolling(20).mean().iloc[-1]
    
    # Prediction logic: If Price > SMA20 -> UP, else DOWN
    prediction = "UP" if last_close > sma20 else "DOWN"
    confidence = "HIGH" if abs(last_close - sma20) / last_close > 0.02 else "LOW"
    
    result = {
        "symbol": symbol,
        "current_price": last_close,
        "prediction": prediction,
        "confidence": confidence,
        "reason": f"Price is {'above' if prediction=='UP' else 'below'} 20-day SMA"
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str)
    args = parser.parse_args()
    predict(args.symbol)
