import sys
import argparse
from data_layer import BISTDataManager
from analysis_layer import FinancialAnalyzer
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description='Stock Analysis Tool')
    parser.add_argument('symbol', type=str, help='Stock symbol (e.g., AAPL, THYAO)')
    parser.add_argument('--period', type=str, default='1y', help='Data period (default: 1y)')
    parser.add_argument('--no-plot', action='store_true', help='Disable plotting')
    
    args = parser.parse_args()
    
    symbol = args.symbol.upper()
    print(f"Analyzing {symbol}...")
    
    # Init layers
    dm = BISTDataManager()
    analyzer = FinancialAnalyzer(dm)
    
    # Get Data
    df = dm.get_stock_data(symbol, period=args.period)
    if df.empty:
        print("No price data found.")
        sys.exit(1)
        
    print(f"Data retrieved: {len(df)} records from {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Latest Close: {df['Close'].iloc[-1]:.2f}")
    
    # Get Ratios
    ratios = analyzer.calculate_ratios(symbol)
    print("\n--- Key Ratios ---")
    print(f"P/E: {ratios.pe_ratio:.2f}")
    print(f"P/B: {ratios.pb_ratio:.2f}")
    print(f"ROE: {ratios.roe:.2f}%")
    print(f"Debt/Equity: {ratios.debt_to_equity:.2f}")

    # Plotting
    if not args.no_plot:
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df['Close'], label='Close Price')
            
            # Simple Moving Average
            if len(df) > 20:
                sma20 = df['Close'].rolling(window=20).mean()
                plt.plot(df.index, sma20, label='SMA 20')
                
            plt.title(f"{symbol} Stock Price ({args.period})")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.grid(True)
            
            output_file = f"{symbol}_chart.png"
            plt.savefig(output_file)
            print(f"\nChart saved to {output_file}")
            
        except Exception as e:
            print(f"Could not generate plot: {e}")

if __name__ == "__main__":
    main()
