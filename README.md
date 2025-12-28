# 📈 Stock Analysis AI System (MIS453 Project)

**Empowering Investment with Hybrid AI Intelligence**

![Deployment Status](https://img.shields.io/badge/Deployment-Automated%20with%20GitHub%20Actions-blue)

This application helps investors identify undervalued stocks and predict market movements by combining two powerful Artificial Intelligence approaches:
1.  **Quantitative Machine Learning (Custom Trained)**: An AdaBoost Classifier trained on 5 years of historical S&P 500 data.
2.  **Natural Language Processing (State-of-the-Art)**: Hugging Face's `ProsusAI/finbert` model for financial news sentiment analysis.

---

## 🚀 Live Demo
Access the running application on Hugging Face Spaces:
**[Insert Your Hugging Face Space URL Here]**

---

## 🧠 AI Models Explained

### 1. The "Academic" Model (Quantitative)
*   **Algorithm**: AdaBoost Classifier (Decision Tree Ensemble)
*   **Training Data**: 5 Years of S&P 500 (SPY) daily price data.
*   **Features Engineered**:
    *   `RSI` (Relative Strength Index) for momentum.
    *   `SMA_Distance` (Distance from 20/50 day moving averages).
    *   `Volume_Change` (Market activity shifts).
*   **Purpose**: Predicts if the stock price will go **UP** or **DOWN** the next trading day based purely on mathematical patterns.

### 2. The "Sentiment" Model (Qualitative)
*   **Model**: `ProsusAI/finbert` (Based on BERT)
*   **Source**: Hugging Face Transformers.
*   **Input**: Real-time news headlines from Yahoo Finance.
*   **Purpose**: Reads the news like a human analyst and scores sentiment (Positive/Negative/Neutral) to capture market psychology.

---

## 🛠️ Technology Stack
*   **Frontend**: Streamlit (Python-based UI)
*   **Backend**: FastAPI (High-performance API)
*   **AI/ML**: `scikit-learn` (AdaBoost), `transformers` (FinBERT), `pytorch`
*   **Data**: `yfinance` (Real-time market data)
*   **Deployment**: Docker & Hugging Face Spaces
*   **Agent Integration**: MCP (Model Context Protocol) Server included for Agent-based interaction.

---

## 🏃‍♂️ How to Run Locally

### Prerequisites
*   Python 3.10+
*   Pip

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone <your-repo-url>
cd project_453
pip install -r stock/requirements.txt
```

### 2. Run the Backend API
This server hosts the AI models and data logic.
```bash
python stock/api.py
```
*Wait for "Application startup complete" message.*

### 3. Run the Frontend Dashboard
Open a new terminal window:
```bash
streamlit run frontend/frontend_app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment
You can also run the entire system using our unified Docker image (same as the production deployment):

```bash
cd stock
docker build -t stock-ai .
docker run -p 8501:8501 stock-ai
```

---

## 📂 Project Structure
*   `stock/`: Core backend, AI models, and training scripts.
    *   `build_model.py`: Script used to train the AdaBoost model.
    *   `api.py`: FastAPI server handling predictions.
    *   `adaboost_model.joblib`: The saved trained model artifact.
*   `frontend/`: Streamlit user interface code.
*   `mcp_server/`: Agent integration layer.

---

**Student**: Enver Erman
**Course**: MIS453
**Date**: December 2025
