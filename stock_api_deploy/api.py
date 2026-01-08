from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from data_layer import BISTDataManager
from analysis_layer import FinancialAnalyzer
from transformers import pipeline
import yfinance as yf
import pandas as pd
import joblib
import numpy as np
import os
import json
import traceback

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Stock Analysis API",
    description="API for finding undervalued stocks and analyzing performance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core
dm = BISTDataManager()
analyzer = FinancialAnalyzer(dm)

# Initialize Sentiment Analysis Model (Hugging Face)
print("Loading Sentiment Model...")
try:
    sentiment_pipe = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    print("Sentiment Model Loaded!")
except Exception as e:
    print(f"Error loading sentiment model: {e}")
    sentiment_pipe = None

# Initialize Custom AdaBoost Model
print("Loading Custom AdaBoost Model...")
try:
    custom_model = joblib.load('adaboost_model.joblib')
    scaler = joblib.load('scaler.joblib')
    print("AdaBoost Model Loaded!")
except Exception as e:
    print(f"Warning: Could not load custom model: {e}")
    custom_model = None
    scaler = None

def calculate_features(df):
    df = df.copy()
    try:
        df['Returns'] = df['Close'].pct_change()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['Dist_SMA_20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
        df['Dist_SMA_50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['Vol_Change'] = df['Volume'].pct_change()
        
        return df[['Returns', 'Dist_SMA_20', 'Dist_SMA_50', 'RSI', 'Vol_Change']].iloc[[-1]]
    except Exception as e:
        print(f"Feature calc error: {e}")
        return pd.DataFrame()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Stock Analysis API is running"}

@app.get("/health")
def health_check():
    metadata = {}
    if os.path.exists("model_metadata.json"):
        with open("model_metadata.json", "r") as f:
            metadata = json.load(f)
    return {"status": "healthy", "model_metadata": metadata}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    """
    Simple prediction endpoint + Custom Model.
    """
    df = dm.get_stock_data(symbol, period="1y")
    if df.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
        
    last_close = float(df['Close'].iloc[-1])
    sma20 = float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) > 20 else last_close
    
    prediction = "UP" if last_close > sma20 else "DOWN"
    
    # Custom Model Prediction
    custom_pred = "Insufficient Data"
    custom_conf = 0.0
    
    if custom_model and scaler:
        try:
            # We need enough data for rolling windows (50 days)
            # Fetch slightly more history ensuring we get it
            # We already fetched 1y above, so reuse 'df'
            if not df.empty and len(df) > 60:
                features = calculate_features(df)
                if not features.empty:
                    features = features.fillna(0)
                    features_scaled = scaler.transform(features)
                    prob = custom_model.predict_proba(features_scaled)[0]
                    # Class 1 is UP
                    custom_pred = "UP" if prob[1] > 0.5 else "DOWN"
                    custom_conf = float(prob[1]) if custom_pred == "UP" else float(prob[0])
            else:
                 print(f"Not enough data for {symbol}: {len(df)} rows")
        except Exception as e:
            print(f"Prediction error for {symbol}: {e}")
            traceback.print_exc()

    return {
        "symbol": symbol,
        "prediction": prediction,
        "current_price": last_close,
        "sma_20": sma20,
        "custom_model": {
            "prediction": custom_pred,
            "confidence": custom_conf,
            "model_type": "AdaBoost"
        }
    }

@app.get("/analyze/{symbol}")
def analyze(symbol: str):
    """
    Returns financial ratios.
    """
    r = analyzer.calculate_ratios(symbol)
    return {
        "symbol": symbol,
        "ratios": {
            "pe_ratio": r.pe_ratio,
            "pb_ratio": r.pb_ratio,
            "roe": r.roe,
            "debt_to_equity": r.debt_to_equity
        }
    }

@app.get("/undervalued")
def get_undervalued(limit: int = 5):
    """
    Returns a list of undervalued stocks.
    """
    stocks = analyzer.find_undervalued_stocks(limit=limit)
    return {"undervalued_stocks": stocks}

@app.get("/sentiment/{symbol}")
def get_sentiment(symbol: str):
    """
    Fetches news and performs sentiment analysis using Hugging Face FinBERT.
    """
    try:
        if sentiment_pipe is None:
             return {"symbol": symbol, "error": "Sentiment model not loaded."}

        # 1. Fetch News
        ticker = yf.Ticker(symbol)
        news_items = ticker.news
        
        if not news_items:
             print(f"No news found for {symbol}. Trying generic market news (SPY)...")
             news_items = yf.Ticker("SPY").news
             if not news_items: 
                return {"symbol": symbol, "overall_sentiment": "Neutral", "news": []}
             
        # 2. Extract Headlines
        headlines = []
        if news_items:
            first_item = news_items[0]
            print(f"DEBUG: First news item structure: {first_item}")
            
            for item in news_items[:5]:
                # Try to get title from various possible keys
                title = item.get('title') or item.get('content', {}).get('title') or item.get('summary')
                if title:
                    headlines.append(title)
        
        if not headlines:
            print("No headlines extractable from news items.")
            return {"symbol": symbol, "overall_sentiment": "Neutral", "news": []}

        # 3. Analyze Sentiment
        results = sentiment_pipe(headlines)
        
        # 4. Aggregate Results
        sentiment_score = 0
        analyzed_news = []
        
        for headline, result in zip(headlines, results):
            score = result['score'] if result['label'] == 'positive' else -result['score'] if result['label'] == 'negative' else 0
            sentiment_score += score
            analyzed_news.append({
                "title": headline,
                "label": result['label'],
                "score": result['score']
            })
            
        overall = "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral"
        
        return {
            "symbol": symbol,
            "overall_sentiment": overall,
            "sentiment_score": sentiment_score,
            "news": analyzed_news
        }
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return {"symbol": symbol, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
