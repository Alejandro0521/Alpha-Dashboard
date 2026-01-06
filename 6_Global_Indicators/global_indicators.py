"""
Global Market Indicators - VIX, S&P 500, Nasdaq, WTI Oil, Gold
Fetches key global market indicators from Yahoo Finance
"""

import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# Yahoo Finance tickers for global indicators
INDICATORS = {
    "^VIX": {"name": "VIX (Índice del Miedo)", "category": "volatility"},
    "^GSPC": {"name": "S&P 500", "category": "index"},
    "^IXIC": {"name": "Nasdaq", "category": "index"},
    "CL=F": {"name": "Petróleo WTI", "category": "commodity"},
    "GC=F": {"name": "Oro", "category": "commodity"}
}

# Output path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "global_indicators_data.csv")


def fetch_indicator(ticker, info):
    """Fetch indicator data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        # Get last 30 days for sparkline
        df = stock.history(period="1mo")
        
        if df.empty:
            print(f"No data for {ticker}")
            return None
        
        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        latest = df.iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest['Close']
        
        # Calculate change
        change = latest['Close'] - prev_close
        change_pct = (change / prev_close) * 100
        
        # Get price history for sparkline
        price_history = [round(p, 2) for p in df['Close'].tail(30).tolist()]
        
        return {
            "ticker": ticker,
            "name": info["name"],
            "category": info["category"],
            "price": round(latest['Close'], 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "date": df.index[-1].strftime("%Y-%m-%d"),
            "price_history": price_history
        }
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def main():
    print("Fetching Global Market Indicators...")
    
    results = []
    for ticker, info in INDICATORS.items():
        print(f"  Processing {info['name']}...")
        data = fetch_indicator(ticker, info)
        if data:
            results.append(data)
    
    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"Data saved to {OUTPUT_PATH}")
        print(f"  {len(results)} indicators processed successfully")
    else:
        print("No data was fetched")


if __name__ == "__main__":
    main()
