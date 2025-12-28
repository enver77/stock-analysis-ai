import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import json
import datetime
import os

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def prepare_data(ticker="SPY", period="2y"):
    """
    Fetches data and engineers features for training.
    """
    print(f"Fetching data for {ticker}...")
    df = yf.ticker.Ticker(ticker).history(period=period)
    
    if df.empty:
        raise ValueError("No data fetched.")
        
    # Feature Engineering
    df['Returns'] = df['Close'].pct_change()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Relative features (normalized) to make model ticker-agnostic
    df['Dist_SMA_20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
    df['Dist_SMA_50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
    df['RSI'] = calculate_rsi(df['Close'])
    df['Vol_Change'] = df['Volume'].pct_change()
    
    # Target: 1 if Next Day Close > Current Close, else 0
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # Drop NaNs created by rolling windows
    df = df.dropna()
    
    features = ['Returns', 'Dist_SMA_20', 'Dist_SMA_50', 'RSI', 'Vol_Change']
    X = df[features]
    y = df['Target']
    
    return X, y

def build_model():
    print("Starting Custom Model Training (AdaBoost)...")
    
    try:
        # 1. Get Training Data (Use SPY as a general proxy for market behavior)
        X, y = prepare_data("SPY", period="5y")
        
        # 2. Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
        
        # 3. Scale Features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 4. Train AdaBoost
        # Base estimator: Random Forest (User mentioned "AdaBoost... powerful combination")
        # Standard AdaBoost uses Decision Stumps (depth=1), but we can use slightly deeper trees.
        dt = DecisionTreeClassifier(max_depth=1, random_state=42)
        model = AdaBoostClassifier(estimator=dt, n_estimators=100, random_state=42)
        
        print("Training model...")
        model.fit(X_train_scaled, y_train)
        
        # 5. Evaluate
        preds = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, preds)
        print("------------------------------------------------")
        print(f"Model Accuracy on Test Set: {acc:.4f}")
        print("------------------------------------------------")
        
        # 6. Save Artifacts
        print("Saving model artifacts...")
        joblib.dump(model, 'adaboost_model.joblib')
        joblib.dump(scaler, 'scaler.joblib')
        
        # Metadata
        metadata = {
            "model_type": "AdaBoostClassifier",
            "trained_at": datetime.datetime.now().isoformat(),
            "accuracy": acc,
            "features": ['Returns', 'Dist_SMA_20', 'Dist_SMA_50', 'RSI', 'Vol_Change']
        }
        
        with open("model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        print("Build Complete! Model is ready for production.")
        
    except Exception as e:
        print(f"Error during training: {e}")

if __name__ == "__main__":
    build_model()
