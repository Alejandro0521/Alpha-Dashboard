"""
US Stock Radar - Magnificent 7 Analysis
Fetches stock data, calculates RSI and SMA crossovers for buy/sell signals
"""

import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

# Configuration
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
COMPANY_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft", 
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "Nvidia",
    "META": "Meta",
    "TSLA": "Tesla"
}

# Output path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "us_stocks_data.csv")


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_signal(sma50, sma200, rsi):
    """Generate trading signal based on SMA crossover and RSI"""
    # SMA Crossover Logic
    if sma50 > sma200 * 1.02:  # Golden Cross (with 2% buffer)
        cross_signal = "COMPRAR"
    elif sma50 < sma200 * 0.98:  # Death Cross (with 2% buffer)
        cross_signal = "VENDER"
    else:
        cross_signal = "MANTENER"
    
    # RSI Override
    if rsi > 75:
        return "SOBRECOMPRA"
    elif rsi < 25:
        return "SOBREVENTA"
    
    return cross_signal


def fetch_stock_data(ticker):
    """Fetch stock data and calculate indicators"""
    try:
        stock = yf.Ticker(ticker)
        # Get 1 year of data for SMA200 calculation
        df = stock.history(period="1y")
        
        if df.empty:
            print(f"No data for {ticker}")
            return None
        
        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate indicators
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['RSI'] = calculate_rsi(df['Close'], 14)
        
        # Get latest values
        latest = df.iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest['Close']
        
        # Calculate change
        change = latest['Close'] - prev_close
        change_pct = (change / prev_close) * 100
        
        # Generate signal
        sma50 = latest['SMA50'] if pd.notna(latest['SMA50']) else latest['Close']
        sma200 = latest['SMA200'] if pd.notna(latest['SMA200']) else latest['Close']
        rsi = latest['RSI'] if pd.notna(latest['RSI']) else 50
        
        signal = get_signal(sma50, sma200, rsi)
        
        # Get last 30 days for sparkline
        last_30_prices = df['Close'].tail(30).tolist()
        price_history = [round(p, 2) for p in last_30_prices]
        
        return {
            "ticker": ticker,
            "name": COMPANY_NAMES.get(ticker, ticker),
            "price": round(latest['Close'], 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "rsi": round(rsi, 1),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "signal": signal,
            "date": df.index[-1].strftime("%Y-%m-%d"),
            "price_history": price_history
        }
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def main():
    print("Fetching US Stock Data (Magnificent 7)...")
    
    results = []
    for ticker in TICKERS:
        print(f"  Processing {ticker}...")
        data = fetch_stock_data(ticker)
        if data:
            results.append(data)
    
    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"Data saved to {OUTPUT_PATH}")
        print(f"  {len(results)} stocks processed successfully")
    else:
        print("No data was fetched")


if __name__ == "__main__":
    main()
