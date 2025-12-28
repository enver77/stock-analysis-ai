from fastmcp import FastMCP
import requests

# Create an MCP server
mcp = FastMCP("Stock Analysis MCP")

# Backend API URL
API_URL = "http://localhost:8000"

@mcp.tool()
def get_stock_prediction(symbol: str) -> str:
    """
    Get a prediction (UP/DOWN) for a specific stock symbol based on its 20-day SMA.
    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT).
    """
    try:
        response = requests.get(f"{API_URL}/predict/{symbol}")
        if response.status_code == 200:
            data = response.json()
            return f"Prediction for {symbol}: {data['prediction']} (Current Price: {data['current_price']:.2f}, SMA20: {data['sma_20']:.2f})"
        else:
            return f"Error: Could not fetch prediction for {symbol}. (Status: {response.status_code})"
    except Exception as e:
        return f"Error connecting to API: {str(e)}"

@mcp.tool()
def get_financial_analysis(symbol: str) -> str:
    """
    Get detailed financial ratios (P/E, ROE, Debt/Equity) for a stock.
    Args:
        symbol: The stock ticker symbol.
    """
    try:
        response = requests.get(f"{API_URL}/analyze/{symbol}")
        if response.status_code == 200:
            data = response.json()
            r = data['ratios']
            return (f"Financial Analysis for {symbol}:\n"
                    f"- P/E Ratio: {r.get('pe_ratio', 'N/A')}\n"
                    f"- P/B Ratio: {r.get('pb_ratio', 'N/A')}\n"
                    f"- ROE: {r.get('roe', 'N/A')}%\n"
                    f"- Debt/Equity: {r.get('debt_to_equity', 'N/A')}")
        else:
            return f"Error: Could not fetch analysis for {symbol}."
    except Exception as e:
        return f"Error connecting to API: {str(e)}"

@mcp.tool()
def find_undervalued_stocks(limit: int = 5) -> str:
    """
    Find a list of potentially undervalued stocks based on financial criteria (Low P/E, High ROE).
    Args:
       limit: Maximum number of stocks to return (default 5).
    """
    try:
        response = requests.get(f"{API_URL}/undervalued?limit={limit}")
        if response.status_code == 200:
            data = response.json()
            stocks = data['undervalued_stocks']
            if not stocks:
                return "No undervalued stocks found matching the criteria."
            
            result = "Undervalued Stocks Recommendations:\n"
            for s in stocks:
                result += f"- {s['symbol']} (Score: {s['score']}/4) | P/E: {s.get('pe_ratio', 'N/A')} | ROE: {s.get('roe', 'N/A')}%\n"
            return result
        else:
            return "Error: Could not fetch undervalued stocks."
    except Exception as e:
        return f"Error connecting to API: {str(e)}"

@mcp.tool()
def get_stock_sentiment(symbol: str) -> str:
    """
    Get the AI-driven sentiment analysis (Positive/Negative/Neutral) and news for a stock.
    Args:
        symbol: The stock ticker symbol.
    """
    try:
        response = requests.get(f"{API_URL}/sentiment/{symbol}")
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                return f"Error analyzing sentiment: {data['error']}"
            
            result = f"Sentiment Analysis for {symbol}:\n"
            result += f"Overall: {data['overall_sentiment']} (Score: {data['sentiment_score']:.2f})\n"
            result += "Top News Headlines:\n"
            for news in data['news']:
                result += f"- [{news['label']}] {news['title']}\n"
            return result
        else:
            return f"Error: Could not fetch sentiment for {symbol}."
    except Exception as e:
        return f"Error connecting to API: {str(e)}"

if __name__ == "__main__":
    # This entry point is used when running directly securely
    mcp.run()
