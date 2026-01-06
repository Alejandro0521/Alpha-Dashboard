import sys
import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_banxico_series

# IDs
ID_RESERVAS = 'SF43707' 
TICKER_USDMXN = 'USDMXN=X'

def fetch_data():
    print("Fetching Risk Data (Advanced)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # 1. Fetch USD/MXN from Yahoo Finance for OHLC (Candles)
    print(f"Fetching {TICKER_USDMXN} for Candles...")
    try:
        df_fx = yf.download(TICKER_USDMXN, start=start_date, end=end_date, progress=False)
        # Handle MultiIndex common in new yfinance
        if isinstance(df_fx.columns, pd.MultiIndex):
            df_fx.columns = df_fx.columns.get_level_values(0)
    except Exception as e:
        print(f"Error fetching YFinance: {e}")
        df_fx = pd.DataFrame()
    
    # 2. Fetch Reservas from Banxico
    s_start = start_date.strftime('%Y-%m-%d')
    s_end = end_date.strftime('%Y-%m-%d')
    df_reservas = get_banxico_series(ID_RESERVAS, description="Reservas Internacionales")
    
    # Clean FX
    if not df_fx.empty:
        df_fx = df_fx[['Open', 'High', 'Low', 'Close']].copy()
        df_fx.dropna(inplace=True)
    
    return df_fx, df_reservas

def analyze_risk(df_fx, df_reservas):
    if df_fx.empty:
        return pd.DataFrame()

    # --- FX ANALYSIS ---
    # Bollinger Bands (20d, 2std)
    df_fx['SMA_20'] = df_fx['Close'].rolling(window=20).mean()
    df_fx['STD_20'] = df_fx['Close'].rolling(window=20).std()
    df_fx['Upper_Band'] = df_fx['SMA_20'] + (df_fx['STD_20'] * 2)
    df_fx['Lower_Band'] = df_fx['SMA_20'] - (df_fx['STD_20'] * 2)
    
    # Volatility Z-Score
    # Annualized Volatility (30d)
    df_fx['Log_Ret'] = np.log(df_fx['Close'] / df_fx['Close'].shift(1))
    df_fx['Volatility_30d'] = df_fx['Log_Ret'].rolling(window=30).std() * np.sqrt(252) * 100
    
    # Z-Score of Volatility (vs last 1 year mean/std of the volatility itself)
    vol_mean = df_fx['Volatility_30d'].mean()
    vol_std = df_fx['Volatility_30d'].std()
    df_fx['Vol_Z_Score'] = (df_fx['Volatility_30d'] - vol_mean) / (vol_std + 1e-9)
    
    # Check for Squeeze (Band Width)
    df_fx['Band_Width'] = (df_fx['Upper_Band'] - df_fx['Lower_Band']) / df_fx['SMA_20']
    
    # --- RESERVAS ANALYSIS ---
    # Merge Reservas logic later or save separately. 
    # For now, let's keep them separate in the return or merge to a daily summary.
    # We will save df_fx as the main risk data, and Reservas as a single current metric or separate csv.
    # Let's merge Reservas to daily fx index (ffill)
    
    if not df_reservas.empty:
        # Reindex Reservas
        # Ensure indexes are tz-naive
        if df_reservas.index.tz is not None: df_reservas.index = df_reservas.index.tz_localize(None)
        if df_fx.index.tz is not None: df_fx.index = df_fx.index.tz_localize(None)
        
        df_reservas = df_reservas.reindex(df_fx.index, method='ffill')
        df_fx['Reservas Internacionales'] = df_reservas['Reservas Internacionales']
    else:
        df_fx['Reservas Internacionales'] = np.nan
        
    return df_fx

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    df_fx, df_reservas = fetch_data()
    if df_fx.empty:
        print("No FX data fetched.")
        return
        
    df_analyzed = analyze_risk(df_fx, df_reservas)
    
    # Verify Columns
    print(f"Columns: {df_analyzed.columns}")
    
    df_analyzed.to_csv('risk_data.csv')
    print("Data saved to risk_data.csv")

    # Signals
    if not df_analyzed.empty:
        last = df_analyzed.iloc[-1]
        print("\n--- LATEST SIGNALS ---")
        print(f"Date: {last.name.date()}")
        print(f"USD/MXN: {last['Close']:.4f}")
        print(f"Bollinger: {last['Lower_Band']:.4f} - {last['Upper_Band']:.4f}")
        if 'Vol_Z_Score' in last:
            print(f"Vol Z-Score: {last['Vol_Z_Score']:.2f}")

if __name__ == "__main__":
    main()
