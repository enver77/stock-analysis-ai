import pandas as pd
import numpy as np

class FinancialAnalyzer:
    """
    Analyzes financial data and calculates ratios/trends.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def calculate_ratios(self, symbol: str):
        """
        Calculates financial ratios based on available data.
        Returns an object (dot-accessible dict) with specific keys expected by MCP.
        """
        data = self.data_manager.get_financials(symbol)
        if not data or not data.get('info'):
            return self._empty_ratios()

        info = data['info']
        
        # Helper to safely get value
        def get_val(key, default=0.0):
            return float(info.get(key, default) or 0.0)

        # Mapping yfinance info keys to our expected structure
        # Note: yfinance keys change sometimes, this is a best-effort mapping for common keys
        
        class Ratios:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        return Ratios(
            # Profitability
            roe=get_val('returnOnEquity', 0) * 100,
            roa=get_val('returnOnAssets', 0) * 100,
            net_profit_margin=get_val('profitMargins', 0) * 100,
            gross_profit_margin=get_val('grossMargins', 0) * 100,

            # Liquidity (Current/Quick often in info, or calc from balance sheet)
            current_ratio=get_val('currentRatio'),
            quick_ratio=get_val('quickRatio'),
            cash_ratio=0.0, # detailed calc needed often not in simple info

            # Leverage
            debt_to_equity=get_val('debtToEquity', 0) / 100.0 if get_val('debtToEquity') else 0.0,
            debt_to_assets=0.0, # complex calc from balance sheet
            equity_multiplier=0.0, # complex calc

            # Efficiency
            asset_turnover=0.0, # complex calc from financials
            inventory_turnover=0.0, # complex calc
            receivables_turnover=0.0, # complex calc

            # Valuation
            pe_ratio=get_val('trailingPE'),
            pb_ratio=get_val('priceToBook'),
            market_cap=get_val('marketCap')
        )

    def _empty_ratios(self):
        class Ratios:
             pass
        r = Ratios()
        for k in ['roe','roa','net_profit_margin','gross_profit_margin','current_ratio','quick_ratio','cash_ratio',
                  'debt_to_equity','debt_to_assets','equity_multiplier','asset_turnover','inventory_turnover',
                  'receivables_turnover','pe_ratio','pb_ratio','market_cap']:
            setattr(r, k, 0.0)
        return r

    def trend_analysis(self, symbol: str):
        """
        Analyze stock trends (SMA, volatility, etc.)
        """
        # This function acts as a placeholder for the logic in MCP.
        # The MCP implementation actually calls `get_stock_data` and computes some trend logic itself 
        # OR it calls this. We'll populate it to be useful.
        
        return {
            'periods': ['1mo', '3mo', '6mo', '1y']
        }

    def compare_companies(self, symbols: list):
        """
        Compares multiple companies.
        """
        results = []
        for sym in symbols:
            r = self.calculate_ratios(sym)
            results.append({
                'Symbol': sym,
                'ROE': r.roe,
                'PE': r.pe_ratio,
                'PB': r.pb_ratio,
                'Debt/Equity': r.debt_to_equity
            })
        return pd.DataFrame(results)

    def find_undervalued_stocks(self, limit: int = 5):
        """
        Finds undervalued stocks from a predefined list.
        """
        # In a real app, this would scan a database.
        # Here we scan a small hardcoded list for demonstration + S&P 500 examples.
        # S&P 100 Tickers
        candidates = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V', 'UNH', 
            'JNJ', 'XOM', 'JPM', 'PG', 'MA', 'LLY', 'HD', 'CVX', 'MRK', 'ABBV', 
            'PEP', 'KO', 'AVGO', 'COST', 'TMO', 'MCD', 'CSCO', 'ACN', 'WMT', 'PFE', 
            'BAC', 'LIN', 'CRM', 'ABT', 'DIS', 'AMD', 'DHR', 'TXN', 'NEE', 'PM', 
            'WFC', 'ADBE', 'NKE', 'UPS', 'RTX', 'BMY', 'T', 'LOW', 'INTC', 'MS', 
            'QCOM', 'HON', 'IBM', 'UNP', 'INTU', 'SBUX', 'GE', 'EL', 'DE', 'GS', 
            'AMAT', 'C', 'CAT', 'PLD', 'BLK', 'BA', 'SCHW', 'CVS', 'AMT', 'MMC', 
            'COP', 'LMT', 'ADP', 'AXP', 'MDT', 'CI', 'GILD', 'ISRG', 'TJX', 'VRTX', 
            'TGT', 'MO', 'ZTS', 'EOG', 'BDX', 'SO', 'FI', 'SPGI', 'REGN', 'NOW', 
            'SYK', 'CB', 'BKNG', 'DUK', 'LRCX', 'ADI', 'Z', 'UBER', 'ABNB', 'PANW'
        ]
        results = []
        
        for sym in candidates:
            r = self.calculate_ratios(sym)
            score = 0
            if 0 < r.pe_ratio < 25: score += 1
            if 0 < r.pb_ratio < 5: score += 1
            if r.roe > 15: score += 1
            if r.debt_to_equity < 1.0: score += 1
            
            if score >= 3:
                results.append({
                    "symbol": sym,
                    "score": score,
                    "pe_ratio": r.pe_ratio,
                    "roe": r.roe
                })
        
        # Sort by score desc
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
