import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from transformers import pipeline
import plotly.graph_objects as go
from data_layer import BISTDataManager
from analysis_layer import FinancialAnalyzer

# --- Configuration ---
st.set_page_config(page_title="Stock Analysis AI (Hugging Face Edition)", layout="wide")

# --- Model Loading (Cached) ---
@st.cache_resource
def load_models():
    print("Loading models...")
    models = {}
    
    # 1. Sentiment Model
    try:
        models['sentiment'] = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    except Exception as e:
        print(f"Sentiment Load Error: {e}")
        models['sentiment'] = None
        
    # 2. Custom AdaBoost
    try:
        models['adaboost'] = joblib.load('adaboost_model.joblib')
        models['scaler'] = joblib.load('scaler.joblib')
    except Exception as e:
        print(f"AdaBoost Load Error: {e}")
        models['adaboost'] = None
        models['scaler'] = None
        
    return models

models = load_models()
dm = BISTDataManager()
analyzer = FinancialAnalyzer(dm)

# --- Helper Functions ---
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
        return pd.DataFrame()

def analyze_sentiment(symbol):
    pipe = models['sentiment']
    if not pipe:
        return None
        
    try:
        ticker = yf.Ticker(symbol)
        news_items = ticker.news
        
        # Fallback to SPY
        if not news_items:
            news_items = yf.Ticker("SPY").news
            
        headlines = []
        if news_items:
            for item in news_items[:5]:
                title = item.get('title') or item.get('content', {}).get('title') or item.get('summary')
                if title:
                    headlines.append(title)
                    
        if not headlines:
            return None
            
        results = pipe(headlines)
        
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
        return {"overall": overall, "score": sentiment_score, "news": analyzed_news}
        
    except Exception as e:
        return None

# --- UI Layout ---
st.title("📈 Stock Analysis AI (Hugging Face Demo)")
st.caption("Powered by Custom AdaBoost, ProsusAI FinBERT, and Python")

symbol = st.text_input("Enter Stock Symbol:", value="AAPL").upper()

if st.button("Analyze Stock"):
    with st.spinner(f"Analyzing {symbol}..."):
        # 1. Fetch Data
        df = dm.get_stock_data(symbol, period="1y")
        
        if df.empty:
            st.error("Stock data not found.")
        else:
            # 2. Basic Metrics
            last_close = float(df['Close'].iloc[-1])
            sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            basic_pred = "UP" if last_close > sma20 else "DOWN"
            
            # 3. Custom Model
            custom_pred = "Insufficient Data"
            custom_conf = 0.0
            if models['adaboost'] and models['scaler'] and len(df) > 60:
                feats = calculate_features(df)
                if not feats.empty:
                     feats = feats.fillna(0)
                     feats_scaled = models['scaler'].transform(feats)
                     prob = models['adaboost'].predict_proba(feats_scaled)[0]
                     custom_pred = "UP" if prob[1] > 0.5 else "DOWN"
                     custom_conf = float(prob[1]) if custom_pred == "UP" else float(prob[0])
            
            # 4. Sentiment
            sent_data = analyze_sentiment(symbol)
            
            # 5. Financials
            ratios = analyzer.calculate_ratios(symbol)
            
            # --- Display ---
            st.success("Analysis Complete!")
            
            # Metrics Row
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"${last_close:.2f}")
            c2.metric("Basic Strategy", basic_pred, delta=f"vs SMA20 {sma20:.2f}")
            
            # Custom Model
            delta_color = "normal" if custom_pred == "UP" else "inverse"
            c3.metric("🎓 Custom AdaBoost", custom_pred, delta=f"Conf: {custom_conf*100:.1f}%", delta_color=delta_color)
            
            st.divider()
            
            # Ratios
            st.subheader("Financial Ratios")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("P/E", f"{ratios.pe_ratio:.2f}")
            r2.metric("P/B", f"{ratios.pb_ratio:.2f}")
            r3.metric("ROE", f"{ratios.roe:.2f}%")
            r4.metric("D/E", f"{ratios.debt_to_equity:.2f}")
            
            # Sentiment
            st.divider()
            st.subheader("📰 AI Sentiment Analysis")
            if sent_data:
                sc1, sc2 = st.columns([1,2])
                color = "green" if sent_data['overall'] == "Positive" else "red" if sent_data['overall'] == "Negative" else "gray"
                sc1.markdown(f"### :{color}[{sent_data['overall']}]")
                sc1.write(f"Score: {sent_data['score']:.2f}")
                
                with sc2:
                    for n in sent_data['news']:
                        icon = "🟢" if n['label'] == 'positive' else "🔴" if n['label'] == 'negative' else "⚪"
                        st.write(f"{icon} **{n['title']}**")
            else:
                st.info("No sentiment data available.")
