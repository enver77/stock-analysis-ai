import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Stock Analysis AI", layout="wide")

st.title("📈 Stock Analysis AI System")
st.markdown("Enter a stock symbol to analyze, or view undervalued stocks.")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Analysis", "Undervalued Stocks"])

def fetch_prediction(symbol):
    try:
        resp = requests.get(f"{API_URL}/predict/{symbol}")
        if resp.status_code == 200:
            return resp.json()
    except:
        return None
    return None

def fetch_analysis(symbol):
    try:
        resp = requests.get(f"{API_URL}/analyze/{symbol}")
        if resp.status_code == 200:
            return resp.json()
    except:
        return None
    return None

def fetch_undervalued(limit=5):
    try:
        resp = requests.get(f"{API_URL}/undervalued?limit={limit}")
        if resp.status_code == 200:
            return resp.json()['undervalued_stocks']
    except:
        return []
    return []

def fetch_sentiment(symbol):
    try:
        resp = requests.get(f"{API_URL}/sentiment/{symbol}")
        if resp.status_code == 200:
            return resp.json()
    except:
        return None
    return None

if page == "Analysis":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", value="AAPL").upper()
        if st.button("Analyze"):
            with st.spinner(f"Analyzing {symbol}..."):
                # Prediction
                pred_data = fetch_prediction(symbol)
                # Analysis
                analysis_data = fetch_analysis(symbol)
                # Sentiment
                sentiment_data = fetch_sentiment(symbol)
                
                if pred_data and analysis_data:
                    st.success("Analysis Complete!")
                    
                    # Store in session state to persist
                    st.session_state['pred_data'] = pred_data
                    st.session_state['analysis_data'] = analysis_data
                    st.session_state['sentiment_data'] = sentiment_data
                else:
                    st.error("Could not fetch data. Check API connection or Symbol.")

    # Display Results
    if 'pred_data' in st.session_state:
        pred = st.session_state['pred_data']
        anl = st.session_state['analysis_data']
        
        # Only show if symbol matches
        if pred['symbol'] == symbol:
            st.divider()
            
            # Key Metrics
            # DEBUG: Show Raw Data
            with st.expander("Debug: Raw API Response"):
                st.json(pred)

            # Key Metrics
            m1, m2 = st.columns(2)
            m1.metric("Current Price", f"${pred['current_price']:.2f}", 
                      delta_color="normal")
            m2.metric("Basic Strategy (SMA)", pred['prediction'], 
                      delta=f"vs SMA20 ({pred['sma_20']:.2f})",
                      delta_color="off")

            # Custom Model Display (Dedicated Section)
            custom = pred.get('custom_model', {})
            if custom:
                st.info(f"🎓 **Custom AdaBoost Model says:** {custom.get('prediction', 'N/A')} (Conf: {custom.get('confidence', 0)*100:.1f}%)")
            else:
                st.warning("Custom model data missing from API response.")
            
            # Ratios
            ratios = anl['ratios']
            st.subheader("Financial Ratios")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("P/E Ratio", f"{ratios.get('pe_ratio', 0):.2f}")
            r2.metric("P/B Ratio", f"{ratios.get('pb_ratio', 0):.2f}")
            r3.metric("ROE", f"{ratios.get('roe', 0):.2f}%")
            r4.metric("Debt/Equity", f"{ratios.get('debt_to_equity', 0):.2f}")

            # Sentiment Analysis
            if 'sentiment_data' in st.session_state and st.session_state['sentiment_data']:
                sent = st.session_state['sentiment_data']
                st.subheader("📰 AI News Sentiment Analysis (FinBERT)")
                
                s_col1, s_col2 = st.columns([1, 2])
                with s_col1:
                    overall = sent.get('overall_sentiment', 'Neutral')
                    s_color = "green" if overall == "Positive" else "red" if overall == "Negative" else "gray"
                    st.markdown(f"### Overall: :{s_color}[{overall}]")
                    st.write(f"Aggregated Score: {sent.get('sentiment_score', 0):.2f}")
                
                with s_col2:
                    st.write("**Latest Analyzed Headlines:**")
                    news = sent.get('news', [])
                    if news:
                        for n in news:
                            label = n['label']
                            icon = "🟢" if label == 'positive' else "🔴" if label == 'negative' else "⚪"
                            st.write(f"{icon} **{n['title']}** ({n['score']:.2f})")
                    else:
                        st.info("No recent news found to analyze.")

elif page == "Undervalued Stocks":
    st.header("💎 Undervalued Stocks Gems")
    st.markdown("Stocks with **low P/E**, **low P/B**, and **high ROE**.")
    
    limit = st.slider("Number of stocks", 3, 10, 5)
    
    if st.button("Find Gems"):
        with st.spinner("Scanning market..."):
            undervalued = fetch_undervalued(limit)
            
            if undervalued:
                for stock in undervalued:
                    with st.expander(f"{stock['symbol']} (Score: {stock['score']}/4)"):
                        c1, c2 = st.columns(2)
                        c1.write(f"**P/E Ratio**: {stock['pe_ratio']:.2f}")
                        c2.write(f"**ROE**: {stock['roe']:.2f}%")
            else:
                st.warning("No undervalued stocks found with current strict criteria.")
